# np-ppt-generation

这是一个基于 `pptxgenjs` 的可复用 PPT 生成 skill。

## 里面包含什么

- 中文版 `SKILL.md`
- `package.json`：列出推荐安装的 Node 依赖
- `assets/pptxgenjs_helpers/`
- `scripts/`：渲染、校验、拼图、字体检查等脚本
- `references/`：helper 使用说明

## 使用方式

这个 skill 默认假设环境总体可用，但不保证依赖已经齐全。缺依赖时，agent 应自己补齐。

常见 Node 安装命令：

```bash
npm install pptxgenjs skia-canvas linebreak fontkit prismjs mathjax-full
```

常见 Python 安装命令：

```bash
python3 -m pip install pdf2image Pillow python-pptx numpy
```

常见系统命令：

- `soffice`
- `pdfinfo`
- `pdftoppm`
- `fc-list`

## 关于 MathJax

不要默认写成：

```js
require("mathjax-full")
```

更稳的方式是使用子路径：

- `mathjax-full/js/mathjax.js`
- `mathjax-full/js/input/tex.js`
- `mathjax-full/js/output/svg.js`
