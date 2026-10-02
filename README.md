# API Marketplace & Developer Platform

## 1. Project Overview

The API Marketplace & Developer Platform is a platform where API providers can publish APIs and developers can subscribe to APIs, generate API keys, call APIs, monitor usage, and view analytics.

### Main Workflow

API Provider
↓
Creates API
↓
Creates API Version
↓
Publishes API
↓
Developer discovers API
↓
Creates Subscription
↓
Generates API Key
↓
Calls API through Gateway
↓
API Key Validation
↓
Subscription Validation
↓
Rate Limit Check
↓
Forward Request
↓
Usage Tracking
↓
Analytics Dashboard

### User Roles

#### Platform Admin
- Manage users
- Approve APIs
- Reject APIs
- Suspend APIs
- View platform usage
- View revenue
- Manage subscriptions

#### API Provider
- Create APIs
- Create API versions
- Add endpoints
- Create pricing plans
- Publish APIs
- View subscriptions
- View API usage
- Configure webhooks

#### Developer
- Browse APIs
- Subscribe to APIs
- Generate API keys
- Test APIs
- Monitor API usage
- View billing
- Revoke API keys

---

# 2. Technology Stack

## Backend

- Python 3.10+
- FastAPI
- MySQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT Authentication
- Redis
- Pytest
- Uvicorn

## Frontend

- React
- Vite
- Tailwind CSS
- React Router
- Axios
- React Hook Form
- Recharts

## Integrations

- Redis - Rate limiting
- Stripe - Subscription billing
- SMTP / SendGrid / Resend - Email notifications
- Cloud storage - API documentation/assets

---

# 3. Architecture

The project follows a frontend, backend, database and external-service architecture.

