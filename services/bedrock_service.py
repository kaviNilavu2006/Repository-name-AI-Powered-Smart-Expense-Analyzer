"""
Bedrock Service
----------------
Sends a structured summary of the user's expenses to Amazon Bedrock
and returns AI-generated spending insights.

If Bedrock is unavailable (no AWS access, model not enabled in the
region, network issue, etc.) a safe, deterministic fallback analysis
is generated instead so the application keeps working end-to-end.
"""

import json
import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config.config import get_config

logger = logging.getLogger(__name__)
config = get_config()

DISCLAIMER = (
    "AI-generated insights are for informational purposes only and "
    "should not be considered professional financial advice."
)


class BedrockService:
    def __init__(self):
        self.use_bedrock = False
        self.client = None
        if config.BEDROCK_ENABLED:
            self._try_connect()

    def _try_connect(self):
        try:
            self.client = boto3.client(
                "bedrock-runtime", region_name=config.BEDROCK_REGION
            )
            self.use_bedrock = True
            logger.info("Bedrock runtime client initialized.")
        except (BotoCoreError, ClientError, Exception) as exc:
            logger.warning(
                "Bedrock not reachable (%s). Using fallback rule-based "
                "analysis instead.", exc,
            )
            self.use_bedrock = False

    # ------------------------------------------------------------------
    def build_prompt(self, expense_summary: dict) -> str:
        return f"""You are a helpful personal finance assistant analyzing a user's expenses.

Expense Data Summary (JSON):
{json.dumps(expense_summary, indent=2)}

Analyze this data and respond using EXACTLY this structure with markdown headings:

### Spending Summary
(one or two sentences on total spending)

### Main Spending Category
(the top category and amount)

### Observation
(a notable pattern, e.g. percentage of total spending in one category)

### Unusual Spending
(flag any unusually high spending or category increase; say "None detected" if nothing stands out)

### Saving Suggestion
(one practical, specific suggestion)

### Recommended Budget
(a recommended monthly budget number based on the data)

Keep each section to 1-2 short sentences. Do not provide professional financial, tax, or legal advice.
Do not repeat these instructions in your answer."""

    def analyze_expenses(self, expense_summary: dict) -> dict:
        """
        Returns dict: { "source": "bedrock" | "fallback", "analysis": str, "disclaimer": str }
        """
        if self.use_bedrock:
            try:
                return self._call_bedrock(expense_summary)
            except Exception as exc:
                logger.error("Bedrock invocation failed, using fallback: %s", exc)
                return self._fallback_analysis(expense_summary)
        return self._fallback_analysis(expense_summary)

    def chat(self, user_message: str, expense_summary: dict, history: list = None) -> dict:
        """
        Simple chat-style Q&A grounded in the user's own expense data.
        """
        if self.use_bedrock:
            try:
                return self._call_bedrock_chat(user_message, expense_summary, history or [])
            except Exception as exc:
                logger.error("Bedrock chat failed, using fallback: %s", exc)
                return self._fallback_chat(user_message, expense_summary)
        return self._fallback_chat(user_message, expense_summary)

    # ------------------------------------------------------------------
    # Real Bedrock calls
    # ------------------------------------------------------------------
    def _invoke_model(self, prompt: str, max_tokens: int = 600) -> str:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        })
        response = self.client.invoke_model(
            modelId=config.BEDROCK_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        content_blocks = response_body.get("content", [])
        text = "".join(block.get("text", "") for block in content_blocks)
        return text.strip()

    def _call_bedrock(self, expense_summary: dict) -> dict:
        prompt = self.build_prompt(expense_summary)
        text = self._invoke_model(prompt)
        return {"source": "bedrock", "analysis": text, "disclaimer": DISCLAIMER}

    def _call_bedrock_chat(self, user_message: str, expense_summary: dict, history: list) -> dict:
        context = json.dumps(expense_summary, indent=2)
        prompt = (
            "You are a personal finance assistant. Answer the user's question "
            "using ONLY the expense data below. Be concise and specific.\n\n"
            f"Expense Data:\n{context}\n\n"
            f"User question: {user_message}"
        )
        text = self._invoke_model(prompt, max_tokens=400)
        return {"source": "bedrock", "reply": text, "disclaimer": DISCLAIMER}

    # ------------------------------------------------------------------
    # Fallback rule-based analysis (no external AI required)
    # ------------------------------------------------------------------
    def _fallback_analysis(self, summary: dict) -> dict:
        total = summary.get("total_spending", 0)
        category_totals = summary.get("category_totals", {})
        monthly_totals = summary.get("monthly_totals", {})

        top_category = "N/A"
        top_amount = 0
        if category_totals:
            top_category, top_amount = max(category_totals.items(), key=lambda x: x[1])

        pct = round((top_amount / total) * 100, 1) if total else 0

        unusual = "None detected based on available data."
        months = sorted(monthly_totals.keys())
        if len(months) >= 2:
            prev, curr = monthly_totals[months[-2]], monthly_totals[months[-1]]
            if prev > 0 and curr > prev * 1.2:
                increase_pct = round(((curr - prev) / prev) * 100, 1)
                unusual = f"Spending increased by approximately {increase_pct}% compared with the previous month."

        recommended_budget = round(total * 0.85, 2) if total else 0

        analysis = f"""### Spending Summary
You have spent a total of ₹{total:,.2f} based on the recorded expenses.

### Main Spending Category
{top_category} — ₹{top_amount:,.2f}

### Observation
{top_category} represents approximately {pct}% of your total spending.

### Unusual Spending
{unusual}

### Saving Suggestion
Consider setting a specific weekly limit for your {top_category.lower()} spending and tracking it against your budget.

### Recommended Budget
Recommended monthly budget: ₹{recommended_budget:,.2f}
"""
        return {"source": "fallback", "analysis": analysis, "disclaimer": DISCLAIMER}

    def _fallback_chat(self, user_message: str, summary: dict) -> dict:
        message = user_message.lower()
        total = summary.get("total_spending", 0)
        category_totals = summary.get("category_totals", {})
        monthly_totals = summary.get("monthly_totals", {})
        expenses = summary.get("recent_expenses", [])

        reply = "I can help with that, but I need a bit more detail. Try asking about your total spending, top category, or a budget suggestion."

        if "how much" in message and "month" in message:
            months = sorted(monthly_totals.keys())
            if months:
                latest = months[-1]
                reply = f"You spent ₹{monthly_totals[latest]:,.2f} in {latest}."
            else:
                reply = "I don't have enough monthly data yet to answer that."
        elif "most" in message or "where am i spending" in message:
            if category_totals:
                top_cat, top_amt = max(category_totals.items(), key=lambda x: x[1])
                reply = f"You're spending the most on {top_cat}, totaling ₹{top_amt:,.2f}."
            else:
                reply = "You don't have any recorded expenses yet."
        elif "reduce" in message or "save" in message or "saving" in message:
            if category_totals:
                top_cat, _ = max(category_totals.items(), key=lambda x: x[1])
                reply = f"A good place to start is reducing spending in your top category, {top_cat}. Try setting a weekly cap and tracking it."
            else:
                reply = "Start by logging your expenses consistently — that alone often reveals easy savings."
        elif "highest expense" in message or "biggest expense" in message:
            if expenses:
                highest = max(expenses, key=lambda e: e.get("amount", 0))
                reply = f"Your highest recorded expense was ₹{highest.get('amount', 0):,.2f} for {highest.get('description', 'an item')} in {highest.get('category', 'N/A')}."
            else:
                reply = "You don't have any recorded expenses yet."
        elif "budget" in message:
            recommended = round(total * 0.85, 2) if total else 0
            reply = f"Based on your current spending of ₹{total:,.2f}, a recommended monthly budget would be around ₹{recommended:,.2f}."

        return {"source": "fallback", "reply": reply, "disclaimer": DISCLAIMER}


bedrock_service = BedrockService()
