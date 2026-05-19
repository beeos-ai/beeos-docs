#!/usr/bin/env python3
"""Create zh/ stubs for any en/ page that doesn't yet have a Chinese translation.

Each stub renders a translation-in-progress note plus a link to the English
original. This lets `mintlify build` pass with a fully nav-resolved tree
while we land high-quality manual translations incrementally.
"""
from __future__ import annotations

from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parent.parent

# (en_path, zh_path, title_zh, description_zh)
STUBS = [
    ("guides/choosing-a-protocol.mdx", "zh/guides/choosing-a-protocol.mdx",
     "选择协议", "在 OpenAPI、A2A、MCP 之间做出选择 —— 翻译进行中。"),
    ("guides/calling-agents.mdx", "zh/guides/calling-agents.mdx",
     "调用智能体", "三种调用模式（同步、流式、异步任务）—— 翻译进行中。"),
    ("guides/conversations.mdx", "zh/guides/conversations.mdx",
     "会话", "长生命周期多轮对话 —— 翻译进行中。"),
    ("guides/webhooks.mdx", "zh/guides/webhooks.mdx",
     "Webhook", "HMAC 签名的终态回调 + 重试 + 审计日志 —— 翻译进行中。"),
    ("guides/streaming.mdx", "zh/guides/streaming.mdx",
     "流式", "三个协议接入面的 SSE 流式 —— 翻译进行中。"),
    ("guides/agent-author-quickstart.mdx", "zh/guides/agent-author-quickstart.mdx",
     "智能体作者快速入门", "agent_reply 的五条铁则 —— 翻译进行中。"),
    ("architecture/public-overview.mdx", "zh/architecture/public-overview.mdx",
     "公开架构总览", "四个公开 BeeOS 域名及请求路径 —— 翻译进行中。"),
    ("reference/errors.mdx", "zh/reference/errors.mdx",
     "错误参考", "所有 error.code 及恢复建议 —— 翻译进行中。"),
    ("sdks/migration.mdx", "zh/sdks/migration.mdx",
     "SDK 迁移", "@beeos-ai/sdk 版本间升级路径 —— 翻译进行中。"),
    ("sdks/changelog.mdx", "zh/sdks/changelog.mdx",
     "SDK 更新日志", "OpenAPI 契约和生成 SDK 的版本变更 —— 翻译进行中。"),
]


TEMPLATE = """---
title: {title}
description: "{description}"
---

<Note>
  本页中文翻译还在进行中。请暂时查看
  [英文原版](/{en_route})。

  This page is being translated. The English version is available at
  [/{en_route}](/{en_route}).
</Note>
"""


def main() -> int:
    written = 0
    for en_path, zh_path, title, desc in STUBS:
        zh_file = DOCS_ROOT / zh_path
        if zh_file.exists():
            print(f"  exists: {zh_path}")
            continue
        zh_file.parent.mkdir(parents=True, exist_ok=True)
        en_route = en_path.removesuffix(".mdx")
        zh_file.write_text(
            TEMPLATE.format(title=title, description=desc, en_route=en_route),
            encoding="utf-8",
        )
        print(f"  stubbed: {zh_path}")
        written += 1
    print()
    print(f"DONE. Wrote {written} stub(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
