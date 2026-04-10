---
name: data-analysis
description: 当用户上传Excel(.xlsx/.xls)或CSV文件并需要进行数据分析、生成统计信息、创建汇总、数据透视表、SQL查询或任何形式的结构化数据探索时使用此技能。支持多工作表Excel工作簿、聚合、筛选、关联查询以及将结果导出为CSV/JSON/Markdown格式。
---

# 数据分析技能

## 概述

本技能使用 DuckDB（进程内分析型SQL引擎）分析用户上传的Excel/CSV文件，支持结构检查、SQL查询、统计汇总和结果导出，所有功能都通过单个Python脚本实现。

## 核心能力

- 检查Excel/CSV文件结构（工作表、列、数据类型、行数）
- 对上传的数据执行任意SQL查询
- 生成统计汇总（平均值、中位数、标准差、百分位数、空值统计）
- 支持多工作表Excel工作簿（每个工作表对应一张表）
- 将查询结果导出为CSV、JSON或Markdown格式
- 使用DuckDB的列式引擎高效处理大文件

## 工作流程

### 步骤1：理解需求
当用户上传数据文件并请求分析时，确认以下信息：
- **文件位置**：上传的Excel/CSV文件路径，位于 `/mnt/user-data/uploads/` 目录下
- **分析目标**：用户需要获取的洞察（汇总、筛选、聚合、对比等）
- **输出格式**：结果展示方式（表格、CSV导出、JSON等）
- 不需要自行检查 `/mnt/user-data` 下的文件夹

### 步骤2：检查文件结构
首先检查上传文件以了解其结构：
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action inspect
```
返回信息包括：
- 工作表名称（Excel文件）或文件名（CSV文件）
- 列名、数据类型和非空值数量
- 每个工作表/文件的行数
- 示例数据（前5行）

### 步骤3：执行分析
根据文件结构，构建SQL查询来回答用户的问题。

#### 运行SQL查询
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action query \
  --sql "SELECT category, COUNT(*) as count, AVG(amount) as avg_amount FROM Sheet1 GROUP BY category ORDER BY count DESC"
```

#### 生成统计汇总
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action summary \
  --table Sheet1
```
对数值型列返回：计数、平均值、标准差、最小值、25%分位数、中位数、75%分位数、最大值、空值数量。
对字符串列返回：计数、唯一值数量、出现频率最高的值、出现频率、空值数量。

#### 导出结果
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action query \
  --sql "SELECT * FROM Sheet1 WHERE amount > 1000" \
  --output-file /mnt/user-data/outputs/filtered-results.csv
```
支持的输出格式（根据扩展名自动识别）：
- `.csv` — 逗号分隔值文件
- `.json` — JSON记录数组
- `.md` — Markdown表格

### 参数说明
| 参数 | 必填 | 描述 |
|-----------|----------|-------------|
| `--files` | 是 | 空格分隔的Excel/CSV文件路径 |
| `--action` | 是 | 操作类型：`inspect`(检查结构)、`query`(执行SQL)、`summary`(统计汇总) |
| `--sql` | `query`操作必填 | 要执行的SQL查询 |
| `--table` | `summary`操作必填 | 要统计的表/工作表名称 |
| `--output-file` | 否 | 结果导出路径（支持CSV/JSON/MD） |

> [!NOTE]
> 不需要阅读Python脚本文件，直接按参数调用即可。

## 表命名规则
- **Excel文件**：每个工作表对应一张表，表名与工作表名相同（如 `Sheet1`、`销售数据`、`营收`）
- **CSV文件**：表名为不带扩展名的文件名（如 `data.csv` → `data`）
- **多文件**：所有文件中的所有表都在同一个查询上下文中可用，支持跨文件关联查询
- **特殊字符**：包含空格或特殊字符的工作表/文件名会自动清理（空格替换为下划线）。对于以数字开头或包含特殊字符的名称，请使用双引号包裹，例如 `"2024_销售数据"`

## 常用分析模式

### 基础探索
```sql
-- 统计行数
SELECT COUNT(*) FROM Sheet1

-- 查询列的唯一值
SELECT DISTINCT category FROM Sheet1

-- 值分布统计
SELECT category, COUNT(*) as cnt FROM Sheet1 GROUP BY category ORDER BY cnt DESC

-- 日期范围
SELECT MIN(date_col), MAX(date_col) FROM Sheet1
```

