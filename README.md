# AI-Powered Smart Expense Analyzer

A cloud-hosted expense management web application that uses **Amazon Bedrock AI** to analyze user spending and provide personalized, actionable insights — built as a college-level cloud computing project on AWS.

![Status](https://img.shields.io/badge/status-complete-brightgreen) ![Python](https://img.shields.io/badge/python-3.11-blue) ![Flask](https://img.shields.io/badge/flask-3.0-black)

---

## Table of Contents

1. [Project Description](#project-description)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Architecture](#architecture)
5. [Folder Structure](#folder-structure)
6. [Prerequisites](#prerequisites)
7. [Python Installation](#python-installation)
8. [Virtual Environment Setup](#virtual-environment-setup)
9. [Dependency Installation](#dependency-installation)
10. [AWS Account Setup](#aws-account-setup)
11. [IAM Setup](#iam-setup)
12. [DynamoDB Setup](#dynamodb-setup)
13. [S3 Setup](#s3-setup)
14. [Bedrock Setup](#bedrock-setup)
15. [Environment Variables](#environment-variables)
16. [Local Execution](#local-execution)
17. [Testing](#testing)
18. [AWS Deployment](#aws-deployment)
19. [Troubleshooting](#troubleshooting)
20. [Screenshots](#screenshots)
21. [Future Enhancements](#future-enhancements)

---

## Project Description

The AI-Powered Smart Expense Analyzer lets users register, log in, and track their daily expenses with receipt uploads, category tagging, and payment method logging. It presents a professional dashboard with interactive charts, a detailed analytics page, and — its centerpiece feature — an **AI Spending Assistant** powered by Amazon Bedrock that analyzes spending patterns and generates a spending summary, unusual-spending alerts, saving suggestions, and a recommended monthly budget, plus a conversational chat assistant for ad-hoc questions.

It is designed to clearly demonstrate real AWS cloud service integration (DynamoDB, S3, Bedrock, IAM, Elastic Beanstalk/EC2) while remaining simple enough for a student to build, run, explain, and defend in a viva.

## Features

- Secure registration & login (hashed passwords, session-based auth)
- Add, edit, delete, and view expenses
- Category tagging (10 categories) and payment method tracking
- Receipt upload (JPG/JPEG/PNG/PDF, max 5MB) stored in Amazon S3
- Expense data stored in Amazon DynamoDB
- Professional dashboard with 4 Chart.js visualizations
- Detailed analytics with period filters (month/year/last 3 months)
- AI-generated spending insights via Amazon Bedrock (with safe fallback)
- AI chat assistant grounded in the user's own expense data
- Search, filter, and sort on the expense list
- Fully responsive, mobile-friendly Bootstrap 5 UI
- Toast notifications, loading indicators, and empty states throughout
- Automated tests (pytest) for auth, expenses, and analytics

## Technology Stack

**Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js
**Backend:** Python, Flask, Boto3
**Database:** Amazon DynamoDB
**Storage:** Amazon S3
**AI:** Amazon Bedrock (with rule-based fallback)
**Hosting:** AWS Elastic Beanstalk (primary) / EC2 (alternative)

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full architecture diagram and explanation. Summary:

```
User → Browser → Flask App → REST API → DynamoDB (expense data)
                                      → S3 (receipt storage)
                                      → Bedrock (AI analysis) → Insights Dashboard
```

## Folder Structure

```
AI-Powered-Smart-Expense-Analyzer/
├── app.py                     # Main Flask application entry point
├── requirements.txt
├── Procfile                   # For Elastic Beanstalk / Gunicorn
├── runtime.txt
├── .env.example
├── README.md
├── LICENSE
├── config/                    # App configuration
├── routes/                    # Flask blueprints (auth, expenses, analytics, ai, upload)
├── services/                  # Business logic + AWS integrations
├── utils/                     # Validators and helper functions
├── templates/                 # Jinja2 HTML pages
├── static/                    # CSS, JS, images
├── uploads/                   # Local receipt fallback storage
├── sample_data/               # Sample expense data
├── aws/                       # AWS setup guides
├── docs/                      # Architecture, API, database, viva docs
└── tests/                     # Pytest test suite
```

## Prerequisites

- Python 3.11+
- pip
- An AWS account (optional for local demo — see [Local Execution](#local-execution))
- AWS CLI (only needed for deployment)

## Python Installation

Download and install Python 3.11 or later from [python.org](https://www.python.org/downloads/). Verify with:

```bash
python --version
```

## Virtual Environment Setup

```bash
cd AI-Powered-Smart-Expense-Analyzer
python -m venv venv

# Activate it:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## Dependency Installation

```bash
pip install -r requirements.txt
```

## AWS Account Setup

1. Create a free AWS account at [aws.amazon.com](https://aws.amazon.com/) if you don't have one.
2. Sign in to the AWS Console.
3. (Recommended) Create an IAM user for yourself with `AdministratorAccess` for initial setup only, then follow least-privilege practices for the app itself — see below.

## IAM Setup

See [`aws/iam_setup.md`](aws/iam_setup.md) for the full least-privilege policy and role setup, and an explanation of why IAM roles are safer than hard-coded credentials.

## DynamoDB Setup

See [`aws/dynamodb_setup.md`](aws/dynamodb_setup.md) for step-by-step table creation instructions (`ExpenseAnalyzerExpenses` and `ExpenseAnalyzerUsers`).

## S3 Setup

See [`aws/s3_setup.md`](aws/s3_setup.md) for bucket creation and security configuration.

## Bedrock Setup

See [`aws/bedrock_setup.md`](aws/bedrock_setup.md) for enabling model access and configuring the AI model. **Note:** not every model is available in every region — check availability first.

## Environment Variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

```env
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your-bucket-name
DYNAMODB_TABLE_NAME=your-table-name
BEDROCK_MODEL_ID=your-model-id
SECRET_KEY=your-secret-key
```

**Never commit your real `.env` file or hard-code credentials in source code.**

## Local Execution

The app can run locally in development mode without production AWS configuration. Local development may use the project's local fallbacks. Production is different: the AWS deployment disables the local receipt-storage fallback and uses the Elastic Beanstalk IAM role for AWS access.

```bash
python app.py
# or
flask run
```

Then open **http://localhost:5000** in your browser.

### Demo mode (pre-populated dashboard)

Register a new account with a blank dashboard, or set `DEMO_MODE=True` in your `.env` first. With demo mode on, every newly-registered account is automatically seeded with ~23 sample expenses (from `sample_data/sample_expenses.json`) so the dashboard stats and all four charts are populated immediately after sign-up — useful for screenshots, demos, or a viva walkthrough without manually entering data. Existing accounts and `DEMO_MODE=False` (the default) are unaffected.

## Testing

```bash
pytest tests/ -v
```

Covers registration, login (success/failure), expense CRUD, and analytics calculations.

## AWS Deployment

See [`aws/deployment.md`](aws/deployment.md) for full Elastic Beanstalk (recommended) and EC2 (alternative) deployment walkthroughs, including environment variable configuration and IAM role attachment.

Quick start (Elastic Beanstalk):

```bash
pip install awsebcli
eb init -p python-3.11 smart-expense-analyzer --region ap-south-1
eb create smart-expense-env
eb setenv SECRET_KEY=... S3_BUCKET_NAME=... DYNAMODB_TABLE_NAME=... BEDROCK_MODEL_ID=...
eb deploy
eb open
```

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| App starts but shows "Falling back to in-memory store" | AWS credentials not configured | Run `aws configure`, or ignore this if you're intentionally running in local demo mode |
| Receipt upload fails with a 502 error | S3 bucket name incorrect or IAM permissions missing | Check `S3_BUCKET_NAME` in `.env` and review `aws/iam_setup.md` |
| AI Insights shows "Fallback Analysis Mode" | Bedrock not enabled, model access not granted, or wrong region | Follow `aws/bedrock_setup.md`; verify `BEDROCK_MODEL_ID` and `BEDROCK_REGION` |
| Dashboard shows all zeros / empty charts | Normal for a brand-new account — no expenses added yet | Add an expense via **Add Expense**, or set `DEMO_MODE=True` in `.env` and register a new account to auto-load sample data |
| Login fails after registering | Browser cookies are blocked | Ensure cookies are enabled for `localhost` |
| `ModuleNotFoundError` on startup | Dependencies not installed / venv not activated | Re-run `pip install -r requirements.txt` inside the activated virtual environment |

## Screenshots

_Add screenshots of your running application here before submission — landing page, dashboard, add expense form, analytics page, and AI insights page are recommended._

## Future Enhancements

- OCR-based automatic receipt scanning and expense extraction
- Voice expense entry
- Email / SMS / WhatsApp expense entry
- Predictive monthly spending forecasts
- Advanced anomaly detection
- Automatic budget alerts
- Multi-currency support
- Native mobile application
- AWS Lambda serverless architecture
- Amazon Cognito authentication

---

## License

This project is licensed under the MIT License — see [`LICENSE`](LICENSE).

## Disclaimer

AI-generated insights in this application are for informational purposes only and should not be considered professional financial advice.

## Security and GitHub

- Do not commit `.env`, AWS access keys, secret keys, session tokens, or private credentials.
- `venv/`, local receipt uploads, caches, and logs are ignored by `.gitignore`.
- Production uses an IAM instance role for AWS access; no AWS credentials are stored in the application.
- Production disables the local receipt-storage fallback and serves private S3 receipts with short-lived presigned URLs.
- Production requires `SECRET_KEY` to be supplied through the deployment environment.

