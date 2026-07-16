# -*- coding: utf-8 -*-
"""
emoji_filter.py — 纯粹的 emoji 过滤逻辑（不依赖 AstrBot，便于单独测试）。

覆盖：
  1. Unicode emoji：各 emoji 平面、ZWJ 组合序列（如 👨‍👩‍👧）、
     肤色修饰符（🏻🏼🏽🏾🏿）、变体选择符（️，含 U+FE0F 让符号变成 emoji）、
     键帽组合（2️⃣）等。
  2. 自定义 emoji 文本表示：
     - 短代码形式 :smile: / :custom_emoji:
     - Discord 形式 <:name:1234567890> / <a:name:1234567890>
"""

import re

# ----------------------------------------------------------------------------
# 1) Unicode emoji
# 选取「明确属于 emoji 语义」的范围，避免误伤普通标点、字母、CJK、
# 以及 ⬅ ➡ 这类在 2190-21FF / 25A0-25FF 中常被当作文本符号使用的图形。
# ----------------------------------------------------------------------------
_UNICODE_EMOJI_PATTERN = re.compile(
    "[\U0001F000-\U0001FAFF"   # 麻将/扑克/象棋、表情符号、符号与 pictographs、补充符号
    "\U00002600-\U000027BF"    # 杂项符号与 Dingbats（☀ ★ ☎ ✔ ➡ ♥ …）
    "\U00002B00-\U00002BFF"    # 杂项符号与箭头（⭐ ⬛ ⬆ …）
    "\U0000FE00-\U0000FE0F"    # 变体选择符（含 U+FE0F 使符号变成 emoji）
    "\U0001F3FB-\U0001F3FF"    # 肤色修饰符
    "\U0000200D"               # 零宽连字 ZWJ（👨‍👩‍👧 等组合 emoji 的粘合剂）
    "\U000020E3"               # 键帽组合符（2️⃣ 的 ⃣）
    "]",
    re.UNICODE,
)

# ----------------------------------------------------------------------------
# 2) 自定义 emoji（文本形式）
# ----------------------------------------------------------------------------
# 短代码：:smile:  :custom_emoji:  :thumbs_up:
_CUSTOM_SHORTCODE_PATTERN = re.compile(r":[A-Za-z0-9_+\-]+:", re.UNICODE)

# Discord 自定义表情：<:name:1234567890> 或动画版 <a:name:1234567890>
_DISCORD_CUSTOM_PATTERN = re.compile(r"<a?:\w+:\d+>", re.UNICODE)


def strip_emoji(
    text: str,
    remove_unicode: bool = True,
    remove_shortcode: bool = True,
    remove_discord: bool = True,
    clean_whitespace: bool = True,
) -> str:
    """移除文本中的 emoji，保留其余内容不变。

    Args:
        text: 待处理文本。
        remove_unicode: 是否移除 Unicode emoji。
        remove_shortcode: 是否移除 :shortcode: 形式的自定义 emoji。
        remove_discord: 是否移除 Discord <:name:id> 形式的自定义 emoji。
        clean_whitespace: 移除 emoji 后是否顺手把多余的空白（连续空格/换行）
                          压缩为单个空格并去掉首尾空白。设为 False 则严格只删
                          emoji、保留原始空白（可能在原 emoji 处留下空格）。

    Returns:
        处理后的文本。
    """
    if not text:
        return text

    if remove_discord:
        text = _DISCORD_CUSTOM_PATTERN.sub("", text)
    if remove_shortcode:
        text = _CUSTOM_SHORTCODE_PATTERN.sub("", text)
    if remove_unicode:
        text = _UNICODE_EMOJI_PATTERN.sub("", text)

    if clean_whitespace:
        # 仅清理因删除 emoji 产生的多余空白，不影响原文正常的单空格/换行
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"\n[ \t]+", "\n", text)
        text = text.strip()

    return text


# 便于直接 `python emoji_filter.py` 跑一组自测
if __name__ == "__main__":
    cases = [
        ("你好😊世界", "你好世界"),
        ("I love 🍎 and 🚀!", "I love and !"),
        ("家庭👨‍👩‍👧合照", "家庭合照"),
        ("皮肤🧑🏽‍🚀测试", "皮肤测试"),
        ("分数2️⃣来了", "分数2来了"),
        ("请投票:thumbs_up:谢谢", "请投票谢谢"),
        ("看看<:rocket:1234567890>发射", "看看发射"),
        ("普通中文与 English 文字保持不变。", "普通中文与 English 文字保持不变。"),
        ("箭头→和方块■应保留", "箭头→和方块■应保留"),
    ]
    for src, expected in cases:
        got = strip_emoji(src)
        status = "OK " if got == expected else "FAIL"
        print(f"[{status}] {src!r} -> {got!r}  (期望 {expected!r})")
