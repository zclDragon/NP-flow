# 立邦 PDF 风格指南

用于生成默认立邦集团简报风格 PDF。

## Assets

资产目录：`assets/nippon_style/`

- `cover-white-left-blue.jpeg`：横版封面背景。
- `footer-slogan-bar.png`：横版内容页底部品牌口号条。
- `nippon-logo.png`：内容页左上 logo。
- `blue-section-background.jpeg`：横版章节/过渡页背景。
- `closing-slogan-background.jpeg`：横版结束页背景。

## Page Formats

- `landscape-16x9`：`13.333in x 7.5in`。
- `portrait-a4`：`210mm x 297mm`。
- 横版用于简报页；纵版用于长文档。

## Typography

- 字体：`"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif`
- 横版标题：`28-34pt`
- 横版正文：`13-16pt`
- 纵版一级标题：`22-28pt`
- 纵版正文：`11-13pt`
- 表格文字：`10.5-12pt`

## Colors

- 深蓝：`#00378A`、`#00388B`、`#0F318A`
- 数据蓝：`#006ECF`、`#0753B8`
- 亮蓝：`#1E6DC1`、`#3176BF`
- 强调红：`#E60012`、`#C51A44`
- 强调橙黄：`#FF6A00`、`#FFC000`
- 弱线/浅底：`#E6EEF7`、`#D9E6F5`
- 背景：`#FFFFFF`

## Landscape Layouts

### Cover

- 铺满 `cover-white-left-blue.jpeg`。
- 标题放右侧白色区域，避开左侧蓝色曲面和右下角橙红曲线。

### Content

- 白底。
- 左上放 `nippon-logo.png`，宽约 `0.70in`。
- 标题从 logo 右侧开始，深蓝。
- 底部贴边铺满 `footer-slogan-bar.png`。
- 页码放右下角页脚条内，白字右对齐。
- 主内容区避开页脚，底部至少留 `0.55in`。

### Section / Closing

- 章节页铺满 `blue-section-background.jpeg`，只放少量白字。
- 结束页铺满 `closing-slogan-background.jpeg`，不叠加大段文字。

## Portrait Layout

- A4 白底，顶部放 logo 和深蓝标题线。
- 页边距建议：上 `18mm`，右 `16mm`，下 `18mm`，左 `16mm`。
- 页脚可使用细蓝线 + 页码；不要强行使用横版 footer bar。
- 长表格允许跨页，但表头需要重复显示。

## Tables

- 表头：深蓝底白字。
- 边框：细线，优先 `#D9E6F5`。
- 数字、金额、百分比、差异值：右对齐。
- 文本列：左对齐。
- 合计/小计行：浅蓝底或深蓝文字加粗。
- 负值或异常值可用 `#C51A44`。

## CSS Hints

```css
td.num, th.num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

td.text, th.text {
  text-align: left;
}

thead {
  display: table-header-group;
}
```
