# Segmentrep PostgreSQL Schema 参考

本文件用于指导 agent 生成 SQL，目标数据库为 `Segmentrep`，目标 schema 为 `segmentrep_model`。

## 模型概览

Excel 的 `YTD3` Sheet 已被拆成长表并建成星型模型：

- `dim_business_unit`：业务单元维表，共 55 个 Excel 重复块。
- `dim_metric`：指标/科目维表，共 92 个正式指标。
- `dim_scenario`：场景维表，共 4 个场景年份组合。
- `dim_period`：期间维表，共 19 个期间。
- `report_value_fact`：正式事实表，共 384,560 行。
- `stg_ytd3_cell`：原始单元格落地表，共 409,564 行，其中 25,004 行为空指标名尾部数据。
- `stg_seg_framework`：`seg框架` 原始落地表，按合并单元格展开 `事业群/事业部/产线`。
- `dim_seg_node`：Segment 组织层级节点维表，统一存储事业群、事业部、产线。
- `bridge_business_unit_seg_node`：业务单元到 Segment 层级节点的桥接表，保留精确匹配、人工确认匹配、歧义匹配和未匹配状态。
- `vw_ytd3_report_value_with_seg`：经营分析主问数视图，直接基于事实表、维表和 Segment 映射表创建，带事业群、事业部、产线字段。

## 主问数视图

默认优先查询：

`segmentrep_model.vw_ytd3_report_value_with_seg`

字段说明：

| 字段 | 含义 |
| --- | --- |
| `load_id` | 导入批次 ID，首次导入为 `1`。 |
| `sheet_name` | 来源 Sheet，通常为 `YTD3`。 |
| `source_block_no` | Excel 中第几个业务块，从 1 开始。 |
| `business_unit_source_code` | Excel 块表头中的业务编号；汇总块可能为空。 |
| `business_unit_name` | 业务单元名称，例如 `Total`、`TU-事业部合计`、`Factory`、`TUC零售`。 |
| `business_unit_is_consolidated` | 是否疑似汇总块；当前按源编号为空初始判断。 |
| `metric_row_order` | 指标在每个 100 行业务块中的顺序。 |
| `metric_name_raw` | Excel 原始指标名，保留原始空格。 |
| `metric_name_norm` | 规范化指标名，压缩多余空格；精确匹配时优先用它。 |
| `parent_metric_name` | 父级指标名，例如 `线上/线下` 对应 `Advertising`。 |
| `metric_group` | 指标组：`P&L`、`HR/Payroll`、`Sales Volume`、`Inventory Movement`、`Internal Check`。 |
| `unit_type` | 单位类型：`amount`、`tons`、`headcount`、`check_value`、`unknown`。 |
| `sign_rule` | 初始口径提示，不是自动换符号规则。 |
| `scenario_name` | 场景名：`Actual`、`Budget`、`Forecast`。 |
| `fiscal_year` | 场景年份，例如 `2026`。 |
| `scenario_source_label` | Excel 原始场景标签：`Actual2026`、`Budget2026`、`Actual2025`、`Forecast2026`。 |
| `period_code` | 期间代码：`Jan` ... `Dec`、`1Q` ... `4Q`、`1H`、`2H`、`Current Mth`。 |
| `period_type` | 期间类型：`month`、`quarter`、`half_year`、`current_month`。 |
| `month_no` | 月份编号，月度行有值。 |
| `quarter_no` | 季度编号，季度行和可推导的月度行有值。 |
| `amount` | 报表数值，类型为 `numeric(20,4)`。 |
| `source_row` | Excel 来源行号。 |
| `source_col` | Excel 来源列号。 |

`vw_ytd3_report_value_with_seg` 在上述字段基础上增加：

