# 主题字段要求

本文件定义每个业务主题最少需要哪些标准字段，才能进入计算。

## 状态定义

- `supported`：必需字段齐全，可正常计算
- `partial`：部分可算，但关键图表或关键指标缺失
- `skipped`：关键字段缺失，不应输出该主题

## 1. 会员概况

### 必需字段

- `member_id`

### 建议字段

- `identity_label`
- `gender`
- `age`
- `member_level`

### 判定规则

- 只有 `member_id`：可部分输出总人数
- `identity_label / gender / age / member_level` 越多，页面越完整

## 2. 一物一码来源已挂靠

### 必需字段

- `member_id`
- `store_id`
- `store_name`
- `is_qr_source`

### 建议字段

- `store_type`
- `store_consume_amount`
- `member_day_count`
- `member_day_redeem_total`

### 判定规则

- 缺 `is_qr_source`：直接跳过
- 缺消费或活动字段：可做规模页，不做转化页

## 3. 一物一码来源待挂靠

### 必需字段

至少满足两种来源之一：

#### 方案 A：专题明细表

- `member_id`
- `identity_final` 或 `identity_label`
- `qr_scan_bags`
- 区域字段

#### 方案 B：已内嵌汇总专题表

- 工种分档表可直接读取
- 区域分档表可直接读取

### 判定规则

- 没有扫码包数字段，就跳过

## 4. 会员消费

### 必需字段

- `member_id`
- `store_consume_amount`

### 建议字段

- `store_type`
- `store_consume_days`
- `last_store_consume_month`
- `member_level`
- `qr_scan_bags`

### 判定规则

- 只有 `member_id + store_consume_amount`：可出基础消费页
- 缺 `last_store_consume_month`：不能做月度活跃分布

## 5. 上门基检 / 上门服务

### 必需字段

至少满足：

- `member_id`
- `store_id`
- `visit_count`

### 建议字段

- `store_name`
- `visit_coupon_get`
- `visit_coupon_use`
- `visit_coupon_linked_amount`
- `visit_recruit_members`
- `visit_maintain_members`

### 判定规则

- 缺 `visit_count`：跳过
- 缺 `visit_recruit_members / visit_maintain_members`：只出覆盖和券转化，不出拓新维旧

## 6. 会员日

### 必需字段

- `member_id`
- `member_day_count`

### 建议字段

- `member_level`
- `store_type`
- `event_month`
- 奖品与核销字段

### 判定规则

- 只有 `member_day_count`：可出参与规模
- 缺月份明细：不能做可靠月度趋势

## 7. 会员分层与风险池

### 必需字段

- `member_id`

### 建议字段

- `store_consume_amount`
- `qr_scan_bags`
- `member_day_count`
- `mall_amount`
- `visit_count`
- `last_store_consume_month`

### 判定规则

- 至少需要 3 类行为字段中的 2 类，才建议输出分层
- 缺 `last_store_consume_month` 时，流失风险只能弱化定义

## 8. 门店经营机会优先级

### 必需字段

- `store_id`
- 至少 2 类门店经营指标

### 建议字段

- 会员盘规模
- 消费人数 / 消费率
- 一物一码挂靠人数
- 会员日参与人数
- 商城购买人数
- 基检人数

### 判定规则

- 缺少足够门店经营指标时跳过

## 9. 联谊会 / 线下活动

### 必需字段

至少满足以下之一：

#### 方案 A：活动明细

- `event_store_id`
- `event_month`
- `event_member_id`

#### 方案 B：门店年度汇总

- `association_signin_count`

### 判定规则

- 只有年度签到汇总：最多做简版活动汇总
- 没有活动明细：不能出可靠的场次分布和新会员占比

## 10. 商城 / GMV

### 必需字段

至少满足以下之一：

#### 方案 A：年累计版

- `member_id`
- `mall_amount`

#### 方案 B：月度版

- `member_id`
- `mall_amount`
- 月份明细或订单日期

### 判定规则

- 只有年累计字段：仅支持年累计页
- 没有月份字段：跳过所有月趋势图
