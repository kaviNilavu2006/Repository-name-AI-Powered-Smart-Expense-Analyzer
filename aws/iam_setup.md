# AWS IAM Setup Guide

This guide explains how to set up secure, least-privilege access for the application to use DynamoDB, S3, and Bedrock.

## Why IAM Roles Are Safer Than Hard-Coded Credentials

Hard-coding an AWS Access Key and Secret Key directly into source code is a serious security risk:

- Anyone who sees the code (classmates, GitHub, screen-share) can use your credentials.
- Keys committed to version control remain in git history forever, even if deleted later.
- Leaked keys are frequently found and abused by automated bots within minutes of being pushed to a public repository.

**IAM roles** solve this by letting AWS services (like an EC2 instance or Elastic Beanstalk environment) assume a role with specific permissions — no keys are ever stored anywhere. Temporary credentials are automatically issued and rotated behind the scenes.

For **local development**, the safe alternative is environment variables (via a `.env` file that is never committed to git) or your AWS CLI's configured profile (`~/.aws/credentials`), which is never included in a shared codebase.

## 1. Create a Least-Privilege IAM Policy

In the AWS Console, go to **IAM → Policies → Create policy**, choose the **JSON** tab, and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-south-1:*:table/ExpenseAnalyzerExpenses",
        "arn:aws:dynamodb:ap-south-1:*:table/ExpenseAnalyzerExpenses/index/*",
        "arn:aws:dynamodb:ap-south-1:*:table/ExpenseAnalyzerUsers",
        "arn:aws:dynamodb:ap-south-1:*:table/ExpenseAnalyzerUsers/index/*"
      ]
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::smart-expense-analyzer-receipts-yourname/*"
    },
    {
      "Sid": "S3BucketCheck",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::smart-expense-analyzer-receipts-yourname"
    },
    {
      "Sid": "BedrockAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

> Replace `smart-expense-analyzer-receipts-yourname` with your actual bucket name, and restrict the Bedrock `Resource` to a specific model ARN if you want tighter scoping.

Name the policy `SmartExpenseAnalyzerPolicy` and click **Create policy**.

## 2. Attach the Policy

### Option A — For EC2 / Elastic Beanstalk (Recommended)

1. Go to **IAM → Roles → Create role**.
2. Trusted entity type: **AWS service**.
3. Use case: **EC2** (Elastic Beanstalk environments use EC2 instances under the hood).
4. Attach the `SmartExpenseAnalyzerPolicy` policy.
5. Name the role `SmartExpenseAnalyzerRole` and create it.
6. When creating your Elastic Beanstalk environment (or EC2 instance), assign this role as the **instance profile**. No access keys are needed anywhere in your code or environment variables.

### Option B — For Local Development Only

1. Go to **IAM → Users → Create user** (only if you don't already have a personal IAM user).
2. Attach the `SmartExpenseAnalyzerPolicy` policy directly, or attach it via a group.
3. Generate an **access key** for this user under **Security credentials**.
4. Run `aws configure` locally and paste in the Access Key ID and Secret Access Key.
5. Boto3 will automatically pick up these credentials — you do **not** need to put them in `.env` or source code.

## 3. Principle of Least Privilege

Notice the policy above only grants:
- Access to the two specific DynamoDB tables (not all tables in the account).
- Access to objects inside one specific S3 bucket (not all buckets).
- The single Bedrock action needed (`InvokeModel`).

Avoid using `"Resource": "*"` broadly, and avoid attaching AWS-managed "FullAccess" policies (e.g. `AmazonDynamoDBFullAccess`) in a real project — they grant far more permission than the app needs.

## 4. Verifying Permissions

After attaching the role/policy, test connectivity:

```bash
aws sts get-caller-identity
aws dynamodb describe-table --table-name ExpenseAnalyzerExpenses --region ap-south-1
aws s3 ls s3://smart-expense-analyzer-receipts-yourname
```

If these commands succeed without an `AccessDenied` error, your IAM setup is correct.