| 字段 | 含义 |
| --- | --- |
| `seg_match_type` | 业务单元与 Segment 层级的匹配状态：`exact_name`、`ambiguous_exact_name`、`unmatched_review`、`manual`。 |
| `seg_matched_level` | 匹配层级：`business_group`、`business_division`、`product_line`。 |
| `seg_match_confidence` | 匹配置信度，唯一精确匹配为 `1.0`。 |
| `seg_node_id` | 匹配到的 Segment 节点 ID。 |
| `seg_node_type` | Segment 节点类型。 |
| `seg_node_name` | Segment 节点名称。 |
| `business_group` | 事业群。 |
| `business_division` | 事业部。 |
| `product_line` | 产线。 |
| `seg_mapping_note` | 映射备注；歧义或未匹配时用于说明待复核原因。 |

## 底层表

### `segmentrep_model.import_batch`

导入批次表，记录来源工作簿路径、Sheet 名、导入时间、行数和备注。

### `segmentrep_model.dim_business_unit`

业务单元维表字段：

- `business_unit_id`：业务单元代理键。
- `source_block_no`：`YTD3` 中第几个 100 行重复块。
- `source_code`：Excel 来源编号，许多汇总块为空。
- `unit_name`：业务单元名称。
- `parent_business_unit_id`：预留的父级业务单元字段，可后续维护层级。
- `is_consolidated`：初始汇总块标记。
- `sort_order`：报表展示顺序。

候选查询：

```sql
select business_unit_id, source_block_no, source_code, unit_name, is_consolidated
from segmentrep_model.dim_business_unit
order by sort_order;
```

### `segmentrep_model.dim_metric`

指标维表字段：

- `metric_id`：指标代理键，当前等于行序号。
- `row_order`：指标在每个重复块内的行序号。
- `metric_name_raw`：Excel 原始指标名。
- `metric_name_norm`：规范化指标名。
- `parent_metric_id`：已映射明细行的父级指标。
- `metric_group`：指标大类。
- `unit_type`：单位类型。
- `sign_rule`：方向/类别提示。
- `calc_formula`：预留 JSON 公式字段，用于后续检核规则。

候选查询：

```sql
select metric_id, row_order, metric_name_norm, parent_metric_id, metric_group, unit_type
from segmentrep_model.dim_metric
where metric_name_norm ilike '%Sales%'
order by row_order;
```

### `segmentrep_model.dim_scenario`

当前场景值：

- `Actual2026`
- `Budget2026`
- `Actual2025`
- `Forecast2026`

### `segmentrep_model.dim_period`

当前期间值：

- 月度：`Jan`、`Feb`、`Mar`、`Apr`、`May`、`Jun`、`Jul`、`Aug`、`Sep`、`Oct`、`Nov`、`Dec`
- 季度：`1Q`、`2Q`、`3Q`、`4Q`
- 半年度：`1H`、`2H`
- 当前月：`Current Mth`

排序时优先使用 `dim_period.sort_order`。如果查询视图中的月度行，可直接按 `month_no` 排序。

### `segmentrep_model.report_value_fact`

正式事实表，粒度为：

`load_id + business_unit_id + metric_id + scenario_id + period_id`

需要严格 ID、约束、或避免视图别名时使用此表。

### `segmentrep_model.stg_ytd3_cell`

原始单元格落地表，粒度为：

`load_id + source_row + source_col`

适用场景：

- 查询空指标名尾部行。
- 检查原始 Excel 坐标。
- 做数据血缘追踪。
- 诊断为什么某个值不在正式事实表中。

空指标名或未映射行满足：`is_unmapped_metric = true`。

### `segmentrep_model.stg_seg_framework`

`seg框架` 原始落地表，来源于 `NPTU 经营数据平台（智能问数）.xlsx` 的 `seg框架` Sheet，已按 Excel 合并单元格展开并压缩为 28 条层级组合。

关键字段：

- `source_row_start` / `source_row_end`：来源行范围。
- `business_group`：事业群。
- `business_division`：事业部。
- `product_line`：产线，部分事业部级或事业群级节点为空。
- `source_tuple`：原始三层组合 JSON。

