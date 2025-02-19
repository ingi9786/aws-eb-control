data "archive_file" "postdeploy_eb_zip" {
  type        = "zip"
  source_file  = "${path.root}/src/postdeploy_eb.py"
  output_path = "${path.root}/dist/postdeploy_eb.zip"
  
}

resource "aws_lambda_function" "postdeploy_eb" {
  filename         = data.archive_file.postdeploy_eb_zip.output_path
  function_name    = "postdeploy_eb"
  role            = aws_iam_role.postdeploy_eb.arn
  handler         = "postdeploy_eb.lambda_handler"
  source_code_hash = data.archive_file.postdeploy_eb_zip.output_base64sha256
  runtime         = "python3.10"
  timeout         = 10

  environment {
    variables = {
      DOMAIN_MAPPINGS = jsonencode(var.domain_mappings)
      WAF_WEB_ACL_ARN = var.waf_web_acl_arn
    }
  }
}

# IAM role section
resource "aws_iam_role" "postdeploy_eb" {
  name = "postdeploy_eb_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "postdeploy_eb_lambda_basic_exec" {
  role       = aws_iam_role.postdeploy_eb.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "postdeploy_eb_eb_readonly" {
  role       = aws_iam_role.postdeploy_eb.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkReadOnly"
}

resource "aws_iam_role_policy" "postdeploy_eb_route53_waf" {
  name = "route53_waf_management"
  role = aws_iam_role.postdeploy_eb.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "route53:ChangeResourceRecordSets",
          "route53:ListResourceRecordSets"
        ]
        Resource = "arn:aws:route53:::hostedzone/*"
      },
            {
        Effect = "Allow"
        Action = [
          "wafv2:AssociateWebACL",
          "wafv2:GetWebACL",
          "elasticloadbalancing:SetWebACL"
        ]
        Resource = "*"
      }
    ]
  })
}
