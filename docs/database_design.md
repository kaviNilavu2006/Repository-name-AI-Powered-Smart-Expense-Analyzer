# Database Design

The application uses **Amazon DynamoDB**, a NoSQL, key-value/document database, instead of a relational database like MySQL or PostgreSQL.

## Table 1: ExpenseAnalyzerExpenses

| Attribute | Type | Description |
|---|---|---|
| `user_id` | String (Partition Key) | ID of the user who owns this expense. Groups all of a user's expenses together for fast queries. |
| `expense_id` | String (Sort Key) | Unique ID for this expense record. |
| `amount` | String (Number) | The expense amount (stored as a string/decimal for precision). |
| `category` | String | One of: Food, Transport, Shopping, Bills, Entertainment, Education, Health, Travel, Rent, Other. |
| `description` | String | Free-text description (sanitized, max 500 chars). |
| `date` | String | Date of the expense, `YYYY-MM-DD`. |
| `payment_method` | String | One of: Cash, UPI, Debit Card, Credit Card, Bank Transfer. |
| `receipt_url` | String | Presigned S3 URL (or local path) to the uploaded receipt, if any. |
| `receipt_key` | String | The S3 object key (used internally for deletion). |
| `created_at` | String (ISO 8601) | Timestamp when the record was created. |

**Access patterns supported:**
- Get all expenses for a user → `Query` on partition key `user_id`.
- Get a single expense → `GetItem` with `user_id` + `expense_id`.
- Update/delete a specific expense → same composite key.

## Table 2: ExpenseAnalyzerUsers

| Attribute | Type | Description |
|---|---|---|
| `user_id` | String (Partition Key) | Unique user identifier. |
| `full_name` | String | User's display name. |
| `email` | String | Lowercased email address, used for login. |
| `password_hash` | String | Salted hash of the user's password (never plain text). |
| `created_at` | String (ISO 8601) | Account creation timestamp. |

**Global Secondary Index:** `email-index` (partition key: `email`) — enables efficient "find user by email" lookups during login without scanning the whole table.

**Access patterns supported:**
- Register a new user → `PutItem`.
- Look up a user during login → `Query` on the `email-index` GSI.
- Fetch a user's profile → `GetItem` with `user_id`.

## Why NoSQL (DynamoDB) Instead of a Relational Database?

1. **Access-pattern-first design:** Almost every query in this app is "get all expenses for this user" or "get one expense by ID" — a perfect fit for DynamoDB's partition-key model, without needing joins.
2. **Serverless & auto-scaling:** No database server to provision, patch, or scale manually — ideal for a student project with unpredictable/low traffic.
3. **Pay-per-request billing:** Costs stay near zero for a demo/college project.
4. **Native AWS integration:** Works seamlessly with IAM roles and the rest of the AWS-based architecture.

## Trade-offs Acknowledged

- DynamoDB does not support ad-hoc joins or complex multi-table aggregate queries the way SQL does. This project avoids that need by keeping the schema simple (two tables, no relational joins) and performing aggregation (totals, percentages) in the application layer (`services/analytics_service.py`) after fetching a user's own expense list.
- Because DynamoDB is schema-flexible, the application layer (`utils/validators.py`) is responsible for enforcing data consistency (valid categories, valid payment methods, etc.) that a relational database might otherwise enforce via constraints.

## Local Development Data Model

When AWS is not configured, `services/dynamodb_service.py` uses an in-memory Python dictionary structured identically to the two DynamoDB tables above, so the same query methods (`list_expenses_for_user`, `get_user_by_email`, etc.) work identically whether backed by real DynamoDB or the local fallback.
