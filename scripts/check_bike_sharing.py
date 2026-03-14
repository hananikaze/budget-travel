#!/usr/bin/env python3
"""
共享单车交叉验证工具 v2
Cross-validate bike sharing availability via Exa web search + 小红书.

用法: python3 check_bike_sharing.py <城市名> [--json]

信源:
  1. Exa 全网语义搜索 (via mcporter)
  2. 小红书实地用户反馈 (via xhs CLI)

检测目标:
  - 御三家: 美团🟡 / 哈啰🔵 / 青桔🟢
  - 政府公共自行车 (如杭州小红车、苏州好行等)
  - 区分人力自行车 🚲 vs 电助力自行车 ⚡

输出:
  - 各品牌存在情况 + 车辆类型
  - 政府公共自行车运营状况 (外地注册便利性、维护情况)
  - 综合评估
"""

import sys
import os
import json
import subprocess
import re
from datetime import datetime


# ── 配置 ──────────────────────────────────────────

PROVIDERS = {
    "美团": {
        "emoji": "🟡",
        "keywords": ["美团单车", "摩拜单车", "美团骑行"],
    },
    "哈啰": {
        "emoji": "🔵",
        "keywords": ["哈啰单车", "哈罗单车", "哈啰骑行"],
    },
    "青桔": {
        "emoji": "🟢",
        "keywords": ["青桔单车", "青桔骑行"],
    },
}

GOV_KEYWORDS = [
    "公共自行车", "市民卡", "有桩", "自行车服务点",
    "城市公共自行车", "免费骑行", "公共单车",
]

EBIKE_KEYWORDS = ["电动", "电助力", "助力车", "电单车", "电瓶", "充电"]
PEDAL_KEYWORDS = ["人力", "脚踏", "普通单车", "自行车"]


# ── Exa 搜索 ─────────────────────────────────────

def search_exa(city: str) -> dict:
    """通过 mcporter 调用 Exa 搜索，返回结构化结果"""
    queries = [
        f"{city} 共享单车 美团 哈啰 青桔 2025 2026",
        f"{city} 公共自行车 政府 市民卡 有桩",
    ]

    all_text = ""
    for q in queries:
        try:
            cmd = f"mcporter call 'exa.web_search_exa(query: \"{q}\", numResults: 5)'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            all_text += result.stdout + "\n"
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"⚠️  Exa 搜索失败: {e}", file=sys.stderr)

    return {"raw": all_text, "source": "exa"}


# ── 小红书搜索 ───────────────────────────────────

def search_xiaohongshu(city: str) -> dict:
    """通过小红书 CLI 搜索实地反馈"""
    xhs_dir = os.path.expanduser("~/.openclaw/skills/xiaohongshu-skills")
    cli_path = os.path.join(xhs_dir, "scripts", "cli.py")

    if not os.path.exists(cli_path):
        return {"raw": "", "source": "xiaohongshu", "error": "CLI not found"}

    queries = [
        f"{city} 共享单车",
        f"{city} 公共自行车",
    ]

    all_text = ""
    for q in queries:
        try:
            result = subprocess.run(
                [
                    "uv", "run", "python", cli_path,
                    "search-feeds",
                    "--keyword", q,
                    "--sort-by", "最新",
                    "--note-type", "图文",
                ],
                capture_output=True, text=True, timeout=30, cwd=xhs_dir,
            )
            all_text += result.stdout + "\n"
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"⚠️  小红书搜索失败: {e}", file=sys.stderr)

    return {"raw": all_text, "source": "xiaohongshu"}


# ── 分析引擎 ─────────────────────────────────────

def _count_mentions(text: str, keywords: list[str]) -> int:
    return sum(text.count(kw) for kw in keywords)


def _detect_bike_type(text: str, provider: str) -> str:
    """
    判断某品牌在该城市的车辆类型:
      "pedal"     = 人力自行车 🚲
      "ebike"     = 电助力自行车 ⚡
      "both"      = 两种都有
      "unknown"   = 无法判断
    """
    # 在提及该品牌的上下文中查找线索
    provider_mentions = []
    for kw in PROVIDERS.get(provider, {}).get("keywords", [provider]):
        for m in re.finditer(re.escape(kw), text):
            start = max(0, m.start() - 80)
            end = min(len(text), m.end() + 80)
            provider_mentions.append(text[start:end])

    context = " ".join(provider_mentions)
    has_ebike = any(kw in context for kw in EBIKE_KEYWORDS)
    has_pedal = any(kw in context for kw in PEDAL_KEYWORDS) or "单车" in context

    if has_ebike and has_pedal:
        return "both"
    elif has_ebike:
        return "ebike"
    elif has_pedal:
        return "pedal"
    return "unknown"


