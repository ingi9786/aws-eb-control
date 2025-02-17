import boto3
import json
import os


def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")

        project_name = "sense-dev"
        # project_name = get_project_name(event)
        # if not project_name:
        #     return {"statusCode": 400, "body": "project_name is required"}

        # 환경변수에서 JSON 문자열 가져오기
        eb_environments_json = os.environ.get("EB_ENVIRONMENTS", "{}")

        # JSON 문자열을 Python 딕셔너리로 변환
        eb_environments_dict = json.loads(eb_environments_json)
        config = eb_environments_dict.get(project_name)
        if not config:
            return {"statusCode": 400, "body": f"Unknown project: {project_name}"}

        eb = boto3.client("elasticbeanstalk")
        response = eb.create_environment(
            ApplicationName=config["application_name"],
            EnvironmentName=config["environment_name"],
            TemplateName=config["template_name"],
        )

        success_message = f"Environment creation started for {project_name}. Environment ID: {response['EnvironmentId']}"
        print(success_message)

        return {"statusCode": 200, "body": success_message}

    except Exception as e:
        error_message = f"Error creating environment: {str(e)}"
        print(f"Error: {error_message}")
        return {"statusCode": 500, "body": error_message}
