# -*- coding: utf-8 -*-
"""
AstrBot 插件：astrbot_plugin_no_emoji
功能：在机器人「发送回复消息之前」，自动检测并移除消息内容中的所有 emoji
      （Unicode emoji 与自定义 emoji），其余内容保持不变。

实现要点：
  - 使用 @filter.on_decorating_result() 钩子，在消息真正发出前介入。
  - 遍历 event.get_result().chain（消息链），对文本组件 Plain 执行 emoji 移除；
    对平台表情类组件（如 face / emoji / sticker）整体剔除。
  - 不改动消息的其它结构与内容，仅删除 emoji 部分。
  - 过滤逻辑集中在 emoji_filter.py，本文件只负责接入 AstrBot 事件总线。
"""

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 纯逻辑模块，无任何 AstrBot 依赖，便于单独测试。
# 多重兜底导入：兼容 AstrBot 以包形式加载、独立运行、以及直接加入 sys.path 等场景。
try:
    from .emoji_filter import strip_emoji
except ImportError:
    try:
        from data.plugins.astrbot_plugin_no_emoji.emoji_filter import strip_emoji
    except ImportError:
        from emoji_filter import strip_emoji

# 需要整体移除的「表情类」消息组件 type（小写比对）。
# 这些通常是各平台自定义的表情/贴纸，不属于纯文本，只能按组件整体删除。
_EMOJI_COMPONENT_TYPES = {"face", "emoji", "sticker", "custom_emoji"}


@register(
    "astrbot_plugin_no_emoji",
    "WorkBuddy",
    "在机器人发送回复前，自动移除消息中的所有 emoji（Unicode 与自定义 emoji）。",
    "1.0.0",
    "https://github.com/SBflz0721/astrbot-plugin-no-emoji",
)
class NoEmojiPlugin(Star):
    def __init__(self, context: Context, config: dict | None = None):
        super().__init__(context)
        self.config = config or {}
        self._refresh_config()

    def _refresh_config(self):
        cfg = self.config
        self.remove_unicode = bool(cfg.get("remove_unicode_emoji", True))
        self.remove_shortcode = bool(cfg.get("remove_custom_shortcode", True))
        self.remove_discord = bool(cfg.get("remove_discord_custom", True))
        self.remove_components = bool(cfg.get("remove_emoji_components", True))
        self.clean_whitespace = bool(cfg.get("clean_whitespace", True))

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        """消息发送前的装饰钩子：在此移除 emoji。

        注意：此钩子只能装饰 event.get_result().chain，不能使用 yield 发送消息。
        """
        try:
            result = event.get_result()
            chain = getattr(result, "chain", None)
            if not chain:
                return

            new_chain = []
            for comp in chain:
                # 整体剔除表情/贴纸类组件（自定义 emoji 的常见载体）
                comp_type = (getattr(comp, "type", "") or "").lower()
                if self.remove_components and comp_type in _EMOJI_COMPONENT_TYPES:
                    logger.debug(f"[no_emoji] 移除表情组件: {comp_type}")
                    continue

                # 仅对纯文本组件做 emoji 文本过滤
                text = getattr(comp, "text", None)
                if text is None:
                    new_chain.append(comp)
                    continue

                stripped = strip_emoji(
                    text,
                    remove_unicode=self.remove_unicode,
                    remove_shortcode=self.remove_shortcode,
                    remove_discord=self.remove_discord,
                    clean_whitespace=self.clean_whitespace,
                )

                # 过滤后为空文本则丢弃该组件，避免残留空段
                if stripped == "":
                    continue

                comp.text = stripped
                new_chain.append(comp)

            # 原地替换消息链（与官方文档中 chain.append(...) 的写法一致）
            try:
                chain[:] = new_chain
            except (TypeError, AttributeError):
                result.chain = new_chain

        except Exception as e:  # 兜底：过滤失败绝不能阻断正常消息发送
            logger.warning(f"[no_emoji] 过滤 emoji 时出错（已跳过本次过滤）：{e}")
