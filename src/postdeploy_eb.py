import boto3
import json
import os


def get_environment_info(eb_client, environment_name: str):
    """Elastic Beanstalk 환경 정보 가져오기"""
    # 환경의 리소스 조회
    resources = eb_client.describe_environment_resources(
        EnvironmentName=environment_name
    )
    print(f"Environment Resources: {json.dumps(resources, default=str)}")

    # 환경 리소스: 로드 밸런서 정보 찾기
    if not resources["EnvironmentResources"]["LoadBalancers"]:
        raise Exception(f"No load balancer found for environment {environment_name}")

    load_balancer = resources["EnvironmentResources"]["LoadBalancers"][0]
    print(f"Load Balancer info: {json.dumps(load_balancer, default=str)}")

    # 로드밸런서 host-zone-id와 domain 조회
    elb = boto3.client("elbv2")
    elb_response = elb.describe_load_balancers(LoadBalancerArns=[load_balancer["Name"]])
    print(f"ELB Response: {json.dumps(elb_response, default=str)}")

    if not elb_response["LoadBalancers"]:
        raise Exception("Load balancer details not found")

    elb_info = elb_response["LoadBalancers"][0]
    hosted_zone_id = elb_info["CanonicalHostedZoneId"]
    dns_name = elb_info["DNSName"]
    load_balancer_arn = load_balancer["Name"]

    return {
        "domain": dns_name,
        "load_balancer_hosted_zone_id": hosted_zone_id,
        "load_balancer_arn": load_balancer_arn,
    }


def associate_waf_to_alb(wafv2_client, web_acl_arn: str, load_balancer_arn: str):
    """WAF Web ACL을 Application Load Balancer에 연결"""
    try:
        response = wafv2_client.associate_web_acl(
            WebACLArn=web_acl_arn, ResourceArn=load_balancer_arn
        )
        print(
            f"Successfully associated WAF Web ACL to ALB: {json.dumps(response, default=str)}"
        )
        return response
    except wafv2_client.exceptions.WAFInvalidParameterException:
        print(f"WAF Web ACL is already associated with the ALB")
        return None
    except Exception as e:
        print(f"Error associating WAF Web ACL to ALB: {str(e)}")
        raise


def update_alias_records(
    route53,
    hosted_zone_id: str,
    target_domains: list,
    elb_domain: str,
    elb_hosted_zone_id: str,
):
    """Route 53의 A 레코드 Alias 업데이트"""
    changes = [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": domain,
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": elb_hosted_zone_id,
                    "DNSName": elb_domain,
                    "EvaluateTargetHealth": True,
                },
            },
        }
        for domain in target_domains
    ]

    response = route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
    )
    return response


def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")

        environment_name = event["detail"]["EnvironmentName"]
        domain_mappings_json = os.environ.get("DOMAIN_MAPPINGS", "{}")
        web_acl_arn = os.environ.get("WAF_WEB_ACL_ARN")

        if not web_acl_arn:
            raise ValueError("WAF_WEB_ACL_ARN environment variable is not set")

        try:
            domain_mappings = json.loads(domain_mappings_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid DOMAIN_MAPPINGS JSON in environment variable")

        project_config = domain_mappings.get(environment_name)
        if not project_config:
            raise ValueError(
                f"No configuration found for environment: {environment_name}"
            )

        hosted_zone_id = project_config.get("hosted_zone_id")
        target_domains = project_config.get("domains", [])

        if not hosted_zone_id or not target_domains:
            raise ValueError(
                f"Missing hosted_zone_id or domains for environment: {environment_name}"
            )

        # EB 환경 정보 가져오기
        eb = boto3.client("elasticbeanstalk")
        env_info = get_environment_info(eb, environment_name)

        # WAF Web ACL 연결
        wafv2 = boto3.client("wafv2")
        associate_waf_to_alb(wafv2, web_acl_arn, env_info["load_balancer_arn"])

        # Route 53 레코드 업데이트
        route53 = boto3.client("route53")
        update_alias_records(
            route53,
            hosted_zone_id,
            target_domains,
            env_info["domain"],
            env_info["load_balancer_hosted_zone_id"],
        )

        print(
            f"Updated A records with Alias: {', '.join(target_domains)} -> {env_info['domain']}"
        )
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": f"Successfully updated domains and associated WAF Web ACL",
                    "updated_domains": target_domains,
                }
            ),
        }

    except Exception as e:
        error_message = f"Error updating domains: {str(e)}"
        print(f"Error: {error_message}")
        return {"statusCode": 500, "body": json.dumps({"error": error_message})}
