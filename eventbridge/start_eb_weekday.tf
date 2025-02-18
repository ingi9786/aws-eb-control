# EventBridge 규칙 생성
resource "aws_cloudwatch_event_rule" "start_eb_daily" {
  name                = "start-eb-environment-daily"
  description         = "Start EB environment every weekday at 8 AM KST"
  schedule_expression = "cron(0 23 ? * 1-5 *)"  # UTC 23시 = KST 8시
}

# EventBridge 규칙 target으로 Lambda 함수 연결
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.start_eb_daily.name
  target_id = "StartEBEnvironment"
  arn       = var.lambda_create_eb_arn

  # Lambda에 전달할 입력 값
  input = jsonencode({
    source = "aws.events"
    detail = {
      project_name = keys(var.eb_environments)[0]
    }
  })
}

# 람다 리소스 기반 정책 추가
# EventBridge가 Lambda를 호출할 수 있는 권한 부여
resource "aws_lambda_permission" "allow_eventbridge_start" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_create_eb_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.start_eb_daily.arn

  depends_on = [aws_cloudwatch_event_rule.start_eb_daily]
}