from __future__ import annotations

from datetime import date, timedelta


RISK_RULEBOOK = [
    {
        "level": "A",
        "label": "稳定区",
        "scoreRange": [0, 34],
        "shotcreteThickness": 18,
        "boltLength": 3.0,
        "boltSpacing": "1.2m x 1.2m",
        "steelArchSpacing": "1.0m",
        "advanceSupport": "常规超前小导管",
        "closureHours": 24,
        "monitoringCycle": "每日 1 次",
    },
    {
        "level": "B",
        "label": "敏感区",
        "scoreRange": [35, 49],
        "shotcreteThickness": 22,
        "boltLength": 3.5,
        "boltSpacing": "1.0m x 1.0m",
        "steelArchSpacing": "0.8m",
        "advanceSupport": "超前小导管 + 锚索局部加密",
        "closureHours": 18,
        "monitoringCycle": "12 小时 1 次",
    },
    {
        "level": "C",
        "label": "预警区",
        "scoreRange": [50, 64],
        "shotcreteThickness": 26,
        "boltLength": 4.0,
        "boltSpacing": "0.9m x 0.9m",
        "steelArchSpacing": "0.6m",
        "advanceSupport": "超前管棚 + 系统锚杆",
        "closureHours": 14,
        "monitoringCycle": "8 小时 1 次",
    },
    {
        "level": "D",
        "label": "高风险区",
        "scoreRange": [65, 79],
        "shotcreteThickness": 30,
        "boltLength": 4.5,
        "boltSpacing": "0.8m x 0.8m",
        "steelArchSpacing": "0.5m",
        "advanceSupport": "长管棚 + 锚索 + 临时仰拱",
        "closureHours": 10,
        "monitoringCycle": "4 小时 1 次",
    },
    {
        "level": "E",
        "label": "应急区",
        "scoreRange": [80, 100],
        "shotcreteThickness": 34,
        "boltLength": 5.0,
        "boltSpacing": "0.7m x 0.7m",
        "steelArchSpacing": "0.4m",
        "advanceSupport": "全断面预加固 + 双层钢拱架",
        "closureHours": 8,
        "monitoringCycle": "2 小时 1 次",
    },
]

GEO_PROFILES = [
    ("ZK1", "IV", 186, "中风化砂岩夹薄层泥岩，层理发育，局部掉块。"),
    ("ZK2", "V", 224, "强风化板岩，富水软弱夹层明显，掌子面稳定性差。"),
    ("ZK3", "III", 152, "完整性较好的石灰岩，节理裂隙中等发育。"),
    ("ZK4", "IV", 278, "千枚岩挤压破碎，围岩有明显松弛区。"),
    ("ZK5", "V", 318, "断层破碎带，围岩含泥量高，遇水软化敏感。"),
    ("ZK6", "III", 138, "灰岩夹白云岩，完整性良好，地下水弱。"),
    ("ZK7", "IV", 246, "片麻岩裂隙水发育，存在局部挤压变形。"),
    ("ZK8", "V", 352, "深埋软岩段，初始应力高，岩爆与大变形并存。"),
    ("ZK9", "II", 108, "弱风化花岗岩，围岩稳定。"),
    ("ZK10", "IV", 232, "泥质粉砂岩与炭质板岩互层，遇水易剥落。"),
    ("ZK11", "V", 296, "偏压浅埋段，地表建筑敏感，洞口变形放大。"),
    ("ZK12", "III", 168, "石英砂岩完整性中等，需常规支护。"),
]

USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "name": "总控台管理员",
        "role": "admin",
        "title": "项目数字化负责人",
        "permissions": ["dashboard", "analysis", "design", "alerts", "reports"],
    },
    {
        "username": "monitor",
        "password": "admin123",
        "name": "监测工程师",
        "role": "monitor",
        "title": "现场监测组",
        "permissions": ["dashboard", "analysis", "alerts"],
    },
    {
        "username": "support",
        "password": "admin123",
        "name": "支护设计师",
        "role": "designer",
        "title": "设计复核组",
        "permissions": ["dashboard", "design", "reports"],
    },
]

REPORT_TEMPLATES = [
    {
        "id": "RPT-WEEKLY",
        "name": "周围岩变形巡检简报",
        "sections": ["概览", "风险段落", "预测趋势", "支护偏差", "监测计划"],
    },
    {
        "id": "RPT-ALERT",
        "name": "预警段应急处置清单",
        "sections": ["触发条件", "现场措施", "复测安排", "复核责任人"],
    },
]


