"""Shared enums and permission definitions."""

from __future__ import annotations


ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
ROLE_OPERATIONS_DIRECTOR = "OPERATIONS_DIRECTOR"
ROLE_SALES = "SALES"
ROLE_PROCUREMENT = "PROCUREMENT"
ROLE_WAREHOUSE = "WAREHOUSE"
ROLE_FINANCE = "FINANCE"
ROLE_AUDITOR = "AUDITOR"

STATUS_ACTIVE = "ACTIVE"
STATUS_DISABLED = "DISABLED"
STATUS_DRAFT = "DRAFT"
STATUS_PENDING = "PENDING_APPROVAL"
STATUS_APPROVED = "APPROVED"
STATUS_REJECTED = "REJECTED"
STATUS_EFFECTIVE = "EFFECTIVE"
STATUS_EXECUTING = "EXECUTING"
STATUS_COMPLETED = "COMPLETED"
STATUS_VOIDED = "VOIDED"
STATUS_OPEN = "OPEN"
STATUS_PARTIAL = "PARTIAL"

BIZ_PROCUREMENT_REQUEST = "PROCUREMENT_REQUEST"
BIZ_CONTRACT = "CONTRACT"
BIZ_EXPENSE = "EXPENSE_CLAIM"
BIZ_SALES_ORDER = "SALES_ORDER"

PERMISSIONS = {
    "iam.manage",
    "masterdata.manage",
    "workflow.manage",
    "workflow.approve",
    "sales.manage",
    "contract.manage",
    "procurement.manage",
    "inventory.manage",
    "finance.manage",
    "dashboard.view",
    "audit.view",
    "notification.view",
    "config.manage",
    "export.use",
}

ROLE_PERMISSION_MAP = {
    ROLE_SYSTEM_ADMIN: sorted(PERMISSIONS),
    ROLE_OPERATIONS_DIRECTOR: [
        "dashboard.view",
        "workflow.approve",
        "notification.view",
        "export.use",
    ],
    ROLE_SALES: ["sales.manage", "contract.manage", "dashboard.view", "notification.view"],
    ROLE_PROCUREMENT: [
        "procurement.manage",
        "workflow.manage",
        "notification.view",
        "dashboard.view",
    ],
    ROLE_WAREHOUSE: ["inventory.manage", "notification.view", "dashboard.view"],
    ROLE_FINANCE: [
        "finance.manage",
        "workflow.approve",
        "dashboard.view",
        "notification.view",
        "audit.view",
    ],
    ROLE_AUDITOR: ["audit.view", "dashboard.view", "notification.view"],
}

ROLE_SCOPE_MAP = {
    ROLE_SYSTEM_ADMIN: "ALL",
    ROLE_OPERATIONS_DIRECTOR: "ORG_TREE",
    ROLE_SALES: "SELF_ORG",
    ROLE_PROCUREMENT: "SELF_ORG",
    ROLE_WAREHOUSE: "SELF_ORG",
    ROLE_FINANCE: "SELF_ORG",
    ROLE_AUDITOR: "ALL",
}

WORKFLOW_STATUS_OPEN = "OPEN"
WORKFLOW_STATUS_DONE = "DONE"

WORKFLOW_ACTION_APPROVE = "APPROVE"
WORKFLOW_ACTION_REJECT = "REJECT"
WORKFLOW_ACTION_TRANSFER = "TRANSFER"
WORKFLOW_ACTION_ADD_SIGN = "ADD_SIGN"