```text
                    React Frontend
                          |
                          |
                       Axios
                          |
                          ↓
                  FastAPI Backend
                          |
          ┌───────────────┼───────────────┐
          ↓               ↓               ↓
      JWT Auth         API Gateway      Services
          |               |               |
          ↓               ↓               ↓
       MySQL            Redis          Stripe
          |                               |
          ↓                               ↓
      SQLAlchemy                     Payments/Webhooks
          |
          ↓
       Alembic

Backend Structure
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── security.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   └── services/
├── alembic/
├── tests/
├── .env
├── .env.example
├── requirements.txt
└── README.md

Frontend Structure
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── routes/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/
├── package.json
└── vite.config.js

4. ER Diagram
User
 |
 | owner_id
 ↓
Organization
 |
 | organization_id
 ↓
API
 ├──────────────→ API Version
 |                    |
 |                    ↓
 |                API Endpoint
 |
 └──────────────→ API Plan
                      |
                      ↓
                  Subscription
                  /          \
                 ↓            ↓
             Developer      API Key
                                |
                                ↓
                         API Request Log
                                |
                                ↓
                         Usage Summary

API
 |
 ↓
Webhook
 |
 ↓
Webhook Delivery

Main Relationships
User → Organization
Organization → API
API → API Version
API Version → API Endpoint
API → API Plan
Developer → Subscription
Subscription → API Key
API → API Request Log
API Version → API Request Log
API Endpoint → API Request Log
API → Usage Summary
API → Webhook
Webhook → Webhook Delivery

5. Database Design
Users
users
-----
id
name
email
password_hash
role
is_active
created_at

Roles:
platform_admin
api_provider
developer

Organizations
organizations
-------------
id
name
owner_id
created_at

APIs
apis
----
id
organization_id
name
slug
description
category
status
created_at

API Versions
api_versions
------------
id
api_id
version
base_url
status
created_at

Version statuses:
active
deprecated
retired

API Endpoints
api_endpoints
-------------
id
api_version_id
method
path
description
authentication_required

API Plans
api_plans
---------
id
api_id
name
price
requests_per_month
requests_per_minute
is_active

Example plans:
Free
Developer
Business
Enterprise

Subscriptions
subscriptions
-------------
id
developer_id
api_id
plan_id
stripe_subscription_id
status
started_at
expires_at

API Keys
api_keys
--------
id
developer_id
subscription_id
key_hash
key_prefix
is_active
created_at
last_used_at
expires_at

The complete API key must never be stored as plain text.
API Request Logs
api_request_logs
----------------
id
api_id
api_version_id
developer_id
endpoint_id
api_key_id
method
status_code
response_time_ms
request_timestamp

Usage Summary
usage_summaries
---------------
id
developer_id
api_id
period_start
period_end
total_requests
successful_requests
failed_requests

Webhooks
webhooks
--------
id
api_id
event_type
target_url
secret
is_active

Webhook Deliveries
webhook_deliveries
------------------
id
webhook_id
event_id
status
response_code
attempt_count
delivered_at

6. API Documentation
Authentication
Register
POST /auth/register

Request:
{
  "name": "John",
  "email": "john@example.com",
  "password": "password123"
}

Login
POST /auth/login

Request:
{
  "email": "john@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}

Use:
Authorization: Bearer <access_token>

APIs
Create API
POST /apis/

Get APIs
GET /apis/

Submit API
POST /apis/{api_id}/submit

Review API
POST /apis/{api_id}/review

Approve API
POST /apis/{api_id}/approve

Reject API
POST /apis/{api_id}/reject

Publish API
POST /apis/{api_id}/publish

Suspend API
POST /apis/{api_id}/suspend

API Versions
POST /api-versions/
GET /api-versions/api/{api_id}
GET /api-versions/{version_id}
PATCH /api-versions/{version_id}/status

API Endpoints
POST /api-endpoints/
GET /api-endpoints/version/{api_version_id}
GET /api-endpoints/{endpoint_id}

API Plans
POST /api-plans/
GET /api-plans/api/{api_id}
GET /api-plans/{plan_id}
PATCH /api-plans/{plan_id}/status

Subscriptions
POST /subscriptions/
POST /subscriptions/{subscription_id}/checkout
GET /subscriptions/my
GET /subscriptions/billing
GET /subscriptions/provider
GET /subscriptions/all
GET /subscriptions/{subscription_id}
POST /subscriptions/{subscription_id}/cancel
POST /subscriptions/{subscription_id}/upgrade
POST /subscriptions/{subscription_id}/downgrade

API Keys
API keys allow developers to access subscribed APIs.
POST /api-keys/
GET /api-keys/my
GET /api-keys/{key_id}
PATCH /api-keys/{key_id}
POST /api-keys/{key_id}/revoke
POST /api-keys/{key_id}/regenerate

The actual API key is shown only once after generation.
API Gateway
/api-gateway/{api_slug}/{path}

Supported methods:
GET
POST
PUT
PATCH
DELETE

Required headers:
X-API-Key
X-API-Version

Gateway flow:
API Key
↓
Subscription
↓
API Version
↓
Rate Limit
↓
Forward Request
↓
Usage Log
↓
Response

Usage Analytics
GET /usage/my
GET /usage/api/{api_id}
GET /usage/analytics

Analytics include:
Total Requests
Successful Requests
Failed Requests
Average Response Time
Error Rate

Webhooks
POST /webhooks/
GET /webhooks/api/{api_id}
PATCH /webhooks/{webhook_id}/status
POST /webhooks/{webhook_id}/test
GET /webhooks/{webhook_id}/deliveries
POST /webhooks/{webhook_id}/retry/{delivery_id}

7. API Publishing Workflow
DRAFT
  ↓
SUBMITTED
  ↓
ADMIN_REVIEW
  ↓
APPROVED
  ↓
PUBLISHED

Rejected flow:
ADMIN_REVIEW
      ↓
   REJECTED
      ↓
     DRAFT

Only approved APIs can be published.
8. Setup Instructions
Clone Project
git clone <your-github-repository-url>
cd <project-folder>

Backend
cd backend
python -m venv venv

Windows
venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Run backend:
uvicorn app.main:app --reload

Backend:
http://127.0.0.1:8000

Swagger:
http://127.0.0.1:8000/docs

9. Database Setup
Create MySQL database:
CREATE DATABASE api_marketplace;

Configure .env:
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/api_marketplace

Run migrations:
alembic upgrade head

10. Redis Setup
Redis is used for API rate limiting.
Start Redis using Docker:
docker run -d \
  --name api-marketplace-redis \
  -p 6379:6379 \
  redis:latest

Check Redis:
docker exec -it api-marketplace-redis redis-cli ping

Expected:
PONG

Redis configuration:
REDIS_HOST=localhost
REDIS_PORT=6379

Rate limiting is enforced on the backend.
When the limit is exceeded:
HTTP 429
Too Many Requests

Response headers:
X-RateLimit-Limit
X-RateLimit-Remaining
X-RateLimit-Reset

11. Stripe Setup
Stripe is used for API subscription billing.
Add Stripe configuration to .env:
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

Create your products and prices in Stripe.
The application flow is:
Developer
   ↓
Select API Plan
   ↓
Checkout
   ↓
Stripe Payment
   ↓
Stripe Webhook
   ↓
Subscription Activated

The backend handles:
- Successful payment
- Failed payment
- Subscription cancellation
- Subscription renewal
- Plan upgrade
- Plan downgrade
- Payment webhook
- Duplicate webhook events
Never commit Stripe secret keys to GitHub.
12. Webhook Setup
API providers can create webhooks with:
API ID
Event Type
Target URL
Secret
Active Status

Example events:
subscription.created
subscription.cancelled
api.request.limit_reached
api.version.deprecated
payment.completed

Webhook security uses signature verification.
Webhook delivery flow:
Event
 ↓
Webhook Request
 ↓
Signature Validation
 ↓
Delivery
 ↓
Success

If delivery fails:
Webhook Failed
 ↓
Retry
 ↓
Retry
 ↓
Retry
 ↓
Mark as FAILED

Duplicate events are handled using event IDs.
13. Testing Instructions
The project uses Pytest.
Test folder:
tests/
├── __init__.py
├── conftest.py
├── test_auth.py
├── test_api_workflow.py
├── test_api_keys.py
├── test_gateway.py
├── test_webhooks.py
└── test_organization_isolation.py

Install Pytest:
pip install pytest

Run all tests:
pytest

Run with verbose output:
pytest -v

Tests Covered
- Registration
- Login
- Role authorization
- API creation
- API approval
- API publishing
- API key generation
- API key revocation
- Invalid API key
- Expired API key
- Subscription validation
- Rate limiting
- API gateway
- Usage tracking
- Duplicate webhook
- Webhook signature validation
- Organization isolation
14. Sample Credentials
Use sample/demo credentials only.
Platform Admin
Email:
admin@example.com

Password:
Admin@123

Role:
platform_admin

API Provider
Email:
provider@example.com

Password:
Provider@123

Role:
api_provider

Developer
Email:
developer@example.com

Password:
Developer@123

Role:
developer

These are sample credentials for demonstration. Change them for actual deployment.

15. Screenshots
Add project screenshots here.
Login
screenshots/login.png

 
Admin Dashboard
screenshots/admin-dashboard.png

 
Provider Dashboard
screenshots/provider-dashboard.png

 
Developer Dashboard
screenshots/developer-dashboard.png

 
API Management
screenshots/api-management.png

 
API Gateway
screenshots/api-gateway.png

 
Usage Analytics
screenshots/usage-analytics.png

 
Swagger API Documentation
screenshots/swagger.png

 
16. Security
The application implements:
- JWT authentication
- Password hashing
- Role-based authorization
- API key hashing
- API key expiration
- Redis rate limiting
- Request validation
- CORS
- Webhook signature validation
- Organization-level isolation
- Audit logging
Sensitive information must not be exposed.
Never commit:
.env
Database passwords
JWT secret
Stripe secret
API keys
Webhook secrets

17. Business Rules
API Access
A developer needs:
Valid API Key
+
Active Subscription
+
Active API
+
Valid API Version

API Keys
Revoked or expired keys cannot access APIs.
Subscriptions
Expired subscriptions cannot access paid APIs.
Rate Limiting
Rate limiting is enforced server-side using Redis.
Organization Isolation
One API provider cannot modify another provider's APIs.
Usage Isolation
Developers can view only their own usage.
API Approval
Only approved APIs can be published.
Webhook Security
Webhook signatures must be verified.
Duplicate Events
Webhook events must be idempotent.

19. Complete Project Flow:

Admin
 ↓
Create API Provider
 ↓
Create Organization
 ↓
Provider Login
 ↓
Create API
 ↓
Create API Version
 ↓
Create Endpoint
 ↓
Create Plan
 ↓
Submit API
 ↓
Admin Review
 ↓
Approve API
 ↓
Publish API
 ↓
Developer Login
 ↓
Create Subscription
 ↓
Stripe Checkout
 ↓
Subscription Active
 ↓
Generate API Key
 ↓
API Gateway
 ↓
Validate API Key
 ↓
Validate Subscription
 ↓
Validate API Version
 ↓
Redis Rate Limit
 ↓
Forward API Request
 ↓
Record Usage
 ↓
Analytics