def analyze(city: str, exa_data: dict, xhs_data: dict) -> dict:
    """综合分析两个信源的数据"""
    combined_text = exa_data["raw"] + "\n" + xhs_data["raw"]

    result = {
        "city": city,
        "timestamp": datetime.now().isoformat(),
        "sources": {
            "exa": bool(exa_data["raw"].strip()),
            "xiaohongshu": bool(xhs_data["raw"].strip()) and "error" not in xhs_data,
        },
        "corporate": {},   # 御三家
        "government": None, # 政府公共自行车
        "summary": "",
    }

    # ── 御三家检测 ──
    for provider, cfg in PROVIDERS.items():
        exa_mentions = _count_mentions(exa_data["raw"], cfg["keywords"])
        xhs_mentions = _count_mentions(xhs_data["raw"], cfg["keywords"])
        total = exa_mentions + xhs_mentions

        if total > 0:
            bike_type = _detect_bike_type(combined_text, provider)
            result["corporate"][provider] = {
                "emoji": cfg["emoji"],
                "detected": True,
                "exa_mentions": exa_mentions,
                "xhs_mentions": xhs_mentions,
                "bike_type": bike_type,
                "confidence": "high" if (exa_mentions > 0 and xhs_mentions > 0) else "medium",
            }
        else:
            result["corporate"][provider] = {
                "emoji": cfg["emoji"],
                "detected": False,
                "exa_mentions": 0,
                "xhs_mentions": 0,
                "bike_type": "n/a",
                "confidence": "high" if result["sources"]["exa"] and result["sources"]["xiaohongshu"] else "low",
            }

    # ── 政府公共自行车检测 ──
    gov_mentions_exa = _count_mentions(exa_data["raw"], GOV_KEYWORDS)
    gov_mentions_xhs = _count_mentions(xhs_data["raw"], GOV_KEYWORDS)

    if gov_mentions_exa + gov_mentions_xhs > 0:
        # 尝试提取系统名称
        gov_name = _extract_gov_name(combined_text, city)
        # 分析运营状况
        ops_status = _analyze_gov_operations(combined_text, city)

        result["government"] = {
            "detected": True,
            "name": gov_name,
            "exa_mentions": gov_mentions_exa,
            "xhs_mentions": gov_mentions_xhs,
            "confidence": "high" if (gov_mentions_exa > 0 and gov_mentions_xhs > 0) else "medium",
            "operations": ops_status,
        }

    # ── 综合摘要 ──
    result["summary"] = _build_summary(result)
    return result


