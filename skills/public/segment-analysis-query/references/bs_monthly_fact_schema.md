# BS 月度问数表结构

仅在需要写 BS/资产负债表相关 SQL 或确认字段名时读取本文件。目标表：`public.bs_monthly_fact`。

## 表定位

- 粒度：`year + month + metric_key`
- 来源：`BS.xlsx` 的 `Sheet1`
- 金额单位：千元
- 周转天数单位：天
- 默认排序：`year, month_no, line_no`

## 字段

| column | type | meaning |
|---|---|---|
| `year` | integer | 年度 |
| `month` | text | 月份英文缩写，如 Jan、Feb |
| `month_no` | integer | 月份序号 |
| `period_date` | date | 月初日期 |
| `line_no` | integer | 原 Excel 列序号，用于默认展示排序 |
| `current_noncurrent` | text | 流动/非流动属性，来自第 1 行 |
| `metric_group` | text | 统称/科目组，来自第 2 行 |
| `metric_cn_name` | text | 中文名称，来自第 3 行 |
| `metric_en_name` | text | 英文/系统名称，来自第 4 行 |
| `metric_key` | text | SQL 友好指标键 |
| `value` | double precision | 指标值 |
| `unit` | text | 单位：千元或天 |
| `metric_kind` | text | 指标类型：金额、周转天数 |

## 使用规则

- 用户问资产、负债、净资产、权益、现金、存货、应收、应付、借款、周转天数、BS 或资产负债表时，优先使用本表。
- 用户问“流动资产”“非流动资产”“流动负债”“非流动负债”时，过滤 `current_noncurrent`。
- 用户问“存货”“应收账款”“货币资金”等统称时，过滤 `metric_group`。
- 用户问具体科目时，优先匹配 `metric_cn_name`，必要时匹配 `metric_en_name` 或 `metric_key`。
- 原 Excel 的 check 校验列不进入本表。
- 默认不要把合计项和明细项重复加总；是否为合计项按中文/英文科目名称判断。
