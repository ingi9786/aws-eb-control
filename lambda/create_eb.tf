resource "aws_iam_role" "create_eb" {
  name = "create_eb_lambda_role"

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

# ElasticBeanstalk 인라인 정책 연결
resource "aws_iam_role_policy" "create_eb_elasticbeanstalk" {
  name = "elasticbeanstalk_access"
  role = aws_iam_role.create_eb.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "elasticbeanstalk:CreateEnvironment",
          "elasticbeanstalk:DescribeEnvironments",
          "elasticbeanstalk:DescribeConfigurationSettings"
        ]
        Resource = "*"
      }
    ]
  })
}

# S3 접근 관리형 정책 연결
resource "aws_iam_role_policy_attachment" "create_eb_s3_readonly" {
  role       = aws_iam_role.create_eb.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# Lambda 기본 관리형 정책 연결
resource "aws_iam_role_policy_attachment" "create_eb_lambda_basic" {
  role       = aws_iam_role.create_eb.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file  = "${path.root}/src/create_eb.py"
  output_path = "${path.root}/dist/create_eb.zip"
  
}

resource "aws_lambda_function" "create_eb" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "create_eb"
  role            = aws_iam_role.create_eb.arn
  handler         = "create_eb.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.10"

  environment {
    variables = {
      EB_ENVIRONMENTS = jsonencode(var.eb_environments) # JSON으로 변환 후 환경변수에 저장
    }
  }
  

}

