# 输出契约

本文件定义 `member-ops-report-planner` 的标准输出。

## 输出文件列表

- `schema_profile.json`
- `field_mapping.json`
- `dimension_support.json`
- `analysis.json`
- `report_plan.json`
- `mapping_report.md`
- `chart_tasks.json`（可选）

## 1. `schema_profile.json`

建议结构：

```json
{
  "files": [],
  "tables": [],
  "candidate_tables": {
    "member_fact": [],
    "store_dim": [],
    "event_fact": [],
    "topic_summary": []
  },
  "notes": []
}
```

要求：

- 记录每个文件和每个表的基础信息
- 记录候选主表和候选维表
- 记录关键结构风险

## 2. `field_mapping.json`

建议结构：

```json
{
  "standard_fields": [
    {
      "field": "member_id",
      "status": "exact",
      "source_file": "xxx.xlsx",
      "source_sheet": "全部会员",
      "source_column": "会员编码",
      "evidence": []
    }
  ],
  "unresolved_fields": [],
  "unsupported_fields": []
}
```

要求：

- 每个字段必须有状态
- 每个已映射字段必须有证据

允许状态：

- `exact`
- `dictionary_verified`
- `unresolved`
- `unsupported`

## 3. `dimension_support.json`

建议结构：

```json
{
  "themes": [
    {
      "theme_id": "member_overview",
      "status": "supported",
      "missing_fields": [],
      "notes": []
    }
  ],
  "supported_theme_ids": [],
  "partial_theme_ids": [],
  "skipped_theme_ids": []
}
```

## 4. `analysis.json`

建议结构：

```json
{
  "meta": {
    "city": null,
    "target_period": null
  },
  "datasets": [],
  "themes": {
    "member_overview": {
      "metrics": {},
      "tables": [],
      "charts": [],
      "notes": []
    }
  }
}
```

要求：

- 不只存最终数字，还要存图表底数
- 每个主题都要有 `notes`
- 如果主题是 `partial`，必须在 `notes` 中写限制

## 5. `report_plan.json`

这是最重要的中性报告结构文件。

建议结构：

```json
{
  "meta": {
    "title": "",
    "city": null,
    "target_period": null,
    "output_layer": "report_content_plan"
  },
  "pages": [
    {
      "theme_id": "member_overview",
      "title": "",
      "status": "supported",
      "reason": "",
      "sections": {
        "kpis": [],
        "tables": [],
        "charts": [],
        "insights": [],
        "method_notes": []
      },
      "render_hints": {
        "recommended_mediums": [],
        "preferred_chart_types": [],
        "visual_priority": "",
        "accent_color_intent": "",
        "table_density": "",
        "number_format_notes": []
      }
    }
  ]
}
```

要求：

- 页面主题固定，但允许跳过
- 每页必须说明 `status`
- 每页必须提供 `method_notes`
- 渲染提示必须保持介质中立
- 每页必须给出视觉重点提示，帮助下游 PPT / HTML / PDF 渲染突出重点
- 表格类 sections 必须说明推荐列数、是否需要合计行、是否需要突出 Top/Bottom
- 指标类 sections 必须说明数值单位、小数位、是否使用百分比

## 6. `mapping_report.md`

建议包含以下章节：

1. 文件概况
2. 候选表识别
3. 字段映射结果
4. 主题支持结果
5. 已跳过主题
6. 关键风险与后续建议

## 7. `chart_tasks.json`（可选）

当存在图表 skill 且需要独立生成图表时，可输出：

```json
{
  "tasks": [
    {
      "theme_id": "member_day",
      "chart_id": "month_trend",
      "chart_type": "column",
      "title": "",
      "data": [],
      "notes": []
    }
  ]
}
```

用途：

- 把图表制作与报告编排解耦
- 下游图表 skill 只负责画图，不重新理解业务口径
