from __future__ import annotations

from statistics import mean
from typing import Any
from uuid import uuid4


ROCK_SCORE = {"II": 8, "III": 18, "IV": 33, "V": 45}
GROUNDWATER_SCORE = {"弱": 4, "中等": 10, "较强": 15, "强": 20}
BIAS_SCORE = {"均压": 3, "左偏压": 8, "右偏压": 8}


def latest_monitor(section: dict[str, Any]) -> dict[str, Any]:
    records = section["monitoring"]
    return records[-1]


def previous_monitor(section: dict[str, Any]) -> dict[str, Any]:
    records = section["monitoring"]
    return records[-2] if len(records) > 1 else records[-1]


def monitor_summary(section: dict[str, Any]) -> dict[str, float]:
    current = latest_monitor(section)
    previous = previous_monitor(section)
    settlement = float(current["crownSettlement"])
    convergence = float(current["convergence"])
    arch_stress = float(current["archStress"])
    side_rate = float(current["sideWallRate"])
    settlement_delta = settlement - float(previous["crownSettlement"])
    convergence_delta = convergence - float(previous["convergence"])
    monitoring = section["monitoring"]
    return {
        "settlement": round(settlement, 2),
        "convergence": round(convergence, 2),
        "archStress": round(arch_stress, 2),
        "sideWallRate": round(side_rate, 2),
        "settlementDelta": round(settlement_delta, 2),
        "convergenceDelta": round(convergence_delta, 2),
        "weeklySettlement": round(mean(item["crownSettlement"] for item in monitoring[-5:]), 2),
        "weeklyConvergence": round(mean(item["convergence"] for item in monitoring[-5:]), 2),
    }


def risk_score(section: dict[str, Any]) -> float:
    summary = monitor_summary(section)
    deformation = summary["settlement"] * 0.8 + summary["convergence"] * 1.05
    rate_penalty = max(summary["settlementDelta"], 0) * 5.4 + max(summary["convergenceDelta"], 0) * 4.7
    support_lag_penalty = max(section["supportClosureHours"] - 12, 0) * 1.35
    burial_penalty = max(section["burialDepth"] - 180, 0) * 0.05
    reserved_gap_penalty = max(summary["convergence"] - section["reservedDeformation"] * 0.1, 0) * 1.8
    score = (
        ROCK_SCORE[section["rockGrade"]]
        + GROUNDWATER_SCORE[section["groundwaterLevel"]]
        + BIAS_SCORE[section["biasPressure"]]
        + deformation
        + rate_penalty
        + support_lag_penalty
        + burial_penalty
        + reserved_gap_penalty
    )
    return round(min(score, 100), 2)