### `segmentrep_model.dim_seg_node`

Segment 组织层级节点维表。当前节点数：

- 事业群：7 个。
- 事业部：12 个。
- 产线：15 个。

关键字段：

- `node_type`：`business_group`、`business_division`、`product_line`。
- `node_name`：节点名称。
- `parent_node_id`：父级节点。
- `business_group`、`business_division`、`product_line`：冗余层级字段，便于查询。
- `is_leaf`：是否叶子节点。

### `segmentrep_model.bridge_business_unit_seg_node`

业务单元与 Segment 层级桥接表。自动匹配状态：

- `exact_name`：唯一精确匹配。
- `ambiguous_exact_name`：多个层级同名候选，例如 `TUB` 同时是事业群和事业部。
- `unmatched_review`：未匹配，待人工复核。
- `manual`：人工确认匹配。当前 `TUB` 已由用户确认：`TUB` 同时是事业群和事业部，`dim_business_unit` 中的 `TUB` 按事业部节点映射，其父级事业群同为 `TUB`。

按 Segment 层级问数时，默认使用 `match_type in ('exact_name','manual')`。歧义和未匹配项要在回答中说明，不要静默纳入。

## 指标分组

可用 `metric_group` 粗筛：

- `P&L`：行序号 1-69。
- `HR/Payroll`：人工成本和人员数相关行。
- `Sales Volume`：销量吨数相关行。
- `Inventory Movement`：成品库存进出相关行。
- `Internal Check`：表内逻辑检核行。

常用规范化指标名：

- `Total Gross Sales`
- `Less: Sales Return`
- `TOTAL GROSS SALES`
- `Less:Discount`
- `TOTAL NET SALES`
- `RMCC`
- `VARIABLE COSTS (ex RMCC)`
- `CONTRIBUTION MARGIN`
- `TOTAL OVERHEADS`
- `EARNINGS B/F INTEREST/TAX`
- `PROFIT BEFORE TAX`
- `PBT After Adjustment`
- `PROFIT AFTER TAXATION`
- `PROFIT TO SHAREHOLDERS`
- `TOTAL PAYROLL COST`
- `FG Delivered-(Tons)`
- `Resin Delivered-(Tons)`
- `Personnel Number`
- `Sales Emulsion (Tons)`
- `Sales Enamel (Tons)`
- `Sales Accry (Tons)`
- `期初库存`
- `入：非关联采购入库`
- `关联采购入库`
- `生产入库`
- `其他入库`
- `出：非关联销售出库`
- `关联销售出库`
- `其他出库`
- `期末库存`
- `期末成品库存`
- `成品产量`
- `表内损益间逻辑检核`

## 默认问数口径

当用户没有明确指定口径时，按以下默认值处理，并在回答中说明：

- 收入：默认 `metric_name_norm = 'TOTAL NET SALES'`。
- 场景：默认当年实际，`scenario_source_label = 'Actual2026'`。
- 组织范围：默认 TU TOTAL，`business_unit_name = 'TU-事业部合计'`。
- 利润：默认税前利润，`metric_name_norm = 'PROFIT BEFORE TAX'`。
- 利润率：默认税前利润率，计算公式为 `PROFIT BEFORE TAX / TOTAL NET SALES`。

示例：

- “Q1的收入是多少？” = `TU-事业部合计` + `TOTAL NET SALES` + `Actual2026` + `1Q`。
- “利润率是多少？” = `TU-事业部合计` + `Actual2026` + `PROFIT BEFORE TAX / TOTAL NET SALES`。
- “TUC收入趋势” = `business_group = 'TUC'` + `TOTAL NET SALES` + `Actual2026` + 月度趋势。

注意：如果用户明确说“毛收入”，再考虑 `Total Gross Sales` 或 `TOTAL GROSS SALES`；如果用户明确说“净收入/销售收入/收入”，默认仍使用 `TOTAL NET SALES`。

