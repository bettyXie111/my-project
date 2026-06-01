CREATE TABLE IF NOT EXISTS performance_indicators (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    dimension TEXT NOT NULL,
    weight REAL NOT NULL,
    scoring_rule TEXT NOT NULL,
    owner_org_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_performance_indicators_dimension ON performance_indicators(dimension, status);

CREATE TABLE IF NOT EXISTS performance_cycles (
    id TEXT PRIMARY KEY,
    cycle_code TEXT NOT NULL UNIQUE,
    cycle_name TEXT NOT NULL,
    period_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    self_review_deadline TEXT NOT NULL,
    manager_review_deadline TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_performance_cycles_dates ON performance_cycles(start_date, end_date, status);

CREATE TABLE IF NOT EXISTS performance_plans (
    id TEXT PRIMARY KEY,
    plan_no TEXT NOT NULL UNIQUE,
    cycle_id TEXT NOT NULL,
    employee_user_id TEXT NOT NULL,
    manager_user_id TEXT NOT NULL,
    org_unit_id TEXT NOT NULL,
    title TEXT NOT NULL,
    scorecard_json TEXT NOT NULL,
    self_review_json TEXT,
    manager_review_json TEXT,
    total_score REAL NOT NULL DEFAULT 0,
    final_grade TEXT,
    workflow_instance_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    UNIQUE(cycle_id, employee_user_id)
);

CREATE INDEX IF NOT EXISTS idx_performance_plans_status ON performance_plans(status, cycle_id, manager_user_id);

CREATE TABLE IF NOT EXISTS improvement_actions (
    id TEXT PRIMARY KEY,
    action_no TEXT NOT NULL UNIQUE,
    plan_id TEXT NOT NULL,
    owner_user_id TEXT NOT NULL,
    sponsor_user_id TEXT NOT NULL,
    due_date TEXT NOT NULL,
    action_title TEXT NOT NULL,
    action_detail TEXT NOT NULL,
    progress_note TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_improvement_actions_status_due ON improvement_actions(status, due_date);
