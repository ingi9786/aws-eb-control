data "archive_file" "create_eb_zip" {
  type        = "zip"
  source_file  = "${path.root}/src/create_eb.py"
  output_path = "${path.root}/dist/create_eb.zip"
  
}

resource "aws_lambda_function" "create_eb" {
  filename         = data.archive_file.create_eb_zip.output_path
  function_name    = "create_eb"
  role            = aws_iam_role.lambda_base.arn
  handler         = "create_eb.lambda_handler"
  source_code_hash = data.archive_file.create_eb_zip.output_base64sha256
  runtime         = "python3.10"
  timeout         = 15

  environment {
    variables = {
      EB_ENVIRONMENTS = jsonencode(var.eb_environments)
      EB_S3_BUCKET_NAME = var.eb_s3_bucket_name
    }
  }
}
