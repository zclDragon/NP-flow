# 固定查询模式

所有 SQL 都是示例。执行前按用户条件替换参数，并保持只读。示例多用 `YTD` 展示累计写法；如果用户没有指定累计，默认用当前报表当月字段，例如当前语境是 3 月时把 `"YTD"` 换成 `"3月"`。

## 1. 单点标准问数

适用：某年、某标准架构、某层级、某标准科目、某期间、某场景。

```sql
SELECT
  "年份",
  "标准架构名称",
  "标准架构层级",
  "标准科目名称",
  "场景角色",
  ROUND(SUM("YTD")::numeric, 0)::bigint AS "YTD"
FROM segmentrep_analysis_v2."数据宽表"
WHERE "年份" = 2026
  AND "标准架构名称" = 'TUC'
  AND "标准架构层级" = '事业群级'
  AND "标准科目名称" = 'TOTAL NET SALES'
  AND "场景角色" = '实际'
GROUP BY 1,2,3,4,5;
```

注意：同名架构可能存在不同层级，标准查询尽量带上 `"标准架构层级"`。

## 2. 标准趋势

适用：某标准架构、某标准科目、跨年实际趋势。

```sql
SELECT
  "年份",
  ROUND(SUM("YTD")::numeric, 0)::bigint AS "实际YTD"
FROM segmentrep_analysis_v2."数据宽表"
WHERE "年份" BETWEEN 2015 AND 2026
  AND "标准架构名称" = 'TUC'
  AND "标准架构层级" = '事业群级'
  AND "标准科目名称" = 'TOTAL NET SALES'
  AND "场景角色" = '实际'
GROUP BY "年份"
ORDER BY "年份";
```

趋势默认使用标准口径。不要自动用子层级汇总补父层级。

## 3. ABF 对比和达成率

达成率默认：`实际 / 预算`。

```sql
WITH ab AS (
  SELECT
    "年份",
    "标准架构名称",
    "标准架构层级",
    "标准科目名称",
    SUM("YTD") FILTER (WHERE "场景角色" = '实际') AS actual_ytd,
    SUM("YTD") FILTER (WHERE "场景角色" = '预算') AS budget_ytd,
    SUM("YTD") FILTER (WHERE "场景角色" = '预测') AS forecast_ytd
  FROM segmentrep_analysis_v2."数据宽表"
  WHERE "年份" = 2026
    AND "标准架构名称" = 'Factory'
    AND "标准架构层级" = '事业群级'
    AND "标准科目名称" = 'TOTAL NET SALES'
    AND "场景角色" IN ('实际', '预算', '预测')
  GROUP BY 1,2,3,4
)
SELECT
  "年份",
  "标准架构名称",
  ROUND(actual_ytd::numeric, 0)::bigint AS "实际YTD",
  ROUND(budget_ytd::numeric, 0)::bigint AS "预算YTD",
  ROUND(forecast_ytd::numeric, 0)::bigint AS "预测YTD",
  ROUND((actual_ytd / NULLIF(budget_ytd, 0) * 100)::numeric, 1) AS "达成率%"
FROM ab;
```

## 4. 成长率

成长率默认：`(当年实际 - 上年实际) / 上年实际`。

```sql
WITH yearly AS (
  SELECT
    "年份",
    SUM("YTD") AS actual_ytd
  FROM segmentrep_analysis_v2."数据宽表"
  WHERE "年份" IN (2025, 2026)
    AND "标准架构名称" = 'TUC'
    AND "标准架构层级" = '事业群级'
    AND "标准科目名称" = 'TOTAL NET SALES'
    AND "场景角色" = '实际'
  GROUP BY "年份"
)
SELECT
  ROUND(curr.actual_ytd::numeric, 0)::bigint AS "当年实际YTD",
  ROUND(prev.actual_ytd::numeric, 0)::bigint AS "上年实际YTD",
  ROUND(((curr.actual_ytd - prev.actual_ytd) / NULLIF(prev.actual_ytd, 0) * 100)::numeric, 1) AS "成长率%"
FROM yearly curr
JOIN yearly prev ON prev."年份" = curr."年份" - 1
WHERE curr."年份" = 2026;
```

## 5. PBT%

`PBT% = PROFIT BEFORE TAX / TOTAL NET SALES`。它不是科目，必须计算。

```sql
WITH base AS (
  SELECT
    "年份",
    "标准架构名称",
    "标准架构层级",
    SUM("YTD") FILTER (WHERE "标准科目名称" = 'PROFIT BEFORE TAX') AS pbt_ytd,
    SUM("YTD") FILTER (WHERE "标准科目名称" = 'TOTAL NET SALES') AS sales_ytd
  FROM segmentrep_analysis_v2."数据宽表"
  WHERE "年份" = 2026
    AND "标准架构名称" = 'TUC'
    AND "标准架构层级" = '事业群级'
    AND "场景角色" = '实际'
    AND "标准科目名称" IN ('PROFIT BEFORE TAX', 'TOTAL NET SALES')
  GROUP BY 1,2,3
)
SELECT
  "年份",
  "标准架构名称",
  ROUND(pbt_ytd::numeric, 0)::bigint AS "PBT",
  ROUND(sales_ytd::numeric, 0)::bigint AS "收入",
  ROUND((pbt_ytd / NULLIF(sales_ytd, 0) * 100)::numeric, 1) AS "PBT%"
FROM base;
```

