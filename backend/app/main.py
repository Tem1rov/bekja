"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as auth_router
from app.modules.tenants.router import router as tenants_router
from app.modules.users.router import router as users_router
from app.modules.products.router import router as products_router
from app.modules.warehouse.router import router as warehouse_router
from app.modules.warehouse.cells_router import router as warehouse_cells_router
from app.modules.orders.router import router as orders_router
from app.modules.finance.router import router as finance_router
from app.modules.integrations.router import router as integrations_router
from app.modules.notifications.router import router as notifications_router
from app.modules.dashboard.router import router as dashboard_router

app = FastAPI(title="FMS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tenants_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(warehouse_router, prefix="/api/v1")
app.include_router(warehouse_cells_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(finance_router, prefix="/api/v1")
app.include_router(integrations_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/health")
async def api_health():
    """API health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
