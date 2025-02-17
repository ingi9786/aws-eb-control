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
