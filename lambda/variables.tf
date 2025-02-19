variable "eb_environments" {
  description = "EB environment configurations"
  type = map(object({
    application_name = string
    environment_name = string
    template_name    = string
  }))
}

variable "eb_s3_bucket_name" {
    type = string
}

variable "domain_mappings" {
  description = "Configuration for different projects including hosted zone and target domains"
  type = map(object({
    hosted_zone_id = string
    domains = list(string)
  }))
  default = {
    "project-dev" = {
      hosted_zone_id = "HOSTING-ID"
      domains = [
        "project.example.com",
        "www.project.example.com"
      ]
    }
  }
}

variable "waf_web_acl_arn" {
    type = string
}
