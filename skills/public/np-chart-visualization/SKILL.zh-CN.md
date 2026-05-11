---
name: 图表可视化
description: 当用户需要可视化数据时使用此技能。它能智能地从 26 种可用选项中选择最合适的图表类型，根据详细规范提取参数，并使用 JavaScript 脚本生成图表图片。
dependency:
  nodejs: ">=18.0.0"
---

# 图表可视化技能

本技能提供了将数据转换为可视化图表的完整工作流。它处理图表选择、参数提取和图片生成。

## 工作流程

要可视化数据，请遵循以下步骤：

### 1. 智能图表选择
分析用户的数据特征以确定最合适的图表类型。使用以下指南（并查阅 `references/` 了解详细规范）：

- **时间序列**：使用 `generate_line_chart`（趋势）或 `generate_area_chart`（累积趋势）。对于两种不同的刻度使用 `generate_dual_axes_chart`。
- **比较**：使用 `generate_bar_chart`（分类）或 `generate_column_chart`。对于频率分布使用 `generate_histogram_chart`。
- **部分与整体**：使用 `generate_pie_chart` 或 `generate_treemap_chart`（层次结构）。
- **关系与流程**：使用 `generate_scatter_chart`（相关性）、`generate_sankey_chart`（流程）或 `generate_venn_chart`（重叠）。
- **地图**：使用 `generate_district_map`（区域）、`generate_pin_map`（点）或 `generate_path_map`（路线）。
- **层次结构与树**：使用 `generate_organization_chart` 或 `generate_mind_map`。
- **专业图表**：
    - `generate_radar_chart`：多维比较。
    - `generate_funnel_chart`：流程阶段。
    - `generate_waterfall_chart`：分步增减与累计变化；对于桥接类场景，通常需包含起始节点、变化贡献节点和结束节点。
    - `generate_liquid_chart`：百分比/进度。
    - `generate_word_cloud_chart`：文本频率。
    - `generate_boxplot_chart` 或 `generate_violin_chart`：统计分布。
    - `generate_network_graph`：复杂的节点-边关系。
    - `generate_fishbone_diagram`：因果分析。
    - `generate_flow_diagram`：流程流程。
    - `generate_spreadsheet`：用于结构化数据展示和交叉制表的表格数据或数据透视表。

### 2. 参数提取
选择图表类型后，阅读 `references/` 目录中的对应文件（例如 `references/generate_line_chart.md`）以识别必填和可选字段。
从用户输入中提取数据并将其映射到预期的 `args` 格式。

### 3. 图表生成
使用 JSON 有效负载调用 `scripts/generate.js` 脚本。

**有效负载格式：**
```json
{
  "tool": "generate_chart_type_name",
  "args": {
    "data": [...],
    "title": "...",
    "theme": "...",
    "style": { ... }
  }
}
```

**执行命令：**
```bash
node ./scripts/generate.js '<payload_json>'
```

### 4. 结果返回
脚本将输出生成的图表图片的 URL。
向用户返回以下内容：
- 图片 URL。
- 用于生成的完整 `args`（规范）。

## 参考资料
每种图表类型的详细规范位于 `references/` 目录中。查阅这些文件以确保传递给脚本的 `args` 符合预期的模式。

## 许可证

本 `SKILL.zh-CN.md` 由 [antvis/chart-visualization-skills](https://github.com/antvis/chart-visualization-skills) 提供。
根据 [MIT 许可证](https://github.com/antvis/chart-visualization-skills/blob/master/LICENSE) 许可。
