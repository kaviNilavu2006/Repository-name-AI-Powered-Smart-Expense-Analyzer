"""
DynamoDB Service
-----------------
Handles all reads/writes to the ExpenseAnalyzerExpenses and
ExpenseAnalyzerUsers tables.

If AWS credentials / DynamoDB are not reachable (e.g. pure local dev
without an AWS account configured), this service transparently falls
back to an in-memory store so the rest of the application keeps working.
This satisfies the "local development possible without AWS" requirement.
"""

import logging
import threading
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config.config import get_config

logger = logging.getLogger(__name__)
config = get_config()

_lock = threading.Lock()


class _InMemoryStore:
    """A minimal in-memory stand-in for the DynamoDB tables."""

    def __init__(self):
        self.expenses = {}  # expense_id -> item
        self.users = {}      # user_id -> item
        self.users_by_email = {}  # email -> user_id

    # ---- Expenses ----
    def put_expense(self, item):
        self.expenses[item["expense_id"]] = item
        return item

    def get_expense(self, user_id, expense_id):
        item = self.expenses.get(expense_id)
        if item and item.get("user_id") == user_id:
            return item
        return None

    def query_expenses_by_user(self, user_id):
        return [e for e in self.expenses.values() if e.get("user_id") == user_id]

    def delete_expense(self, user_id, expense_id):
        item = self.expenses.get(expense_id)
        if item and item.get("user_id") == user_id:
            del self.expenses[expense_id]
            return True
        return False

    def update_expense(self, user_id, expense_id, updates):
        item = self.get_expense(user_id, expense_id)
        if not item:
            return None
        item.update(updates)
        self.expenses[expense_id] = item
        return item

    # ---- Users ----
    def put_user(self, item):
        self.users[item["user_id"]] = item
        self.users_by_email[item["email"].lower()] = item["user_id"]
        return item

    def get_user_by_email(self, email):
        user_id = self.users_by_email.get(email.lower())
        if user_id:
            return self.users.get(user_id)
        return None

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)


_memory_store = _InMemoryStore()


class DynamoDBService:
    """
    Wraps boto3 DynamoDB resource calls. Falls back to an in-memory
    store automatically if AWS is not configured/reachable, so the app
    remains fully functional for local demos without an AWS account.
    """

    def __init__(self):
        self.use_aws = False
        self.expenses_table = None
        self.users_table = None
        self._try_connect()

    def _try_connect(self):
        try:
            kwargs = {"region_name": config.AWS_REGION}
            if config.DYNAMODB_ENDPOINT_URL:
                kwargs["endpoint_url"] = config.DYNAMODB_ENDPOINT_URL

            resource = boto3.resource("dynamodb", **kwargs)
            self.expenses_table = resource.Table(config.DYNAMODB_TABLE_NAME)
            self.users_table = resource.Table(config.DYNAMODB_USERS_TABLE_NAME)

            # A lightweight call to verify connectivity/credentials
            self.expenses_table.load()
            self.users_table.load()
            self.use_aws = True
            logger.info("Connected to DynamoDB tables successfully.")
        except (BotoCoreError, ClientError, Exception) as exc:
            logger.warning(
                "DynamoDB not reachable (%s). Falling back to in-memory store "
                "for local development.", exc,
            )
            self.use_aws = False

    # ------------------------------------------------------------------
    # Expense operations
    # ------------------------------------------------------------------
    def create_expense(self, expense_item: dict) -> dict:
        if self.use_aws:
            self.expenses_table.put_item(Item=expense_item)
            return expense_item
        with _lock:
            return _memory_store.put_expense(expense_item)

    def get_expense(self, user_id: str, expense_id: str):
        if self.use_aws:
            response = self.expenses_table.get_item(
                Key={"user_id": user_id, "expense_id": expense_id}
            )
            return response.get("Item")
        return _memory_store.get_expense(user_id, expense_id)

    def list_expenses_for_user(self, user_id: str) -> list:
        if self.use_aws:
            response = self.expenses_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id)
            )
            return response.get("Items", [])
        with _lock:
            return _memory_store.query_expenses_by_user(user_id)

    def update_expense(self, user_id: str, expense_id: str, updates: dict):
        if self.use_aws:
            existing = self.get_expense(user_id, expense_id)
            if not existing:
                return None
            existing.update(updates)
            self.expenses_table.put_item(Item=existing)
            return existing
        with _lock:
            return _memory_store.update_expense(user_id, expense_id, updates)

    def delete_expense(self, user_id: str, expense_id: str) -> bool:
        if self.use_aws:
            existing = self.get_expense(user_id, expense_id)
            if not existing:
                return False
            self.expenses_table.delete_item(
                Key={"user_id": user_id, "expense_id": expense_id}
            )
            return True
        with _lock:
            return _memory_store.delete_expense(user_id, expense_id)

    # ------------------------------------------------------------------
    # User operations
    # ------------------------------------------------------------------
    def create_user(self, user_item: dict) -> dict:
        if self.use_aws:
            self.users_table.put_item(Item=user_item)
            return user_item
        with _lock:
            return _memory_store.put_user(user_item)

    def get_user_by_email(self, email: str):
        if self.use_aws:
            response = self.users_table.query(
                IndexName="email-index",
                KeyConditionExpression=boto3.dynamodb.conditions.Key("email").eq(email.lower()),
            )
            items = response.get("Items", [])
            return items[0] if items else None
        return _memory_store.get_user_by_email(email)

    def get_user_by_id(self, user_id: str):
        if self.use_aws:
            response = self.users_table.get_item(Key={"user_id": user_id})
            return response.get("Item")
        return _memory_store.get_user_by_id(user_id)


# Singleton instance used across the app
dynamodb_service = DynamoDBService()
