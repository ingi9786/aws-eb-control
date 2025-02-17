variable "region" {
  description = "AWS Region"
  type        = string
  default     = "ap-northeast-2"
}

variable "aws_profile" {
  description = "AWS Profile"
  type        = string
}

variable "eb_environments" {
  description = "EB environment configurations"
  type = map(object({
    application_name = string
    environment_name = string
    template_name    = string
  }))
}
