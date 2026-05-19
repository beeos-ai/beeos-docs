#!/usr/bin/env python3
"""Port docs/*.md sources into beeos-docs/*.mdx with link rewrites + frontmatter.

This is a one-shot tool for the v2 docs roadmap. It is NOT a maintained
sync pipeline — once the MDX content is hand-tuned, this script's role
ends. Future docs/ updates are merged into beeos-docs by hand to avoid
clobbering manual MDX-only polish.

Usage:
  python3 scripts/port-md-to-mdx.py
  python3 scripts/port-md-to-mdx.py --check   # dry-run, prints diffs

The mapping table below is the single source of truth for source→target
file routes.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # openagent/
DOCS_ROOT = REPO_ROOT / "docs"
TARGET_ROOT = Path(__file__).resolve().parent.parent  # beeos-docs/

GITHUB_BLOB = "https://github.com/beeos-ai/openagent/blob/main"


@dataclass(frozen=True)
class Port:
    src: str  # relative to docs/
    dst: str  # relative to beeos-docs/
    title: str
    description: str


# Mapping table — keep in sync with plan §2b
PORTS = [
    Port(
        "guides/auth-api-keys.md",
        "authentication.mdx",
        "Authentication & API Keys",
        "Credentials accepted by every BeeOS public surface — User JWT, oag_ User API Keys, bak_ Agent API Keys, and OAuth 2.1.",
    ),
    Port(
        "guides/a2a-external.md",
        "a2a/overview.mdx",
        "A2A Gateway",
        "Agent-to-Agent JSON-RPC protocol entry at a2a.beeos.ai — agent cards, tasks, streaming, and optional REST invoke.",
    ),
    Port(
        "guides/mcp-gateway.md",
        "mcp/overview.mdx",
        "MCP Gateway",
        "Model Context Protocol entry at mcp.beeos.ai — tools/list, tools/call, OAuth 2.1 + PKCE for spec-compliant clients.",
    ),
    Port(
        "guides/calling-agents.md",
        "guides/calling-agents.mdx",
        "Calling Agents",
        "Three invocation modes — synchronous blocking, streaming SSE, and asynchronous tasks — across OpenAPI, A2A, and MCP.",
    ),
    Port(
        "guides/conversations.md",
        "guides/conversations.mdx",
        "Conversations",
        "Long-lived multi-turn dialogs with the agent. Compare against tasks (single-shot) and pick the right primitive.",
    ),
    Port(
        "guides/webhooks.md",
        "guides/webhooks.mdx",
        "Webhooks",
        "Receive terminal-state task notifications with HMAC-signed payloads, exponential-backoff retry, and audit log.",
    ),
    Port(
        "guides/streaming.md",
        "guides/streaming.mdx",
        "Streaming",
        "SSE streaming across all three protocol surfaces — connection rules, reconnect with since cursor, and frame shapes.",
    ),
    Port(
        "guides/choosing-a-protocol.md",
        "guides/choosing-a-protocol.mdx",
        "Choosing a Protocol",
        "Decide between OpenAPI (platform REST), A2A (agent-to-agent), and MCP (model-context tools) for a given integration.",
    ),
    Port(
        "guides/agent-author-quickstart.md",
        "guides/agent-author-quickstart.mdx",
        "Agent Author Quickstart",
        "Five rules every agent must follow to reply correctly through the BeeOS message bus.",
    ),
    Port(
        "guides/sdk-migration.md",
        "sdks/migration.mdx",
        "SDK Migration",
        "Upgrade paths between @beeos-ai/sdk versions (0.3.x → 0.4.x and beyond), plus hand-rolled HTTP migration recipes.",
    ),
    Port(
        "architecture/public-overview.md",
        "architecture/public-overview.mdx",
        "Public Architecture Overview",
        "The four public BeeOS hosts (openapi, a2a, mcp, agent) and how requests flow through each into the control plane.",
    ),
    Port(
        "reference/errors.md",
        "reference/errors.mdx",
        "Error Reference",
        "Every error.code returned by the BeeOS public surfaces, the HTTP status that wraps it, and the recovery hint.",
    ),
    Port(
        "CHANGELOG.md",
        "sdks/changelog.mdx",
        "SDK Changelog",
        "Versioned changes to the OpenAPI contract and the generated @beeos-ai/sdk and github.com/beeos-ai/sdk-go SDKs.",
    ),
]


# Rewrites from `./relative.md` and `../relative.md` to Mintlify routes
SAME_DIR_TO_ROUTE = {
    # docs/guides/foo.md → from another file in docs/guides/
    "auth-api-keys.md": "/authentication",
    "a2a-external.md": "/a2a/overview",
    "mcp-gateway.md": "/mcp/overview",
    "calling-agents.md": "/guides/calling-agents",
    "conversations.md": "/guides/conversations",
    "webhooks.md": "/guides/webhooks",
    "streaming.md": "/guides/streaming",
    "choosing-a-protocol.md": "/guides/choosing-a-protocol",
    "agent-author-quickstart.md": "/guides/agent-author-quickstart",
    "sdk-migration.md": "/sdks/migration",
}

# `../guides/foo.md` / `../reference/foo.md` / `../architecture/foo.md`
PARENT_DIR_TO_ROUTE = {
    "guides/auth-api-keys.md": "/authentication",
    "guides/a2a-external.md": "/a2a/overview",
    "guides/mcp-gateway.md": "/mcp/overview",
    "guides/calling-agents.md": "/guides/calling-agents",
    "guides/conversations.md": "/guides/conversations",
    "guides/webhooks.md": "/guides/webhooks",
    "guides/streaming.md": "/guides/streaming",
    "guides/choosing-a-protocol.md": "/guides/choosing-a-protocol",
    "guides/agent-author-quickstart.md": "/guides/agent-author-quickstart",
    "guides/sdk-migration.md": "/sdks/migration",
    "reference/errors.md": "/reference/errors",
    "architecture/public-overview.md": "/architecture/public-overview",
    "CHANGELOG.md": "/sdks/changelog",
}


def _route_for_same_dir(name_with_anchor: str) -> str | None:
    """Map `./foo.md#anchor` → `/guides/foo#anchor`."""
    m = re.match(r"([^#]+\.md)(#.*)?$", name_with_anchor)
    if not m:
        return None
    fname, anchor = m.group(1), m.group(2) or ""
    base = SAME_DIR_TO_ROUTE.get(fname)
    if not base:
        return None
    return f"{base}{anchor}"


def _route_for_parent_dir(path_with_anchor: str) -> str | None:
    """Map `../guides/foo.md#anchor` → `/guides/foo#anchor`."""
    m = re.match(r"([^#]+\.md)(#.*)?$", path_with_anchor)
    if not m:
        return None
    fname, anchor = m.group(1), m.group(2) or ""
    base = PARENT_DIR_TO_ROUTE.get(fname)
    if not base:
        return None
    return f"{base}{anchor}"


# Patterns
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def rewrite_link(target: str) -> str:
    """Rewrite a single markdown link target (the inside of `](...)`)."""
    # absolute or non-relative — pass through
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return target

    # Normalize `./../` → `../` (sloppy author shorthand)
    if target.startswith("./../"):
        target = target[2:]

    # ./guides/foo.md (e.g. from docs/CHANGELOG.md referencing siblings of guides/)
    # — same logic as ../guides/foo.md from inside docs/guides/
    if target.startswith("./guides/") or target.startswith("./reference/") or target.startswith("./architecture/"):
        inner = target[2:]
        route = _route_for_parent_dir(inner)
        if route:
            return route
        return target

    # ./foo.md or ./foo.md#anchor (same-dir guide-to-guide)
    if target.startswith("./"):
        rest = target[2:]
        route = _route_for_same_dir(rest)
        if route:
            return route
        # `./foo.md` where foo.md isn't in our port set — keep as relative
        return target

    # ../guides/foo.md
    if target.startswith("../"):
        # Try to handle ../../backend/... paths (deep up paths to repo root)
        if target.startswith("../../"):
            inner = target[len("../../"):]
            # Drop ".cursor/rules/..." — these are internal-only
            if inner.startswith(".cursor/"):
                return ""  # signal "drop the link"
            return f"{GITHUB_BLOB}/{inner}"

        # ../guides/foo.md or ../reference/foo.md etc.
        inner = target[len("../"):]
        # Drop internal-only runbooks
        if inner.startswith("runbooks/"):
            return ""  # signal drop
        route = _route_for_parent_dir(inner)
        if route:
            return route

        # bare ../sdks/foo or ../backend/foo from one-level-deep doc — github URL
        if "/" in inner and inner.split("/")[0] in (
            "backend",
            "agents",
            "sdks",
            "services",
        ):
            return f"{GITHUB_BLOB}/{inner}"
        return target

    # bare path like `backend/...` or `agents/...` — github blob URL
    if not target.startswith("/"):
        # could be a partial path that we should turn into GitHub URL
        if "/" in target and target.split("/")[0] in (
            "backend",
            "agents",
            "sdks",
            "docs",
            "web",
            "mobile",
            "services",
        ):
            return f"{GITHUB_BLOB}/{target}"

        # bare same-dir guide reference without ./ prefix: `auth-api-keys.md`
        route = _route_for_same_dir(target)
        if route:
            return route

    return target


def rewrite_links_in(text: str) -> tuple[str, list[str]]:
    """Apply link rewrites to the entire text. Returns (new_text, warnings)."""
    warnings: list[str] = []

    def _sub(m: re.Match[str]) -> str:
        target = m.group(1)
        new_target = rewrite_link(target)
        if new_target == "":
            # link target dropped — keep the anchor text but de-link by
            # replacing the whole `[anchor](target)` link with just `anchor`.
            # we can't do that from inside this inner sub easily — instead
            # emit a placeholder we'll postprocess.
            return "]({{DROP_LINK}})"
        if new_target == target and target.startswith(("./", "../")):
            warnings.append(f"unrewritten relative link: {target}")
        return f"]({new_target})"

    result = LINK_RE.sub(_sub, text)

    # Postprocess: collapse `[text]({{DROP_LINK}})` to just `text`
    result = re.sub(r"\[([^\]]*)\]\(\{\{DROP_LINK\}\}\)", r"\1", result)

    return result, warnings


# Frontmatter
def add_frontmatter(text: str, title: str, description: str) -> str:
    """Strip leading H1, add YAML frontmatter."""
    lines = text.splitlines()
    # Strip leading blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    # Strip leading H1 if present (Mintlify renders title from frontmatter)
    if lines and lines[0].startswith("# "):
        lines.pop(0)
        # also strip the blank line after
        while lines and not lines[0].strip():
            lines.pop(0)

    fm = [
        "---",
        f"title: {title}",
        f'description: "{description}"',
        "---",
        "",
    ]
    return "\n".join(fm + lines) + "\n"


# Blockquote → callout component
# Convert leading `> ` blockquotes that look like callouts.
# Conservative: only convert blockquotes that start with `**Note:**`, `**Warning:**`,
# `**Tip:**`, `**Info:**`, or `> Note:` / `> Warning:` / `> Tip:` patterns.
CALLOUT_RE = re.compile(
    r"((?:^> .*\n)+)",
    re.MULTILINE,
)


def _convert_blockquote_to_callout(match: re.Match[str]) -> str:
    block = match.group(1)
    # strip the `> ` prefix from each line
    lines = [ln[2:] if ln.startswith("> ") else ln[1:] if ln.startswith(">") else ln
             for ln in block.rstrip().splitlines()]
    body = "\n".join(lines).strip()

    component = "Note"
    if re.match(r"^\*\*(Warning|Caution|Deprecated)[:\.]\*\*", body):
        component = "Warning"
    elif re.match(r"^\*\*(Info|Background)[:\.]\*\*", body):
        component = "Info"
    elif re.match(r"^\*\*(Tip|Note)[:\.]\*\*", body):
        component = "Note"

    # Strip the leading "**Note:**" etc. since the component itself signals intent
    body = re.sub(r"^\*\*(Note|Warning|Caution|Info|Tip|Deprecated|Background)[:\.]\*\*\s*", "", body)

    return f"<{component}>\n{body}\n</{component}>\n"


# Run conversion only on blockquotes that span >=2 lines AND aren't inside
# fenced code blocks. Simpler approach: process text outside ``` fences.
FENCE_RE = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)


def convert_blockquotes(text: str) -> str:
    """Convert markdown blockquotes to Mintlify <Note>/<Warning>/<Info>."""
    # Split text by fenced code blocks, only convert in the non-code segments
    parts: list[str] = []
    last = 0
    for m in FENCE_RE.finditer(text):
        parts.append(CALLOUT_RE.sub(_convert_blockquote_to_callout, text[last:m.start()]))
        parts.append(m.group(0))
        last = m.end()
    parts.append(CALLOUT_RE.sub(_convert_blockquote_to_callout, text[last:]))
    return "".join(parts)


def port_one(p: Port, check: bool = False) -> list[str]:
    """Port a single file. Returns warnings."""
    src_path = DOCS_ROOT / p.src
    dst_path = TARGET_ROOT / p.dst

    if not src_path.exists():
        return [f"SKIP: source not found: {src_path}"]

    raw = src_path.read_text(encoding="utf-8")
    text, warnings = rewrite_links_in(raw)
    text = add_frontmatter(text, p.title, p.description)
    text = convert_blockquotes(text)

    if check:
        print(f"=== {p.src} → {p.dst} ===")
        print(f"  warnings: {len(warnings)}")
        for w in warnings:
            print(f"    {w}")
        return warnings

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(text, encoding="utf-8")
    print(f"  {p.src:48s} → {p.dst}")
    if warnings:
        print(f"    ! {len(warnings)} unresolved links:")
        for w in warnings:
            print(f"      {w}")
    return warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="dry-run, don't write")
    args = ap.parse_args()

    total_warnings = 0
    for p in PORTS:
        warnings = port_one(p, check=args.check)
        total_warnings += len(warnings)

    print()
    print(f"DONE. Ported {len(PORTS)} files, {total_warnings} unresolved links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
