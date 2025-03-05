resource "aws_cloudwatch_event_rule" "eb_creation_successful" {
  name        = "eb-creation-successful"
  description = "Elastic Beanstalk 환경 생성 완료 시 도메인 매핑 및 waf web-acl 추가"

  event_pattern = jsonencode({
    source      = ["aws.elasticbeanstalk"]
    detail-type = ["Elastic Beanstalk resource status change"]
    detail = {
      Status          = ["Environment creation successful"]
      EnvironmentName = keys(var.eb_environments)
    }
  })
}

resource "aws_cloudwatch_event_target" "postdeploy_eb" {
  rule      = aws_cloudwatch_event_rule.eb_creation_successful.name
  target_id = "PostdeployEB"
  arn       = var.lambda_postdeploy_eb_arn

  retry_policy {
    maximum_event_age_in_seconds = 3600
    maximum_retry_attempts       = 2
  }
}

resource "aws_lambda_permission" "allow_eventbridge_update_domain" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_postdeploy_eb_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.eb_creation_successful.arn
}
