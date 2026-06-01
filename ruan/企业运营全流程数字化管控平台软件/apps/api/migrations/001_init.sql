CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    permissions_json TEXT NOT NULL,
    data_scope_type TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS org_units (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    name TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    manager_user_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_org_units_parent_name ON org_units(parent_id, name);

CREATE TABLE IF NOT EXISTS positions (
    id TEXT PRIMARY KEY,
    org_unit_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    display_name TEXT NOT NULL,
    email TEXT,
    mobile TEXT,
    org_unit_id TEXT NOT NULL,
    position_id TEXT,
    role_codes_json TEXT NOT NULL,
    status TEXT NOT NULL,
    failed_login_count INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS system_configs (
    id TEXT PRIMARY KEY,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cost_centers (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    org_unit_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    industry TEXT,
    owner_user_id TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);

CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    rating INTEGER NOT NULL DEFAULT 3,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS item_master (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    item_type TEXT NOT NULL,
    uom TEXT NOT NULL,
    safety_stock REAL NOT NULL DEFAULT 0,
    unit_price REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_item_master_type ON item_master(item_type);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    owner_org_id TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS warehouses (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    org_unit_id TEXT NOT NULL,
    location TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS workflow_templates (
    id TEXT PRIMARY KEY,
    biz_type TEXT NOT NULL,
    name TEXT NOT NULL,
    definition_json TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_workflow_templates_biz_type ON workflow_templates(biz_type);

CREATE TABLE IF NOT EXISTS workflow_instances (
    id TEXT PRIMARY KEY,
    biz_type TEXT NOT NULL,
    biz_id TEXT NOT NULL,
    title TEXT NOT NULL,
    template_id TEXT NOT NULL,
    initiator_user_id TEXT NOT NULL,
    current_node TEXT,
    result TEXT,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    UNIQUE (biz_type, biz_id)
);

CREATE TABLE IF NOT EXISTS approval_tasks (
    id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    biz_type TEXT NOT NULL,
    biz_id TEXT NOT NULL,
    node_code TEXT NOT NULL,
    node_name TEXT NOT NULL,
    assignee_user_id TEXT NOT NULL,
    action TEXT,
    comment TEXT,
    due_at TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_approval_tasks_assignee_status ON approval_tasks(assignee_user_id, status);

CREATE TABLE IF NOT EXISTS sales_orders (
    id TEXT PRIMARY KEY,
    order_no TEXT NOT NULL UNIQUE,
    customer_id TEXT NOT NULL,
    amount_total REAL NOT NULL,
    currency TEXT NOT NULL,
    delivery_date TEXT NOT NULL,
    remark TEXT,
    items_json TEXT NOT NULL,
    workflow_instance_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_sales_orders_customer_id ON sales_orders(customer_id);

CREATE TABLE IF NOT EXISTS contracts (
    id TEXT PRIMARY KEY,
    contract_no TEXT NOT NULL UNIQUE,
    sales_order_id TEXT NOT NULL,
    amount_total REAL NOT NULL,
    version_no INTEGER NOT NULL DEFAULT 1,
    effective_date TEXT,
    expire_date TEXT NOT NULL,
    receipt_progress REAL NOT NULL DEFAULT 0,
    attachments_json TEXT NOT NULL,
    workflow_instance_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_contracts_expire_date ON contracts(expire_date);

CREATE TABLE IF NOT EXISTS procurement_requests (
    id TEXT PRIMARY KEY,
    request_no TEXT NOT NULL UNIQUE,
    request_org_id TEXT NOT NULL,
    cost_center_id TEXT NOT NULL,
    project_id TEXT,
    budget_key TEXT NOT NULL,
    amount_total REAL NOT NULL,
    need_date TEXT NOT NULL,
    items_json TEXT NOT NULL,
    budget_check_result TEXT NOT NULL,
    workflow_instance_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_procurement_requests_org_id ON procurement_requests(request_org_id);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id TEXT PRIMARY KEY,
    po_no TEXT NOT NULL UNIQUE,
    request_id TEXT NOT NULL,
    supplier_id TEXT NOT NULL,
    amount_total REAL NOT NULL,
    expected_receipt_date TEXT NOT NULL,
    items_json TEXT NOT NULL,
    received_amount REAL NOT NULL DEFAULT 0,
    execution_rate REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_purchase_orders_supplier_id ON purchase_orders(supplier_id);

CREATE TABLE IF NOT EXISTS inventory_txns (
    id TEXT PRIMARY KEY,
    txn_no TEXT NOT NULL UNIQUE,
    warehouse_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    txn_type TEXT NOT NULL,
    qty REAL NOT NULL,
    biz_ref_type TEXT NOT NULL,
    biz_ref_id TEXT NOT NULL,
    remark TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_inventory_txns_lookup ON inventory_txns(warehouse_id, item_id, created_at);

CREATE TABLE IF NOT EXISTS stock_balances (
    id TEXT PRIMARY KEY,
    warehouse_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    qty_on_hand REAL NOT NULL DEFAULT 0,
    qty_reserved REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    UNIQUE (warehouse_id, item_id)
);

CREATE TABLE IF NOT EXISTS expense_claims (
    id TEXT PRIMARY KEY,
    claim_no TEXT NOT NULL UNIQUE,
    claim_user_id TEXT NOT NULL,
    cost_center_id TEXT NOT NULL,
    project_id TEXT,
    amount_total REAL NOT NULL,
    expense_type TEXT NOT NULL,
    attachments_json TEXT NOT NULL,
    budget_key TEXT NOT NULL,
    budget_check_result TEXT NOT NULL,
    workflow_instance_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_expense_claims_claim_user ON expense_claims(claim_user_id);

CREATE TABLE IF NOT EXISTS budgets (
    id TEXT PRIMARY KEY,
    budget_year INTEGER NOT NULL,
    budget_month INTEGER NOT NULL,
    org_unit_id TEXT NOT NULL,
    project_id TEXT,
    cost_center_id TEXT NOT NULL,
    budget_key TEXT NOT NULL UNIQUE,
    budget_amount REAL NOT NULL,
    used_amount REAL NOT NULL DEFAULT 0,
    warning_amount REAL NOT NULL DEFAULT 0,
    control_mode TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS payment_requests (
    id TEXT PRIMARY KEY,
    payment_no TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    payee_name TEXT NOT NULL,
    amount_total REAL NOT NULL,
    planned_date TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_payment_requests_source ON payment_requests(source_type, source_id);

CREATE TABLE IF NOT EXISTS receipt_records (
    id TEXT PRIMARY KEY,
    receipt_no TEXT NOT NULL UNIQUE,
    contract_id TEXT NOT NULL,
    amount REAL NOT NULL,
    receipt_date TEXT NOT NULL,
    method TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_receipt_records_contract_date ON receipt_records(contract_id, receipt_date);

CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    receiver_user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    read_at TEXT,
    biz_ref_type TEXT,
    biz_ref_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_notifications_receiver_read ON notifications(receiver_user_id, read_at);

CREATE TABLE IF NOT EXISTS file_assets (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    object_key TEXT NOT NULL,
    content_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    biz_ref_type TEXT,
    biz_ref_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_file_assets_biz_ref ON file_assets(biz_ref_type, biz_ref_id);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    actor_user_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    biz_type TEXT NOT NULL,
    biz_id TEXT NOT NULL,
    diff_json TEXT NOT NULL,
    request_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_biz_lookup ON audit_logs(biz_type, biz_id, created_at);

CREATE TABLE IF NOT EXISTS idempotency_keys (
    id TEXT PRIMARY KEY,
    idem_key TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (idem_key, endpoint)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    created_at TEXT NOT NULL
);