## SQL 模板

### 候选值匹配

用户使用简称、中文片段或英文片段时，先查询候选值。

```sql
select unit_name, source_code, source_block_no
from segmentrep_model.dim_business_unit
where unit_name ilike '%' || :term || '%'
order by sort_order;
```

```sql
select metric_name_norm, metric_group, unit_type, row_order
from segmentrep_model.dim_metric
where metric_name_norm ilike '%' || :term || '%'
order by row_order;
```

### 默认收入查询

用户问“收入”但没有说明实际/预算/组织范围时使用此模板。

```sql
select business_unit_name, metric_name_norm, scenario_source_label, period_code, amount
from segmentrep_model.vw_ytd3_report_value_with_seg
where business_unit_name = 'TU-事业部合计'
  and metric_name_norm = 'TOTAL NET SALES'
  and scenario_source_label = 'Actual2026'
  and period_code = :period_code;
```

### 默认税前利润率

```sql
with base as (
  select
    period_code,
    max(amount) filter (where metric_name_norm = 'PROFIT BEFORE TAX') as pre_tax_profit,
    max(amount) filter (where metric_name_norm = 'TOTAL NET SALES') as total_net_sales
  from segmentrep_model.vw_ytd3_report_value_with_seg
  where business_unit_name = coalesce(:business_unit_name, 'TU-事业部合计')
    and scenario_source_label = coalesce(:scenario_source_label, 'Actual2026')
    and period_code = :period_code
    and metric_name_norm in ('PROFIT BEFORE TAX', 'TOTAL NET SALES')
  group by period_code
)
select
  period_code,
  pre_tax_profit,
  total_net_sales,
  pre_tax_profit / nullif(total_net_sales, 0) as pre_tax_profit_margin
from base;
```

### 月度时间序列

```sql
select period_code, amount
from segmentrep_model.vw_ytd3_report_value_with_seg
where business_unit_name = :business_unit_name
  and metric_name_norm = :metric_name_norm
  and scenario_source_label = :scenario_source_label
  and period_type = 'month'
order by month_no;
```

适合：

- 折线图
- 双线/多线趋势图
- 实际 vs 预算 vs 去年同期对比图

### 场景对比

```sql
with base as (
  select
    business_unit_name,
    metric_name_norm,
    period_code,
    month_no,
    sum(amount) filter (where scenario_source_label = :scenario_a) as value_a,
    sum(amount) filter (where scenario_source_label = :scenario_b) as value_b
  from segmentrep_model.vw_ytd3_report_value_with_seg
  where business_unit_name = :business_unit_name
    and metric_name_norm = :metric_name_norm
    and period_type = 'month'
  group by business_unit_name, metric_name_norm, period_code, month_no
)
select
  *,
  value_a - value_b as diff,
  (value_a - value_b) / nullif(value_b, 0) as diff_pct
from base
order by month_no;
```

适合：

- 分组柱状图
- 带差异率标注的趋势图
- 图表 + 指标卡联合展示

### 业务单元排名

```sql
select business_unit_name, amount
from segmentrep_model.vw_ytd3_report_value_with_seg
where metric_name_norm = :metric_name_norm
  and scenario_source_label = :scenario_source_label
  and period_code = :period_code
order by amount desc nulls last;
```

适合：

- 排名条形图
- Top N / Bottom N 对比图

### 按事业群汇总

```sql
select
  business_group,
  period_code,
  sum(amount) as amount
from segmentrep_model.vw_ytd3_report_value_with_seg
where seg_match_type in ('exact_name','manual')
  and business_group = :business_group
  and metric_name_norm = :metric_name_norm
  and scenario_source_label = :scenario_source_label
  and period_type = 'month'
group by business_group, period_code, month_no
order by month_no;
```

### 按事业部或产线过滤

