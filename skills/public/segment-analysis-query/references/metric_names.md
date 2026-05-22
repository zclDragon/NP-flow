# 指标名称与别名

仅在需要解析指标、中文别名或回答展示名称时读取本文件。底层 SQL 查询使用 `sql_column`。回答时优先使用 `display_name`。

| excel_header | sql_column | display_name | aliases |
|---|---|---|---|
| Total Gross Sales | `total_gross_sales` | 销额 | 销额, Total Gross Sales |
| Less: Sales Return | `less_sales_return` | 退货 | 退货, 销售退回, Less: Sales Return |
| TOTAL NET SALES | `total_net_sales` | 销售净额 | 销售净额, 收入, TOTAL NET SALES |
| RMCC | `rmcc` | RMCC | RMCC, 销售成本 |
| Free Gifts | `free_gifts` | 样品 | 样品, Free Gifts |
| Commission | `commission` | 通路 | 通路, Commission |
| Less:Discount | `less_discount` | 折扣 | 折扣, Less:Discount |
| 其中：CP消费者促销 | `cp_consumer_promotion` | CP | CP, CP折扣, 其中：CP消费者促销 |
| TP代理商促销 | `tp_dealer_promotion` | TP | TP, TP折扣, TP代理商促销,      TP代理商促销 |
| 工程价格折扣 | `project_price_discount` | 工程价格折扣 | 工程价格折扣,      工程价格折扣 |
| TP专项 | `tp_special` | TP专项 | TP专项 |
| Sales Bonus & Incentives | `sales_bonus_incentives` | 年奖 | 年奖, 年终奖励, Sales Bonus & Incentives |
| Logistics | `logistics` | 运费 | 运费, Logistics |
| Royalties | `royalties` | 特许权使用费 | 特许权使用费, Royalties |
| Management Fees | `management_fees` | 管理费 | 管理费, Management Fees |
| VARIABLE COSTS (ex RMCC) | `variable_costs_ex_rmcc` | 变动成本（除RMCC） | 变动成本（除RMCC）, VARIABLE COSTS (ex RMCC) |
| CONTRIBUTION MARGIN | `contribution_margin` | 边际贡献 | 边际贡献, CONTRIBUTION MARGIN |
| Production Expenses | `production_expenses` | 制造费用 | 制造费用, 工厂列制费, Production Expenses |
| Direct Labour | `direct_labour` | 直接人工 | 直接人工, Direct Labour |
| Factory Expense | `factory_expense` | 工厂费用 | 工厂费用, Factory Expense |
| Laboratory Expenses | `laboratory_expenses` | 技术费用 | 技术费用, 研发费用, Laboratory Expenses |
| Advertising | `advertising` | 广告费 | 广告费, Advertising |
| 其中：线上 | `online_advertising` | 线上广告费 | 线上广告费, 其中：线上 |
| 线下 | `offline_advertising` | 线下广告费 | 线下广告费, 线下,      线下 |
| Indirect Selling Expenses | `indirect_selling_expenses` | 销售费用 | 销售费用, 销费, 间接销售费用, Indirect Selling Expenses |
| 其中：       办事处费用 | `office_expenses` | 办事处费用 | 办事处费用, 其中：       办事处费用 |
| 公司销售部门费用 | `company_sales_department_expenses` | 公司销售部门费用 | 公司销售部门费用,  公司销售部门费用 |
| 事业部本部销费 | `business_unit_selling_expenses` | 事业部本部销费 | 事业部本部销费,  事业部本部销费 |
| General & Admin Expenses | `general_admin_expenses` | 管理费用 | 管理费用, 管费, General & Admin Expenses |
| 其中：公司管理费用 | `company_admin_expenses` | 公司管理费用 | 公司管理费用, 其中：公司管理费用 |
| 集团管理费用 | `group_admin_expenses` | 集团管理费用 | 集团管理费用,  集团管理费用 |
| Depreciation - Production/QC | `depreciation_production_qc` | 生产性折旧 | 生产性折旧, Depreciation - Production/QC |
| Depreciation - Non Production | `depreciation_non_production` | 非生产性折旧 | 非生产性折旧, Depreciation - Non Production |
| 间接销售类折旧费 | `depreciation_indirect_selling` | 间接销售类折旧费 | 间接销售类折旧费 |
| 管理类折旧费 | `depreciation_admin` | 管理类折旧费 | 管理类折旧费 |
| 技术类折旧费 | `depreciation_technical` | 技术类折旧费 | 技术类折旧费 |
| Debtors WriteOff/Provision | `debtors_writeoff_provision` | 坏账费用 | 坏账费用, Debtors WriteOff/Provision |
| Stocks WriteOff/Provision | `stocks_writeoff_provision` | 坏货费用 | 坏货费用, Stocks WriteOff/Provision |
| Production Fees/(Revenue)-Paint | `production_fees_revenue_paint` | 事业部制费 | 事业部制费, PDT制费, 分摊制费, 事业部加工费, Production Fees/(Revenue)-Paint |
| Production Fees/(Revenue)-Resin | `production_fees_revenue_resin` | 创色费用 | 创色费用, Production Fees/(Revenue)-Resin |
| 物流操作费 | `logistics_operation_fee` | 物流操作费 | 物流操作费 |
| Management Fees/(Revenue) | `management_fees_revenue` | 吃水线 | 吃水线, TU管理费, Management Fees/(Revenue) |
| Intra Fees/(Revenue) | `intra_fees_revenue` | 吃水线 | 吃水线, RHQ管理费, Intra Fees/(Revenue) |
| TOTAL OVERHEADS | `total_overheads` | 固定费用 | 固定费用, 固费, TOTAL OVERHEADS |
| 关联销售收入(中国) | `interco_sales_income_china` | 关联销售收入(中国) | 关联销售收入(中国) |
| 关联销售收入(香港/台湾) | `interco_sales_income_hk_tw` | 关联销售收入(香港/台湾) | 关联销售收入(香港/台湾) |
| 关联销售收入(其他) | `interco_sales_income_other` | 关联销售收入(其他) | 关联销售收入(其他) |
| 关联销售加成收入 | `interco_sales_markup_income` | 关联销售加成收入 | 关联销售加成收入 |
| 关联销售成本(中国) | `interco_sales_cost_china` | 关联销售成本(中国) | 关联销售成本(中国) |
| 关联销售成本(香港/台湾) | `interco_sales_cost_hk_tw` | 关联销售成本(香港/台湾) | 关联销售成本(香港/台湾) |
| 关联销售成本(其他) | `interco_sales_cost_other` | 关联销售成本(其他) | 关联销售成本(其他) |
| 关联销售加成支出 | `interco_sales_markup_expense` | 关联销售加成支出 | 关联销售加成支出 |
| InterCo Income/(Loss) | `interco_income_loss` | 关联收入 | 关联收入, InterCo Income/(Loss) |
| Other Operational Income/(Expense) | `other_operational_income_expense` | 其他业务收入 | 其他业务收入, OI, Other Operational Income/(Expense) |
| EARNINGS B/F INTEREST/TAX | `earnings_before_interest_tax` | 息税前利润 | 息税前利润, EBIT, EARNINGS B/F INTEREST/TAX |
| Interest Income/(Expense) | `interest_income_expense` | 利息收入 | 利息收入, 利息费用, Interest Income/(Expense) |
| Foreign Exchange Gain/(Loss) | `foreign_exchange_gain_loss` | 汇兑损益 | 汇兑损益, Foreign Exchange Gain/(Loss) |
| Financial Subsidy | `financial_subsidy` | 政府补贴 | 政府补贴, Financial Subsidy |
| PROFIT BEFORE TAX | `profit_before_tax` | 税前利润 | 税前利润, PBT, PROFIT BEFORE TAX |
| PBT After Adjustment | `pbt_after_adjustment` | 调整后税前利润 | 调整后税前利润, PBT After Adjustment |
| Taxation | `taxation` | 所得税费用 | 所得税费用, Taxation |
| PROFIT AFTER TAXATION | `profit_after_taxation` | 税后利润 | 税后利润, PAT, PROFIT AFTER TAXATION |
| Minority Interests | `minority_interests` | 少数股东损益 | 少数股东损益, Minority Interests |
| PROFIT TO SHAREHOLDERS | `profit_to_shareholders` | 归属于股东的净利润 | 归属于股东的净利润, PROFIT TO SHAREHOLDERS |
| 毛利 | `gross_profit` | 毛利 | 毛利 |
| CHC调拨加成成本 | `chc_transfer_markup_cost` | CHC调拨加成成本 | CHC调拨加成成本 |
| Less:销售税金（Sales Tax） | `sales_tax` | 销售税金 | 销售税金, Less:销售税金（Sales Tax） |
| TOTAL GROSS SALES2 | `total_gross_sales2` | 调整后销额 | 调整后销额, TOTAL GROSS SALES2 |
| 资金成本 | `capital_cost` | 资金成本 | 资金成本 |
| Share of Profit of Equity-Accounted Affiliates | `share_profit_equity_accounted_affiliates` | 投资收益 | 投资收益, 按权益法核算的联营及合营企业之利润份额, Share of Profit of Equity-Accounted Affiliates |
| 销量 | `volume` | 销量 | 销量 |
