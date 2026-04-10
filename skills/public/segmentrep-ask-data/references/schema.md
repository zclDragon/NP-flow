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
- `vw_ytd3_report_value`：查询友好视图，适合大多数问数问题。

## 首选分析视图

优先查询：

`segmentrep_model.vw_ytd3_report_value`

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

### 月度时间序列

```sql
select period_code, amount
from segmentrep_model.vw_ytd3_report_value
where business_unit_name = :business_unit_name
  and metric_name_norm = :metric_name_norm
  and scenario_source_label = :scenario_source_label
  and period_type = 'month'
order by month_no;
```

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
  from segmentrep_model.vw_ytd3_report_value
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

### 业务单元排名

```sql
select business_unit_name, amount
from segmentrep_model.vw_ytd3_report_value
where metric_name_norm = :metric_name_norm
  and scenario_source_label = :scenario_source_label
  and period_code = :period_code
order by amount desc nulls last;
```

### 原始 Excel 来源检查

```sql
select source_row, source_col, business_unit_name_raw, metric_name_norm, scenario_id, period_id, amount, is_unmapped_metric
from segmentrep_model.stg_ytd3_cell
where load_id = :load_id
  and source_row = :source_row
order by source_col;
```

## 回答口径

- 用户表达模糊时，说明最终使用的精确数据库标签。
- 结果涉及单位时，结合 `unit_type` 说明是金额、吨数、人数还是检核值。
- 百分比可在自然语言中格式化成百分数；如果展示 SQL 原始结果，可保留小数。
- 不要把月度、季度、半年度混在一起，除非用户明确要求。
- `Current Mth` 只表示报表列名 `Current Mth`；不要在没有额外来源时猜测它等于哪个自然月。
