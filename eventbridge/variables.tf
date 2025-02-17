variable "eb_environments" {
  description = "EB environment configurations"
  type = map(object({
    application_name = string
    environment_name = string
    template_name    = string
  }))
}

variable "lambda_create_eb_arn" {
  description = "ARN of the Lambda function to be triggered"
  type        = string
}

variable "lambda_create_eb_function_name" {
  description = "Name of the Lambda function to be triggered"
  type        = string
}