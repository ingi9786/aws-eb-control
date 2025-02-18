data "archive_file" "delete_eb_zip" {
  type        = "zip"
  source_file = "${path.root}/src/delete_eb.py"
  output_path = "${path.root}/dist/delete_eb.zip"
}

resource "aws_lambda_function" "delete_eb" {
  filename         = data.archive_file.delete_eb_zip.output_path
  function_name    = "delete_eb"
  role            = aws_iam_role.lambda_base.arn
  handler         = "delete_eb.lambda_handler"
  source_code_hash = data.archive_file.delete_eb_zip.output_base64sha256
  runtime         = "python3.10"
  timeout         = 10

  environment {
    variables = {
      EB_ENVIRONMENTS = jsonencode(var.eb_environments)
      EB_S3_BUCKET_NAME = var.eb_s3_bucket_name
    }
  }
}