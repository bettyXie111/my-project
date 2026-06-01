"""Seed demo data for local development and tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .database import init_database, transaction
from .security import generate_salt, hash_password, iso_now
from ..modules.common import generate_document_no, generate_id, json_dumps
from ..modules.constants import (
    BIZ_CONTRACT,
    BIZ_EXPENSE,
    BIZ_PERFORMANCE_PLAN,
    BIZ_PROCUREMENT_REQUEST,
    ROLE_AUDITOR,
    ROLE_FINANCE,
    ROLE_OPERATIONS_DIRECTOR,
    ROLE_PERMISSION_MAP,
    ROLE_PROCUREMENT,
    ROLE_SALES,
    ROLE_SCOPE_MAP,
    ROLE_SYSTEM_ADMIN,
    ROLE_WAREHOUSE,
    STATUS_ACTIVE,
    STATUS_APPROVED,
    STATUS_COMPLETED,
    STATUS_EFFECTIVE,
    STATUS_OPEN,
    STATUS_PARTIAL,
    STATUS_PENDING,
    WORKFLOW_STATUS_DONE,
    WORKFLOW_STATUS_OPEN,
)


def _clear_all(connection: Any) -> None:
    tables = [
        "approval_tasks",
        "workflow_instances",
        "workflow_templates",
        "payment_requests",
        "receipt_records",
        "expense_claims",
        "improvement_actions",
        "performance_plans",
        "performance_cycles",
        "performance_indicators",
        "stock_balances",
        "inventory_txns",
        "purchase_orders",
        "procurement_requests",
        "contracts",
        "sales_orders",
        "notifications",
        "file_assets",
        "audit_logs",
        "budgets",
        "warehouses",
        "projects",
        "item_master",
        "suppliers",
        "customers",
        "cost_centers",
        "system_configs",
        "users",
        "positions",
        "org_units",
        "roles",
        "refresh_tokens",
        "idempotency_keys",
    ]
    for table in tables:
        connection.execute(f"DELETE FROM {table}")


def _insert_role(connection: Any, code: str, name: str) -> str:
    role_id = generate_id("role")
    now = iso_now()
    connection.execute(
        """
        INSERT INTO roles(
            id, code, name, permissions_json, data_scope_type, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
        """,
        (
            role_id,
            code,
            name,
            json_dumps(ROLE_PERMISSION_MAP[code]),
            ROLE_SCOPE_MAP[code],
            STATUS_ACTIVE,
            now,
            now,
        ),
    )
    return role_id


def _insert_org(connection: Any, parent_id: str | None, name: str, unit_type: str) -> str:
    org_id = generate_id("org")
    now = iso_now()
    connection.execute(
        """
        INSERT INTO org_units(
            id, parent_id, name, unit_type, manager_user_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, NULL, ?, ?, 'seed', ?, 'seed', 1)
        """,
        (org_id, parent_id, name, unit_type, STATUS_ACTIVE, now, now),
    )
    return org_id


def _insert_position(connection: Any, org_unit_id: str, name: str) -> str:
    position_id = generate_id("pos")
    now = iso_now()
    connection.execute(
        """
        INSERT INTO positions(
            id, org_unit_id, name, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
        """,
        (position_id, org_unit_id, name, STATUS_ACTIVE, now, now),
    )
    return position_id


def _insert_user(
    connection: Any,
    *,
    username: str,
    display_name: str,
    org_unit_id: str,
    position_id: str,
    roles: list[str],
    email: str,
    mobile: str,
    password: str = "admin123",
) -> str:
    user_id = generate_id("user")
    salt = generate_salt()
    now = iso_now()
    connection.execute(
        """
        INSERT INTO users(
            id, username, password_hash, password_salt, display_name, email, mobile,
            org_unit_id, position_id, role_codes_json, status,
            failed_login_count, locked_until, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, 'seed', ?, 'seed', 1)
        """,
        (
            user_id,
            username,
            hash_password(password, salt),
            salt,
            display_name,
            email,
            mobile,
            org_unit_id,
            position_id,
            json_dumps(roles),
            STATUS_ACTIVE,
            now,
            now,
        ),
    )
    return user_id


def _seed_performance_domain(
    connection: Any,
    *,
    users: dict[str, str],
    primary_org_id: str,
    secondary_org_id: str,
    owner_org_id: str,
) -> dict[str, int]:
    from ..modules.workflows import create_workflow_instance

    now = iso_now()
    indicators = [
        ("KPI-DELIVERY", "目标达成率", "结果业绩", 30, "按实际达成率映射到 0-100 分"),
        ("KPI-COLLAB", "跨部门协同", "行为协同", 20, "依据项目协作反馈和及时性评分"),
        ("KPI-QUALITY", "交付质量", "专业质量", 20, "依据返工率和一次交付通过率评分"),
        ("KPI-INNOVATION", "改进创新", "成长创新", 15, "依据优化提案落地效果评分"),
        ("KPI-CUSTOMER", "客户满意度", "客户价值", 15, "依据内外部客户反馈评分"),
    ]
    indicator_rows: list[dict[str, Any]] = []
    for code, name, dimension, weight, rule in indicators:
        indicator_id = generate_id("kpi")
        indicator_rows.append(
            {
                "indicatorId": indicator_id,
                "code": code,
                "name": name,
                "dimension": dimension,
                "weight": float(weight),
                "scoringRule": rule,
            }
        )
        connection.execute(
            """
            INSERT INTO performance_indicators(
                id, code, name, dimension, weight, scoring_rule, owner_org_id, status,
                created_at, created_by, updated_at, updated_by, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, 'seed', ?, 'seed', 1)
            """,
            (indicator_id, code, name, dimension, float(weight), rule, owner_org_id, now, now),
        )

    cycles = [
        {
            "id": generate_id("cycle"),
            "code": "2026Q1",
            "name": "2026 年第一季度绩效周期",
            "periodType": "QUARTER",
            "startDate": "2026-01-01",
            "endDate": "2026-03-31",
            "selfDeadline": "2026-04-05",
            "managerDeadline": "2026-04-12",
        },
        {
            "id": generate_id("cycle"),
            "code": "2026Q2",
            "name": "2026 年第二季度绩效周期",
            "periodType": "QUARTER",
            "startDate": "2026-04-01",
            "endDate": "2026-06-30",
            "selfDeadline": "2026-07-05",
            "managerDeadline": "2026-07-12",
        },
    ]
    for cycle in cycles:
        connection.execute(
            """
            INSERT INTO performance_cycles(
                id, cycle_code, cycle_name, period_type, start_date, end_date,
                self_review_deadline, manager_review_deadline, status,
                created_at, created_by, updated_at, updated_by, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, 'seed', ?, 'seed', 1)
            """,
            (
                cycle["id"],
                cycle["code"],
                cycle["name"],
                cycle["periodType"],
                cycle["startDate"],
                cycle["endDate"],
                cycle["selfDeadline"],
                cycle["managerDeadline"],
                now,
                now,
            ),
        )

    connection.execute(
        """
        INSERT INTO workflow_templates(
            id, biz_type, name, definition_json, enabled, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, 1, 'ACTIVE', ?, 'seed', ?, 'seed', 1)
        """,
        (
            generate_id("wft"),
            BIZ_PERFORMANCE_PLAN,
            "绩效计划审批流程",
            json_dumps(
                {
                    "copyRoles": [ROLE_AUDITOR],
                    "nodes": [
                        {
                            "code": "DIRECTOR",
                            "name": "绩效委员会审批",
                            "assigneeRole": ROLE_OPERATIONS_DIRECTOR,
                            "timeoutHours": 24,
                        },
                        {
                            "code": "MANAGER",
                            "name": "直属经理确认",
                            "assigneeRole": ROLE_FINANCE,
                            "timeoutHours": 24,
                        },
                    ],
                }
            ),
            now,
            now,
        ),
    )

    high_scores = [
        {"code": "KPI-DELIVERY", "score": 90, "comment": "达成度稳定"},
        {"code": "KPI-COLLAB", "score": 88, "comment": "跨部门配合顺畅"},
        {"code": "KPI-QUALITY", "score": 92, "comment": "返工率低"},
        {"code": "KPI-INNOVATION", "score": 84, "comment": "有优化提案"},
        {"code": "KPI-CUSTOMER", "score": 86, "comment": "满意度良好"},
    ]
    low_scores = [
        {"code": "KPI-DELIVERY", "score": 68, "comment": "延期较多"},
        {"code": "KPI-COLLAB", "score": 72, "comment": "协同需要加强"},
        {"code": "KPI-QUALITY", "score": 70, "comment": "质量波动"},
        {"code": "KPI-INNOVATION", "score": 65, "comment": "主动改进不足"},
        {"code": "KPI-CUSTOMER", "score": 69, "comment": "反馈一般"},
    ]

    completed_plan_id = generate_id("plan")
    low_plan_id = generate_id("plan")
    approved_plan_id = generate_id("plan")
    pending_plan_id = generate_id("plan")

    connection.execute(
        """
        INSERT INTO performance_plans(
            id, plan_no, cycle_id, employee_user_id, manager_user_id, org_unit_id, title,
            scorecard_json, self_review_json, manager_review_json, total_score, final_grade,
            workflow_instance_id, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 'COMPLETED', ?, 'seed', ?, 'seed', 1)
        """,
        (
            completed_plan_id,
            generate_document_no("PP"),
            cycles[0]["id"],
            users["sales"],
            users["finance"],
            primary_org_id,
            "北方销售团队 2026Q1 绩效计划",
            json_dumps(indicator_rows),
            json_dumps({"summary": "已完成季度自评", "scores": high_scores, "submittedBy": users["sales"], "submittedAt": now}),
            json_dumps(
                {
                    "summary": "整体表现稳定，适合作为骨干培养对象",
                    "scores": high_scores,
                    "submittedBy": users["finance"],
                    "submittedAt": now,
                    "totalScore": 88.4,
                    "grade": "B",
                    "improvementRequired": False,
                }
            ),
            88.4,
            "B",
            now,
            now,
        ),
    )

    connection.execute(
        """
        INSERT INTO performance_plans(
            id, plan_no, cycle_id, employee_user_id, manager_user_id, org_unit_id, title,
            scorecard_json, self_review_json, manager_review_json, total_score, final_grade,
            workflow_instance_id, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 'COMPLETED', ?, 'seed', ?, 'seed', 1)
        """,
        (
            low_plan_id,
            generate_document_no("PP"),
            cycles[1]["id"],
            users["procurement"],
            users["finance"],
            secondary_org_id,
            "北方 HRBP 团队 2026Q2 绩效计划",
            json_dumps(indicator_rows),
            json_dumps({"summary": "项目推进压力较大，需要更多支持", "scores": low_scores, "submittedBy": users["procurement"], "submittedAt": now}),
            json_dumps(
                {
                    "summary": "目标承接和跨部门协同存在明显短板",
                    "scores": low_scores,
                    "submittedBy": users["finance"],
                    "submittedAt": now,
                    "totalScore": 69.0,
                    "grade": "D",
                    "improvementRequired": True,
                }
            ),
            69.0,
            "D",
            now,
            now,
        ),
    )

    connection.execute(
        """
        INSERT INTO performance_plans(
            id, plan_no, cycle_id, employee_user_id, manager_user_id, org_unit_id, title,
            scorecard_json, self_review_json, manager_review_json, total_score, final_grade,
            workflow_instance_id, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, 0, NULL, NULL, 'APPROVED', ?, 'seed', ?, 'seed', 1)
        """,
        (
            approved_plan_id,
            generate_document_no("PP"),
            cycles[1]["id"],
            users["warehouse"],
            users["finance"],
            primary_org_id,
            "数据分析岗 2026Q2 绩效计划",
            json_dumps(indicator_rows),
            now,
            now,
        ),
    )

    connection.execute(
        """
        INSERT INTO performance_plans(
            id, plan_no, cycle_id, employee_user_id, manager_user_id, org_unit_id, title,
            scorecard_json, self_review_json, manager_review_json, total_score, final_grade,
            workflow_instance_id, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, 0, NULL, NULL, 'DRAFT', ?, 'seed', ?, 'seed', 1)
        """,
        (
            pending_plan_id,
            generate_document_no("PP"),
            cycles[1]["id"],
            users["sales"],
            users["finance"],
            primary_org_id,
            "北方销售团队 2026Q2 绩效计划",
            json_dumps(indicator_rows),
            now,
            now,
        ),
    )

    create_workflow_instance(
        connection,
        biz_type=BIZ_PERFORMANCE_PLAN,
        biz_id=pending_plan_id,
        title="绩效计划审批（样例）",
        payload={"cycleName": cycles[1]["name"], "employeeName": "销售专员", "scoreItemCount": len(indicator_rows)},
        initiator_user_id=users["admin"],
        request_id="req_seed_performance_plan",
    )

    connection.execute(
        """
        INSERT INTO improvement_actions(
            id, action_no, plan_id, owner_user_id, sponsor_user_id, due_date, action_title,
            action_detail, progress_note, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, 'seed', ?, 'seed', 1)
        """,
        (
            generate_id("action"),
            generate_document_no("IA"),
            low_plan_id,
            users["procurement"],
            users["director"],
            "2026-07-31",
            "跨部门协同提升计划",
            "针对低分项制定每周复盘机制，并补充关键沟通节点负责人。",
            "已安排一对一辅导",
            now,
            now,
        ),
    )

    return {"indicators": len(indicator_rows), "cycles": len(cycles), "plans": 4, "improvementActions": 1}


def seed_database(force: bool = False) -> dict[str, int]:
    init_database()
    with transaction() as connection:
        existing_users = connection.execute("SELECT COUNT(1) AS total FROM users").fetchone()["total"]
        if existing_users and not force:
            return {"users": existing_users}
        if force:
            _clear_all(connection)

        role_names = {
            ROLE_SYSTEM_ADMIN: "系统管理员",
            ROLE_OPERATIONS_DIRECTOR: "运营总监",
            ROLE_SALES: "销售专员",
            ROLE_PROCUREMENT: "采购专员",
            ROLE_WAREHOUSE: "仓库管理员",
            ROLE_FINANCE: "财务专员",
            ROLE_AUDITOR: "审计人员",
        }
        for code, name in role_names.items():
            _insert_role(connection, code, name)

        org_hq = _insert_org(connection, None, "集团总部", "COMPANY")
        org_north = _insert_org(connection, org_hq, "北方事业部", "DIVISION")
        org_south = _insert_org(connection, org_hq, "南方事业部", "DIVISION")
        org_north_sales = _insert_org(connection, org_north, "北方销售部", "DEPARTMENT")
        org_north_proc = _insert_org(connection, org_north, "北方采购部", "DEPARTMENT")
        org_north_fin = _insert_org(connection, org_north, "北方财务部", "DEPARTMENT")
        org_north_wh = _insert_org(connection, org_north, "北方仓配中心", "DEPARTMENT")
        org_south_sales = _insert_org(connection, org_south, "南方销售部", "DEPARTMENT")
        org_south_proc = _insert_org(connection, org_south, "南方采购部", "DEPARTMENT")
        org_south_fin = _insert_org(connection, org_south, "南方财务部", "DEPARTMENT")
        org_south_wh = _insert_org(connection, org_south, "南方仓配中心", "DEPARTMENT")

        pos_admin = _insert_position(connection, org_hq, "平台管理员")
        pos_director = _insert_position(connection, org_north, "运营总监")
        pos_sales = _insert_position(connection, org_north_sales, "销售经理")
        pos_proc = _insert_position(connection, org_north_proc, "采购经理")
        pos_fin = _insert_position(connection, org_north_fin, "财务经理")
        pos_wh = _insert_position(connection, org_north_wh, "仓储主管")
        pos_auditor = _insert_position(connection, org_hq, "审计经理")

        users = {
            "admin": _insert_user(
                connection,
                username="admin",
                display_name="平台管理员",
                org_unit_id=org_hq,
                position_id=pos_admin,
                roles=[ROLE_SYSTEM_ADMIN, ROLE_AUDITOR],
                email="admin@example.com",
                mobile="13800000000",
            ),
            "director": _insert_user(
                connection,
                username="director",
                display_name="运营总监",
                org_unit_id=org_north,
                position_id=pos_director,
                roles=[ROLE_OPERATIONS_DIRECTOR],
                email="director@example.com",
                mobile="13800000001",
            ),
            "sales": _insert_user(
                connection,
                username="sales01",
                display_name="销售专员",
                org_unit_id=org_north_sales,
                position_id=pos_sales,
                roles=[ROLE_SALES],
                email="sales01@example.com",
                mobile="13800000002",
            ),
            "procurement": _insert_user(
                connection,
                username="proc01",
                display_name="采购专员",
                org_unit_id=org_north_proc,
                position_id=pos_proc,
                roles=[ROLE_PROCUREMENT],
                email="proc01@example.com",
                mobile="13800000003",
            ),
            "finance": _insert_user(
                connection,
                username="fin01",
                display_name="财务专员",
                org_unit_id=org_north_fin,
                position_id=pos_fin,
                roles=[ROLE_FINANCE],
                email="fin01@example.com",
                mobile="13800000004",
            ),
            "warehouse": _insert_user(
                connection,
                username="wh01",
                display_name="仓储专员",
                org_unit_id=org_north_wh,
                position_id=pos_wh,
                roles=[ROLE_WAREHOUSE],
                email="wh01@example.com",
                mobile="13800000005",
            ),
            "auditor": _insert_user(
                connection,
                username="audit01",
                display_name="审计专员",
                org_unit_id=org_hq,
                position_id=pos_auditor,
                roles=[ROLE_AUDITOR],
                email="audit01@example.com",
                mobile="13800000006",
            ),
        }

        now = iso_now()
        configs = [
            ("oidc.enabled", "false", "是否启用 OIDC 单点登录"),
            ("attachment.maxSize", "10485760", "附件大小限制"),
            ("workflow.timeoutHours", "24", "审批超时小时数"),
            ("budget.controlMode", "HARD", "预算控制模式"),
        ]
        for key, value, desc in configs:
            connection.execute(
                """
                INSERT INTO system_configs(
                    id, config_key, config_value, description, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (generate_id("cfg"), key, value, desc, STATUS_ACTIVE, now, now),
            )

        cost_centers = []
        org_sequence = [org_north_sales, org_north_proc, org_north_fin, org_north_wh, org_south_sales, org_south_proc]
        for index in range(1, 13):
            cost_center_id = generate_id("cc")
            cost_centers.append(cost_center_id)
            connection.execute(
                """
                INSERT INTO cost_centers(
                    id, code, name, org_unit_id, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    cost_center_id,
                    f"CC{index:03d}",
                    f"成本中心{index:02d}",
                    org_sequence[(index - 1) % len(org_sequence)],
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        customers = []
        for index in range(1, 26):
            customer_id = generate_id("cust")
            customers.append(customer_id)
            connection.execute(
                """
                INSERT INTO customers(
                    id, code, name, industry, owner_user_id, contact_name, contact_phone, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    customer_id,
                    f"CUST{index:03d}",
                    f"客户{index:03d}",
                    ["制造", "零售", "科技", "物流"][index % 4],
                    users["sales"],
                    f"联系人{index:02d}",
                    f"1390000{index:04d}",
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        suppliers = []
        for index in range(1, 21):
            supplier_id = generate_id("sup")
            suppliers.append(supplier_id)
            connection.execute(
                """
                INSERT INTO suppliers(
                    id, code, name, category, rating, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    supplier_id,
                    f"SUP{index:03d}",
                    f"供应商{index:03d}",
                    ["办公", "物流", "服务", "设备"][index % 4],
                    3 + index % 3,
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        items = []
        for index in range(1, 31):
            item_id = generate_id("item")
            items.append(item_id)
            connection.execute(
                """
                INSERT INTO item_master(
                    id, code, name, item_type, uom, safety_stock, unit_price, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    item_id,
                    f"ITEM{index:03d}",
                    f"物料{index:03d}",
                    "MATERIAL" if index % 3 else "SERVICE",
                    "EA",
                    float(20 + index),
                    float(50 + index * 3),
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        projects = []
        for index in range(1, 11):
            project_id = generate_id("proj")
            projects.append(project_id)
            connection.execute(
                """
                INSERT INTO projects(
                    id, code, name, owner_org_id, start_date, end_date, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    project_id,
                    f"PRJ{index:03d}",
                    f"项目{index:03d}",
                    org_north if index <= 5 else org_south,
                    f"2026-0{(index % 9) + 1}-01",
                    f"2026-12-{(index % 27) + 1:02d}",
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        warehouses = []
        warehouse_orgs = [org_north_wh, org_south_wh, org_north_wh, org_south_wh, org_hq]
        for index in range(1, 6):
            warehouse_id = generate_id("wh")
            warehouses.append(warehouse_id)
            connection.execute(
                """
                INSERT INTO warehouses(
                    id, code, name, org_unit_id, location, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    warehouse_id,
                    f"WH{index:03d}",
                    f"仓库{index:03d}",
                    warehouse_orgs[index - 1],
                    f"城市{index:02d}仓",
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        for month in range(1, 13):
            budget_id = generate_id("budget")
            budget_key = f"2026-{month:02d}-{org_north_proc}-{cost_centers[month % len(cost_centers)]}"
            connection.execute(
                """
                INSERT INTO budgets(
                    id, budget_year, budget_month, org_unit_id, project_id, cost_center_id,
                    budget_key, budget_amount, used_amount, warning_amount, control_mode, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, 2026, ?, ?, ?, ?, ?, ?, ?, ?, 'HARD', ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    budget_id,
                    month,
                    org_north_proc,
                    projects[month % len(projects)],
                    cost_centers[month % len(cost_centers)],
                    budget_key,
                    float(100000 + month * 5000),
                    float(month * 1200),
                    float(80000),
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        workflow_templates = [
            (
                BIZ_PROCUREMENT_REQUEST,
                "采购申请标准流程",
                {
                    "nodes": [
                        {"code": "DIRECTOR", "name": "运营总监审批", "assigneeRole": ROLE_OPERATIONS_DIRECTOR, "timeoutHours": 24},
                        {"code": "FINANCE", "name": "财务审批", "assigneeRole": ROLE_FINANCE, "timeoutHours": 24},
                    ],
                    "copyRoles": [ROLE_AUDITOR],
                },
            ),
            (
                BIZ_CONTRACT,
                "合同标准流程",
                {
                    "nodes": [
                        {"code": "DIRECTOR", "name": "运营总监审批", "assigneeRole": ROLE_OPERATIONS_DIRECTOR, "timeoutHours": 24},
                        {"code": "FINANCE", "name": "财务审批", "assigneeRole": ROLE_FINANCE, "timeoutHours": 24},
                    ],
                    "copyRoles": [ROLE_AUDITOR],
                },
            ),
            (
                BIZ_EXPENSE,
                "报销标准流程",
                {
                    "nodes": [
                        {"code": "DIRECTOR", "name": "直属负责人审批", "assigneeRole": ROLE_OPERATIONS_DIRECTOR, "timeoutHours": 24},
                        {"code": "FINANCE", "name": "财务审批", "assigneeRole": ROLE_FINANCE, "timeoutHours": 24},
                    ],
                    "copyRoles": [ROLE_AUDITOR],
                },
            ),
        ]
        for biz_type, name, definition in workflow_templates:
            connection.execute(
                """
                INSERT INTO workflow_templates(
                    id, biz_type, name, definition_json, enabled, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, 1, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (generate_id("wft"), biz_type, name, json_dumps(definition), STATUS_ACTIVE, now, now),
            )

        sales_orders = []
        for index in range(1, 11):
            order_id = generate_id("so")
            sales_orders.append(order_id)
            order_amount = float(10000 + index * 2500)
            items_json = json_dumps(
                [
                    {"itemId": items[index % len(items)], "qty": 5 + index, "unitPrice": 200 + index * 10},
                    {"itemId": items[(index + 1) % len(items)], "qty": 2 + index, "unitPrice": 180 + index * 12},
                ]
            )
            connection.execute(
                """
                INSERT INTO sales_orders(
                    id, order_no, customer_id, amount_total, currency, delivery_date, remark, items_json,
                    workflow_instance_id, status, created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, 'CNY', ?, ?, ?, NULL, ?, ?, ?, ?, ?, 1)
                """,
                (
                    order_id,
                    generate_document_no("SO"),
                    customers[index % len(customers)],
                    order_amount,
                    f"2026-06-{index:02d}",
                    f"样例销售订单 {index}",
                    items_json,
                    "DRAFT" if index % 3 else STATUS_APPROVED,
                    now,
                    users["sales"],
                    now,
                    users["sales"],
                ),
            )

        contracts = []
        for index in range(1, 11):
            contract_id = generate_id("ct")
            contracts.append(contract_id)
            status = STATUS_EFFECTIVE if index <= 6 else (STATUS_PENDING if index <= 8 else STATUS_COMPLETED)
            effective_date = f"2026-05-{index:02d}" if status != STATUS_PENDING else None
            expire_date = (datetime(2026, 12, 1) + timedelta(days=index * 5)).date().isoformat()
            receipt_progress = float(index * 10 if index <= 6 else 0)
            connection.execute(
                """
                INSERT INTO contracts(
                    id, contract_no, sales_order_id, amount_total, version_no, effective_date, expire_date,
                    receipt_progress, attachments_json, workflow_instance_id, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 1)
                """,
                (
                    contract_id,
                    generate_document_no("CT"),
                    sales_orders[index - 1],
                    float(15000 + index * 3000),
                    effective_date,
                    expire_date,
                    receipt_progress,
                    json_dumps([{"name": f"合同附件{index}.pdf"}]),
                    status,
                    now,
                    users["sales"],
                    now,
                    users["sales"],
                ),
            )

        procurement_requests = []
        purchase_orders = []
        for index in range(1, 11):
            request_id = generate_id("pr")
            procurement_requests.append(request_id)
            request_status = STATUS_APPROVED if index <= 5 else STATUS_PENDING
            budget_key = f"2026-{((index - 1) % 12) + 1:02d}-{org_north_proc}-{cost_centers[index % len(cost_centers)]}"
            request_items = [
                {"itemId": items[index % len(items)], "qty": 5 + index, "unitPrice": 120 + index * 8},
                {"itemId": items[(index + 2) % len(items)], "qty": 3 + index, "unitPrice": 80 + index * 7},
            ]
            amount_total = sum(item["qty"] * item["unitPrice"] for item in request_items)
            connection.execute(
                """
                INSERT INTO procurement_requests(
                    id, request_no, request_org_id, cost_center_id, project_id, budget_key, amount_total, need_date,
                    items_json, budget_check_result, workflow_instance_id, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 1)
                """,
                (
                    request_id,
                    generate_document_no("PR"),
                    org_north_proc,
                    cost_centers[index % len(cost_centers)],
                    projects[index % len(projects)],
                    budget_key,
                    amount_total,
                    f"2026-07-{index:02d}",
                    json_dumps(request_items),
                    json_dumps({"allowed": True, "requestedAmount": amount_total}),
                    request_status,
                    now,
                    users["procurement"],
                    now,
                    users["procurement"],
                ),
            )
            po_id = generate_id("po")
            purchase_orders.append(po_id)
            po_status = STATUS_COMPLETED if index <= 3 else (STATUS_PARTIAL if index <= 6 else STATUS_OPEN)
            received_amount = amount_total if po_status == STATUS_COMPLETED else amount_total * 0.5 if po_status == STATUS_PARTIAL else 0
            execution_rate = 100 if po_status == STATUS_COMPLETED else 50 if po_status == STATUS_PARTIAL else 0
            connection.execute(
                """
                INSERT INTO purchase_orders(
                    id, po_no, request_id, supplier_id, amount_total, expected_receipt_date,
                    items_json, received_amount, execution_rate, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    po_id,
                    generate_document_no("PO"),
                    request_id,
                    suppliers[index % len(suppliers)],
                    amount_total,
                    f"2026-08-{index:02d}",
                    json_dumps(request_items),
                    received_amount,
                    execution_rate,
                    po_status,
                    now,
                    users["procurement"],
                    now,
                    users["procurement"],
                ),
            )

        for index in range(1, 11):
            stock_balance_id = generate_id("stock")
            qty_on_hand = float(40 + index * 6)
            connection.execute(
                """
                INSERT INTO stock_balances(
                    id, warehouse_id, item_id, qty_on_hand, qty_reserved, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, 0, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    stock_balance_id,
                    warehouses[index % len(warehouses)],
                    items[index % len(items)],
                    qty_on_hand,
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO inventory_txns(
                    id, txn_no, warehouse_id, item_id, txn_type, qty, biz_ref_type, biz_ref_id,
                    remark, status, created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, 'RECEIPT', ?, 'SEED', ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    generate_id("txn"),
                    generate_document_no("IT"),
                    warehouses[index % len(warehouses)],
                    items[index % len(items)],
                    qty_on_hand,
                    purchase_orders[index - 1],
                    "期初库存导入",
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        expense_claims = []
        for index in range(1, 11):
            claim_id = generate_id("claim")
            expense_claims.append(claim_id)
            status = STATUS_APPROVED if index <= 4 else STATUS_PENDING
            amount_total = float(1500 + index * 260)
            budget_key = f"2026-{((index - 1) % 12) + 1:02d}-{org_north_proc}-{cost_centers[index % len(cost_centers)]}"
            connection.execute(
                """
                INSERT INTO expense_claims(
                    id, claim_no, claim_user_id, cost_center_id, project_id, amount_total, expense_type,
                    attachments_json, budget_key, budget_check_result, workflow_instance_id, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 1)
                """,
                (
                    claim_id,
                    generate_document_no("EC"),
                    users["sales"],
                    cost_centers[index % len(cost_centers)],
                    projects[index % len(projects)],
                    amount_total,
                    "TRAVEL" if index % 2 else "MARKETING",
                    json_dumps([{"name": f"报销附件{index}.pdf"}]),
                    budget_key,
                    json_dumps({"allowed": True, "requestedAmount": amount_total}),
                    status,
                    now,
                    users["sales"],
                    now,
                    users["sales"],
                ),
            )

        for index in range(1, 6):
            connection.execute(
                """
                INSERT INTO payment_requests(
                    id, payment_no, source_type, source_id, payee_name, amount_total, planned_date, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    generate_id("pay"),
                    generate_document_no("PAY"),
                    "EXPENSE_CLAIM",
                    expense_claims[index - 1],
                    f"收款方{index:02d}",
                    float(1000 + index * 200),
                    f"2026-09-{index:02d}",
                    STATUS_OPEN,
                    now,
                    now,
                ),
            )

        for index in range(1, 6):
            receipt_id = generate_id("receipt")
            amount = float(2000 + index * 800)
            connection.execute(
                """
                INSERT INTO receipt_records(
                    id, receipt_no, contract_id, amount, receipt_date, method, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    receipt_id,
                    generate_document_no("REC"),
                    contracts[index - 1],
                    amount,
                    f"2026-10-{index:02d}",
                    "BANK_TRANSFER",
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        open_workflows = [
            (
                BIZ_PROCUREMENT_REQUEST,
                procurement_requests[7],
                "采购申请待审批",
                users["director"],
                users["procurement"],
                {"requestOrgId": org_north_proc, "amountTotal": 48000},
            ),
            (
                BIZ_EXPENSE,
                expense_claims[8],
                "费用报销待审批",
                users["director"],
                users["sales"],
                {"amountTotal": 3680},
            ),
            (
                BIZ_CONTRACT,
                contracts[7],
                "合同待审批",
                users["director"],
                users["sales"],
                {"amountTotal": 42000},
            ),
        ]
        for biz_type, biz_id, title, assignee_user_id, initiator_user_id, payload in open_workflows:
            instance_id = generate_id("wf")
            task_id = generate_id("task")
            connection.execute(
                """
                INSERT INTO workflow_instances(
                    id, biz_type, biz_id, title, template_id, initiator_user_id,
                    current_node, result, payload_json, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, 'DIRECTOR', NULL, ?, 'IN_PROGRESS', ?, ?, ?, ?, 1)
                """,
                (
                    instance_id,
                    biz_type,
                    biz_id,
                    title,
                    generate_id("wft_link"),
                    initiator_user_id,
                    json_dumps(payload),
                    now,
                    initiator_user_id,
                    now,
                    initiator_user_id,
                ),
            )
            connection.execute(
                """
                INSERT INTO approval_tasks(
                    id, instance_id, biz_type, biz_id, node_code, node_name, assignee_user_id,
                    action, comment, due_at, status, created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, 'DIRECTOR', '运营总监审批', ?, NULL, NULL, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    task_id,
                    instance_id,
                    biz_type,
                    biz_id,
                    assignee_user_id,
                    (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
                    WORKFLOW_STATUS_OPEN,
                    now,
                    initiator_user_id,
                    now,
                    initiator_user_id,
                ),
            )

        done_workflows = [
            (BIZ_PROCUREMENT_REQUEST, procurement_requests[1], users["finance"], users["procurement"]),
            (BIZ_EXPENSE, expense_claims[1], users["finance"], users["sales"]),
            (BIZ_CONTRACT, contracts[1], users["finance"], users["sales"]),
        ]
        for biz_type, biz_id, assignee_user_id, initiator_user_id in done_workflows:
            instance_id = generate_id("wf")
            task_id = generate_id("task")
            connection.execute(
                """
                INSERT INTO workflow_instances(
                    id, biz_type, biz_id, title, template_id, initiator_user_id,
                    current_node, result, payload_json, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, '{}', 'COMPLETED', ?, ?, ?, ?, 1)
                """,
                (
                    instance_id,
                    biz_type,
                    biz_id,
                    f"{biz_type} 已审批",
                    generate_id("wft_link"),
                    initiator_user_id,
                    STATUS_APPROVED,
                    now,
                    initiator_user_id,
                    now,
                    assignee_user_id,
                ),
            )
            connection.execute(
                """
                INSERT INTO approval_tasks(
                    id, instance_id, biz_type, biz_id, node_code, node_name, assignee_user_id,
                    action, comment, due_at, status, created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, ?, ?, ?, 'FINANCE', '财务审批', ?, 'APPROVE', '样例通过', ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    task_id,
                    instance_id,
                    biz_type,
                    biz_id,
                    assignee_user_id,
                    (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z",
                    WORKFLOW_STATUS_DONE,
                    now,
                    initiator_user_id,
                    now,
                    assignee_user_id,
                ),
            )

        for index in range(1, 16):
            connection.execute(
                """
                INSERT INTO notifications(
                    id, channel, receiver_user_id, title, content, read_at, biz_ref_type, biz_ref_id, status,
                    created_at, created_by, updated_at, updated_by, version
                ) VALUES (?, 'IN_APP', ?, ?, ?, ?, ?, ?, ?, ?, 'seed', ?, 'seed', 1)
                """,
                (
                    generate_id("notice"),
                    users["director"] if index % 2 else users["finance"],
                    f"系统通知 {index:02d}",
                    f"这是第 {index} 条样例通知",
                    None if index % 3 else now,
                    "PROCUREMENT_REQUEST" if index % 2 else "EXPENSE_CLAIM",
                    procurement_requests[index % len(procurement_requests)] if index % 2 else expense_claims[index % len(expense_claims)],
                    STATUS_ACTIVE,
                    now,
                    now,
                ),
            )

        for index in range(1, 31):
            connection.execute(
                """
                INSERT INTO audit_logs(
                    id, actor_user_id, action_type, biz_type, biz_id, diff_json, request_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    generate_id("audit"),
                    users["admin"] if index % 3 else users["finance"],
                    ["LOGIN_SUCCESS", "BUDGET_CREATED", "WORKFLOW_APPROVE", "INVENTORY_RECEIVED"][index % 4],
                    ["CUSTOMER", "PROCUREMENT_REQUEST", "CONTRACT", "EXPENSE_CLAIM"][index % 4],
                    procurement_requests[index % len(procurement_requests)],
                    json_dumps({"seedIndex": index}),
                    f"req_seed_{index:03d}",
                    now,
                ),
            )

        performance_seed = _seed_performance_domain(
            connection,
            users=users,
            primary_org_id=org_north_sales,
            secondary_org_id=org_north_proc,
            owner_org_id=org_hq,
        )

        return {
            "users": 7,
            "customers": 25,
            "suppliers": 20,
            "items": 30,
            "projects": 10,
            "warehouses": 5,
            "budgets": 12,
            "contracts": 10,
            "procurementRequests": 10,
            "purchaseOrders": 10,
            "expenseClaims": 10,
            "performanceIndicators": performance_seed["indicators"],
            "performanceCycles": performance_seed["cycles"],
            "performancePlans": performance_seed["plans"],
        }
