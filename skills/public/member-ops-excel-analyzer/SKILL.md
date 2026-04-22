---
name: member-ops-excel-analyzer
description: 根据固定模板的会员运营 Excel 工作簿，自动完成会员运营分析、计算页面级指标、生成结构化汇报内容与 slide spec。适用于用户只上传这套固定模板 Excel，希望自动产出一套标准化会员运营汇报内容，并把结果进一步交给 PowerPoint/PPT skill 制作正式 PPT 的场景。只要用户上传这类固定模板工作簿，或明确提出“根据这个 Excel 生成运营汇报/PPT 内容”，就应优先使用本 skill。
---

# 会员运营 Excel 分析

本 skill 负责把固定模板 Excel 解析成可交付的内容层，而不是自己完成最终 `.pptx`。
它不依赖任何原始 PPT、历史汇报稿或人工补充模板。

## 核心职责

1. 校验上传文件是否符合固定模板
2. 识别关键 sheet 和字段
3. 按既定口径完成分析计算
4. 生成：
   - `analysis.json`
   - `slide_spec.json`
   - 必要时生成简短页面说明
5. 将 `slide_spec.json` 交给现有的 PowerPoint skill 继续做 PPT

## 不做的事

- 不依赖原 PPT 中的数值或结构
- 不猜测 Excel 中无法闭环的数据
- 不在本 skill 内直接完成最终 PPT 制作

## 工作流程

### 1. 先检查模板

优先运行：

```bash
python3 skills/member-ops-excel-analyzer/scripts/inspect_workbook.py --input "<excel-path>"
```

如果关键 sheet 或字段缺失：

- 明确告诉用户缺什么
- 不要硬算

### 2. 生成分析结果

运行：

```bash
python3 skills/member-ops-excel-analyzer/scripts/build_analysis_json.py \
  --input "<excel-path>" \
  --output "<analysis-json-path>"
```

输出结果必须只包含 Excel 可闭环的内容。
如果 Excel 里没有足够依据，就不要用外部记忆补全页面。

### 3. 生成 slide spec

运行：

```bash
python3 skills/member-ops-excel-analyzer/scripts/build_slide_spec.py \
  --analysis "<analysis-json-path>" \
  --output "<slide-spec-path>"
```

`slide_spec.json` 是给 PPT skill 的标准输入，不是给终端用户直接看的最终产物。

### 4. 交给 PPT skill

当用户要求正式 PPT 时：

- 将 `slide_spec.json` 交给现有的 PowerPoint/PPT skill
- 本 skill 不直接写 `.pptx`

## 固定页面清单

默认输出以下 11 页标准汇报页：

1. 封面
2. 分析框架
3. 会员概况
4. 一物一码来源已挂靠会员
5. 一物一码待挂靠会员
6. 会员消费
7. 上门基检
8. 会员日
9. 会员分层与风险池
10. 门店经营机会优先级
11. 转化路径与运营建议

## 数据原则

- `全部会员` 是核心底表
- 第 3、6、8、9、11 页优先使用 `全部会员`
- `门店别` 主要用于门店状态、门店汇总补充、可控店筛选
- `一物一码来源已挂靠会员分析` 用于已挂靠专题
- `扫码>=50游离会员` 用于待挂靠专题
- `每月会员日参与名单` 用于会员日月度趋势
- 这套页面是标准输出 deck，不要求与任何既有 PPT 页码或内容一一对应

## 风格要求

- 所有输出内容必须适合后续转成 PPT
- 每页内容要控制在可汇报密度内
- 优先输出页面模块化结构：
  - 标题
  - 副标题
  - 指标卡
  - 图表数据
  - 表格数据
  - 页面洞察
  - 口径说明

## 参考资料

根据任务需要按需阅读：

- [template-spec.md](references/template-spec.md)
- [metric-definitions.md](references/metric-definitions.md)
- [slide-outline.md](references/slide-outline.md)

## 输出要求

### analysis.json

必须包含：

- `meta`
- `workbook_summary`
- `pages`

其中 `pages` 下至少要有：

- `member_overview`
- `qr_attached`
- `qr_pending`
- `consumption`
- `home_visit`
- `member_day`
- `segment_risk`
- `store_priority`
- `conversion_path`

### slide_spec.json

每页必须至少包含：

- `slide_id`
- `title`
- `subtitle`
- `layout`
- `kpis`
- `charts`
- `tables`
- `insights`
- `notes`

## 失败处理

如果模板结构不完整：

- 输出清晰错误
- 指明缺失的 sheet 或字段
- 不继续生成 slide spec

如果只有部分页面不可闭环：

- 继续生成可计算页面
- 在对应页面 notes 中明确标注限制
