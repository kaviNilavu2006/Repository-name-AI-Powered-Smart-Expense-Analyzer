# Project Modules Documentation

This document explains each functional module of the AI-Powered Smart Expense Analyzer for presentation and evaluation purposes.

---

## 1. Authentication Module

**Purpose:** Allows users to securely register, log in, and log out.

- **Input:** Full name, email, password (registration); email, password (login).
- **Processing:** Validates input format, hashes passwords with Werkzeug's `generate_password_hash`, verifies credentials with `check_password_hash`, and manages Flask server-side sessions.
- **Output:** A logged-in session (`session["user_id"]`) or a validation/authentication error.
- **AWS Service Used:** Amazon DynamoDB (`ExpenseAnalyzerUsers` table) for storing user accounts.
- **Files:** `routes/auth_routes.py`, `services/auth_service.py`, `utils/validators.py`.

---

## 2. Expense Management Module

**Purpose:** Full CRUD (Create, Read, Update, Delete) operations on individual expenses.

- **Input:** Amount, category, description, date, payment method, optional receipt file.
- **Processing:** Validates amount/category/date/payment method, generates a unique `expense_id`, associates the record with the logged-in `user_id`, and coordinates with the Receipt Management Module for file uploads.
- **Output:** Persisted expense records in DynamoDB; JSON responses for the frontend to render.
- **AWS Service Used:** Amazon DynamoDB (`ExpenseAnalyzerExpenses` table).
- **Files:** `routes/expense_routes.py`, `services/dynamodb_service.py`, `utils/validators.py`.

---

## 3. Receipt Management Module

**Purpose:** Handles uploading, storing, and retrieving receipt images/PDFs.

- **Input:** An image or PDF file (JPG, JPEG, PNG, PDF), max 5 MB.
- **Processing:** Validates file type and size, generates a unique object key, uploads the file to S3, and generates a presigned URL for secure, temporary viewing.
- **Output:** An S3 object key + URL, stored alongside the related expense record.
- **AWS Service Used:** Amazon S3.
- **Files:** `routes/upload_routes.py`, `services/s3_service.py`, `utils/validators.py`.

---

## 4. Analytics Module

**Purpose:** Computes spending statistics and trends from raw expense data.

- **Input:** A user's full list of expenses (optionally filtered by period).
- **Processing:** Calculates total spending, average daily/transaction spending, highest/lowest expense, category totals and percentages, monthly and daily totals, and payment method breakdowns.
- **Output:** A structured JSON summary consumed by both the Analytics page and the AI Analysis Module.
- **AWS Service Used:** Reads from Amazon DynamoDB (via the Expense Management Module); computation itself happens in the Flask application layer.
- **Files:** `routes/analytics_routes.py`, `services/analytics_service.py`.

---

## 5. AI Analysis Module

**Purpose:** Generates natural-language spending insights and answers user questions about their finances.

- **Input:** The structured analytics summary for the logged-in user; free-text chat questions.
- **Processing:** Builds a prompt describing the user's spending pattern and sends it to Amazon Bedrock. If Bedrock is unavailable, a deterministic rule-based fallback produces an equivalent structured analysis.
- **Output:** A structured spending analysis (summary, main category, observation, unusual spending, saving suggestion, recommended budget) and conversational chat replies — each always paired with a financial-advice disclaimer.
- **AWS Service Used:** Amazon Bedrock (`bedrock-runtime` InvokeModel API).
- **Files:** `routes/ai_routes.py`, `services/bedrock_service.py`.

---

## 6. Dashboard Module

**Purpose:** Presents an at-a-glance visual summary of the user's finances.

- **Input:** Analytics summary data (fetched via API on page load).
- **Processing:** Renders four Chart.js visualizations (category doughnut, payment method pie, monthly bar, daily line) and four key stat cards (total spending, this month, top category, transaction count).
- **Output:** An interactive, responsive dashboard page.
- **AWS Service Used:** Indirectly uses DynamoDB (via the Analytics Module) for the underlying data.
- **Files:** `templates/dashboard.html`, `static/js/dashboard.js`.

---

## 7. Cloud Integration Module

**Purpose:** Centralizes all AWS SDK (boto3) interactions and configuration, keeping cloud logic isolated from business logic.

- **Input:** Application configuration from environment variables (`config/config.py`).
- **Processing:** Initializes boto3 clients/resources for DynamoDB, S3, and Bedrock; performs connectivity checks on startup; provides automatic local fallbacks (in-memory store, local file storage, rule-based analysis) if AWS services are unreachable, so the app remains demoable without an AWS account.
- **Output:** A consistent internal API (`dynamodb_service`, `s3_service`, `bedrock_service`) used by all route modules.
- **AWS Service Used:** Amazon DynamoDB, Amazon S3, Amazon Bedrock, and (at the infrastructure level) IAM and Elastic Beanstalk/EC2.
- **Files:** `services/dynamodb_service.py`, `services/s3_service.py`, `services/bedrock_service.py`, `config/config.py`.