def _extract_gov_name(text: str, city: str) -> str:
    """尝试从文本中提取政府公共自行车系统的名称"""
    # 常见命名模式
    patterns = [
        rf"{city}(公共自行车)",
        rf"「(.{{2,10}}(?:公共自行车|单车|小[红绿蓝]车))」",
        rf"(小[红绿蓝]车)",
        rf"({city}.{{0,4}}(?:好行|畅行|绿行|公共自行车))",
        r"(永安行)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1) if m.lastindex else m.group(0)
    return f"{city}公共自行车"


def _analyze_gov_operations(text: str, city: str) -> dict:
    """
    分析政府公共自行车运营状况:
      - 外地注册便利性
      - 车辆维护状况
      - 总体运营评价
    """
    ops = {
        "registration_ease": "unknown",  # easy / moderate / difficult / unknown
        "registration_notes": "",
        "maintenance": "unknown",  # good / fair / poor / unknown
        "maintenance_notes": "",
        "bike_type": "pedal",  # 政府公共自行车通常是人力
        "overall": "unknown",
    }

    lower_text = text.lower()

    # ── 注册便利性 ──
    easy_signals = ["支付宝扫码", "微信扫码", "免押金", "扫码即骑", "无需办卡", "免押"]
    moderate_signals = ["需要办卡", "押金", "市民卡", "实名认证", "需下载APP"]
    hard_signals = ["本地户籍", "本地社保", "本地身份证", "不支持外地", "仅限本地"]

    easy_count = _count_mentions(text, easy_signals)
    moderate_count = _count_mentions(text, moderate_signals)
    hard_count = _count_mentions(text, hard_signals)

    if hard_count > 0:
        ops["registration_ease"] = "difficult"
        ops["registration_notes"] = "可能限制外地用户，需本地证件或社保"
    elif easy_count > moderate_count:
        ops["registration_ease"] = "easy"
        ops["registration_notes"] = "支持支付宝/微信扫码，外地用户友好"
    elif moderate_count > 0:
        ops["registration_ease"] = "moderate"
        ops["registration_notes"] = "需办卡或下载APP，可能需押金"
    # else: unknown

    # ── 维护状况 ──
    good_signals = ["维护好", "车况好", "新车", "很新", "干净", "好骑"]
    poor_signals = [
        "破旧", "坏车", "找不到", "没车", "车少", "难骑",
        "锈", "掉链", "没气", "坏了", "废弃", "停运",
    ]

    good_count = _count_mentions(text, good_signals)
    poor_count = _count_mentions(text, poor_signals)

    if poor_count > good_count and poor_count >= 2:
        ops["maintenance"] = "poor"
        ops["maintenance_notes"] = "用户反馈车辆维护较差，可能遇到坏车"
    elif good_count > poor_count and good_count >= 2:
        ops["maintenance"] = "good"
        ops["maintenance_notes"] = "用户反馈车况良好"
    elif good_count > 0 or poor_count > 0:
        ops["maintenance"] = "fair"
        ops["maintenance_notes"] = "评价不一，建议现场确认"

    # ── 电助力检测 ──
    if any(kw in text for kw in EBIKE_KEYWORDS):
        # 政府系统中同时有电助力
        ops["bike_type"] = "both"

    # ── 总体评价 ──
    if ops["registration_ease"] == "easy" and ops["maintenance"] in ("good", "fair"):
        ops["overall"] = "recommended"
    elif ops["registration_ease"] == "difficult":
        ops["overall"] = "not_recommended_for_tourists"
    elif ops["maintenance"] == "poor":
        ops["overall"] = "caution"
    else:
        ops["overall"] = "needs_verification"

    return ops


def _build_summary(result: dict) -> str:
    """生成人类可读的综合摘要"""
    city = result["city"]
    lines = []

    # 御三家
    detected_corps = [
        (p, info) for p, info in result["corporate"].items() if info["detected"]
    ]
    if detected_corps:
        names = []
        for p, info in detected_corps:
            type_label = {
                "pedal": "🚲人力",
                "ebike": "⚡电助力",
                "both": "🚲人力+⚡电助力",
                "unknown": "❓类型待确认",
            }.get(info["bike_type"], "❓")
            names.append(f"{info['emoji']}{p}({type_label})")
        lines.append(f"御三家: {', '.join(names)}")
    else:
        lines.append("御三家: 未检测到")

    # 政府
    gov = result["government"]
    if gov and gov["detected"]:
        ops = gov["operations"]
        type_label = "🚲人力" if ops["bike_type"] == "pedal" else "🚲人力+⚡电助力"
        lines.append(f"政府公共自行车: {gov['name']} ({type_label})")
        if ops["registration_notes"]:
            lines.append(f"  注册: {ops['registration_notes']}")
        if ops["maintenance_notes"]:
            lines.append(f"  维护: {ops['maintenance_notes']}")
        overall_map = {
            "recommended": "✅ 推荐使用",
            "not_recommended_for_tourists": "⚠️ 不推荐外地游客使用",
            "caution": "⚠️ 需注意车况",
            "needs_verification": "❓ 建议到达后实地确认",
        }
        lines.append(f"  评价: {overall_map.get(ops['overall'], '待确认')}")
    else:
        lines.append("政府公共自行车: 未检测到")

    # 信源
    src = result["sources"]
    src_list = []
    if src["exa"]:
        src_list.append("Exa✅")
    else:
        src_list.append("Exa❌")
    if src["xiaohongshu"]:
        src_list.append("小红书✅")
    else:
        src_list.append("小红书❌")
    lines.append(f"信源: {' / '.join(src_list)}")

    return "\n".join(lines)


# ── 格式化输出 ────────────────────────────────────

BIKE_TYPE_DISPLAY = {
    "pedal": "🚲 人力自行车",
    "ebike": "⚡ 电助力自行车",
    "both": "🚲 人力 + ⚡ 电助力",
    "unknown": "❓ 类型待现场确认",
    "n/a": "—",
}

CONFIDENCE_DISPLAY = {
    "high": "高（双信源验证）",
    "medium": "中（单信源）",
    "low": "低（信源不足）",
}


def print_result(result: dict):
    """格式化输出"""
    city = result["city"]
    print(f"\n{'='*60}")
    print(f"  🚲 {city} 共享单车检测报告")
    print(f"  📅 {result['timestamp'][:10]}")
    print(f"{'='*60}\n")

    # ── 御三家 ──
    print("【御三家企业共享单车】\n")
    any_corp = False
    for provider, info in result["corporate"].items():
        emoji = info["emoji"]
        if info["detected"]:
            any_corp = True
            bt = BIKE_TYPE_DISPLAY[info["bike_type"]]
            conf = CONFIDENCE_DISPLAY[info["confidence"]]
            print(f"  {emoji} {provider}: ✅ 已检测到")
            print(f"     车辆类型: {bt}")
            print(f"     Exa 提及 {info['exa_mentions']} 次 / 小红书 提及 {info['xhs_mentions']} 次")
            print(f"     置信度: {conf}")
        else:
            print(f"  {emoji} {provider}: ❌ 未检测到")
        print()

    if not any_corp:
        print("  ⚠️  该城市可能没有御三家共享单车，或已撤出\n")

    # ── 政府公共自行车 ──
    print("【政府公共自行车】\n")
    gov = result["government"]
    if gov and gov["detected"]:
        ops = gov["operations"]
        bt = BIKE_TYPE_DISPLAY.get(ops["bike_type"], "🚲 人力自行车")
        conf = CONFIDENCE_DISPLAY[gov["confidence"]]
        print(f"  ✅ {gov['name']}")
        print(f"     车辆类型: {bt}")
        print(f"     置信度: {conf}")

        print(f"\n  📋 运营状况:")
        # 注册
        reg_map = {
            "easy": "🟢 便捷（外地友好）",
            "moderate": "🟡 一般（需额外步骤）",
            "difficult": "🔴 不便（可能限制外地用户）",
            "unknown": "❓ 未知",
        }
        print(f"     外地注册: {reg_map[ops['registration_ease']]}")
        if ops["registration_notes"]:
            print(f"       → {ops['registration_notes']}")

        # 维护
        maint_map = {
            "good": "🟢 良好",
            "fair": "🟡 一般",
            "poor": "🔴 较差",
            "unknown": "❓ 未知",
        }
        print(f"     车辆维护: {maint_map[ops['maintenance']]}")
        if ops["maintenance_notes"]:
            print(f"       → {ops['maintenance_notes']}")

        # 总体
        overall_map = {
            "recommended": "✅ 推荐穷游使用（便宜、外地友好）",
            "not_recommended_for_tourists": "⚠️ 不推荐外地游客（注册门槛高）",
            "caution": "⚠️ 可用但需注意车况",
            "needs_verification": "❓ 建议到达后实地确认",
        }
        print(f"     总体评价: {overall_map.get(ops['overall'], '待确认')}")
    else:
        print("  ❌ 未检测到政府公共自行车系统\n")

    # ── 穷游建议 ──
    print(f"\n{'='*60}")
    print("  💡 穷游出行建议")
    print(f"{'='*60}\n")

    pedal_options = []
    ebike_options = []

    # 政府车
    if gov and gov["detected"]:
        ops = gov["operations"]
        if ops["bike_type"] in ("pedal", "both"):
            if ops["overall"] != "not_recommended_for_tourists":
                pedal_options.append(f"政府{gov['name']}（通常1h内免费）")
        if ops["bike_type"] in ("ebike", "both"):
            ebike_options.append(f"政府{gov['name']}电助力")

    # 御三家
    for provider, info in result["corporate"].items():
        if info["detected"]:
            if info["bike_type"] in ("pedal", "both", "unknown"):
                pedal_options.append(f"{info['emoji']}{provider}单车（1.5元/30min）")
            if info["bike_type"] in ("ebike", "both"):
                ebike_options.append(f"{info['emoji']}{provider}电助力（2-4元/次）")

    if pedal_options:
        print("  🚲 人力自行车（推荐，省钱）:")
        for opt in pedal_options:
            print(f"     • {opt}")
    if ebike_options:
        print("  ⚡ 电助力自行车（贵，仅应急）:")
        for opt in ebike_options:
            print(f"     • {opt}")
    if not pedal_options and not ebike_options:
        print("  🚨 该城市无共享单车！")
        print("     → 使用公交 + 步行")
        print("     → 问青旅是否有自行车租赁")
        print("     → 预留打车应急预算")

    # 信源
    src = result["sources"]
    print(f"\n  📡 信源状态: ", end="")
    parts = []
    parts.append(f"Exa {'✅' if src['exa'] else '❌'}")
    parts.append(f"小红书 {'✅' if src['xiaohongshu'] else '❌'}")
    print(" / ".join(parts))

    if not all(src.values()):
        print("  ⚠️  部分信源不可用，结果可能不完整，建议到达后实地确认")

    print(f"\n{'='*60}\n")


# ── 主函数 ────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python3 check_bike_sharing.py <城市名> [--json]")
        print("示例: python3 check_bike_sharing.py 苏州")
        print()
        print("通过 Exa + 小红书 交叉验证共享单车情况")
        print("区分: 御三家(美团/哈啰/青桔) + 政府公共自行车")
        print("区分: 🚲人力自行车 vs ⚡电助力自行车")
        sys.exit(1)

    city = sys.argv[1]
    json_mode = "--json" in sys.argv

    print(f"🔍 正在检测 {city} 的共享单车情况...", file=sys.stderr)
    print(f"   信源1: Exa 全网搜索...", file=sys.stderr)
    exa_data = search_exa(city)

    print(f"   信源2: 小红书实地反馈...", file=sys.stderr)
    xhs_data = search_xiaohongshu(city)

    print(f"   📊 交叉分析中...", file=sys.stderr)
    result = analyze(city, exa_data, xhs_data)

    if json_mode:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
