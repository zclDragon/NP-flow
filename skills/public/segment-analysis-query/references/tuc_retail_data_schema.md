# TUC 零售明细表结构 (tuc_retail_data)

仅在需要下钻查询极其明细的客户、物料 (SKU)、省市、特权费、创色费等底层维度数据时，才读取本文件并使用 `public.tuc_retail_data` 表。
对于宏观汇总级别的利润、收入等通用分析，优先使用 `seg_all_year`。

## 连接
- 数据库：`Segmentrep`
- 表：`public.tuc_retail_data`
- 查询限制：由于该表明细到 SKU 和客户级，禁止全量明细查询！对于包含“客户”、“物料”等低维度查询，默认必须加 `ORDER BY ... DESC LIMIT 30` 限制返回的行数（即 Top 30 明细）。
- 字段名规范：表内大部分列名均为纯中文，SQL 查询时**必须用双引号包围字段名**（例如：`SELECT "数据类型", "年度", "收入" FROM public.tuc_retail_data`）。

## 字段映射与别名
该表的底层 SQL 字段名 (`sql_column`) 即为高度业务化的中文词汇，通常直接就是用户的提问词，无需复杂的别名映射。

### 1. 维度字段 (Dimensions)
| sql_column (严格匹配，需加双引号) | type | role | 备注 / aliases |
|---|---|---|---|
| `"年度"` | smallint | time_dimension | 格式如 2026 |
| `"月份"` | smallint | time_dimension | 格式如 4 |
| `"数据类型"` | text | dimension | `实际` 或 `预算` |
| `"公司代码"` | text | dimension | |
| `"销售组织代码"` | text | dimension | |
| `"销售组织描述"` | text | dimension | |
| `"物料号"` | text | dimension | SKU 代码 |
| `"物料描述"` | text | dimension | SKU 名称 |
| `"客户分类代码"` | text | dimension | |
| `"客户分类描述"` | text | dimension | |
| `"客户代码"` | text | dimension | |
| `"客户描述"` | text | dimension | 客户名称、经销商名称 |
| `"事业部"` | text | dimension | |
| `"事业部简称"` | text | dimension | |
| `"产线"` | text | dimension | |
| `"销售部代码"` | text | dimension | |
| `"销售部描述"` | text | dimension | |
| `"销售分部代码"` | text | dimension | |
| `"销售分部描述"` | text | dimension | |
| `"事业群"` | text | dimension | |
| `"省份TUCTUB"` | text | dimension | 省份 |
| `"大区"` | text | dimension | 大区 |
| `"城市TUCTUB"` | text | dimension | 城市 |
| `"TUC产品渠道TUB渠道工程"` | text | dimension | 渠道 (如专卖店、同城分销) |
| `"M01产品市场分类描述"` | text | dimension | |
| `"M02品牌描述"` | text | dimension | 品牌 |
| `"M03子品牌描述"` | text | dimension | 子品牌 |
| `"M04系列描述"` | text | dimension | 系列 |
| `"M05系列细分描述"` | text | dimension | 系列细分 |
| `"M06产品细分描述"` | text | dimension | 产品细分 |
| `"M07档次描述"` | text | dimension | 档次 (高端、大众) |
| `"M08产品渠道描述"` | text | dimension | 产品渠道 |
| `"T09所属PDT描述"` | text | dimension | 所属PDT |
| `"是否自制"` | text | dimension | 自制 / 外购 |
| `"商机号"` | text | dimension | |

### 2. 指标字段 (Metrics - 均为 NUMERIC 类型，金额单位为千元，数量单位为吨)
| sql_column (严格匹配，需加双引号) | aliases |
|---|---|
| `"净重"` | 净重 |
| `"销售数量"` | 销售数量, 销量 |
| `"收入"` | 收入, 销售收入 |
| `"销售税金"` | 销售税金 |
| `"成本"` | 成本, 销售成本 |
| `"运费"` | 运费 |
| `"加工费"` | 加工费 |
| `"折扣（汇总）"` | 折扣（汇总）, 汇总折扣, 总折扣 |
| `"TP折扣"` | TP折扣, TP |
| `"CP折扣"` | CP折扣, CP |
| `"TP专项"` | TP专项 |
| `"工程价格折扣"` | 工程价格折扣 |
| `"折扣ZZ02"` | 折扣ZZ02 |
| `"创色费"` | 创色费, 调色费 |
| `"物流操作费"` | 物流操作费 |
| `"通路管理费"` | 通路管理费 |
| `"线上广告费"` | 线上广告费 |
| `"年终奖励"` | 年终奖励, 年奖 |
| `"产品特权费"` | 产品特权费 |
| `"样品费"` | 样品费 |
| `"Production Expenses"` | 制造费用 |
| `"Laboratory Expenses"` | 技术费用, 研发费用 |
| `"Advertising"` | 广告费 |
| `"Advertising： 线下"` | 线下广告费 |
| `"Indirect Selling Expenses"` | 间接销售费用, 销售费用 |
| `"Indirect Selling Expenses其中：办事处费用"` | 办事处费用 |
| `"Indirect Selling Expenses 公司销售部门费用"` | 公司销售部门费用 |
| `"Indirect Selling Expenses 事业部本部销费"` | 事业部本部销费 |
| `"General & Admin Expenses其中：公司管理费用"` | 公司管理费用 |
| `"General & Admin Expenses 集团管理费用"` | 集团管理费用 |
| `"Depreciation - Production/QC"` | 生产性折旧 |
| `"Depreciation - Non Production"` | 非生产性折旧 |
| `"间接销售类折旧费"` | 间接销售类折旧费 |
| `"管理类折旧费"` | 管理类折旧费 |
| `"技术类折旧费"` | 技术类折旧费 |
| `"Debtors WriteOff/Provision"` | 坏账费用 |
| `"Stocks WriteOff/Provision"` | 坏货费用, 存货跌价准备 |
| `"资金成本"` | 资金成本 |
| `"Management Fees/(Revenue)"` | 吃水线, 管理费分摊 |
| `"Intra Fees/(Revenue)"` | 内部交易费用 |
| `"interest  income/(expense)"` | 利息收支 |
| `"foreign exchange gain/(loss)"` | 汇兑损益 |
| `"OTHEROPERATIONALINCOMEEXPENSE"` | 其他业务收支 |
| `"销售净额"` | 销售净额 |
| `"PDT考核利润"` | PDT考核利润 |
| `"税前利润"` | 税前利润 |