def monitor_series(section_index: int, base_settlement: float, base_convergence: float) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    start_date = date(2026, 5, 1)
    for offset in range(10):
        wave = ((section_index + offset) % 4) * 0.6
        growth = offset * (0.42 + section_index * 0.015)
        rows.append(
            {
                "date": (start_date + timedelta(days=offset)).isoformat(),
                "crownSettlement": round(base_settlement + growth + wave, 2),
                "convergence": round(base_convergence + growth * 0.88 + wave * 0.4, 2),
                "archStress": round(110 + section_index * 9 + offset * 3.4 + wave * 8, 2),
                "sideWallRate": round(0.32 + section_index * 0.03 + offset * 0.045 + wave * 0.06, 2),
                "advanceMeters": round(1.25 + (section_index % 3) * 0.24 + offset * 0.03, 2),
            }
        )
    return rows


def initial_support(rock_grade: str) -> dict[str, str | int | float]:
    matrix = {
        "II": {"shotcreteThickness": 14, "boltLength": 2.5, "steelArch": "无", "reservedDeformation": 35},
        "III": {"shotcreteThickness": 18, "boltLength": 3.0, "steelArch": "I18", "reservedDeformation": 45},
        "IV": {"shotcreteThickness": 24, "boltLength": 3.8, "steelArch": "I20b", "reservedDeformation": 70},
        "V": {"shotcreteThickness": 28, "boltLength": 4.5, "steelArch": "H175", "reservedDeformation": 110},
    }
    return matrix[rock_grade]


def build_section(index: int, zone: str, rock_grade: str, burial_depth: int, remark: str) -> dict[str, object]:
    base_settlement = 5.2 + index * 1.4
    base_convergence = 4.4 + index * 1.1
    support_lag = 8 + index * 2
    water = ["弱", "中等", "较强", "强"][index % 4]
    bias = ["左偏压", "均压", "右偏压"][index % 3]
    risk = ["LOW", "MEDIUM", "HIGH", "CRITICAL"][min(index // 3, 3)]
    return {
        "id": f"SEC-{index + 1:03d}",
        "name": f"{zone} 掌子面",
        "zone": zone,
        "projectId": "PJ-TUNNEL-001",
        "rockGrade": rock_grade,
        "burialDepth": burial_depth,
        "biasPressure": bias,
        "groundwaterLevel": water,
        "designLevel": ["A", "B", "C", "D", "E"][min(index // 3, 4)],
        "advanceRate": round(1.35 + index * 0.09, 2),
        "supportClosureHours": support_lag,
        "reservedDeformation": 45 + index * 8,
        "monitoringFrequency": "8h" if rock_grade in {"IV", "V"} else "24h",
        "currentRisk": risk,
        "remarks": remark,
        "initialSupport": initial_support(rock_grade),
        "monitoring": monitor_series(index, base_settlement, base_convergence),
        "geologyNote": remark,
        "controlPoints": [
            "控制掌子面至仰拱闭合时差",
            "监测拱顶沉降与周边收敛同步增长",
            "超前支护与锁脚锚杆必须在当班闭合",
        ],
    }


def build_demo_dataset() -> dict[str, object]:
    sections = [build_section(index, *profile) for index, profile in enumerate(GEO_PROFILES)]
    return {
        "meta": {
            "softwareName": "隧道围岩变形预测与支护设计辅助软件",
            "version": "V1.0",
            "generatedAt": "2026-05-15T10:00:00",
            "siteName": "青云岭隧道右洞进口工区",
            "ownerUnit": "西南山岭交通建设项目部",
        },
        "users": USERS,
        "projects": [
            {
                "id": "PJ-TUNNEL-001",
                "name": "青云岭双线隧道围岩智能管控工程",
                "lineLength": 3840,
                "segmentCount": len(sections),
                "status": "construction",
                "designInstitute": "山地地下工程设计院",
                "monitoringVendor": "岩土监测中心",
            }
        ],
        "supportTemplates": RISK_RULEBOOK,
        "reportTemplates": REPORT_TEMPLATES,
        "sections": sections,
        "predictions": [],
        "recommendations": [],
        "auditTrail": [],
    }

