terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "${var.region}"
  profile = "${var.aws_profile}"
}

module "lambda" {
  source = "./lambda"
  eb_environments = var.eb_environments
  eb_s3_bucket_name = var.eb_s3_bucket_name
  domain_mappings = var.domain_mappings
}

module "eventbridge" {
  source = "./eventbridge"
  eb_environments = var.eb_environments

  lambda_create_eb_arn = module.lambda.create_eb_arn
  lambda_create_eb_function_name = module.lambda.create_eb_function_name

  lambda_delete_eb_arn = module.lambda.delete_eb_arn
  lambda_delete_eb_function_name = module.lambda.delete_eb_function_name
  
  lambda_update_domain_arn = module.lambda.update_domain_arn
  lambda_update_domain_function_name = module.lambda.update_domain_function_name
}