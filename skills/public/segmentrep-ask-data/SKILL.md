---
name: segmentrep-ask-data
description: 使用可用的 PostgreSQL MCP 查询工具回答 Segmentrep 经营分析数据库中的自然语言问数问题。适用于用户询问 Segmentrep、YTD3、经营分析、问数、Actual/Budget/Forecast 对比、业务单元指标、P&L、销售、库存、人工、销量、表内逻辑检核，以及需要把查询结果进一步生成图表并展示为精美 HTML 页面等数据分析场景。
---

# Segmentrep 问数

使用此 skill 查询 PostgreSQL 数据库 `Segmentrep` 中的 `segmentrep_model` schema，回答经营分析相关问题。

## 工作流程

1. 优先使用 PostgreSQL MCP 查询工具，不要重新解析 Excel，除非用户明确要求检查原始工作簿。
2. 写 SQL 前先阅读 [references/schema.md](references/schema.md)，除非问题只是简单行数统计或本文件已经覆盖的直接查询。
3. 分析类问题优先查询视图 `segmentrep_model.vw_ytd3_report_value`。只有在需要 ID、表注释、原始落地数据或 Excel 源坐标时，才查询底层表。
4. 将用户口语转成维度字段：
   - 业务单元：`business_unit_name`
   - 指标/科目：`metric_name_norm` 或 `metric_name_raw`
   - 场景：`scenario_source_label`，例如 `Actual2026`、`Budget2026`、`Actual2025`、`Forecast2026`
   - 期间：`period_code`，例如 `Jan`、`1Q`、`1H`、`Current Mth`
5. 用户表达不精确时，先用 `ILIKE` 查询业务单元或指标候选值，不要直接猜。只有多个候选差异明显且会影响结论时，才简短追问用户。
6. 如果用户要求“生成图表”“可视化”“做 dashboard”“输出 HTML 展示”，先查询出干净、可直接作图的数据集，再调用其他图表可视化 skill 生成图表（要求返回可公网访问的远程图片URL，禁止返回base64编码或本地路径），最后将图表绘制到一个精美的 HTML 页面中进行展示。
7. 回答时说明使用了哪些过滤条件、期间、场景和关键假设。只有当用户需要溯源时，才展示 `source_row` 和 `source_col`。
8. 如果用户要求"生成PDF"、"导出PDF"、"下载PDF"，先将所有内容调整为适配A4纵向排版的格式，再生成PDF文件，避免排版错乱。

## 查询规则

- 不要在 skill 文件、SQL 注释或回答中暴露/保存数据库密码。
- 普通问数只使用只读 SQL：`SELECT`、CTE、元数据查询。除非用户明确要求修改模型，否则不要执行 `INSERT`、`UPDATE`、`DELETE`、`TRUNCATE`、`DROP`。
- SQL 对象名始终带上 schema 前缀：`segmentrep_model.`。
- 展示时间序列时，使用期间维表的排序字段，或在视图中按 `month_no`、`period_code` 排序。
- 做对比时，同时给出绝对差异和分母不为 0 时的差异率：
  `diff = actual - comparator`；`diff_pct = diff / nullif(comparator, 0)`。
- 将导入值视为报表值。不要擅自做会计方向取反，除非规则已明确记录，或用户明确要求做口径归一。
- 当用户问到空指标行、原始 Excel 坐标、正式事实表外的数据时，查询 `segmentrep_model.stg_ytd3_cell`。
- 当用户要求图表时，先把 SQL 结果整理成适合作图的结构：
  - 时间序列图：`x=period_code/month_no`，`y=amount`，`series=scenario_source_label` 或 `business_unit_name`
  - 排名条形图：`x=business_unit_name`，`y=amount`
  - 结构占比图：仅在分类数较少、口径明确时使用
- 图表生成后，不要只返回图片或裸图表配置；要继续输出一个带标题、摘要、指标卡、图表区和必要注释的精美 HTML 页面，页面内所有 `<img>` 标签必须使用可视化 skill 返回的可公网访问的远程图片URL，禁止使用base64编码、本地文件路径或相对路径引用图片。
- 如果当前环境里存在多个可视化 skill，优先选择支持返回可公网访问远程图片URL的可视化 skill；其次选择能生成交互式图表和 HTML 的 skill；若没有现成可视化 skill，再退回到直接生成 HTML + 内嵌图表实现，但内嵌图片也必须使用远程URL。
- 生成PDF时严格遵循A4纵向排版规范：页面边距上下左右各2cm，字体大小适配打印需求，图表宽度不超过A4页面宽度，内容分页合理，避免出现内容截断、布局错乱问题。

## 常用 SQL

业务单元候选查询：

```sql
select unit_name, source_code, source_block_no
from segmentrep_model.dim_business_unit
where unit_name ilike '%Factory%'
order by sort_order;
```

单指标查询：

```sql
select business_unit_name, metric_name_norm, scenario_source_label, period_code, amount
from segmentrep_model.vw_ytd3_report_value
where business_unit_name = 'TU-事业部合计'
  and metric_name_norm = 'Total Gross Sales'
  and scenario_source_label = 'Actual2026'
  and period_code = 'Jan';
```

Actual vs Budget 对比：

```sql
select
  business_unit_name,
  metric_name_norm,
  period_code,
  sum(amount) filter (where scenario_source_label = 'Actual2026') as actual_2026,
  sum(amount) filter (where scenario_source_label = 'Budget2026') as budget_2026,
  sum(amount) filter (where scenario_source_label = 'Actual2026')
    - sum(amount) filter (where scenario_source_label = 'Budget2026') as diff,
  (
    sum(amount) filter (where scenario_source_label = 'Actual2026')
    - sum(amount) filter (where scenario_source_label = 'Budget2026')
  ) / nullif(sum(amount) filter (where scenario_source_label = 'Budget2026'), 0) as diff_pct
from segmentrep_model.vw_ytd3_report_value
where business_unit_name = 'Factory'
  and metric_name_norm = 'TOTAL NET SALES'
  and period_code in ('Jan','Feb','Mar')
group by business_unit_name, metric_name_norm, period_code, month_no
order by month_no;
```

## 回答风格

- 明确说明结果是月度、季度、半年度还是 `Current Mth`。
- 如果用户说法是模糊匹配而不是精确字段值，说明最终采用了哪个数据库字段值。
- 如果没有查到数据，说明已检查的最接近候选项，并给出下一步查询建议。
- 如果用户要图表，最终输出应以 HTML 页面为主，而不是只给 SQL 结果或只给一张静态图。
- 如果用户要求PDF格式输出，最终应返回符合A4纵向排版规范的PDF文件，确保所有表格、图表、文字内容完整展示、布局美观，无截断或错乱问题。