### 聚合与分组
```sql
-- 按类别和月份统计营收
SELECT category, DATE_TRUNC('month', order_date) as month,
       SUM(revenue) as total_revenue
FROM Sales
GROUP BY category, month
ORDER BY month, total_revenue DESC

-- 按消费额排名前10的客户
SELECT customer_name, SUM(amount) as total_spend
FROM Orders GROUP BY customer_name
ORDER BY total_spend DESC LIMIT 10
```

### 跨文件关联查询
```sql
-- 关联不同文件的销售数据和客户信息
SELECT s.order_id, s.amount, c.customer_name, c.region
FROM sales s
JOIN customers c ON s.customer_id = c.id
WHERE s.amount > 500
```

### 窗口函数
```sql
-- 计算累计总额和排名
SELECT order_date, amount,
       SUM(amount) OVER (ORDER BY order_date) as running_total,
       RANK() OVER (ORDER BY amount DESC) as amount_rank
FROM Sales
```

### 数据透视分析
```sql
-- 透视：按类别统计月度营收
SELECT category,
       SUM(CASE WHEN MONTH(date) = 1 THEN revenue END) as 一月,
       SUM(CASE WHEN MONTH(date) = 2 THEN revenue END) as 二月,
       SUM(CASE WHEN MONTH(date) = 3 THEN revenue END) as 三月
FROM Sales
GROUP BY category
```

## 完整示例
用户上传 `sales_2024.xlsx`（包含工作表：`Orders`、`Products`、`Customers`）并询问："分析我的销售数据，展示营收最高的产品和月度趋势。"

### 步骤1：检查文件结构
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action inspect
```

### 步骤2：查询营收最高的产品
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action query \
  --sql "SELECT p.product_name, SUM(o.quantity * o.unit_price) as total_revenue, SUM(o.quantity) as total_units FROM Orders o JOIN Products p ON o.product_id = p.id GROUP BY p.product_name ORDER BY total_revenue DESC LIMIT 10"
```

### 步骤3：查询月度营收趋势
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action query \
  --sql "SELECT DATE_TRUNC('month', order_date) as month, SUM(quantity * unit_price) as revenue FROM Orders GROUP BY month ORDER BY month" \
  --output-file /mnt/user-data/outputs/monthly-trends.csv
```

### 步骤4：生成统计汇总
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action summary \
  --table Orders
```

向用户展示结果时，需清晰解释发现的趋势和可操作的洞察。

## 多文件示例
用户上传 `orders.csv` 和 `customers.xlsx` 并询问："哪个地区的平均订单价值最高？"
```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/orders.csv /mnt/user-data/uploads/customers.xlsx \
  --action query \
  --sql "SELECT c.region, AVG(o.amount) as avg_order_value, COUNT(*) as order_count FROM orders o JOIN Customers c ON o.customer_id = c.id GROUP BY c.region ORDER BY avg_order_value DESC"
```

## 输出处理
分析完成后：
- 将查询结果直接作为格式化表格在对话中展示
- 对于大量结果，导出为文件并通过 `present_files` 工具分享
- 始终用通俗易懂的语言解释发现的结论和关键要点
- 当发现有趣的模式时，建议后续可以进行的分析
- 如果用户需要保存结果，主动提供导出服务

## 缓存机制
脚本会自动缓存已加载的数据，避免每次调用都重新解析文件：
- 首次加载时，文件会被解析并存储在 `/mnt/user-data/workspace/.data-analysis-cache/` 目录下的持久化DuckDB数据库中
- 缓存键是所有输入文件内容的SHA256哈希值 — 如果文件发生变化，会自动创建新的缓存
- 后续使用相同文件的调用会直接使用缓存的数据库（启动速度接近实时）
- 缓存是透明的 — 不需要额外参数

这对于对同一数据文件运行多个查询的场景特别有用（检查结构 → 查询 → 汇总）。

## 注意事项
- DuckDB支持完整SQL语法，包括窗口函数、CTE、子查询和高级聚合
- Excel日期列会自动解析；可以使用DuckDB日期函数（`DATE_TRUNC`、`EXTRACT`等）处理
- 对于非常大的文件（100MB+），DuckDB可以高效处理，不需要将全部内容加载到内存
- 包含空格的列名需要使用双引号访问：`"列名"`