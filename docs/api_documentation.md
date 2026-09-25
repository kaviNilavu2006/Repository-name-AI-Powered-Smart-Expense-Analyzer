# API Documentation

All endpoints return JSON in the format:

```json
{ "success": true, "data": { ... }, "message": "..." }
```

or, on error:

```json
{ "success": false, "error": "Human-readable error message" }
```

Endpoints marked **🔒 Auth Required** require an active login session (a session cookie set by `/api/auth/login` or `/api/auth/register`). Requests without a valid session return `401 Unauthorized`.

---

## Authentication

### `POST /api/auth/register`
Registers a new user account.

**Body (JSON):**
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "password123",
  "confirm_password": "password123"
}
```

**Success (201):**
```json
{ "success": true, "message": "Registration successful.", "data": { "user": { "user_id": "...", "full_name": "Jane Doe", "email": "jane@example.com" } } }
```

**Errors:** `400` invalid input, `409` email already registered.

---

### `POST /api/auth/login`
Logs in an existing user.

**Body (JSON):** `{ "email": "...", "password": "..." }`

**Success (200):** Same shape as register. **Errors:** `400` missing fields, `401` invalid credentials.

---

### `POST /api/auth/logout`
🔒 Clears the current session. **Success (200):** `{ "success": true, "message": "Logged out successfully." }`

---

### `GET /api/auth/me`
🔒 Returns the currently logged-in user's basic info.

---

## Expenses

### `GET /api/expenses`
🔒 Lists the logged-in user's expenses.

**Query params (all optional):**
| Param | Description |
|---|---|
| `category` | Filter by exact category name |
| `search` | Case-insensitive substring match on description |
| `date_from` | `YYYY-MM-DD`, inclusive lower bound |
| `date_to` | `YYYY-MM-DD`, inclusive upper bound |
| `sort_by` | `date` (default) or `amount` |
| `order` | `asc` or `desc` (default) |

**Success (200):** `{ "success": true, "data": { "expenses": [...], "count": 5 } }`

---

### `POST /api/expenses`
🔒 Creates a new expense. **Content-Type:** `multipart/form-data` (to support file upload).

**Fields:** `amount` (number, >0), `category` (one of the fixed category list), `description` (string, optional), `date` (`YYYY-MM-DD`), `payment_method` (one of the fixed list), `receipt` (file, optional — JPG/JPEG/PNG/PDF, max 5MB).

**Success (201):** `{ "success": true, "message": "Expense added successfully.", "data": { "expense": {...} } }`

**Errors:** `400` validation failure, `502` receipt upload failure.

---

### `GET /api/expenses/<id>`
🔒 Fetches a single expense by ID (must belong to the logged-in user). **Errors:** `404` not found.

---

### `PUT /api/expenses/<id>`
🔒 Updates an existing expense. Same fields as `POST`, all optional (unspecified fields keep their existing value). Supports replacing the receipt file.

---

### `DELETE /api/expenses/<id>`
🔒 Deletes an expense (and its associated S3 receipt, if any). **Success (200):** `{ "success": true, "message": "Expense deleted successfully." }`

---

## Analytics

### `GET /api/analytics/summary`
🔒 Returns a full analytics summary: totals, averages, highest/lowest expense, category and payment method breakdowns, monthly/daily totals, and the 10 most recent expenses.

**Optional query param:** `period` — `current_month`, `previous_month`, `last_3_months`, or `current_year`. Omit to include all-time data.

---

### `GET /api/analytics/category`
🔒 Returns just `category_totals` and `category_percentages`. Accepts the same optional `period` param.

---

### `GET /api/analytics/monthly`
🔒 Returns `monthly_totals` and `daily_totals` across all recorded data (used for the dashboard's bar and line charts).

---

## AI

### `GET /api/ai/analyze`
🔒 Generates a structured AI spending analysis for the logged-in user's expenses.

**Success (200):**
```json
{
  "success": true,
  "data": {
    "source": "bedrock",
    "analysis": "### Spending Summary\n...",
    "disclaimer": "AI-generated insights are for informational purposes only..."
  }
}
```

`source` is `"bedrock"` when Amazon Bedrock generated the response, `"fallback"` when the rule-based local analysis was used instead, or `"none"` if the user has no expenses yet.

---

### `POST /api/ai/chat`
🔒 Chat-style Q&A grounded in the user's own expense data. **Never** exposes another user's data.

**Body (JSON):** `{ "message": "How much did I spend this month?" }`

**Success (200):**
```json
{ "success": true, "data": { "source": "fallback", "reply": "You spent ₹8,250.00 in 2026-09.", "disclaimer": "..." } }
```

---

## Uploads

### `POST /api/upload/receipt`
🔒 Standalone receipt upload (independent of a specific expense). **Content-Type:** `multipart/form-data`, field name `receipt`.

**Success (200):** `{ "success": true, "message": "Receipt uploaded successfully.", "data": { "key": "...", "url": "..." } }`

---

## Error Codes Summary

| Code | Meaning |
|---|---|
| 400 | Invalid or missing input |
| 401 | Not authenticated (no valid session) |
| 404 | Resource not found (or not owned by the current user) |
| 409 | Conflict (e.g. duplicate email on registration) |
| 500 | Internal server error (never exposes internal AWS error details) |
| 502 | Upstream cloud service (S3) failure during upload |
