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

variable "lambda_update_domain_arn" {
  description = "ARN of update_domain Lambda"
  type        = string
}

variable "lambda_update_domain_function_name" {
  description = "Name of update_domain Lambda"
  type        = string
}