---
name: np-ppt-generation
description: 使用 PptxGenJS、配套 helper、立邦品牌资产和渲染校验脚本生成或编辑可编辑 PowerPoint（`.pptx`）演示文稿。每次触发本技能时，先重新读取本目录 `SKILL.md`，以当前文件内容为准。适用于新建/修改 PPT、把材料转成 PPT、复刻参考稿、生成业务汇报或数据汇报；默认输出立邦集团简报模板风格，除非用户明确指定其他品牌或模板。
compatibility:
  tools: ["shell", "filesystem"]
  runtimes: ["node", "python"]
---

# np-ppt-generation

用 JavaScript + `pptxgenjs` 构建或修改可编辑 PowerPoint。默认视觉风格为立邦集团简报模板。

## Resources

- `assets/pptxgenjs_helpers/`：文本、图片、SVG、LaTeX、代码块、布局和校验 helper。
- `assets/nippon_style/`：立邦模板背景、logo、页脚条。
- `scripts/render_slides.py`：PPT/PDF 渲染为 PNG。
- `scripts/slides_test.py`：溢出检测。
- `scripts/create_montage.py`：生成缩略总览图。
- `scripts/detect_font.py`：字体检测。
- `scripts/check_pptx_package.py`：纯 Python PPTX 包结构检查，用于发现可能触发 Windows PowerPoint 修复提示的问题。
- `references/pptxgenjs-helpers.md`：helper API 参考。
- `references/nippon-style-guide.md`：立邦模板风格参数。生成立邦风格 PPT 前先读。

## Dependencies

缺依赖时自行补齐，不要直接放弃。

Node:

```bash
npm install pptxgenjs skia-canvas linebreak fontkit prismjs mathjax-full
```

Python:

```bash
python3 -m pip install pdf2image Pillow python-pptx numpy
```

System tools:

- `soffice` / LibreOffice
- `pdfinfo`
- `pdftoppm`
- `fc-list`

`mathjax-full` 优先使用子路径导入，例如 `mathjax-full/js/mathjax.js`，不要默认 `require("mathjax-full")`。

## Workflow

1. 判断任务类型：新建 deck、修改 deck、材料转 PPT，或复刻参考稿。
2. 在当前任务下创建独立工作目录。
3. 复制 `assets/pptxgenjs_helpers/` 和 `assets/nippon_style/` 到工作目录，从本地副本导入。
4. 使用 `pptxgenjs` 生成或修改 `.pptx`。
5. 默认套用立邦模板风格；若用户明确给出其他品牌/参考模板，则以用户指定风格为准。
6. 按 Windows-safe authoring rules 生成；不要依赖事后安装 LibreOffice 修复。
7. 生成后先运行 `check_pptx_package.py`，再渲染成 PNG，逐页检查；页面密集或边界紧时运行溢出和字体检测。
8. 修正问题后重新检查和渲染复核。

## Editable Layer Rules

- 标题、正文、日期、页码、KPI、表格文字、图表标签、图例、注释和结论必须保持可编辑。
- 表格中的数字、金额、百分比和差异值必须右对齐；文本列保持左对齐。
- 品牌背景、logo、页脚条、装饰纹理可作为图片层。
- 不要把业务数据、用户可能修改的文本或图表烘进整页截图。
- 不要在页面上出现制作过程语言，例如“AI 生成”“自动生成”“可编辑 PPT”“已验证输出”。
- 列表使用 PowerPoint bullet 配置，不要手打项目符号。
- 需要公式时再使用 `latexToSvgDataUri()`。

## Nippon Default Style

默认风格为立邦模板。详细参数见 `references/nippon-style-guide.md`。

核心规则：

- 页面尺寸：16:9 wide。
- 中文字体：`微软雅黑`。
- 主色：立邦深蓝 `#00378A` / `#00388B`。
- 正文页：白底、左上 logo、深蓝标题、底部品牌口号条、右下页码。
- 封面页：使用 `cover-white-left-blue.jpeg`。
- 章节/过渡页：使用 `blue-section-background.jpeg`。
- 结束页：使用 `closing-slogan-background.jpeg`。
- 正文页底部固定使用 `footer-slogan-bar.png`；不要重绘或改写口号条，除非用户要求。

## Build Guardrails

- 显式设置 `LAYOUT_WIDE` 和主题字体。
- 图片放置优先使用 helper，不要随手硬算裁切。
- Windows-safe authoring rules：
  - 优先使用本地 PNG/JPEG 文件路径作为图片源；避免把重复 logo、footer、背景转成 data URI 或临时文件。
  - 同一品牌图片在所有页面复用同一个文件路径。
  - 不需要讲稿时不要生成 notes。
  - 不手工改写 PPTX 内部 XML、关系文件、Content Types、docProps 或 master/layout。
  - 避免把 SVG 直接作为最终 PPT 图片源；需要矢量图时优先转为 PNG 或用 PowerPoint 原生 shape 重建。
  - 不写自定义属性、保护标签、外部链接、嵌入对象、OLE、视频或宏，除非用户明确要求。
  - 表格、文本、基础图形和简单图表优先使用 PptxGenJS 原生 API。
- 生成后必须运行 `check_pptx_package.py`。若出现 ERROR，不能交付；先调整生成代码并重建。WARN 需在最终说明中记录，能消除则消除。
- 对新建或大改 deck，源码中保留：
  - `warnIfSlideHasOverlaps(slide, pptx)`
  - `warnIfSlideElementsOutOfBounds(slide, pptx)`
- 如果 overlap 是背景/容器与内部内容的预期重叠，在源码旁写短注释说明。

## Render And Verify

只要环境支持，交付前执行：

```bash
python3 scripts/check_pptx_package.py deck.pptx
python3 scripts/render_slides.py deck.pptx --output_dir rendered
python3 scripts/create_montage.py --input_dir rendered --output_file montage.png
python3 scripts/slides_test.py deck.pptx
python3 scripts/detect_font.py deck.pptx --json
```

必须逐页查看渲染图；不能只看命令成功或 montage。记录是否完成渲染复核；如果没完成，记录缺哪一步。
