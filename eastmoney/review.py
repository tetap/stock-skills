"""报告多重审核协议（结构化，供 MCP/Agent 调用）。"""

from __future__ import annotations

from typing import Any

FLOWS = ("B", "C", "D")

GATES = {
    "min_confidence_final": 5,
    "recommended_confidence": 7,
    "max_initial_confidence": 6,
    "min_tool_calls_b": 20,
    "min_tool_calls_c": 12,
    "min_challenge_questions_b": 5,
}


def get_review_protocol(*, flow: str = "B") -> dict[str, Any]:
    """返回指定流程的审核轮次、门禁与 §7 模板要求。"""
    flow = flow.upper()
    if flow not in FLOWS:
        raise ValueError(f"flow 必须是 {FLOWS}，收到: {flow}")

    base = {
        "flow": flow,
        "protocol_doc": "agent-skills/stock-main/review-protocol.md",
        "report_templates": {
            "B": "agent-skills/stock-main/analysis-report.md",
            "C": "agent-skills/stock-main/sector-report.md",
            "D": "agent-skills/stock-main/market-brief.md",
        },
        "gates": GATES,
        "confidence_rules": [
            "初稿置信度不得高于 6",
            "终稿 ≤4 禁止定稿，仅可列事实",
            "终稿 5~6 评级不得高于「右侧等待」",
            "终稿 ≥7 须完成 R4+R5 且无未解 P0",
        ],
        "mandatory_output": "终稿必须含 §7 审核纪要（轮次表 + 终稿/初稿置信度）",
        "quant_note": "quant_verdict 为研究辅助，不等于通过 OOS 回测的策略信号",
    }

    if flow == "B":
        base["min_tool_calls"] = GATES["min_tool_calls_b"]
        base["rounds"] = [
            {"id": "R0", "name": "数据采集", "required": ["工具≥20", "含 get_quant_technical"]},
            {"id": "R1", "name": "初稿", "internal_only": True},
            {"id": "R2", "name": "数据审计", "checklist": [
                "每个数字可指向工具字段",
                "四维度各有硬指标",
                "quant 5d/60d/158 已写入 §3",
                "新闻≥2条个股+1条行业",
            ]},
            {"id": "R3", "name": "魔鬼质疑", "min_questions": 5, "topics": [
                "基本面", "技术面", "资金面", "情绪面", "交易计划",
            ]},
            {"id": "R4", "name": "一致性矩阵", "pairs": [
                "Alpha158 vs Alpha360 5d/60d",
                "quant_verdict vs MA",
                "主力 vs 股价",
                "财报 vs 估值",
                "板块 vs 沪深300",
            ]},
            {"id": "R5", "name": "压力测试", "scenarios": 3},
            {"id": "R6", "name": "置信度门禁", "output_section": "§7"},
        ]
    elif flow == "C":
        base["min_tool_calls"] = GATES["min_tool_calls_c"]
        base["required_tools"] = [
            "search_sectors",
            "get_sector_detail",
            "get_sector_overview",
            "get_market_news",
            "get_market_fund_flow",
            "get_fund_flow_rank",
        ]
        base["rounds"] = [
            {"id": "R0", "name": "板块数据", "required": ["工具≥12", "含 search_sectors + 板块 kline/资金/成分"]},
            {"id": "R2", "name": "数据审计"},
            {"id": "R3", "name": "选股质疑"},
            {"id": "R4", "name": "板块-个股一致性"},
            {"id": "R6", "name": "门禁", "output_section": "§6 审核纪要"},
        ]
    else:
        base["min_tool_calls"] = 8
        base["required_tools"] = [
            "get_market_news",
            "get_sector_overview",
            "get_market_fund_flow",
            "get_fund_flow_rank",
            "get_market_snapshot",
        ]
        base["rounds"] = [
            {"id": "R0", "name": "快讯+板块+资金", "required": ["flash/headline/xueqiu_hot", "概念+行业 overview"]},
            {"id": "R3", "name": "热点持续性"},
            {"id": "R4", "name": "新闻-板块-资金交叉"},
            {"id": "R6", "name": "门禁", "output_section": "§7 审核纪要"},
        ]

    base["forbidden"] = [
        "跳过 R2~R5 直接输出终稿",
        "无工具来源的数字",
        "把 quant_verdict 当 guaranteed 策略信号",
    ]
    return base