```sql
select
  business_group,
  business_division,
  product_line,
  period_code,
  sum(amount) as amount
from segmentrep_model.vw_ytd3_report_value_with_seg
where seg_match_type in ('exact_name','manual')
  and business_division = :business_division
  and metric_name_norm = :metric_name_norm
  and scenario_source_label = :scenario_source_label
  and period_type = 'month'
group by business_group, business_division, product_line, period_code, month_no
order by min(seg_node_id), month_no;
```

### 按架构展示事业部/产线列表

涉及事业部、产线列表展现时，默认使用 `seg_node_id` 排序，保持 `seg框架` 的架构顺序。

```sql
select
  business_group,
  business_division,
  product_line,
  seg_node_id,
  sum(amount) as amount
from segmentrep_model.vw_ytd3_report_value_with_seg
where seg_match_type in ('exact_name','manual')
  and metric_name_norm = coalesce(:metric_name_norm, 'TOTAL NET SALES')
  and scenario_source_label = coalesce(:scenario_source_label, 'Actual2026')
  and period_code = :period_code
group by business_group, business_division, product_line, seg_node_id
order by seg_node_id;
```

### 检查 Segment 匹配状态

```sql
select match_type, count(*)
from segmentrep_model.bridge_business_unit_seg_node
group by match_type
order by match_type;
```

### 原始 Excel 来源检查

```sql
select source_row, source_col, business_unit_name_raw, metric_name_norm, scenario_id, period_id, amount, is_unmapped_metric
from segmentrep_model.stg_ytd3_cell
where load_id = :load_id
  and source_row = :source_row
order by source_col;
```

## 图表与 HTML 展示约定

当用户明确要求生成图表、看板、可视化页面、经营分析报告页时，遵循以下顺序：

1. 先用 SQL 产出结构化结果集，字段名尽量清晰，例如：
   - 时间趋势：`period_code`, `month_no`, `scenario_source_label`, `amount`
   - 排名对比：`business_unit_name`, `amount`
   - 结构分析：`metric_name_norm`, `amount`
2. 再调用其他图表可视化 skill 生成合适的图表，要求图表工具返回可公网访问的图片链接。
3. 最后把图表绘制到一个精美 HTML 页面中，而不是只返回数据表。

任何类型文件的报表，包括 HTML、PDF、PPTX、Word、Excel，图表都要优先使用图表可视化 skill 得到的图片链接。不要自己用代码生成图表图片；如果没有可用图表工具，先说明限制并输出数据表/指标卡，不要自行画图替代。

HTML 页面至少应包含：

- 页面标题
- 业务问题摘要
- 关键指标卡
- 1 到 3 张主图
- 必要的数据口径说明
- 查询条件说明，例如业务单元、期间、场景

颜色语义：

- 达成、优于预算、同比改善：绿色。
- 未达成、低于预算、同比恶化：红色。
- 接近目标、无明确好坏方向、结构性占比：中性色。

颜色只能作为视觉辅助，必须同时展示数值、差异和文字说明。不要只用颜色表达结论。

图表类型建议：

- 月度/季度趋势：折线图或分组柱状图
- 实际 vs 预算 vs 去年：多系列折线图或分组柱状图
- 业务单元排名：横向条形图
- 占比分析：仅在分类数量较少且总量关系明确时使用饼图/环图

除非用户明确要求，不要把过多图表堆在同一页中。

## 回答口径

- 用户表达模糊时，说明最终使用的精确数据库标签。
- 结果涉及单位时，结合 `unit_type` 说明是金额、吨数、人数还是检核值。
- 百分比可在自然语言中格式化成百分数；如果展示 SQL 原始结果，可保留小数。
- 不要把月度、季度、半年度混在一起，除非用户明确要求。
- `Current Mth` 只表示报表列名 `Current Mth`；不要在没有额外来源时猜测它等于哪个自然月。
