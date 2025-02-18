import boto3
import json
import os
from datetime import datetime


def store_version_info_to_s3(
    s3_client, bucket_name: str, application_name: str, version_label: str
):
    """현재 환경의 version을 S3 버킷에 적재"""
    version_info = {
        "version_label": version_label,
        "stored_at": datetime.now().isoformat(),
    }

    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{application_name}/version_info.json",
        Body=json.dumps(version_info),
    )


def save_environment_configuration(
    eb_client,
    application_name: str,
    environment_name: str,
    template_name: str,
):
    """현재 환경의 configuration을 저장"""
    try:
        env_response = eb_client.describe_environments(
            ApplicationName=application_name, EnvironmentNames=[environment_name]
        )

        if not env_response["Environments"]:
            raise Exception(f"Environment {environment_name} not found")

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
        template_response = eb_client.create_configuration_template(
            ApplicationName=application_name,
            TemplateName=template_name,
            EnvironmentId=environment_id,
        )

        print(f"Saved configuration template: {template_name}")
        return template_response, current_version

    except Exception as e:
        print(f"Error saving configuration: {str(e)}")
        raise


def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")

        project_name = "sense-dev"
        eb_environments_json = os.environ.get("EB_ENVIRONMENTS", "{}")
        eb_environments_dict = json.loads(eb_environments_json)
        config = eb_environments_dict.get(project_name)

        if not config:
            return {"statusCode": 400, "body": f"Unknown project: {project_name}"}

        bucket_name = os.environ.get("EB_S3_BUCKET_NAME")
        if not bucket_name:
            return {
                "statusCode": 500,
                "body": "EB_S3_BUCKET_NAME environment variable is not set",
            }

        eb = boto3.client("elasticbeanstalk")
        s3 = boto3.client("s3")

        try:
            _, current_version = save_environment_configuration(
                eb,
                config["application_name"],
                config["environment_name"],
                config["template_name"],
            )

            store_version_info_to_s3(
                s3, bucket_name, config["application_name"], current_version
            )
        except Exception as save_error:
            return {
                "statusCode": 500,
                "body": f"Warning: Failed to save configuration: {str(save_error)}",
            }

        # 환경 종료
        response = eb.terminate_environment(EnvironmentName=config["environment_name"])

        success_message = f"Environment termination started for {project_name}. Environment ID: {response['EnvironmentId']}"
        print(success_message)

        return {"statusCode": 200, "body": success_message}

    except Exception as e:
        error_message = f"Error terminating environment: {str(e)}"
        print(f"Error: {error_message}")
        return {"statusCode": 500, "body": error_message}