预算 PBT% 用预算场景的 PBT / 预算场景的收入。预测同理。

## 6. 经营情况默认看板

用户只问“经营情况”且未指定架构时，默认看事业群级。下面示例用 `YTD`，当月口径时把 `YTD` 换成当前报表月份字段。

- `TUC`
- `TUB`
- `长润发`
- `Factory`
- `TU-HQ`
- `I8-TU`

同时补充 `Total`，但 `Total` 来自原始表。

标准事业群列：

```sql
WITH base AS (
  SELECT
    "标准架构名称",
    SUM("YTD") FILTER (WHERE "标准科目名称" = 'TOTAL NET SALES') AS sales_ytd,
    SUM("YTD") FILTER (WHERE "标准科目名称" = 'PROFIT BEFORE TAX') AS pbt_ytd
  FROM segmentrep_analysis_v2."数据宽表"
  WHERE "年份" = 2026
    AND "标准架构层级" = '事业群级'
    AND "标准架构名称" IN ('TUC', 'TUB', '长润发', 'Factory', 'TU-HQ', 'I8-TU')
    AND "场景角色" = '实际'
    AND "标准科目名称" IN ('TOTAL NET SALES', 'PROFIT BEFORE TAX')
  GROUP BY "标准架构名称"
)
SELECT
  "标准架构名称",
  ROUND(sales_ytd::numeric, 0)::bigint AS "收入",
  ROUND(pbt_ytd::numeric, 0)::bigint AS "PBT",
  ROUND((pbt_ytd / NULLIF(sales_ytd, 0) * 100)::numeric, 1) AS "PBT%"
FROM base
ORDER BY array_position(ARRAY['TUC','TUB','长润发','Factory','TU-HQ','I8-TU'], "标准架构名称");
```

Total 列：

```sql
SELECT
  'Total' AS "架构",
  ROUND((SUM("YTD") FILTER (WHERE "原始科目名称" = 'TOTAL NET SALES'))::numeric, 0)::bigint AS "收入",
  ROUND((SUM("YTD") FILTER (WHERE "原始科目名称" = 'PROFIT BEFORE TAX'))::numeric, 0)::bigint AS "PBT",
  ROUND((
    (SUM("YTD") FILTER (WHERE "原始科目名称" = 'PROFIT BEFORE TAX'))
    / NULLIF((SUM("YTD") FILTER (WHERE "原始科目名称" = 'TOTAL NET SALES')), 0)
    * 100
  )::numeric, 1) AS "PBT%"
FROM segmentrep_analysis_v2."原始YTD事实表"
WHERE "年份" = 2026
  AND "原始架构名称" = 'Total'
  AND "场景角色" = '实际'
  AND "原始科目名称" IN ('TOTAL NET SALES', 'PROFIT BEFORE TAX');
```

## 7. TU 整体

`TU` 表示所有事业群。默认展开事业群级列表，不把 `TU` 当作 `TU-HQ` 查询。

如果用户要“TU合计”，优先确认是否等同 `Total`。用户明确要所有事业群合计时，可对事业群级标准架构求和，并说明这是标准事业群合计，不是原始 `Total`。

## 8. 原始历史问数

```sql
SELECT
  "年份",
  "原始架构名称",
  "原始科目名称",
  "原始场景标签",
  ROUND("7月"::numeric, 0)::bigint AS "7月",
  ROUND("YTD"::numeric, 0)::bigint AS "YTD"
FROM segmentrep_analysis_v2."原始YTD事实表"
WHERE "年份" = 2015
  AND "原始架构名称" = 'DIY-Emulsion'
  AND "原始科目名称" = '应用中心支出'
  AND "场景角色" = '实际';
```

## 9. 来源解释

`数据宽表` 已保留标准结果对应的原始架构和原始科目。

```sql
SELECT
  "年份",
  "标准架构名称",
  "标准架构层级",
  "标准科目名称",
  "场景角色",
  "原始架构名称",
  "原始架构层级",
  "原始架构键",
  "原始科目列表",
  "来源记录数",
  ROUND("YTD"::numeric, 0)::bigint AS "YTD"
FROM segmentrep_analysis_v2."数据宽表"
WHERE "年份" = 2018
  AND "标准架构名称" = 'TUC'
  AND "标准架构层级" = '事业群级'
  AND "标准科目名称" = 'TOTAL NET SALES'
  AND "场景角色" = '实际';
```

如果 `原始架构名称` 或 `原始科目列表` 有多个值，回答时说成“由这些原始项匹配/汇总而来”。
