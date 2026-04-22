#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build slide spec from analysis JSON.")
    parser.add_argument("--analysis", required=True, help="Path to analysis.json.")
    parser.add_argument("--output", required=True, help="Path to slide_spec.json.")
    return parser.parse_args()


def load_analysis(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_slide_spec(analysis: dict) -> dict:
    pages = analysis["pages"]
    slides = [
        {
            "slide_id": "cover",
            "title": "会员标签与精准化运营研讨会",
            "subtitle": "基于固定模板 Excel 自动生成的汇报内容包",
            "layout": "cover",
            "kpis": [],
            "charts": [],
            "tables": [],
            "insights": [],
            "notes": {
                "source_sheets": [],
                "metric_logic": "封面页不含业务计算口径。",
            },
        },
        {
            "slide_id": "framework",
            "title": "分析框架与数据边界",
            "subtitle": "本报告仅使用 Excel 中可闭环的数据内容。",
            "layout": "framework",
            "kpis": [
                {"label": "核心底表", "value": "全部会员"},
                {"label": "门店补充", "value": "门店别"},
                {"label": "专题分析", "value": "已挂靠 / 待挂靠 / 会员日"},
            ],
            "charts": [],
            "tables": [],
            "insights": [
                "会员视角分析默认按会员去重。",
                "不可闭环的 PPT 人工页不直接沿用。",
                "后续 PPT 由独立 PPT skill 完成。"
            ],
            "notes": {
                "source_sheets": ["全部会员", "门店别", "一物一码来源已挂靠会员分析", "扫码>=50游离会员", "每月会员日参与名单"],
                "metric_logic": "说明页，不承载单独业务计算。",
            },
        },
        {
            "slide_id": "member_overview",
            "title": "会员概况：规模、标签覆盖与结构分布",
            "subtitle": "口径：总人数、年龄、等级来自全部会员；身份结构按身份标签。",
            "layout": "kpi_plus_charts",
            "kpis": [
                {"label": "累计会员人数", "value": pages["member_overview"]["total_members"]},
                {"label": "身份标注人数", "value": pages["member_overview"]["identity_labeled"]},
                {"label": "性别标注人数", "value": pages["member_overview"]["gender_labeled"]},
                {"label": "平均年龄", "value": pages["member_overview"]["avg_age"]},
            ],
            "charts": [
                {"kind": "bar", "title": "身份 Top 结构", "data": pages["member_overview"]["identity_top"]},
                {"kind": "column_pct", "title": "年龄分布", "data": pages["member_overview"]["age_distribution"]},
                {"kind": "column", "title": "会员等级分布", "data": pages["member_overview"]["level_distribution"]},
            ],
            "tables": [],
            "insights": [
                "当前身份标签覆盖率高，适合继续做工种分层运营。",
                "年龄结构集中在成熟施工人群。",
                "高等级会员池仍然偏小。"
            ],
            "notes": {
                "source_sheets": ["全部会员", "门店别"],
                "metric_logic": "身份统计使用身份标签字段，不使用最终身份字段。",
            },
        },
        {
            "slide_id": "qr_attached",
            "title": "一物一码来源已挂靠会员：可控店分布与转化现状",
            "subtitle": "仅保留当前上线的专卖店和涂装服务中心。",
            "layout": "kpi_plus_table",
            "kpis": [
                {"label": "可控上线门店", "value": pages["qr_attached"]["summary"]["store_count"]},
                {"label": "累计挂靠会员", "value": pages["qr_attached"]["summary"]["attached_members"]},
                {"label": "一物一码挂靠", "value": pages["qr_attached"]["summary"]["qr_attached_members"]},
                {"label": "会员日抽奖参与", "value": pages["qr_attached"]["summary"]["lottery_members"]},
            ],
            "charts": [],
            "tables": [
                {"title": "可控店一物一码挂靠情况", "data": pages["qr_attached"]["rows"]}
            ],
            "insights": [
                "挂靠规模最大的门店同时也是后续转化运营的优先对象。",
                "挂靠与消费、抽奖、核销之间的衔接可直接用来判断门店转化效率。"
            ],
            "notes": {
                "source_sheets": ["门店别", "一物一码来源已挂靠会员分析"],
                "metric_logic": "按可控上线门店筛选后汇总。",
            },
        },
        {
            "slide_id": "qr_pending",
            "title": "一物一码待挂靠会员：按工种与区域的待转化结构",
            "subtitle": "直接使用固定模板中的专题分析区域。",
            "layout": "double_table",
            "kpis": [
                {"label": "待挂靠人数", "value": pages["qr_pending"]["summary"]["pending_total"]},
                {"label": "头部工种", "value": pages["qr_pending"]["summary"]["top_job"]},
                {"label": "头部工种占比", "value": pages["qr_pending"]["summary"]["top_job_pct"]},
            ],
            "charts": [],
            "tables": [
                {"title": "按工种看扫码档位", "data": pages["qr_pending"]["job_table"]},
                {"title": "按区域看待挂靠人数", "data": pages["qr_pending"]["area_table"]},
            ],
            "insights": [
                "待挂靠人群首先应按工种和区域做优先级排序，不宜平均分配资源。",
                "50-99 包和 100-299 包是后续转化的核心分层。"
            ],
            "notes": {
                "source_sheets": ["扫码>=50游离会员"],
                "metric_logic": "使用固定区域取值，保留专题表原结构。",
            },
        },
        {
            "slide_id": "consumption",
            "title": "会员消费：去重消费、等级贡献与风险识别",
            "subtitle": "全部按会员去重口径统计。",
            "layout": "kpi_table_chart",
            "kpis": [
                {"label": "进店消费人数", "value": pages["consumption"]["overview"]["store_buyers"]},
                {"label": "扫码消费人数", "value": pages["consumption"]["overview"]["scan_buyers"]},
                {"label": "进店且扫码", "value": pages["consumption"]["overview"]["both_buyers"]},
                {"label": "去重活跃人数", "value": pages["consumption"]["overview"]["union_members"]},
            ],
            "charts": [
                {"kind": "column", "title": "最近一次消费月份", "data": pages["consumption"]["recent_consume_months"]}
            ],
            "tables": [
                {"title": "门店类型消费表现", "data": pages["consumption"]["by_store_type"]},
                {"title": "会员等级消费贡献", "data": pages["consumption"]["by_level"]},
            ],
            "insights": [
                "会员消费页必须按会员去重，不能直接用门店汇总人数替代。",
                "流失风险与需关注人群需单独成池。"
            ],
            "notes": {
                "source_sheets": ["全部会员"],
                "metric_logic": "风险池使用固定规则判断，不沿用原 PPT 值。",
            },
        },
        {
            "slide_id": "home_visit",
            "title": "上门基检：门店覆盖、拓新维旧与券转化",
            "subtitle": "全部来自 Excel，不引用原 PPT 混合页数值。",
            "layout": "kpi_plus_table",
            "kpis": [
                {"label": "覆盖会员", "value": pages["home_visit"]["summary"]["covered_members"]},
                {"label": "基检次数", "value": pages["home_visit"]["summary"]["times"]},
                {"label": "券获得", "value": pages["home_visit"]["summary"]["coupon_get"]},
                {"label": "券核销", "value": pages["home_visit"]["summary"]["coupon_use"]},
            ],
            "charts": [],
            "tables": [
                {"title": "重点门店基检表现", "data": pages["home_visit"]["rows"]}
            ],
            "insights": [
                "当前基检更偏维旧而不是拓新。",
                "基检动作与后续券核销、连带消费之间仍存在提升空间。"
            ],
            "notes": {
                "source_sheets": ["全部会员", "门店别"],
                "metric_logic": "总人数和券数据来自会员聚合，拓新维旧来自门店汇总字段。",
            },
        },
        {
            "slide_id": "member_day",
            "title": "会员日：参与频次、等级表现与奖券转化",
            "subtitle": "总体参与与中奖核销来自会员表，月度趋势来自会员日明细。",
            "layout": "kpi_chart_table",
            "kpis": [
                {"label": "参与人数", "value": pages["member_day"]["summary"]["participants"]},
                {"label": "参与率", "value": pages["member_day"]["summary"]["participant_pct"]},
                {"label": "人均参与次数", "value": pages["member_day"]["summary"]["avg_times"]},
                {"label": "SVIP参与率", "value": pages["member_day"]["summary"]["svip_pct"]},
            ],
            "charts": [
                {"kind": "column", "title": "月度会员日参与记录", "data": pages["member_day"]["month_trend"]}
            ],
            "tables": [
                {"title": "按店型参与率", "data": pages["member_day"]["by_store_type"]},
                {"title": "按等级参与与转化", "data": pages["member_day"]["by_level"]},
            ],
            "insights": [
                "会员日页适合同时看参与规模、等级表现和奖券转化。",
                "应优先关注高参与但低核销的人群层级。"
            ],
            "notes": {
                "source_sheets": ["全部会员", "每月会员日参与名单"],
                "metric_logic": "月度趋势按明细记录数统计。",
            },
        },
        {
            "slide_id": "segment_risk",
            "title": "会员分层与风险池：谁该被激活、谁在流失边缘",
            "subtitle": "这页完全由 Excel 行为数据重新定义，不再沿用原 9 页内容。",
            "layout": "kpi_plus_table",
            "kpis": [
                {"label": item["name"], "value": item["members"]}
                for item in pages["segment_risk"]["segments"]
            ],
            "charts": [],
            "tables": [
                {"title": "风险池规则", "data": pages["segment_risk"]["risk_rules"]}
            ],
            "insights": [
                "待转化潜力会员应成为后续门店运营的第一优先人群。",
                "沉默会员不适合用高成本方式全面运营。"
            ],
            "notes": {
                "source_sheets": ["全部会员"],
                "metric_logic": "基于消费、扫码、会员日、商城、基检五类行为构建分层。",
            },
        },
        {
            "slide_id": "store_priority",
            "title": "门店经营机会优先级：先做哪几家门店最有增量",
            "subtitle": "仅看当前上线的可控门店。",
            "layout": "table_with_ranking",
            "kpis": [],
            "charts": [
                {"kind": "bar", "title": "门店机会分", "data": pages["store_priority"]["rows"]}
            ],
            "tables": [
                {"title": "门店机会分排序", "data": pages["store_priority"]["rows"]}
            ],
            "insights": [
                "门店机会分是第一版自动汇报模型，可作为汇报中的优先级排序基础。",
                "不建议把它直接视为最终业务评分模型。"
            ],
            "notes": {
                "source_sheets": ["门店别"],
                "metric_logic": "按会员盘、消费率、挂靠、扫码、会员日、商城渗透等指标加权计算。",
            },
        },
        {
            "slide_id": "conversion_path",
            "title": "转化路径与运营建议：从标签覆盖到消费沉淀",
            "subtitle": "展示会员盘在关键运营触点上的覆盖情况。",
            "layout": "pathway_summary",
            "kpis": [],
            "charts": [
                {"kind": "funnel_like", "title": "关键触点覆盖", "data": pages["conversion_path"]["touchpoints"]}
            ],
            "tables": [],
            "insights": [
                "扫码与参与行为体量可观，但到消费和高等级沉淀之间仍有明显断层。",
                "后续汇报可围绕“如何把行为池转成消费池”来展开建议。"
            ],
            "notes": {
                "source_sheets": ["全部会员", "门店别"],
                "metric_logic": "这不是严格顺序漏斗，而是关键运营触点覆盖概览。",
            },
        },
    ]
    return {"meta": analysis["meta"], "slides": slides}


def main() -> None:
    args = parse_args()
    analysis_path = Path(args.analysis).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    analysis = load_analysis(analysis_path)
    slide_spec = build_slide_spec(analysis)
    output_path.write_text(json.dumps(slide_spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
