# generate_waterfall_chart — 瀑布图

## 功能概述
展示起点、连续增减项与最终结果之间的累计变化，适合利润桥、收入变动、成本拆解、预算调整等场景。

## 输入字段
### 必填
- `data`: array<object>，每条至少含 `category`（string）与 `value`（number）。`category` 表示步骤名称，`value` 表示该步骤的增减值或节点值，数据顺序即展示顺序。

### 可选
- `data[].isTotal`: boolean，默认 `false`。当某一条记录表示最终结果/总计柱时，必须将该字段设为 `true`，否则接口会把它当成普通增减项继续累加，导致最右侧柱子位置错误。
- `data[].isIntermediateTotal`: boolean，默认 `false`。用于标记中间小计柱；开启后该记录会被作为阶段性累计结果展示。
- `style.backgroundColor`: string，自定义背景色。
- `style.palette`: object，定义瀑布图颜色映射。
- `style.palette.positiveColor`: string，正向增长颜色，合法颜色值。
- `style.palette.negativeColor`: string，负向下降颜色，合法颜色值。
- `style.palette.totalColor`: string，总计柱颜色，合法颜色值。
- `style.texture`: string，默认 `default`，可选 `default`/`rough`。
- `theme`: string，默认 `default`，可选 `default`/`academy`/`dark`。
- `width`: number，默认 `600`。
- `height`: number，默认 `400`。
- `title`: string，默认空字符串。
- `axisXTitle`: string，默认空字符串。
- `axisYTitle`: string，默认空字符串。

## 使用建议
数据应按业务发生顺序排列；正数表示增加，负数表示减少。若用户要表达某个起始状态经过若干变化到达结束状态的桥接过程，建议在 `data` 中显式包含起始节点、变化节点和结束节点，而不是只传中间变化项。推荐结构为：第 1 条记录 = 起始节点；中间记录 = 各项变化贡献；最后 1 条记录 = 结束节点，并在需要将其渲染为总结性柱子时显式传入 `isTotal: true`。若需要阶段性小计，可对对应记录设置 `isIntermediateTotal: true`。如需控制不同类型柱子的颜色，请使用 `style.palette.positiveColor / negativeColor / totalColor`。

## 返回结果
- 返回瀑布图 URL，并随 `_meta.spec` 提供配置详情。
