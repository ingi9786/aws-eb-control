import boto3
import json
import os


def get_latest_version_from_s3(s3_client, bucket_name: str, application_name: str):
    """S3 버킷에서 저장된 version 정보 가져오기"""
    try:
        response = s3_client.get_object(
            Bucket=bucket_name, Key=f"{application_name}/version_info.json"
        )
        version_info = json.loads(response["Body"].read().decode("utf-8"))
        return version_info.get("version_label")
    except Exception as e:
        print(f"Error reading version from S3: {str(e)}")
        return


def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")

        project_name = "sense-dev"
        eb_environments_json = os.environ.get("EB_ENVIRONMENTS", "{}")
        eb_environments_dict = json.loads(eb_environments_json)
        config = eb_environments_dict.get(project_name)

        if not config:
            return {"statusCode": 400, "body": f"Unknown project: {project_name}"}

        eb = boto3.client("elasticbeanstalk")
        s3 = boto3.client("s3")

        bucket_name = os.environ.get("EB_S3_BUCKET_NAME")
        if not bucket_name:
            return {
                "statusCode": 500,
                "body": "EB_S3_BUCKET_NAME environment variable is not set",
            }

        version_label = get_latest_version_from_s3(
            s3, bucket_name, config["application_name"]
        )

        if not version_label:
            return {
                "statusCode": 404,
                "body": f"Not Found {config['application_name']}",
            }

        # 환경 생성
        response = eb.create_environment(
            ApplicationName=config["application_name"],
            EnvironmentName=config["environment_name"],
            TemplateName=config["template_name"],
            VersionLabel=version_label,
        )

        success_message = (
            f"Environment creation started for {project_name}.\n"
            f"Environment ID: {response['EnvironmentId']}\n"
            f"Using version: {version_label}"
        )
        print(success_message)

        return {"statusCode": 200, "body": success_message}

    except Exception as e:
        error_message = f"Error creating environment: {str(e)}"
        print(f"Error: {error_message}")
        return {"statusCode": 500, "body": error_message}
