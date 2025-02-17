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
}

module "eventbridge" {
  source = "./eventbridge"
  eb_environments = var.eb_environments
  lambda_create_eb_arn = module.lambda.create_eb_arn
  lambda_create_eb_function_name = module.lambda.create_eb_function_name
}