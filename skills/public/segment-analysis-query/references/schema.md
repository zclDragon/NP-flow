# Segment 问数表结构

仅在需要写 SQL 或确认字段名时读取本文件。数据库中只使用一张事实表：`public.seg_all_year`。

## 连接

- 数据库：`Segmentrep`
- 表：`public.seg_all_year`
- 查询方式：使用可用的 PostgreSQL 数据库查询工具。
- `data_type` 枚举值：`实际`、`预算`
- 金额类指标单位：千元。
- 非金额指标：`volume`（销量），按原表单位展示。

## 字段映射

| excel_header | sql_column | type | role |
|---|---|---|---|
| TOTAL | `total` | text | dimension |
| 事业群 | `business_group` | text | dimension |
| 事业部 | `business_unit` | text | dimension |
| 数据类型 | `data_type` | text | dimension |
| 水木基辅 | `shuimu_jifu` | text | dimension |
| PDT | `pdt` | text | dimension |
| 产线 | `product_line` | text | dimension |
| Org | `org` | text | dimension |
| Year | `year` | integer | time_dimension |
| Period | `period` | text | dimension |
| Total Gross Sales | `total_gross_sales` | double precision | metric |
| Less: Sales Return | `less_sales_return` | double precision | metric |
| TOTAL NET SALES | `total_net_sales` | double precision | metric |
| RMCC | `rmcc` | double precision | metric |
| Free Gifts | `free_gifts` | double precision | metric |
| Commission | `commission` | double precision | metric |
| Less:Discount | `less_discount` | double precision | metric |
| 其中：CP消费者促销 | `cp_consumer_promotion` | double precision | metric |
| TP代理商促销 | `tp_dealer_promotion` | double precision | metric |
| 工程价格折扣 | `project_price_discount` | double precision | metric |
| TP专项 | `tp_special` | double precision | metric |
| Sales Bonus & Incentives | `sales_bonus_incentives` | double precision | metric |
| Logistics | `logistics` | double precision | metric |
| Royalties | `royalties` | double precision | metric |
| Management Fees | `management_fees` | double precision | metric |
| VARIABLE COSTS (ex RMCC) | `variable_costs_ex_rmcc` | double precision | metric |
| CONTRIBUTION MARGIN | `contribution_margin` | double precision | metric |
| Production Expenses | `production_expenses` | double precision | metric |
| Direct Labour | `direct_labour` | double precision | metric |
| Factory Expense | `factory_expense` | double precision | metric |
| Laboratory Expenses | `laboratory_expenses` | double precision | metric |
| Advertising | `advertising` | double precision | metric |
| 其中：线上 | `online_advertising` | double precision | metric |
| 线下 | `offline_advertising` | double precision | metric |
| Indirect Selling Expenses | `indirect_selling_expenses` | double precision | metric |
| 其中：       办事处费用 | `office_expenses` | double precision | metric |
| 公司销售部门费用 | `company_sales_department_expenses` | double precision | metric |
| 事业部本部销费 | `business_unit_selling_expenses` | double precision | metric |
| General & Admin Expenses | `general_admin_expenses` | double precision | metric |
| 其中：公司管理费用 | `company_admin_expenses` | double precision | metric |
| 集团管理费用 | `group_admin_expenses` | double precision | metric |
| Depreciation - Production/QC | `depreciation_production_qc` | double precision | metric |
| Depreciation - Non Production | `depreciation_non_production` | double precision | metric |
| 间接销售类折旧费 | `depreciation_indirect_selling` | double precision | metric |
| 管理类折旧费 | `depreciation_admin` | double precision | metric |
| 技术类折旧费 | `depreciation_technical` | double precision | metric |
| Debtors WriteOff/Provision | `debtors_writeoff_provision` | double precision | metric |
| Stocks WriteOff/Provision | `stocks_writeoff_provision` | double precision | metric |
| Production Fees/(Revenue)-Paint | `production_fees_revenue_paint` | double precision | metric |
| Production Fees/(Revenue)-Resin | `production_fees_revenue_resin` | double precision | metric |
| 物流操作费 | `logistics_operation_fee` | double precision | metric |
| Management Fees/(Revenue) | `management_fees_revenue` | double precision | metric |
| Intra Fees/(Revenue) | `intra_fees_revenue` | double precision | metric |
| TOTAL OVERHEADS | `total_overheads` | double precision | metric |
| 关联销售收入(中国) | `interco_sales_income_china` | double precision | metric |
| 关联销售收入(香港/台湾) | `interco_sales_income_hk_tw` | double precision | metric |
| 关联销售收入(其他) | `interco_sales_income_other` | double precision | metric |
| 关联销售加成收入 | `interco_sales_markup_income` | double precision | metric |
| 关联销售成本(中国) | `interco_sales_cost_china` | double precision | metric |
| 关联销售成本(香港/台湾) | `interco_sales_cost_hk_tw` | double precision | metric |
| 关联销售成本(其他) | `interco_sales_cost_other` | double precision | metric |
| 关联销售加成支出 | `interco_sales_markup_expense` | double precision | metric |
| InterCo Income/(Loss) | `interco_income_loss` | double precision | metric |
| Other Operational Income/(Expense) | `other_operational_income_expense` | double precision | metric |
| EARNINGS B/F INTEREST/TAX | `earnings_before_interest_tax` | double precision | metric |
| Interest Income/(Expense) | `interest_income_expense` | double precision | metric |
| Foreign Exchange Gain/(Loss) | `foreign_exchange_gain_loss` | double precision | metric |
| Financial Subsidy | `financial_subsidy` | double precision | metric |
| PROFIT BEFORE TAX | `profit_before_tax` | double precision | metric |
| PBT After Adjustment | `pbt_after_adjustment` | double precision | metric |
| Taxation | `taxation` | double precision | metric |
| PROFIT AFTER TAXATION | `profit_after_taxation` | double precision | metric |
| Minority Interests | `minority_interests` | double precision | metric |
| PROFIT TO SHAREHOLDERS | `profit_to_shareholders` | double precision | metric |
| 毛利 | `gross_profit` | double precision | metric |
| CHC调拨加成成本 | `chc_transfer_markup_cost` | double precision | metric |
| Less:销售税金（Sales Tax） | `sales_tax` | double precision | metric |
| TOTAL GROSS SALES2 | `total_gross_sales2` | double precision | metric |
| 资金成本 | `capital_cost` | double precision | metric |
| Share of Profit of Equity-Accounted Affiliates | `share_profit_equity_accounted_affiliates` | double precision | metric |
| 销量 | `volume` | double precision | metric |
