---
name: segmentrep-analysis-query
description: 使用 Segmentrep v2 查询层回答经营问数、P&L、YTD、Actual/Budget/Forecast、达成率、成长率、标准架构、标准科目、历史原始块头、Total、TU整体、CRF合并、I8 和来源解释问题。适用于通过数据库 MCP / PostgreSQL 工具对 segmentrep_analysis_v2 执行只读 SQL 的场景。
---

# Segmentrep v2 经营分析

这是面向问数产品的 skill。默认只使用最终可查询数据，不讲导数过程，不暴露映射表和刷新逻辑。

## Core Workflow

1. 使用已配置的数据库 MCP / PostgreSQL 工具查库；不要向用户索要数据库账号密码，也不要暴露连接串。
2. 先读 [references/defaults-and-aliases.md](references/defaults-and-aliases.md)，把自然语言中的架构、指标、时间、场景归一化。
3. 再读 [references/query-routing.md](references/query-routing.md)，选择 `数据宽表` 或 `原始YTD事实表`。
4. 需要字段、粒度和期间列时，读 [references/schema.md](references/schema.md)。
5. 需要 SQL 模式、PBT%、达成率、成长率、经营情况默认看板时，读 [references/query-patterns.md](references/query-patterns.md)。
6. 需要回答口径差异、Total、TU、父层级、未查到数据时，读 [references/analysis-guidelines.md](references/analysis-guidelines.md)。

## Query Surfaces

普通问数只使用两张产品表：

- `segmentrep_analysis_v2."数据宽表"`：默认入口。回答标准架构、标准科目、跨年趋势、ABF、达成率、成长率、经营情况、来源原始构成。
- `segmentrep_analysis_v2."原始YTD事实表"`：原始入口。回答 Total、历史原始块头、历史原始科目、原始报表还原。

`年度架构匹配表` 和 `年度科目匹配表` 是刷新和排查用表。除非用户明确要求排查建模或数据映射，否则不要在问数答案中使用或提及。

## Default Routing

- 当前、今年、当年、最新、本年、现在、目前：默认标准口径，查 `数据宽表`。
- 未指定时间：默认当年 + 当前报表当月。用户说累计、YTD、全年累计时使用 `YTD`；没有月份上下文时简短确认当月。
- 标准架构、标准科目、趋势、达成率、成长率、ABF 对比：查 `数据宽表`。
- `Total`、总计、总盘子、总损益、历史块头、原始科目、原始报表：查 `原始YTD事实表`。
- 问“经营情况”且未指定架构：默认呈现事业群级 `TUC`、`TUB`、`长润发/CRF`、`Factory`、`TU-HQ`、`I8-TU`，并补充 `Total`。
- `TU` 默认表示所有事业群，不等同于 `TU-HQ`。

## Hard Rules

- 只执行只读 SQL；不要执行 `INSERT`、`UPDATE`、`DELETE`、`TRUNCATE`、`DROP`、`ALTER`。
- SQL 对象名始终带 schema 前缀：`segmentrep_analysis_v2.`。
- 不要要求用户提供数据库账号密码。
- 普通回答不要暴露导数、建模、刷新、映射表等内部过程。
- 问哪一层架构，就按那一层查；查不到就说明该层级在当前条件下无数据，不自动汇总子层级补数。
- `Total` 默认查原始表，不从标准架构加总硬凑。
- 百分比结果保留 1 位小数；金额相关结果保留整数。
- `PBT%` 是派生指标：`PROFIT BEFORE TAX / TOTAL NET SALES`，不要把它当标准科目查。

## Answer Style

- 结论优先，随后给数值、口径和必要解释。
- 明确说明年份、期间、场景、架构口径、科目口径。
- 对比类回答同时给差异额和比例。
- 未查到数据时，优先从口径、层级、时间、场景解释，不把内部建模细节甩给用户。
