resource "aws_cloudwatch_event_rule" "stop_eb_daily" {
  name                = "stop-eb-environment-daily"
  description         = "Stop EB environment every weekday at 22 PM KST"
  schedule_expression = "cron(0 13 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "stop_lambda_target" {
  rule      = aws_cloudwatch_event_rule.stop_eb_daily.name
  target_id = "StopEBEnvironment"
  arn       = var.lambda_delete_eb_arn

  input = jsonencode({
    environments = keys(var.eb_environments)
  })
}

resource "aws_lambda_permission" "allow_eventbridge_stop" {
  statement_id  = "AllowEventBridgeInvokeStop"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_delete_eb_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.stop_eb_daily.arn

  depends_on = [aws_cloudwatch_event_rule.stop_eb_daily]
}
