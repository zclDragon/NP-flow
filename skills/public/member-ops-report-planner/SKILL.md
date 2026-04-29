---
name: member-ops-report-planner
description: 当用户上传会员运营相关的 Excel(.xlsx/.xls) 或 CSV 数据文件，希望基于这些文件生成结构化报告内容、分析页面规划、图表底数、表格结果、指标口径说明时，使用本 skill。适用于需要跨城市、跨年份、跨模板做会员概况、一物一码、消费、会员日、基检、分层、GMV、联谊会等主题分析，并把结果继续交给 PPT / HTML / PDF / 图表技能渲染的场景。遇到“根据这个 Excel 做会员运营分析报告”“先分析数据能支持哪些页”“输出可用于做汇报的页面结构”等请求时，应优先使用本 skill。（（通过知识蒸馏生成））
---
####立邦会员运营
# 会员运营报告规划

本 skill 负责把会员运营类数据文件转成**中性的报告内容层**，而不是直接完成最终渲染。

## 核心职责

1. 调用 `data-analysis` skill 观察文件结构
2. 识别候选主表、维表、活动表、专题表
3. 建立标准语义字段映射
4. 判断哪些业务主题可计算、哪些应跳过
5. 输出结构化分析结果与报告计划

## 协作依赖

### 强制依赖

- `data-analysis`
  - 用于 `inspect`
  - 用于 `summary`
  - 用于 `query`

### 可选依赖

- 图表制作 skill
  - 用于将已确认底数转成图表配置、图表中间文件或图像
- 报告渲染 skill
  - 用于把 `report_plan.json` 渲染为 PPT / HTML / PDF

## 输入

- 一个或多个 Excel / CSV 文件
- 用户的报告目标
- 可选输出介质偏好：PPT / HTML / PDF / 其他

## 输出

必须输出以下文件或等价结构：

- `schema_profile.json`
- `field_mapping.json`
- `dimension_support.json`
- `analysis.json`
- `report_plan.json`
- `mapping_report.md`

如果后续需要图表，还可以补充：

- `chart_tasks.json`

## 绝对约束

1. 不允许模糊映射字段。
2. 不允许仅凭字段名相似就使用字段。
3. 不允许为了页面完整而编造不可闭环指标。
4. 不允许直接绑定 `2025`、某个固定城市、某个固定模板。
5. 禁止把字段映射、业务计算、最终 HTML/PPT/PDF 渲染塞进一个单体脚本。
6. 本 skill 只能产出第二层结构文件；最终渲染必须交给下游技能或下一步动作。

## 字段映射判定规则

字段只有在满足以下规则之一时才允许映射：

### 规则 A：精确命中

- 原始列名与字段词典中的标准别名完全一致
- 数据类型与预期一致

### 规则 B：词典别名命中 + 值域验证

同时满足：

- 原始列名命中字段词典中的允许别名
- 数据类型符合预期
- 样例值符合预期值域或编码方式
- 所在 sheet 的角色也符合预期

### 规则 C：人工确认待补

如果存在多个候选字段，或证据不足：

- 不自动映射
- 记录为 `unresolved`
- 将依赖该字段的主题标记为不支持

禁止使用：

- 模糊相似度拍脑袋映射
- 不带证据的“应该是这个字段”
- 只看字段名不看样例值

## 标准工作流

### 第 1 步：调用 `data-analysis` 做结构观察

必须先使用 `data-analysis` skill：

- `inspect` 所有输入文件
- 必要时对候选主表做 `summary`
- 必要时运行 SQL 检查主键、金额列、日期列、分类列

这一阶段的目标不是算结论，而是产出：

- sheet / table 清单
- 候选主表清单
- 候选维表清单
- 关键字段候选清单

如果结构观察没完成，不要直接进入业务计算。

### 第 2 步：建立字段映射

使用 [field-dictionary.md](references/field-dictionary.md) 中的标准语义字段。

对每个标准字段记录：

- `source_file`
- `source_sheet`
- `source_column`
- `mapping_status`
  - `exact`
  - `dictionary_verified`
  - `unresolved`
  - `unsupported`
- `evidence`
  - 列名证据
  - 类型证据
  - 样例值证据
  - sheet 角色证据

### 第 3 步：判断主题支持范围

使用 [dimension-requirements.md](references/dimension-requirements.md) 检查每个主题。

输出：

- 支持的主题
- 不支持的主题
- 每个不支持主题缺失的字段
- 是否仅支持年累计、不支持月趋势

### 第 4 步：调用 `data-analysis` 做业务聚合

仅对支持的主题使用 `data-analysis` 执行 SQL 聚合。

SQL 目标包括：

- 指标卡
- 主表格
- 图表底数
- 补充核对表

如果某个指标只能算“年度总额”，不能算“月度趋势”，必须在结果中写明。

### 第 5 步：组装中性报告内容层

使用 [page-themes.md](references/page-themes.md) 和 [output-contract.md](references/output-contract.md) 输出：

- `analysis.json`
- `report_plan.json`
- `mapping_report.md`

注意：

- `report_plan.json` 是报告规划，不是最终 PPT spec
- 页面主题固定，但允许跳过
- 页面标题中不要写死年份或城市，除非这些信息已从数据中明确识别
- 页面内容要给下游渲染提供清晰的重点、颜色强调、表格密度和数值格式建议

### 第 6 步：可选图表与渲染协作

如果用户明确需要图表、HTML、PDF、PPT 等后续介质：

- 先确认 `report_plan.json` 已稳定
- 如果提供了图表制作 skill，基于 `chart_tasks.json` 或 `report_plan.json` 中的图表配置调用
- 再交给具体渲染 skill

## 输出风格要求

使用 [format-and-style-guide.md](references/format-and-style-guide.md) 控制数值格式、表格密度、百分比、小数位和视觉强调建议。

### `analysis.json`

重点记录：

- 指标原值
- 统计口径
- 聚合维度
- 结果表
- 图表底数
- 警告信息

### `report_plan.json`

必须以页面主题为单位，包含：

- `theme_id`
- `title`
- `status`
  - `supported`
  - `partial`
  - `skipped`
- `reason`
- `sections`
  - 指标卡
  - 表格
  - 图表
  - 洞察
  - 口径说明
- `render_hints`
  - 适合表格
  - 适合柱图
  - 适合折线图
  - 不建议绘图

### `mapping_report.md`

必须对人类可读，至少说明：

- 文件结构概况
- 候选主表判断
- 字段映射结果
- 主题支持情况
- 跳过主题原因
- 关键风险

## 参考资料

根据需要按顺序阅读：

1. [workflow-with-data-analysis.md](references/workflow-with-data-analysis.md)
2. [field-dictionary.md](references/field-dictionary.md)
3. [analysis-dimensions.md](references/analysis-dimensions.md)
4. [dimension-requirements.md](references/dimension-requirements.md)
5. [page-themes.md](references/page-themes.md)
6. [format-and-style-guide.md](references/format-and-style-guide.md)
7. [output-contract.md](references/output-contract.md)

## 失败处理

如果文件不像会员运营数据：

- 明确说明原因
- 输出最小 `schema_profile.json`
- 不继续做业务主题计算

如果只支持部分主题：

- 保留支持的主题
- 对不支持的主题标记 `skipped`
- 说明缺失字段和原因

如果某些字段存在歧义：

- 标记 `unresolved`
- 不自动使用
