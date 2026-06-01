"""WSGI application factory."""

from __future__ import annotations

from .core.database import init_database
from .core.seed import seed_database
from .core.routing import Application, Router
from .modules import audit, auth, dashboard, files, finance, iam, inventory, masterdata, notifications, procurement, sales, workflows


def create_application() -> Application:
    init_database()
    seed_database()
    router = Router()
    auth.register(router)
    iam.register(router)
    masterdata.register(router)
    workflows.register(router)
    sales.register(router)
    procurement.register(router)
    inventory.register(router)
    finance.register(router)
    dashboard.register(router)
    notifications.register(router)
    files.register(router)
    audit.register(router)
    return Application(router)
