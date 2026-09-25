# AWS Deployment Guide

This guide covers two ways to deploy the AI-Powered Smart Expense Analyzer to AWS: **Elastic Beanstalk** (recommended, simplest) and **EC2** (alternative, more manual control).

---

## Option A: AWS Elastic Beanstalk (Recommended)

### 1. Install Required Tools

```bash
# Install the AWS CLI
pip install awscli --upgrade

# Install the Elastic Beanstalk CLI
pip install awsebcli --upgrade
```

### 2. Configure AWS Credentials

```bash
aws configure
```

Enter your Access Key ID, Secret Access Key, default region (`ap-south-1`), and output format (`json`).

> For a real deployment, prefer using an IAM role attached to your Beanstalk environment instead of long-lived access keys wherever possible (see `aws/iam_setup.md`).

### 3. Initialize Elastic Beanstalk

From the project root folder:

```bash
eb init -p python-3.11 smart-expense-analyzer --region ap-south-1
```

Follow the prompts. When asked about SSH, you can enable it for debugging or skip it.

### 4. Create the Environment

```bash
eb create smart-expense-env --instance-type t3.micro
```

This provisions an EC2 instance, load balancer (optional), and security groups automatically, and deploys your Flask app.

### 5. Configure Environment Variables

Set your app's configuration (mirroring `.env.example`) directly on the Beanstalk environment — never commit real secrets to your repository:

```bash
eb setenv SECRET_KEY=your-real-secret-key \
  AWS_REGION=ap-south-1 \
  DYNAMODB_TABLE_NAME=ExpenseAnalyzerExpenses \
  DYNAMODB_USERS_TABLE_NAME=ExpenseAnalyzerUsers \
  S3_BUCKET_NAME=smart-expense-analyzer-receipts-yourname \
  BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0 \
  BEDROCK_REGION=ap-south-1 \
  BEDROCK_ENABLED=True \
  FLASK_ENV=production
```

### 6. Attach the IAM Role

In the Elastic Beanstalk console, go to your environment → **Configuration** → **Security** → set the **IAM instance profile** to `SmartExpenseAnalyzerRole` (created in `aws/iam_setup.md`). This grants DynamoDB, S3, and Bedrock access without any hard-coded keys.

### 7. Deploy

```bash
eb deploy
```

### 8. Test the Public URL

```bash
eb open
```

This opens your live application URL (something like `smart-expense-env.eba-xxxxx.ap-south-1.elasticbeanstalk.com`) in your browser. Register an account and confirm the full workflow — add an expense, view the dashboard, check AI Insights.

### 9. View Logs (Troubleshooting)

```bash
eb logs
```

---

## Option B: EC2 (Alternative / Manual Deployment)

### 1. Launch an EC2 Instance

1. Go to **EC2 → Launch instance**.
2. Choose **Amazon Linux 2023** AMI.
3. Instance type: `t3.micro` (Free Tier eligible).
4. Under **IAM instance profile**, attach `SmartExpenseAnalyzerRole`.
5. Configure the security group to allow inbound traffic on **port 80** (HTTP) and **port 22** (SSH, restricted to your IP).
6. Launch with a key pair you control.

### 2. Connect and Install Dependencies

```bash
ssh -i your-key.pem ec2-user@<public-ip>

sudo yum update -y
sudo yum install -y python3.11 python3.11-pip git
```

### 3. Clone/Upload the Project

```bash
git clone <your-repo-url> smart-expense-analyzer
cd smart-expense-analyzer
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
nano .env   # fill in your real bucket name, table names, model ID, etc.
```

### 5. Run with Gunicorn (Production WSGI Server)

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

### 6. Put Nginx in Front (Recommended)

```bash
sudo yum install -y nginx
```

Configure `/etc/nginx/nginx.conf` (or a site config) to reverse proxy port 80 → 8000, then:

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 7. Keep the App Running

Use a process manager such as `systemd` or `supervisor` to keep Gunicorn running after you disconnect, and to restart it automatically if it crashes.

### 8. Test the Public URL

Visit `http://<ec2-public-ip>/` in your browser.

---

## Post-Deployment Checklist

- [ ] Registration and login work over HTTPS or HTTP as configured.
- [ ] Adding an expense with a receipt successfully uploads to S3 (not local fallback).
- [ ] DynamoDB tables show new items in the AWS Console.
- [ ] AI Insights page shows `Powered by Amazon Bedrock` (not "Fallback Analysis Mode") if Bedrock is configured correctly.
- [ ] No AWS credentials appear anywhere in your deployed source code or committed `.env` file.

## Region Note

This project defaults to **ap-south-1 (Mumbai)** for DynamoDB and S3. Amazon Bedrock model availability differs by region — if your desired model isn't available in `ap-south-1`, set `BEDROCK_REGION` independently in your environment configuration (see `aws/bedrock_setup.md`).
