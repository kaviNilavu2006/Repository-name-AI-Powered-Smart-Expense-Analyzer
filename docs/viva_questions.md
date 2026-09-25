# Viva Preparation — Questions &amp; Answers

Simple, student-friendly answers you can use directly in your project viva/demonstration.

---

**1. What is cloud computing?**
Cloud computing means using computing resources — servers, storage, databases, AI services — over the internet instead of owning physical hardware. You pay only for what you use, and the provider (AWS) manages the infrastructure.

**2. Why did you choose AWS for this project?**
AWS offers a mature, well-documented set of managed services (DynamoDB, S3, Bedrock) that cover every need of this project — database, file storage, and AI — without having to manage servers ourselves. It also has a free tier suitable for a student project.

**3. What is Amazon S3?**
S3 (Simple Storage Service) is AWS's object storage service. It stores files (like our receipt images and PDFs) as "objects" inside "buckets," and is highly durable and scalable.

**4. Why did you use S3 for receipts?**
Receipt images/PDFs are unstructured file data, not relational data — S3 is purpose-built for storing files like this cheaply and reliably, while DynamoDB stores only the lightweight metadata (the file's link).

**5. What is Amazon DynamoDB?**
DynamoDB is a fully managed, serverless NoSQL database from AWS. Data is stored as key-value/document items in tables, without needing a fixed schema like a SQL database.

**6. Why did you use DynamoDB instead of MySQL/PostgreSQL?**
Our main queries are simple — "get all expenses for this user" — which DynamoDB handles very efficiently using a partition key (`user_id`). DynamoDB is also serverless, so we don't need to manage or scale a database server ourselves.

**7. What is Amazon Bedrock?**
Bedrock is AWS's managed service for accessing foundation AI models (like Anthropic's Claude) through a single API, without hosting or training your own model.

**8. How does AI work in your project?**
We calculate a structured summary of the user's expenses (totals, categories, trends) in Python, then send that summary as a prompt to a Bedrock model. The model returns a structured, easy-to-read analysis: spending summary, top category, unusual spending, a saving suggestion, and a recommended budget.

**9. What is IAM?**
IAM (Identity and Access Management) is AWS's service for controlling who/what can access which AWS resources, and what actions they're allowed to perform.

**10. Why did you use IAM?**
IAM lets us grant our application only the exact permissions it needs (read/write to two specific DynamoDB tables, upload/read/delete in one S3 bucket, invoke one Bedrock model) — this is called the "principle of least privilege," and it's far safer than using broad admin access or hard-coded keys.

**11. What is AWS Elastic Beanstalk?**
Elastic Beanstalk is a "Platform as a Service" — you upload your application code, and AWS automatically handles provisioning servers, load balancing, and scaling for you.

**12. What is a REST API?**
REST (Representational State Transfer) is an architectural style for web APIs where resources (like "expenses") are accessed via standard HTTP methods (GET, POST, PUT, DELETE) at predictable URLs, and data is typically exchanged as JSON.

**13. Why did you use Flask?**
Flask is a lightweight Python web framework that's easy to learn and explain, yet powerful enough to build a complete REST API and serve HTML pages — ideal for a college project.

**14. How is a receipt stored, step by step?**
The user uploads a file in the "Add Expense" form → Flask validates its type and size → the file is uploaded to S3 with a unique key → S3 returns a location → we save that location (as a presigned URL) in the expense's DynamoDB record.

**15. How is expense data stored?**
Each expense becomes one "item" in the `ExpenseAnalyzerExpenses` DynamoDB table, with `user_id` as the partition key and a unique `expense_id` as the sort key.

**16. How does the AI receive expense data?**
The backend first aggregates the user's raw expenses into a summary (totals, category breakdowns, monthly trends) using our own analytics logic — this summary (not the raw list) is what's sent to Bedrock as context in the prompt.

**17. How do you protect user data?**
Passwords are hashed (never stored in plain text), sessions are server-side, and every API endpoint checks that data belongs to the logged-in user before returning or modifying it — one user can never see another user's expenses.

**18. What happens if Bedrock is unavailable?**
The app automatically falls back to a rule-based analysis written in plain Python, which calculates the same categories of insight from the data directly — the app never breaks, it just clearly labels the source as "Fallback Analysis Mode."

**19. What are the limitations of your project?**
It currently supports only manual expense entry (no OCR/auto-extraction from receipts), a fixed set of categories, and single-currency (INR) tracking. AI insights are informational, not professional financial advice.

**20. What are your future enhancements?**
OCR-based automatic receipt scanning, voice/SMS expense entry, predictive monthly spending, automated budget alerts, multi-currency support, and a mobile app (see `README.md` → Future Enhancements for the full list).

**21. What is a partition key and sort key?**
The partition key determines which physical partition an item is stored on (and is used to group related items — here, all expenses for one user). The sort key orders items within that same partition (here, distinguishing individual expenses).

**22. What is a Global Secondary Index (GSI)?**
A GSI lets you query a DynamoDB table using an attribute other than its primary key — we use one on `email` in the Users table so login can quickly look up a user without scanning the whole table.

**23. How do you validate user input?**
`utils/validators.py` checks that amounts are positive numbers, emails match a valid pattern, categories/payment methods come from a fixed allowed list, and uploaded files match allowed extensions and size limits, before anything is saved.

**24. What is password hashing, and why not just encrypt passwords?**
Hashing is a one-way transformation — you can verify a password without ever being able to reverse the hash back to the original. Encryption is reversible (given the key), which is riskier for storing passwords. We use Werkzeug's `generate_password_hash`/`check_password_hash`, which use a strong salted hash algorithm.

**25. How does your app handle errors?**
Every API endpoint returns a consistent JSON shape (`{ "success": false, "error": "..." }`) with an appropriate HTTP status code, and internal AWS error details are never shown directly to the user — only friendly, safe messages.

**26. What is a presigned URL?**
A presigned URL is a temporary, time-limited link to a private S3 object, generated using your AWS credentials. It lets a user view their own receipt without making the whole S3 bucket public.

**27. How would you scale this application for many more users?**
DynamoDB and S3 already scale automatically. We'd add Elastic Beanstalk auto-scaling rules for the compute layer, consider AWS Lambda for a fully serverless backend, and add caching (e.g. for repeated analytics queries) if needed.

**28. What testing did you do?**
We wrote automated `pytest` tests covering registration, login (success and failure), expense creation/listing/deletion, and analytics calculations, located in the `tests/` folder.

**29. Why is the AWS region important?**
Not all AWS services and models are available in every region. We chose `ap-south-1` (Mumbai) for DynamoDB/S3 for lower latency to Indian users, and documented that Bedrock model availability should be checked separately, since it isn't available in every region.

**30. What did you learn from this project?**
Answers will vary by student, but consider mentioning: integrating multiple AWS services together, designing a NoSQL data model around access patterns, building secure authentication, and using AI responsibly with clear disclaimers and safe fallbacks.

**31. Could this app work without any AWS account at all?**
Yes — every AWS-dependent service (DynamoDB, S3, Bedrock) has a safe local fallback, so the full application (including AI insights) can be demonstrated entirely on a laptop with no AWS account configured.

**32. How do you keep AWS credentials safe in this project?**
Credentials are never hard-coded in source code. Locally, they come from environment variables in a `.env` file (excluded from version control) or the AWS CLI's configured profile. In production, an IAM role attached to the Elastic Beanstalk/EC2 environment provides temporary, automatically-rotated credentials.
