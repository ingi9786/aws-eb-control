import boto3
import json
import os


def get_latest_version_from_s3(s3_client, bucket_name: str, application_name: str):
    """S3 버킷에서 저장된 version 정보 가져오기"""
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=f"version_info.json")
        version_info = json.loads(response["Body"].read().decode("utf-8"))
        return version_info.get(application_name)["version_label"]
    except Exception as e:
        print(f"Error reading version from S3: {str(e)}")
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
        started_envs = []

        for env_name in requested_envs:
            config = eb_environments_dict.get(env_name)
            if not config:
                print(f"Unknown project: {env_name}")
                continue

            version_label = get_latest_version_from_s3(
                s3, bucket_name, config["environment_name"]
            )
            if not version_label:
                print(f"Version not found for {config['environment_name']}")
                continue

            response = eb.create_environment(
                ApplicationName=config["application_name"],
                EnvironmentName=config["environment_name"],
                TemplateName=config["template_name"],
                VersionLabel=version_label,
            )
            started_envs.append(
                {
                    "environment_name": config["environment_name"],
                    "version": version_label,
                }
            )

        return {"statusCode": 200, "body": json.dumps({"started_envs": started_envs})}

    except Exception as e:
        error_message = f"Error starting environments: {str(e)}"
        print(f"Error: {error_message}")
        return {"statusCode": 500, "body": error_message}
