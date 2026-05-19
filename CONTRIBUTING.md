# Contributing to beeos-docs

This site is published with Mintlify. Source-of-truth content lives in the
[main `openagent` repository](https://github.com/beeos-ai/openagent) under
`docs/`; this repo is a curated, MDX-formatted, bilingual (en + zh) public
copy. PRs that update content here without updating the source-of-truth
will be rejected — keep the two in sync.

This guide locks the conventions for: (a) Markdown → MDX conversion, (b)
Mintlify component usage, (c) routing/linking, and (d) how to sync the
OpenAPI specs without footguns.

## 1. File layout

```
beeos-docs/
├── introduction.mdx          # Landing page
├── quickstart.mdx
├── authentication.mdx
├── guides/                   # Public concept guides (new in v2)
├── architecture/             # Public-overview / domain map
├── reference/                # Error tables, glossary
├── a2a/                      # A2A protocol surface docs
├── mcp/                      # MCP protocol surface docs
├── sdks/                     # SDK reference + changelog + migration
├── openapi/                  # AUTO-SYNCED — see §5
├── zh/                       # Chinese mirror of the above
├── scripts/sync-spec.sh      # Sync helper, do not bypass
└── docs.json                 # Mintlify nav + theme
```

zh/ mirrors the en/ tree 1:1. Any new en file MUST be paired with a zh
translation in the same PR, using the terminology table at
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
- If `description` contains a colon (`:`), wrap the whole value in double
  quotes: `description: "Tasks: long-running invocation primitive"`.
- No emojis in titles or descriptions.

## 3. Mintlify component usage

Use the components below in place of raw HTML or markdown blockquotes.
Mixing markdown blockquotes (`>`) with MDX components causes inconsistent
rendering — pick one.

### CodeGroup (TS + Go + curl)

```mdx
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
```

The fence language tag (`typescript`, `go`, `bash`) AND the human-readable
label (`TypeScript`, `Go`, `curl`) are both required.

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

Use `cols={2}` by default. `cols={3}` only for the introduction page.

### Mermaid diagrams

Use fenced ```mermaid blocks — Mintlify renders them natively. Follow the
[`mermaid syntax rules`](../docs/MERMAID_GUIDE.md) (no spaces in node IDs,
no explicit colors, etc.).

## 4. Routing

| Link type | Format |
|---|---|
| Internal to another doc | `/guides/foo` (absolute path, no `.mdx`) |
| Internal anchor on same page | `#section-heading-slug` (Mintlify lower-cases + dashes) |
| External | Full `https://…` URL |
| GitHub source code | `https://github.com/beeos-ai/openagent/blob/main/...` |

**Heading slugs**: Mintlify slugifies headings by lower-casing, replacing
spaces with `-`, and **keeping leading numbers** like `## 4. Invoke the agent`
→ `#4-invoke-the-agent`. To avoid number-prefix slugs, drop the `4.` from
the heading text (renumber via `<Steps>` instead).

## 5. OpenAPI sync

`openapi/beeos-platform-v1.yaml` and `openapi/beeos-agent-integration-v1.yaml`
are **AUTO-SYNCED** from
`https://github.com/beeos-ai/openagent/tree/main/backend/openapi/`. The top
of each file has a banner — **do not edit them by hand**.

Sync workflow:

```bash
# In openagent repo
$EDITOR backend/openapi/beeos-platform-v1.yaml
cd sdks/openapi-sdk && npm run sync-spec && npm run gen   # update SDKs

# In beeos-docs repo (this one)
npm run sync-spec   # copies backend/openapi/*.yaml → openapi/ with banner
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

- [ ] `npm run build` passes locally (`mintlify build`)
- [ ] `npx @redocly/cli@1.12.0 lint openapi/beeos-platform-v1.yaml` passes
- [ ] No `>`-style markdown blockquotes (search: `rg "^> " *.mdx`)
- [ ] No relative `.md` links (search: `rg "\]\(\./|\.\./" *.mdx`)
- [ ] No `backend/` paths leaked into MDX (search: `rg "backend/" *.mdx`)
- [ ] New en file paired with zh translation
- [ ] zh translation follows `zh/_terminology.md`
- [ ] PR is against `docs-roadmap-v2` (or successor feature branch),
      **not** `main` — main pushes auto-deploy production via
      `.github/workflows/deploy.yml`.

## 8. Deployment

`.github/workflows/deploy.yml` triggers `mintlify/github-action@v4` on
every push to `main` → publishes immediately to <https://docs.beeos.ai>.
Always use a feature branch + PR review. Never force-push `main`.
