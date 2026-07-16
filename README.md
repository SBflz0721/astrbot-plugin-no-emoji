# AstrBot 插件：去表情符号 (astrbot_plugin_no_emoji)

![License](https://img.shields.io/github/license/SBflz0721/astrbot-plugin-no-emoji?style=flat-square)
![AstrBot](https://img.shields.io/badge/AstrBot-plugin-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.9+-blue?style=flat-square)

在机器人 **发送回复消息之前**，自动检测并移除消息内容中的所有 emoji（Unicode emoji 与自定义 emoji），
**保持消息其它内容不变**，仅删除 emoji 部分。

## 功能特性

- **Unicode emoji 全覆盖**：表情符号、符号与 pictographs、补充符号、旗帜、杂项符号/Dingbats、变体选择符（️ 让符号变 emoji）、肤色修饰符（🏻🏼🏽🏾🏿）、ZWJ 组合序列（如 👨‍👩‍👧）、键帽组合（2️⃣）等。
- **自定义 emoji**：
  - 短代码形式 `:smile:` / `:custom_emoji:`；
  - Discord 形式 `<:name:1234567890>` / `<a:name:1234567890>`；
  - 平台表情/贴纸类消息组件（`face` / `emoji` / `sticker` 等）整体剔除。
- **非侵入**：仅过滤 `on_decorating_result` 钩子里的待发送消息链，不动用户发来的消息，也不影响其它插件。
- **兜底安全**：过滤过程任何异常都会被捕获并跳过，绝不会阻断正常消息的发送。

## 安装

### 方式一：命令行克隆（推荐）

进入 AstrBot 的插件目录，直接把本仓库克隆进去：

```bash
cd <AstrBot>/data/plugins
git clone https://github.com/SBflz0721/astrbot-plugin-no-emoji.git
```

> 注意目录名需保持为 `astrbot-plugin-no-emoji/`（与插件 id `astrbot_plugin_no_emoji` 对应）。

### 方式二：手动复制

将本插件目录（`astrbot-plugin-no-emoji/`）整体放入 AstrBot 的插件目录：

```
<AstrBot>/data/plugins/astrbot-plugin-no-emoji/
```

放入后在 AstrBot 管理面板启用插件，无需重启也可热加载。

目录结构：

```
astrbot-plugin-no-emoji/
├── main.py            # 插件入口（Star 子类 + on_decorating_result 钩子）
├── emoji_filter.py    # 纯粹的 emoji 过滤逻辑（无 AstrBot 依赖，可单独测试）
├── metadata.yaml      # 插件元信息
├── _conf_schema.json  # 管理面板可视化配置 Schema
└── README.md
```

放入后在 AstrBot 管理面板启用插件，无需重启也可热加载。

## 配置

在管理面板的插件配置中可调整（均有默认值，开箱即用）：

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `remove_unicode_emoji` | `true` | 移除 Unicode emoji |
| `remove_custom_shortcode` | `true` | 移除 `:name:` 短代码自定义 emoji |
| `remove_discord_custom` | `true` | 移除 Discord `<:name:id>` 自定义 emoji |
| `remove_emoji_components` | `true` | 整体剔除表情/贴纸类消息组件 |
| `clean_whitespace` | `true` | 移除 emoji 后顺手压缩残留空白；关闭则严格只删 emoji、保留原始空白 |

## 工作原理

AstrBot 在「发送消息前」会触发 `on_decorating_result` 钩子。插件在此：

1. 取 `result = event.get_result()`，拿到待发送的消息链 `result.chain`；
2. 遍历每个消息组件：
   - 表情/贴纸类组件（`face`/`emoji`/`sticker`/`custom_emoji`）→ 整体剔除；
   - 纯文本组件 `Plain` → 对其 `text` 执行 emoji 移除；
   - 其它组件（图片、@、回复等）→ 原样保留；
3. 将过滤后的消息链原地写回，随后由 AstrBot 正常发送。

因此最终发出的文本中不含任何 emoji，其余内容与结构完全不变。

## 测试过滤逻辑

`emoji_filter.py` 不依赖 AstrBot，可单独验证正则效果：

```bash
python emoji_filter.py
```

会输出若干用例（中文 emoji、ZWJ 组合、肤色修饰、键帽、短代码、Discord 表情、应保留的箭头/方块等）的通过情况。

## 备注 / 可扩展点

- 当前 Unicode 范围聚焦「明确属于 emoji 语义」的码段，**有意不**覆盖 `→`、几何方块 `■` 等常被当作文本符号使用的图形，避免误伤。
  如需把这些也一并移除，在 `emoji_filter.py` 的 `_UNICODE_EMOJI_PATTERN` 中补充对应区间即可（如 `\U00002190-\U000021FF`、`\U000025A0-\U000025FF`、`\U00002300-\U000023FF`、`\U00002460-\U000024FF`）。
- 若你的平台使用其它自定义 emoji 文本格式（如 Telegram `<tg-emoji ...>`），可在 `emoji_filter.py` 增加对应正则后接入 `strip_emoji`。

## 开源协议

本项目基于 [MIT License](LICENSE) 开源。欢迎 Fork、修改与二次分发。

## 仓库

- GitHub：<https://github.com/SBflz0721/astrbot-plugin-no-emoji>
- 问题反馈：<https://github.com/SBflz0721/astrbot-plugin-no-emoji/issues>
