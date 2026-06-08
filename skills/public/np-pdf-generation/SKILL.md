---
name: np-pdf-generation
description: 使用 HTML/CSS、Playwright/Chromium 和立邦品牌资产生成 PDF 文件。适用于把报告、方案、数据分析、表格内容或 Markdown/HTML 材料制作成立邦集团简报风格 PDF；支持 16:9 横版报告页和 A4 纵版文档页；表格数字默认右对齐。
compatibility:
  tools: ["shell", "filesystem"]
  runtimes: ["node"]
---

# np-pdf-generation

用 HTML/CSS 生成 PDF。默认视觉风格为立邦集团简报模板。

## Resources

- `assets/nippon_style/`：立邦模板背景、logo、页脚条。
- `scripts/render_pdf.mjs`：把 HTML 渲染成 PDF。
- `references/nippon-pdf-style.md`：页面尺寸、布局、颜色、表格规则。生成前先读。

## Dependencies

缺依赖时自行补齐：

```bash
npm install playwright
npx playwright install chromium
```

如果系统已有可用 Chromium，也可让 Playwright 使用现有浏览器。

## Workflow

1. 判断输出方向：`landscape-16x9` 或 `portrait-a4`。
2. 在任务目录中创建 HTML/CSS，并复制 `assets/nippon_style/` 到任务目录。
3. 默认套用立邦 PDF 风格；若用户明确指定其他品牌/模板，则以用户指定风格为准。
4. 内容先排成 HTML 页面，再用 `scripts/render_pdf.mjs` 输出 PDF。
5. 渲染后检查 PDF 页面数量、分页、表格、页眉页脚、图片和文字是否被截断。

## Authoring Rules

- 横版报告页使用 `16:9`，适合汇报、数据看板、业务总结。
- 纵版文档页使用 `A4 portrait`，适合正式报告、长文档、说明书。
- 中文字体默认 `微软雅黑`，回退到系统无衬线字体。
- 文字默认偏大，优先保证投影、打印和截图阅读清晰。
- 背景、logo、页脚条可作为图片层；业务文字、数据和表格必须是 HTML 文本。
- 表格中的数字、金额、百分比和差异值必须右对齐；文本列左对齐。
- 表格不要用截图替代，除非用户只要求视觉复刻且不需要文本可复制。
- 不要在页面上出现制作过程语言，例如“AI 生成”“自动生成”“已验证输出”。

## Render

从 skill 目录运行：

```bash
node scripts/render_pdf.mjs input.html output.pdf --format landscape-16x9
node scripts/render_pdf.mjs input.html output.pdf --format portrait-a4
```

也可以把脚本复制到任务目录后运行。最终交付 PDF、源 HTML/CSS 和必要资产。
