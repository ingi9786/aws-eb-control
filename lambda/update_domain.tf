data "archive_file" "update_domain_zip" {
  type        = "zip"
  source_file  = "${path.root}/src/update_domain.py"
  output_path = "${path.root}/dist/update_domain.zip"
  
}

resource "aws_lambda_function" "update_domain" {
  filename         = data.archive_file.update_domain_zip.output_path
  function_name    = "update_domain"
  role            = aws_iam_role.update_domain.arn
  handler         = "update_domain.lambda_handler"
  source_code_hash = data.archive_file.update_domain_zip.output_base64sha256
  runtime         = "python3.10"
  timeout         = 10

  environment {
    variables = {
      DOMAIN_MAPPINGS = jsonencode(var.domain_mappings)
    }
  }
}

# IAM role section
resource "aws_iam_role" "update_domain" {
  name = "update_domain_lambda_role"

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

resource "aws_iam_role_policy_attachment" "update_domain_lambda_basic_exec" {
  role       = aws_iam_role.update_domain.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "update_domain_eb_readonly" {
  role       = aws_iam_role.update_domain.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkReadOnly"
}

resource "aws_iam_role_policy" "update_domain_route53" {
  name = "route53_record_management"
  role = aws_iam_role.update_domain.id

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
      }
    ]
  })
}