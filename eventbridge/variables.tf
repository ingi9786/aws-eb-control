variable "eb_environments" {
  description = "EB environment configurations"
  type = map(object({
    application_name = string
    environment_name = string
    template_name    = string
  }))
}

variable "lambda_create_eb_arn" {
  description = "ARN of create_eb Lambda"
  type        = string
}

variable "lambda_create_eb_function_name" {
  description = "Name of create_eb Lambda"
  type        = string
}

variable "lambda_delete_eb_arn" {
  description = "ARN of delete_eb Lambda"
  type        = string
}

variable "lambda_delete_eb_function_name" {
  description = "Name of delete_eb Lambda"
  type        = string
}

variable "lambda_postdeploy_eb_arn" {
  description = "ARN of postdeploy_eb Lambda"
  type        = string
}

variable "lambda_postdeploy_eb_function_name" {
  description = "Name of postdeploy_eb Lambda"
  type        = string
}