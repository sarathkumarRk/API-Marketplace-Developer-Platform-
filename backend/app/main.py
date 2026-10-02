from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models

from app.routes import (
    auth,
    users,
    organizations,
    apis,
    api_versions,
    api_endpoints,
    api_plans,
    subscriptions,
    api_keys,
    gateway,
    usage,
    webhooks,
    dashboards,
    storage,
    advanced_sql
)


app = FastAPI(
    title="API Marketplace & Developer Platform",
    description="API Marketplace and Developer Platform Backend",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizations.router)
app.include_router(apis.router)
app.include_router(api_versions.router)
app.include_router(api_endpoints.router)
app.include_router(api_plans.router)
app.include_router(subscriptions.router)
app.include_router(api_keys.router)
app.include_router(gateway.router)
app.include_router(usage.router)
app.include_router(webhooks.router)
app.include_router(dashboards.router)
app.include_router(storage.router)
app.include_router(advanced_sql.router)


@app.get("/")
def root():
    return {
        "message": "API Marketplace & Developer Platform API is running"
    }