def risk_level(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 65:
        return "HIGH"
    if score >= 48:
        return "MEDIUM"
    return "LOW"


def support_level(score: float) -> str:
    if score >= 80:
        return "E"
    if score >= 65:
        return "D"
    if score >= 50:
        return "C"
    if score >= 35:
        return "B"
    return "A"


def support_template(level: str, templates: list[dict[str, Any]]) -> dict[str, Any]:
    for template in templates:
        if template["level"] == level:
            return template
    raise KeyError(level)


def trend_factor(section: dict[str, Any], excavation_intensity: float, rainfall_factor: float, safety_factor: float) -> float:
    history = section["monitoring"][-4:]
    daily_jump = []
    for previous, current in zip(history, history[1:]):
        daily_jump.append((current["crownSettlement"] - previous["crownSettlement"]) * 0.7)
        daily_jump.append((current["convergence"] - previous["convergence"]) * 0.9)
    base = mean(daily_jump) if daily_jump else 0.6
    geology_factor = ROCK_SCORE[section["rockGrade"]] / 40.0
    water_factor = GROUNDWATER_SCORE[section["groundwaterLevel"]] / 25.0
    closure_factor = max(section["supportClosureHours"] - 12, 0) / 8.0
    return round(base * (1 + geology_factor + water_factor + closure_factor + excavation_intensity * 0.18 + rainfall_factor * 0.12) / safety_factor, 3)


def predict_section(section: dict[str, Any], scenario: dict[str, Any], templates: list[dict[str, Any]]) -> dict[str, Any]:
    summary = monitor_summary(section)
    excavation_intensity = float(scenario.get("excavationIntensity", 1.0))
    rainfall_factor = float(scenario.get("rainfallFactor", 0.5))
    safety_factor = max(float(scenario.get("safetyFactor", 1.15)), 0.8)
    increment = trend_factor(section, excavation_intensity, rainfall_factor, safety_factor)
    predicted_settlement = []
    predicted_convergence = []
    base_settlement = summary["settlement"]
    base_convergence = summary["convergence"]
    for day in range(1, 8):
        load_correction = day * 0.12 * excavation_intensity
        settle = round(base_settlement + day * increment + load_correction, 2)
        converge = round(base_convergence + day * increment * 0.86 + load_correction * 0.8, 2)
        predicted_settlement.append(settle)
        predicted_convergence.append(converge)
    predicted_peak = max(predicted_convergence)
    score = min(risk_score(section) + predicted_peak * 0.4 + excavation_intensity * 3 + rainfall_factor * 4, 100)
    level = risk_level(score)
    support = support_template(support_level(score), templates)
    return {
        "id": f"PRED-{uuid4().hex[:10].upper()}",
        "sectionId": section["id"],
        "sectionName": section["name"],
        "scenarioName": scenario.get("scenarioName", "默认情景"),
        "generatedAt": scenario.get("generatedAt", "2026-05-15T10:30:00"),
        "riskScore": round(score, 2),
        "riskLevel": level,
        "predictedSettlement": predicted_settlement,
        "predictedConvergence": predicted_convergence,
        "trendIncrement": increment,
        "recommendedSupportLevel": support["level"],
        "notes": [
            f"围岩级别 {section['rockGrade']}，日增量基于近 4 次监测趋势外推。",
            f"施工扰动系数按 {excavation_intensity:.2f} 计入，降雨放大系数按 {rainfall_factor:.2f} 计入。",
            f"若周边收敛超过 {round(section['reservedDeformation'] * 0.7, 1)} mm，应提前转入复核会商。",
        ],
    }


def generate_recommendation(
    section: dict[str, Any],
    scenario: dict[str, Any],
    templates: list[dict[str, Any]],
) -> dict[str, Any]:
    prediction = predict_section(section, scenario, templates)
    level = prediction["recommendedSupportLevel"]
    template = support_template(level, templates)
    summary = monitor_summary(section)
    adjusted_shotcrete = template["shotcreteThickness"] + (2 if summary["archStress"] > 170 else 0)
    arch_spacing = template["steelArchSpacing"]
    if prediction["riskLevel"] == "CRITICAL":
        arch_spacing = "0.35m"
    summary_text = (
        f"{section['zone']} 建议采用 {level} 级支护，喷射混凝土 {adjusted_shotcrete} cm，"
        f"锚杆长度 {template['boltLength']} m，拱架间距 {arch_spacing}。"
    )
    return {
        "id": f"REC-{uuid4().hex[:10].upper()}",
        "sectionId": section["id"],
        "sectionName": section["name"],
        "generatedAt": prediction["generatedAt"],
        "predictionId": prediction["id"],
        "level": level,
        "summary": summary_text,
        "measures": [
            f"初期支护闭合时差控制在 {template['closureHours']} 小时内。",
            f"采用 {template['advanceSupport']}，锁脚锚杆与钢拱架同步施工。",
            f"监测频率提升至 {template['monitoringCycle']}，并设置超限短信推送。",
            "当预测周边收敛日增量连续 2 天大于 1.5 mm 时，启动设计复核流程。",
        ],
        "materialPlan": {
            "shotcreteThicknessCm": adjusted_shotcrete,
            "boltLengthM": template["boltLength"],
            "boltSpacing": template["boltSpacing"],
            "steelArchSpacing": arch_spacing,
            "reservedDeformationMm": section["reservedDeformation"] + 10,
        },
        "comparison": {
            "initialShotcreteThicknessCm": section["initialSupport"]["shotcreteThickness"],
            "suggestedShotcreteThicknessCm": adjusted_shotcrete,
            "initialBoltLengthM": section["initialSupport"]["boltLength"],
            "suggestedBoltLengthM": template["boltLength"],
            "riskScoreBefore": risk_score(section),
            "riskScoreAfterMeasure": max(round(prediction["riskScore"] - 12.0, 2), 0),
        },
        "decisionBasis": [
            f"当前拱顶沉降 {summary['settlement']} mm，周边收敛 {summary['convergence']} mm。",
            f"围岩级别 {section['rockGrade']}，埋深 {section['burialDepth']} m，地下水 {section['groundwaterLevel']}。",
            f"监测速率 {summary['settlementDelta']} / {summary['convergenceDelta']} mm·d，呈连续增长。",
        ],
    }


def build_alerts(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for section in sections:
        summary = monitor_summary(section)
        score = risk_score(section)
        level = risk_level(score)
        if level == "LOW":
            continue
        alerts.append(
            {
                "id": f"ALT-{section['id']}",
                "sectionId": section["id"],
                "sectionName": section["name"],
                "riskLevel": level,
                "riskScore": round(score, 2),
                "trigger": f"周边收敛 {summary['convergence']} mm，单日增量 {summary['convergenceDelta']} mm",
                "action": "组织监测、施工、设计三方 2 小时内会商" if level == "CRITICAL" else "提升监测频率并复核开挖步距",
                "owner": "设计复核组" if level in {"HIGH", "CRITICAL"} else "监测工程师",
            }
        )
    return sorted(alerts, key=lambda item: item["riskScore"], reverse=True)


def dashboard_snapshot(dataset: dict[str, Any]) -> dict[str, Any]:
    sections = dataset["sections"]
    summaries = []
    for section in sections:
        score = risk_score(section)
        level = risk_level(score)
        summary = monitor_summary(section)
        summaries.append(
            {
                "id": section["id"],
                "name": section["name"],
                "zone": section["zone"],
                "rockGrade": section["rockGrade"],
                "riskScore": round(score, 2),
                "riskLevel": level,
                "settlement": summary["settlement"],
                "convergence": summary["convergence"],
                "archStress": summary["archStress"],
                "delta": summary["convergenceDelta"],
            }
        )
    high_risk = [item for item in summaries if item["riskLevel"] in {"HIGH", "CRITICAL"}]
    average_score = mean(item["riskScore"] for item in summaries)
    return {
        "siteName": dataset["meta"]["siteName"],
        "projectName": dataset["projects"][0]["name"],
        "totalSections": len(summaries),
        "highRiskSections": len(high_risk),
        "averageRiskScore": round(average_score, 2),
        "maxSettlement": round(max(item["settlement"] for item in summaries), 2),
        "maxConvergence": round(max(item["convergence"] for item in summaries), 2),
        "statusBoard": summaries,
        "alerts": build_alerts(sections)[:5],
    }

