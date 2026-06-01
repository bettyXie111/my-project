from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
CONTRACT_ROOT = ROOT / "packages" / "shared-contracts"

import sys

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from seed_data import RISK_RULEBOOK, build_demo_dataset  # noqa: E402


def build_api_contract() -> dict:
    return {
        "software": "隧道围岩变形预测与支护设计辅助软件",
        "version": "V1.0",
        "style": "REST JSON",
        "endpoints": [
            {"method": "POST", "path": "/api/auth/login", "summary": "登录并获取令牌"},
            {"method": "POST", "path": "/api/auth/logout", "summary": "退出并注销令牌"},
            {"method": "GET", "path": "/api/session", "summary": "读取当前登录身份"},
            {"method": "GET", "path": "/api/dashboard", "summary": "读取总览看板"},
            {"method": "GET", "path": "/api/sections", "summary": "筛选区段列表"},
            {"method": "GET", "path": "/api/sections/{id}", "summary": "读取区段详情"},
            {"method": "GET", "path": "/api/alerts", "summary": "读取预警处置卡片"},
            {"method": "GET", "path": "/api/predictions", "summary": "读取最近预测结果"},
            {"method": "POST", "path": "/api/predictions", "summary": "创建 7 天变形预测"},
            {"method": "GET", "path": "/api/recommendations", "summary": "读取最近支护建议"},
            {"method": "POST", "path": "/api/recommendations", "summary": "创建支护复核建议"},
            {"method": "GET", "path": "/api/contracts", "summary": "读取接口与支护规则摘要"},
        ],
        "requestSchemas": [
            {
                "name": "LoginRequest",
                "fields": [
                    {"name": "username", "type": "string", "required": True},
                    {"name": "password", "type": "string", "required": True},
                ],
            },
            {
                "name": "PredictionRequest",
                "fields": [
                    {"name": "sectionId", "type": "string", "required": True},
                    {"name": "scenarioName", "type": "string", "required": True},
                    {"name": "excavationIntensity", "type": "number", "required": True},
                    {"name": "rainfallFactor", "type": "number", "required": True},
                    {"name": "safetyFactor", "type": "number", "required": True},
                ],
            },
        ],
        "errorCodes": [
            {"code": 401, "message": "未登录或令牌失效"},
            {"code": 404, "message": "资源不存在"},
            {"code": 400, "message": "请求字段缺失或区段不存在"},
        ],
    }


def build_rulebook() -> dict:
    return {
        "name": "围岩支护规则簿",
        "description": "按综合风险分映射到支护级别与措施。",
        "levels": RISK_RULEBOOK,
        "decisionFactors": [
            "围岩级别",
            "地下水等级",
            "偏压类型",
            "拱顶沉降与周边收敛",
            "支护闭合时差",
            "施工扰动与降雨因子",
        ],
    }


def main() -> None:
    data_path = ROOT / "apps" / "api" / "data" / "demo_dataset.json"
    contract_path = CONTRACT_ROOT / "api_contract.json"
    rulebook_path = CONTRACT_ROOT / "support_rulebook.json"

    data_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.parent.mkdir(parents=True, exist_ok=True)

    data_path.write_text(json.dumps(build_demo_dataset(), ensure_ascii=False, indent=2), encoding="utf-8")
    contract_path.write_text(json.dumps(build_api_contract(), ensure_ascii=False, indent=2), encoding="utf-8")
    rulebook_path.write_text(json.dumps(build_rulebook(), ensure_ascii=False, indent=2), encoding="utf-8")

    print(data_path)
    print(contract_path)
    print(rulebook_path)


if __name__ == "__main__":
    main()

