---
name: segment-analysis-query
description: 用于基于 PostgreSQL 中的 Segment 经营分析表做中文问数、简化利润表、收入/利润/利润率、事业群/事业部/segment 分析。适用于用户询问 ALL YEAR、Segmentrep、SEG、经营分析、事业部、PDT、产线、Org、收入、利润、利润表、同比、YTD、季度或月度经营指标。
---

# Segment 经营分析问数

这是一个纯问数 skill。只负责理解业务口径、生成查询、解释结果。不要读取 Excel 源文件，不要做数据入库，不要修改数据库结构。

## 工作流

1. 解析用户问题中的时间、组织范围、指标和展示方式。
2. 用默认口径补齐缺失信息。
3. 需要写 SQL 或确认字段名时，读取 `references/schema.md`。
4. 需要解析科目别名、中文展示名或指标口径时，读取 `references/metric_names.md`。
5. 使用可用的 PostgreSQL 数据库查询工具查询 `public.seg_all_year`。
6. 回答时优先使用中文指标名，并说明关键默认口径。

## 数据源

- 数据库：`Segmentrep`
- 表：`public.seg_all_year`
- 表类型：单表经营分析事实表
- 查询方式：使用数据库查询工具执行 SQL

## 默认口径

- 未说明年份时，默认当前年份。
- 未说明实际/预算/同期时，默认当年实际。
- 当前表只承载实际数据；用户明确问预算而表中没有预算字段时，说明当前问数表不支持预算。
- 用户问“同期”或“同比”时，默认使用上一年相同 `period` 的实际值。
- 未说明组织范围时，默认所有事业部的 `TOTAL` 范围。
- 用户问“收入”时，默认指标是 `TOTAL NET SALES`。
- 用户问“利润”且未说明利润类型时，默认指标是 `PROFIT BEFORE TAX`。
- 用户问“利润率”且未说明利润类型时，默认公式是 `PROFIT BEFORE TAX / TOTAL NET SALES`。
- 金额类指标单位为千元；回答金额时默认按千元展示，必要时可换算为万元、百万元或亿元。`销量` 不是金额指标。

## 组织维度

默认汇总分析只使用高层级：

- `TOTAL`
- `事业群`
- `事业部`

以下四个字段是平级 segment 口径，不是上下级链路：

- `水木基辅`
- `PDT`
- `产线`
- `Org`

只有用户明确问到这些字段时才使用。跨年查询中，如果目标年份没有对应字段值，直接说明该年份没有该 segment 口径，不要强行映射。

## 时间口径

`Period` 同时包含月度、季度、半年和 YTD。不要混合不同粒度求和。

- 月度：`Jan` 到 `Dec`
- 季度：`1Q` 到 `4Q`
- 半年：`1H`、`2H`
- 累计：`YTD`

用户没有说明时间粒度时，按问题语义选择最自然的单一粒度；无法判断时先给出所采用的默认口径。

## 简化利润表

用户问核心行、简化利润表或利润表摘要时，固定使用以下行次：

1. `TOTAL NET SALES`
2. `RMCC`
3. `VARIABLE COSTS (ex RMCC)`
4. `CONTRIBUTION MARGIN`
5. `TOTAL OVERHEADS`
6. `EARNINGS B/F INTEREST/TAX`
7. `PROFIT BEFORE TAX`
8. `PROFIT AFTER TAXATION`

展示时读取 `references/metric_names.md`，优先使用中文名称。

## 衍生指标

衍生指标在查询或回答阶段计算，不要求数据库中存在对应列。

- 税前利润率 = `profit_before_tax / total_net_sales`
- 息税前利润率 = `earnings_before_interest_tax / total_net_sales`
- 税后利润率 = `profit_after_taxation / total_net_sales`
- 毛利率 = `gross_profit / total_net_sales`
- 固费率 = `total_overheads / total_net_sales`
- 折扣率 = `less_discount / total_gross_sales2`
- 单位收入 = `total_net_sales / volume`
- 单位毛利 = `gross_profit / volume`

计算率类指标时，用 `NULLIF(分母, 0)` 避免除零。

## 回答规则

- 优先回答用户问题本身，不主动展开全量字段说明。
- 只披露当前问题需要的口径、过滤条件和计算公式。
- 指标名称优先用中文；必要时在括号中补充 SQL 字段名。
- 金额类结果要标注单位“千元”，比例类结果标注为百分比，销量按原表单位展示。
- 如果字段或年份不可用，直接说明不可用原因和已查询的范围。
- 如果用户要求明细 SQL，可以给出实际使用的 SQL。
