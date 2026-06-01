"""Workflow template, instance, and approval task endpoints."""

from __future__ import annotations

from typing import Any

from ..core.exceptions import ConflictError, NotFoundError, ValidationError
from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    apply_business_status,
    audit_log,
    create_notification,
    generate_id,
    get_entity,
    json_dumps,
    json_loads,
    notify_workflow_result,
    now_plus_hours,
    require_fields,
    require_permission,
    workflow_final_status_for,
)
from .constants import (
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
    WORKFLOW_ACTION_ADD_SIGN,
    WORKFLOW_ACTION_APPROVE,
    WORKFLOW_ACTION_REJECT,
    WORKFLOW_ACTION_TRANSFER,
    WORKFLOW_STATUS_DONE,
    WORKFLOW_STATUS_OPEN,
)


def _find_template(connection: Any, biz_type: str) -> dict[str, Any]:
    row = connection.execute(
        """
        SELECT * FROM workflow_templates
        WHERE biz_type = ? AND enabled = 1 AND status = 'ACTIVE'
        ORDER BY created_at DESC LIMIT 1
        """,
        (biz_type,),
    ).fetchone()
    if row is None:
        raise ValidationError(f"未找到 {biz_type} 的流程模板")
    return {key: row[key] for key in row.keys()}


def _find_assignee_by_role(connection: Any, role_code: str) -> dict[str, Any]:
    row = connection.execute(
        """
        SELECT * FROM users
        WHERE status = 'ACTIVE' AND role_codes_json LIKE ?
        ORDER BY created_at ASC LIMIT 1
        """,
        (f'%"{role_code}"%',),
    ).fetchone()
    if row is None:
        raise ValidationError(f"未找到角色 {role_code} 的审批人")
    return {key: row[key] for key in row.keys()}


def _create_task(
    connection: Any,
    *,
    instance: dict[str, Any],
    node: dict[str, Any],
    assignee_user_id: str,
    created_by: str,
) -> dict[str, Any]:
    task_id = generate_id("task")
    now = iso_now()
    connection.execute(
        """
        INSERT INTO approval_tasks(
            id, instance_id, biz_type, biz_id, node_code, node_name,
            assignee_user_id, action, comment, due_at, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            task_id,
            instance["id"],
            instance["biz_type"],
            instance["biz_id"],
            node["code"],
            node["name"],
            assignee_user_id,
            now_plus_hours(int(node.get("timeoutHours", 24))),
            WORKFLOW_STATUS_OPEN,
            now,
            created_by,
            now,
            created_by,
        ),
    )
    create_notification(
        connection,
        receiver_user_id=assignee_user_id,
        title=f"待审批: {instance['title']}",
        content=f"{instance['biz_type']} 单据 {instance['biz_id']} 等待您的处理",
        biz_ref_type=instance["biz_type"],
        biz_ref_id=instance["biz_id"],
    )
    return {
        "id": task_id,
        "assigneeUserId": assignee_user_id,
        "nodeCode": node["code"],
        "nodeName": node["name"],
        "dueAt": now_plus_hours(int(node.get("timeoutHours", 24))),
    }


def create_workflow_instance(
    connection: Any,
    *,
    biz_type: str,
    biz_id: str,
    title: str,
    payload: dict[str, Any],
    initiator_user_id: str,
    request_id: str,
) -> dict[str, Any]:
    template = _find_template(connection, biz_type)
    definition = json_loads(template["definition_json"], {"nodes": []})
    nodes = definition.get("nodes", [])
    if not nodes:
        raise ValidationError("流程模板未配置节点")
    instance_id = generate_id("wf")
    now = iso_now()
    instance = {
        "id": instance_id,
        "biz_type": biz_type,
        "biz_id": biz_id,
        "title": title,
        "template_id": template["id"],
        "initiator_user_id": initiator_user_id,
        "current_node": nodes[0]["code"],
        "status": "IN_PROGRESS",
    }
    connection.execute(
        """
        INSERT INTO workflow_instances(
            id, biz_type, biz_id, title, template_id, initiator_user_id,
            current_node, result, payload_json, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            instance_id,
            biz_type,
            biz_id,
            title,
            template["id"],
            initiator_user_id,
            nodes[0]["code"],
            json_dumps(payload),
            "IN_PROGRESS",
            now,
            initiator_user_id,
            now,
            initiator_user_id,
        ),
    )
    first_node = nodes[0]
    assignee_user_id = first_node.get("assigneeUserId")
    if not assignee_user_id:
        assignee_user_id = _find_assignee_by_role(connection, first_node["assigneeRole"])["id"]
    task = _create_task(
        connection,
        instance=instance,
        node=first_node,
        assignee_user_id=assignee_user_id,
        created_by=initiator_user_id,
    )
    apply_business_status(
        connection,
        biz_type=biz_type,
        biz_id=biz_id,
        status=STATUS_PENDING,
        workflow_instance_id=instance_id,
    )
    audit_log(
        connection,
        actor_user_id=initiator_user_id,
        action_type="WORKFLOW_STARTED",
        biz_type=biz_type,
        biz_id=biz_id,
        diff={"instanceId": instance_id, "taskId": task["id"], "title": title},
        request_id=request_id,
    )
    for role_code in definition.get("copyRoles", []):
        copy_user = _find_assignee_by_role(connection, role_code)
        create_notification(
            connection,
            receiver_user_id=copy_user["id"],
            title=f"抄送: {title}",
            content=f"{biz_type} {biz_id} 已发起审批",
            biz_ref_type=biz_type,
            biz_ref_id=biz_id,
        )
    return {
        "instanceId": instance_id,
        "currentNode": first_node["code"],
        "status": "IN_PROGRESS",
        "firstTask": task,
    }


