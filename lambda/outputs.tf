output "create_eb_arn" {
  value = aws_lambda_function.create_eb.arn
}

output "create_eb_function_name" {
  value = aws_lambda_function.create_eb.function_name
}
