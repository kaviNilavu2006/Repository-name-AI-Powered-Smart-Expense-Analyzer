# DynamoDB Setup Guide

This guide walks you through creating the DynamoDB tables used by the AI-Powered Smart Expense Analyzer.

## Tables Required

1. **ExpenseAnalyzerExpenses** — stores all expense records.
2. **ExpenseAnalyzerUsers** — stores registered user accounts.

## 1. Create the Expenses Table

1. Sign in to the [AWS Console](https://console.aws.amazon.com/).
2. Search for **DynamoDB** and open the service.
3. Make sure the region selector (top-right) is set to **Asia Pacific (Mumbai) ap-south-1**.
4. Click **Create table**.
5. Fill in:
   - **Table name:** `ExpenseAnalyzerExpenses`
   - **Partition key:** `user_id` (String)
   - **Sort key:** `expense_id` (String)
6. Under **Table settings**, choose **Customize settings**.
7. **Billing mode:** select **On-demand** (pay-per-request) — ideal for a college project since you don't need to guess capacity.
8. Leave encryption at the default (AWS owned key) unless your institution requires otherwise.
9. Click **Create table** and wait for status to become **Active**.

## 2. Create the Users Table

1. Click **Create table** again.
2. Fill in:
   - **Table name:** `ExpenseAnalyzerUsers`
   - **Partition key:** `user_id` (String)
3. Billing mode: **On-demand**.
4. Click **Create table**.

### Add a Global Secondary Index (GSI) for email lookups

Since login happens by email, add a GSI so the app can query users by email efficiently:

1. Open the `ExpenseAnalyzerUsers` table.
2. Go to the **Indexes** tab.
3. Click **Create index**.
4. **Partition key:** `email` (String)
5. **Index name:** `email-index`
6. Projected attributes: **All**.
7. Click **Create index**.

> If you skip this step, the app's in-memory fallback store still works for local demos, but production login-by-email queries on real DynamoDB require this index.

## 3. Verify Table Access

Run this from your terminal (with AWS CLI configured) to confirm the tables exist:

```bash
aws dynamodb list-tables --region ap-south-1
```

You should see both `ExpenseAnalyzerExpenses` and `ExpenseAnalyzerUsers` in the output.

## Table Design Summary

| Table | Partition Key | Sort Key | Purpose |
|---|---|---|---|
| ExpenseAnalyzerExpenses | user_id | expense_id | Stores individual expense records per user |
| ExpenseAnalyzerUsers | user_id | — | Stores registered accounts, with an `email-index` GSI for login lookups |

## Why DynamoDB?

- **Serverless** — no servers to patch or manage, ideal for a student project.
- **Pay-per-request billing** — costs stay near zero during development and demos.
- **Scales automatically** — no capacity planning needed.
- **Native AWS SDK (boto3) support** — integrates cleanly with Flask via `services/dynamodb_service.py`.
