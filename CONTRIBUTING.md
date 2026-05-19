# Contributing to beeos-docs

This repository is the **single source of truth** for the public BeeOS
documentation site published at <https://docs.beeos.ai> via Mintlify.
All MDX prose is hand-authored here. The only files that come from
elsewhere are the OpenAPI specs under `openapi/`, which are synced from
the `backend/` submodule (see [§5](#5-openapi-sync)).

> **Note for cross-repo navigation:** `beeos-docs/` and the internal
> `github.com/beeos-ai/docs` repository are **not related**. The
> internal repo is private dev documentation (runbooks, ADR drafts);
> this one is the public Mintlify site. Files with the same name in
> the two repos are independent — **do not sync content between them**.

This guide locks the conventions for: (a) Markdown -> MDX conversion,
(b) Mintlify component usage, (c) routing/linking, (d) OpenAPI sync,
and (e) translation rules.

## 1. File layout

```
beeos-docs/
├── introduction.mdx          # Landing page
├── quickstart.mdx
├── authentication.mdx
├── guides/                   # Public concept guides
├── architecture/             # Public-overview / domain map
├── reference/                # Error tables, glossary
├── a2a/                      # A2A protocol surface docs
├── mcp/                      # MCP protocol surface docs
├── sdks/                     # SDK reference + changelog + migration
├── openapi/                  # AUTO-SYNCED from backend/openapi/ (§5)
├── zh/                       # Chinese mirror of the above (§9)
├── scripts/sync-spec.sh      # Sync helper (do not bypass)
└── docs.json                 # Mintlify nav + theme (v4 schema)
```

`zh/` mirrors the en/ tree 1:1. Any new en file MUST be paired with a
zh translation in the same PR, using the terminology table at
[`zh/_terminology.md`](zh/_terminology.md).

## 2. Frontmatter

Every page starts with YAML frontmatter:

```mdx
---
title: Calling agents
description: Send messages to deployed agents and receive replies (REST, A2A, MCP).
---
```

- `title` is required — shows in sidebar and page header.
- `description` is required — 1-2 sentences, SEO-friendly, no trailing period.
- Quote `description` only when its value contains YAML-special characters:
  a colon (`:`), a quote (`"` or `'`), a newline, or starts with `[`/`{`/`-`/`*`.
  Plain English or Chinese prose does not need quoting.
- No emojis in titles or descriptions.

## 3. Mintlify component usage

Use the components below in place of raw HTML or markdown blockquotes.
Mixing markdown blockquotes (`>`) with MDX components causes inconsistent
rendering — pick one.

### CodeGroup (TS + Go + curl)

````mdx
<CodeGroup>

```typescript TypeScript
const reply = await agentsApi.invokeAgent({ ... });
```

```go Go
reply, _ := agentsClient.Invoke(ctx, ...)
```

```bash curl
curl -X POST https://openapi.beeos.ai/api/v1/agents/{id}/invoke ...
```

</CodeGroup>
````

The fence language tag (`typescript`, `go`, `bash`) AND the human-readable
label (`TypeScript`, `Go`, `curl`) are both required. Keep the labels in
English in zh translations too — they are language IDs by convention.

### Procedural steps

```mdx
<Steps>
  <Step title="Install the SDK">
    `npm install @beeos-ai/sdk`
  </Step>
  <Step title="Configure auth">
    Set `Authorization: Bearer oag_…` on every request.
  </Step>
</Steps>
```

Use `<Steps>` for ordered procedures of 3+ items. For 2 items use a
numbered list.

### Callouts

| Intent | Component |
|---|---|
| Recommended path / quick tip | `<Note>` |
| Pitfall / breaking-change warning | `<Warning>` |
| Background info, not actionable | `<Info>` |
| Deprecated / removed feature | `<Warning>` + leading "**Deprecated:**" |

Do **not** use raw markdown blockquotes (`> ...`) for callouts — switch to
`<Note>`/`<Warning>`/`<Info>` instead.

### Side-by-side comparison

```mdx
<Tabs>
  <Tab title="Blocking (default)">
    Returns a single JSON payload with the full reply.
  </Tab>
  <Tab title="Streaming (SSE)">
    Set `Accept: text/event-stream` to receive `agent_reply_delta` events.
  </Tab>
</Tabs>
```

### "See also" / link cards

```mdx
<CardGroup cols={2}>
  <Card title="Calling agents" icon="message-bot" href="/guides/calling-agents">
    Three invocation modes — OpenAPI, A2A, MCP.
  </Card>
  <Card title="Webhooks" icon="webhook" href="/guides/webhooks">
    HMAC-signed delivery with retry and audit log.
  </Card>
</CardGroup>
```

Default to `cols={2}`. Use `cols={3}` only when all card titles are
short (< 12 chars) and you have at least three cards.

### Mermaid diagrams

Use fenced ```mermaid blocks — Mintlify renders them natively. Three
hard rules to avoid silent render failures:

1. **Node IDs must be ASCII without spaces** (`UserService`, not
   `User Service`). Display labels in `["..."]` can be any language
   including Chinese.
2. **Quote edge labels with special characters** —
   `A -->|"O(1) lookup"| B`, not `A -->|O(1) lookup| B`. In zh
   translations, any label with Chinese punctuation or parens needs
   quoting too.
3. **Never set explicit colors** (`style`, `fill:`, `classDef`) —
   they break in dark mode. Let the theme handle it.

## 4. Routing

| Link type | Format |
|---|---|
| Internal to another doc | `/guides/foo` (absolute path, no `.mdx`) |
| Internal anchor on same page | `#section-heading-slug` (Mintlify lower-cases + dashes) |
| External | Full `https://…` URL |
| GitHub source code | `https://github.com/beeos-ai/openagent/blob/main/...` |

**Heading slugs**: Mintlify slugifies headings by lower-casing, replacing
spaces with `-`, and **keeping leading numbers** like `## 4. Invoke the agent`
-> `#4-invoke-the-agent`. For zh pages, Chinese heading text produces
unpredictable slugs — if you need a stable cross-page anchor, add an
explicit id with raw HTML: `<h2 id="invoke-the-agent">调用智能体</h2>`.

## 5. OpenAPI sync

`openapi/beeos-platform-v1.yaml` and `openapi/beeos-agent-integration-v1.yaml`
are **AUTO-SYNCED** from the [`backend/openapi/`](https://github.com/beeos-ai/openagent/tree/main/backend/openapi)
directory of the openagent meta repo. The top of each file has a banner
with the source SHA — **do not edit them by hand**.

Sync workflow:

```bash
# 1. Edit the source spec in the openagent meta repo
cd path/to/openagent
$EDITOR backend/openapi/beeos-platform-v1.yaml
cd backend && git add -A && git commit && cd ..

# 2. Regenerate SDKs from the new source (separate concern)
cd sdks/openapi-sdk && npm run sync-spec && npm run gen

# 3. In beeos-docs (this repo), pull the new spec in
cd beeos-docs && npm run sync-spec   # copies + adds banner
git add openapi/ && git commit
```

`openapi/beeos-platform-v1-zh.yaml` is **hand-translated**, not synced.
Update it manually following [`zh/_terminology.md`](zh/_terminology.md)
after the en spec lands.

## 6. Style conventions

- Heading hierarchy: H1 is implicit from frontmatter `title`; start body
  with `##`. Don't use `#`.
- Lists: prefer `-` for unordered, `1.` for ordered (Mintlify renders both).
- Code voice: imperative ("Set …", "Pass …"), present tense.
- Avoid second-person if it can be removed cleanly ("the client must …"
  > "you must …" in reference docs; opposite in tutorials).
- Tables: max 5 columns; if more, switch to `<CardGroup>` or split.

## 7. PR checklist

Before opening a PR to this repo:

- [ ] `npm run validate` passes locally (`mintlify validate`)
- [ ] `npm run broken-links` resolves cleanly (`mintlify broken-links`)
- [ ] `npx @redocly/cli@1.12.0 lint openapi/beeos-platform-v1.yaml` passes
- [ ] No `>`-style markdown blockquotes (search: `grep -lE "^> " *.mdx **/*.mdx`)
- [ ] No relative `.md` links (search: `grep -lE "\]\(\.\./|\]\(\./" *.mdx **/*.mdx`)
- [ ] No `backend/` paths leaked into MDX (search: `grep -l "backend/" *.mdx **/*.mdx`)
- [ ] New en file paired with zh translation (or explicitly tracked as TODO)
- [ ] zh translation follows `zh/_terminology.md`; new terms added there
      before being used in prose

## 8. Deployment

`.github/workflows/deploy.yml` triggers `mintlify/github-action@v4` on
every push to `main` -> publishes immediately to <https://docs.beeos.ai>.
Always use a feature branch + PR review. Never force-push `main`.

## 9. Translation rules (zh)

The zh tree under `zh/` is hand-maintained alongside the en tree. Rules
that lock translation quality:

- **Mirror the file tree exactly**: every `foo/bar.mdx` in en has a
  `zh/foo/bar.mdx` peer with the same MDX structure (frontmatter,
  components, headings, code blocks).
- **Use `zh/_terminology.md`**: the locked en/zh term table. Add a row
  for any new term *before* using it in prose. Words marked "保留" stay
  in English (`API key`, `JWT`, `JSON-RPC`, `chat_message`, etc.).
- **Code blocks**: never translate fence content. English comments inside
  code stay English (preserves runnability + lint clarity).
- **CodeGroup labels**: keep language IDs and human labels in English
  (`TypeScript`, `Go`, `curl`) — they are conventional, not prose.
- **Spacing**: leave a single space between Chinese characters and inline
  English / code / digits: `用户 API Key`, not `用户API Key`.
- **Error codes, token prefixes, JSON field names**: keep verbatim
  (`oag_`, `bak_`, `error.code`, `agent_reply_delta`, `tools/call`).
- **Anchors**: prefer not to rely on auto-slugified Chinese heading ids
  for cross-page links. If unavoidable, add explicit `<h2 id="...">`.
- **Mermaid**: see [§3 mermaid rules](#mermaid-diagrams) — node IDs ASCII,
  edge labels with Chinese punctuation quoted.