def _list_templates(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "workflow.manage")
    rows = context.db.execute(
        "SELECT * FROM workflow_templates ORDER BY biz_type, created_at DESC"
    ).fetchall()
    items = [{key: row[key] for key in row.keys()} for row in rows]
    for item in items:
        item["definition"] = json_loads(item.pop("definition_json"), {})
    return json_response(items, context.request_id)


def _create_template(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "workflow.manage")
    require_fields(context.body, "bizType", "name", "definition")
    now = iso_now()
    template_id = generate_id("wft")
    context.db.execute(
        """
        INSERT INTO workflow_templates(
            id, biz_type, name, definition_json, enabled, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            template_id,
            context.body["bizType"],
            context.body["name"],
            json_dumps(context.body["definition"]),
            int(context.body.get("enabled", True)),
            "ACTIVE",
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="WORKFLOW_TEMPLATE_CREATED",
        biz_type="WORKFLOW_TEMPLATE",
        biz_id=template_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"templateId": template_id, "status": "ACTIVE"}, context.request_id, status_code=201)


def _start_instance(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "workflow.manage")
    require_fields(context.body, "bizType", "bizId", "title", "payload")
    result = create_workflow_instance(
        context.db,
        biz_type=context.body["bizType"],
        biz_id=context.body["bizId"],
        title=context.body["title"],
        payload=context.body["payload"],
        initiator_user_id=context.user["id"],
        request_id=context.request_id,
    )
    return json_response(result, context.request_id, status_code=201)


def _list_tasks(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "workflow.approve")
    view = context.query.get("view", "todo")
    if view == "done":
        rows = context.db.execute(
            """
            SELECT * FROM approval_tasks
            WHERE assignee_user_id = ? AND status = ?
            ORDER BY updated_at DESC
            """,
            (context.user["id"], WORKFLOW_STATUS_DONE),
        ).fetchall()
        items = [{key: row[key] for key in row.keys()} for row in rows]
    elif view == "initiated":
        rows = context.db.execute(
            """
            SELECT * FROM workflow_instances
            WHERE initiator_user_id = ?
            ORDER BY created_at DESC
            """,
            (context.user["id"],),
        ).fetchall()
        items = [{key: row[key] for key in row.keys()} for row in rows]
    else:
        rows = context.db.execute(
            """
            SELECT * FROM approval_tasks
            WHERE assignee_user_id = ? AND status = ?
            ORDER BY created_at DESC
            """,
            (context.user["id"], WORKFLOW_STATUS_OPEN),
        ).fetchall()
        items = [{key: row[key] for key in row.keys()} for row in rows]
    return json_response(items, context.request_id)


def _task_action(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "workflow.approve")
    require_fields(context.body, "action")
    task_row = context.db.execute(
        "SELECT * FROM approval_tasks WHERE id = ?",
        (context.path_params["taskId"],),
    ).fetchone()
    if task_row is None:
        raise NotFoundError("审批任务不存在")
    task = {key: task_row[key] for key in task_row.keys()}
    if task["status"] != WORKFLOW_STATUS_OPEN:
        raise ConflictError("审批任务已处理", code="WORKFLOW_409_01")
    if task["assignee_user_id"] != context.user["id"]:
        raise ConflictError("审批任务处理人与当前登录用户不匹配", code="WORKFLOW_409_01")
    action = context.body["action"]
    if action not in {
        WORKFLOW_ACTION_APPROVE,
        WORKFLOW_ACTION_REJECT,
        WORKFLOW_ACTION_TRANSFER,
        WORKFLOW_ACTION_ADD_SIGN,
    }:
        raise ValidationError("不支持的审批动作")
    now = iso_now()
    if action == WORKFLOW_ACTION_TRANSFER:
        next_assignee_ids = context.body.get("nextAssigneeIds") or []
        if not next_assignee_ids:
            raise ValidationError("转交必须指定 nextAssigneeIds")
        context.db.execute(
            """
            UPDATE approval_tasks
            SET assignee_user_id = ?, updated_at = ?, updated_by = ?, version = version + 1
            WHERE id = ?
            """,
            (next_assignee_ids[0], now, context.user["id"], task["id"]),
        )
        create_notification(
            context.db,
            receiver_user_id=next_assignee_ids[0],
            title=f"待审批转交: {task['biz_type']}",
            content=f"任务 {task['id']} 已转交给您",
            biz_ref_type=task["biz_type"],
            biz_ref_id=task["biz_id"],
        )
        return json_response({"taskId": task["id"], "instanceStatus": "IN_PROGRESS"}, context.request_id)
    if action == WORKFLOW_ACTION_ADD_SIGN:
        next_assignee_ids = context.body.get("nextAssigneeIds") or []
        if not next_assignee_ids:
            raise ValidationError("加签必须指定 nextAssigneeIds")
        _create_task(
            context.db,
            instance={
                "id": task["instance_id"],
                "biz_type": task["biz_type"],
                "biz_id": task["biz_id"],
                "title": f"{task['biz_type']} 加签任务",
            },
            node={"code": task["node_code"], "name": task["node_name"], "timeoutHours": 24},
            assignee_user_id=next_assignee_ids[0],
            created_by=context.user["id"],
        )
        return json_response({"taskId": task["id"], "instanceStatus": "IN_PROGRESS"}, context.request_id)

    context.db.execute(
        """
        UPDATE approval_tasks
        SET status = ?, action = ?, comment = ?, updated_at = ?, updated_by = ?, version = version + 1
        WHERE id = ?
        """,
        (
            WORKFLOW_STATUS_DONE,
            action,
            context.body.get("comment"),
            now,
            context.user["id"],
            task["id"],
        ),
    )
    instance_row = context.db.execute(
        "SELECT * FROM workflow_instances WHERE id = ?",
        (task["instance_id"],),
    ).fetchone()
    if instance_row is None:
        raise NotFoundError("审批实例不存在")
    instance = {key: instance_row[key] for key in instance_row.keys()}
    template = _find_template(context.db, instance["biz_type"])
    nodes = json_loads(template["definition_json"], {"nodes": []}).get("nodes", [])
    current_index = next((idx for idx, node in enumerate(nodes) if node["code"] == task["node_code"]), -1)
    if current_index < 0:
        raise ValidationError("流程模板节点缺失")

    if action == WORKFLOW_ACTION_APPROVE and current_index + 1 < len(nodes):
        next_node = nodes[current_index + 1]
        assignee_user_id = next_node.get("assigneeUserId")
        if not assignee_user_id:
            assignee_user_id = _find_assignee_by_role(context.db, next_node["assigneeRole"])["id"]
        _create_task(
            context.db,
            instance=instance,
            node=next_node,
            assignee_user_id=assignee_user_id,
            created_by=context.user["id"],
        )
        context.db.execute(
            """
            UPDATE workflow_instances
            SET current_node = ?, updated_at = ?, updated_by = ?, version = version + 1
            WHERE id = ?
            """,
            (next_node["code"], now, context.user["id"], instance["id"]),
        )
        instance_status = "IN_PROGRESS"
    else:
        result = STATUS_APPROVED if action == WORKFLOW_ACTION_APPROVE else STATUS_REJECTED
        final_status = workflow_final_status_for(result, instance["biz_type"])
        context.db.execute(
            """
            UPDATE workflow_instances
            SET current_node = NULL, result = ?, status = 'COMPLETED',
                updated_at = ?, updated_by = ?, version = version + 1
            WHERE id = ?
            """,
            (result, now, context.user["id"], instance["id"]),
        )
        apply_business_status(
            context.db,
            biz_type=instance["biz_type"],
            biz_id=instance["biz_id"],
            status=final_status,
        )
        notify_workflow_result(
            context.db,
            biz_type=instance["biz_type"],
            biz_id=instance["biz_id"],
            initiator_user_id=instance["initiator_user_id"],
            result=result,
        )
        instance_status = "COMPLETED"
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type=f"WORKFLOW_{action}",
        biz_type=task["biz_type"],
        biz_id=task["biz_id"],
        diff={"taskId": task["id"], "comment": context.body.get("comment")},
        request_id=context.request_id,
    )
    return json_response({"taskId": task["id"], "instanceStatus": instance_status}, context.request_id)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/workflows/templates", _list_templates, permission="workflow.manage")
    router.add("POST", "/api/v1/workflows/templates", _create_template, permission="workflow.manage")
    router.add("POST", "/api/v1/workflows/instances", _start_instance, permission="workflow.manage")
    router.add("GET", "/api/v1/approvals/tasks", _list_tasks, permission="workflow.approve")
    router.add("POST", "/api/v1/approvals/tasks/{taskId}/actions", _task_action, permission="workflow.approve")
