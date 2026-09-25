# Amazon Bedrock Setup Guide

This guide explains how to enable Amazon Bedrock so the application can generate AI-powered spending insights.

> **Important:** Not every Bedrock model is available in every AWS region, and some models require you to explicitly request access before you can use them. Always check model availability for your chosen region first.

## 1. Open Amazon Bedrock

1. Sign in to the [AWS Console](https://console.aws.amazon.com/).
2. Search for **Bedrock** and open the service.
3. Check the region selector — Bedrock model availability varies by region. If your primary region (`ap-south-1` / Mumbai) does not yet offer your desired model, you may need to use a supported region such as `us-east-1` for the Bedrock calls specifically (set `BEDROCK_REGION` separately from `AWS_REGION` in `.env`).

## 2. Check Model Availability

1. In the Bedrock console, go to **Model access** (left sidebar).
2. Review the list of available foundation models for your selected region.
3. Look for a text-generation model such as an Anthropic Claude model (e.g. `anthropic.claude-3-haiku`) or another provider's text model available in your account.

## 3. Request Model Access (If Required)

1. On the **Model access** page, click **Manage model access** (or **Enable specific models**, depending on console version).
2. Select the checkbox next to the model(s) you want to use.
3. Click **Request model access** / **Save changes**.
4. Some models grant access instantly; others may take a few minutes to become **Access granted**.
5. Wait until the status shows **Access granted** before testing the app's AI features.

## 4. Select a Supported Model

Once access is granted, note the **Model ID** shown in the console (for example, `anthropic.claude-3-haiku-20240307-v1:0`). You will need this exact string.

## 5. Configure the Application

Update your `.env` file:

```
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_REGION=ap-south-1
BEDROCK_ENABLED=True
```

If Bedrock is not available in your account/region at all, set:

```
BEDROCK_ENABLED=False
```

The application will then always use its built-in fallback analysis (see below) — this keeps the whole project fully demoable even without Bedrock access.

## 6. Configure IAM Permissions

Ensure the IAM role/user used by the app has `bedrock:InvokeModel` permission. See `aws/iam_setup.md` for the exact policy statement.

## 7. Test Bedrock Connectivity

```bash
aws bedrock list-foundation-models --region ap-south-1
```

If this returns a list of models without an error, your credentials and region are configured correctly.

## What Happens If Bedrock Is Unavailable?

`services/bedrock_service.py` is designed to **never break the application**. If:

- Bedrock is disabled in configuration,
- the model has not been granted access,
- the region doesn't support the chosen model, or
- there is any network/credentials issue,

...the service automatically falls back to a **rule-based analysis** that calculates the same categories of insight (spending summary, top category, unusual spending, saving suggestion, recommended budget) directly from the expense data using plain Python logic — no external AI call required. This fallback is clearly labeled in the UI ("Fallback Analysis Mode") so it's transparent to the user and easy to explain in a viva.

## Why Amazon Bedrock?

- **Fully managed** — no need to host or fine-tune your own model.
- **Multiple model providers** available through one unified API.
- **Pay-per-use** — ideal for a low-traffic student project.
- **Serverless invocation** via the `bedrock-runtime` API, matching the serverless theme of the rest of the architecture (DynamoDB, S3).
