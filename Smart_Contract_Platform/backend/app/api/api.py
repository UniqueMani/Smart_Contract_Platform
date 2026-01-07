from fastapi import APIRouter
from app.api.routers import auth, users, contracts, changes, payments, quantities, notifications, audits, dashboard

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(contracts.router)
api_router.include_router(changes.router)
api_router.include_router(payments.router)
api_router.include_router(quantities.router)
api_router.include_router(notifications.router)
api_router.include_router(audits.router)
api_router.include_router(dashboard.router)
