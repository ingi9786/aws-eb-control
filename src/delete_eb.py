import boto3
import json
import os
from datetime import datetime


def update_version_info_in_s3(s3_client, bucket_name: str, updated_versions: dict):
    """S3의 version_info.json을 한 번만 업데이트 (없으면 생성)"""
    try:
        # 기존 version_info.json 불러오기 (없을 경우 예외 발생)
        response = s3_client.get_object(Bucket=bucket_name, Key="version_info.json")
        version_info = json.loads(response["Body"].read().decode("utf-8"))
    except s3_client.exceptions.NoSuchKey:
        print("version_info.json does not exist in S3. Creating a new one...")
        version_info = {}

    # 여러 환경의 버전 정보 한꺼번에 업데이트
    version_info.update(updated_versions)

    try:
        # 최종적으로 한 번만 S3에 저장
        s3_client.put_object(
            Bucket=bucket_name,
            Key="version_info.json",
            Body=json.dumps(version_info, indent=2),
            ContentType="application/json",
        )
        print(
            f"Successfully updated version info for {list(updated_versions.keys())} in S3"
        )
    except Exception as e:
        print(f"Error updating version_info.json in S3: {str(e)}")


def save_environment_configuration(
    eb_client, application_name: str, environment_name: str, template_name: str
):
    """현재 환경의 설정을 저장"""
    try:
        env_response = eb_client.describe_environments(
            ApplicationName=application_name, EnvironmentNames=[environment_name]
        )

        if not env_response["Environments"]:
            print(f"Environment {environment_name} not found")
            return None

        environment = env_response["Environments"][0]
        environment_id = environment["EnvironmentId"]
        current_version = environment["VersionLabel"]

        # 기존 템플릿이 있다면 삭제
        try:
            eb_client.delete_configuration_template(
                ApplicationName=application_name, TemplateName=template_name
            )
        except eb_client.exceptions.ResourceNotFoundException:
            pass

        # 현재 설정을 새 템플릿으로 저장
        eb_client.create_configuration_template(
            ApplicationName=application_name,
            TemplateName=template_name,
            EnvironmentId=environment_id,
        )

        print(f"Saved configuration template for {environment_name}")
        return current_version

    except Exception as e:
        print(f"Error saving configuration for {environment_name}: {str(e)}")
        return None


def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")

        eb = boto3.client("elasticbeanstalk")
        s3 = boto3.client("s3")

        bucket_name = os.environ.get("EB_S3_BUCKET_NAME")
        if not bucket_name:
            return {
                "statusCode": 500,
                "body": "EB_S3_BUCKET_NAME environment variable is not set",
            }

        eb_environments_json = os.environ.get("EB_ENVIRONMENTS", "{}")
        eb_environments_dict = json.loads(eb_environments_json)

        requested_envs = event.get("environments", list(eb_environments_dict.keys()))
        stopped_envs = []
        updated_versions = {}

        # 한 번의 describe 호출로 모든 환경 정보 가져오기
        env_response = eb.describe_environments(
            EnvironmentNames=[
                config["environment_name"] for config in eb_environments_dict.values()
            ]
        )
        env_dict = {env["EnvironmentName"]: env for env in env_response["Environments"]}

        for env_name in requested_envs:
            config = eb_environments_dict.get(env_name)
            if not config:
                print(f"Unknown project: {env_name}")
                continue

            environment = env_dict.get(config["environment_name"])
            if not environment:
                print(f"Environment {config['environment_name']} not found")
                continue

            current_version = environment["VersionLabel"]
            updated_versions[env_name] = {
                "version_label": current_version,
                "stored_at": datetime.now().isoformat(),
            }

            # 환경 설정 저장
            save_environment_configuration(
                eb,
                config["application_name"],
                config["environment_name"],
                config["template_name"],
            )

            # EB 환경 종료
            response = eb.terminate_environment(
                EnvironmentName=config["environment_name"]
            )
            stopped_envs.append(
                {
                    "environment_name": config["environment_name"],
                }
            )

        # S3에 한 번만 저장
        if updated_versions:
            update_version_info_in_s3(s3, bucket_name, updated_versions)

        return {"statusCode": 200, "body": json.dumps({"stopped_envs": stopped_envs})}

    except Exception as e:
        error_message = f"Error stopping environments: {str(e)}"
        print(f"Error: {error_message}")
        return {"statusCode": 500, "body": error_message}
