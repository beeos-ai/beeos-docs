# 术语表 (Terminology)

本文档锁定 BeeOS 公开文档的中英术语对应关系。所有 zh OpenAPI spec、MDX 文档和未来翻译工作都**必须**遵循本表。

**约束**：

- 表内未列的新术语，先在本文档加一行再翻译。
- "保留" 列表示该词在中文上下文里也直接用英文，不翻。
- 缩写（API, SSE, JSON, JWT 等）一律保留英文。

## 核心实体

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| agent | 智能体 | 「Agent」首次出现可加括号注英文 |
| agent card | 智能体卡片 | A2A 协议术语 |
| instance | 实例 | 部署后的运行体 |
| task | 任务 | 异步单次请求 |
| conversation | 会话 | 多轮对话 |
| message | 消息 | IM 概念 |
| owner | 拥有者 | 平台账号语义 |
| visibility | 可见性 | `private`/`public`/`org` 等 |
| caller | 调用方 | 发起请求的一侧 |
| target agent | 目标智能体 | 被调用的一侧 |

## 协议 / 接入

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| OpenAPI Gateway | OpenAPI 网关 | 平台 REST 总入口 |
| A2A Gateway | A2A 网关 | Agent-to-Agent 协议入口 |
| MCP Gateway | MCP 网关 | Model Context Protocol 入口 |
| Agent Gateway | Agent 网关 | 智能体反向上行入口 |
| host / surface | 接入面 | 4 个公共域名各算一个接入面 |
| protocol | 协议 | |
| envelope | 信封 | `{success,data}` 包装 |
| chat_message | chat_message (保留) | 内部消息类型，不翻 |

## 认证

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| API key | API Key (保留) | |
| User API Key | 用户 API Key | `oag_` 开头 |
| Agent API Key | 智能体 API Key | `bak_` 开头 |
| credential | 凭证 | |
| JWT | JWT (保留) | |
| OAuth | OAuth (保留) | |
| PKCE | PKCE (保留) | |
| signing | 签名 | |
| HMAC signing | HMAC 签名 | |
| nonce | nonce (保留) | |

## 任务 / 投递

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| delivery mode | 投递模式 | `push`/`queue` |
| push (mode) | push (保留) | |
| queue (mode) | queue (保留) | |
| idempotency key | 幂等键 | `idempotency_key` |
| in_reply_to | in_reply_to (保留) | 字段名直接保留 |
| message_id | message_id (保留) | |
| webhook | Webhook (保留) | |
| delivery | 投递 | webhook delivery row |
| redeliver | 重投 | |
| retry | 重试 | |
| backoff | 退避 | 「指数退避」 |
| dead letter | 死信 | |
| audit log | 审计日志 | |

## 流式 / 数据

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| streaming | 流式 | |
| stream | 流 (动词) / 流式 (形容) | |
| SSE | SSE (保留) | Server-Sent Events |
| offset / cursor | 偏移量 / 游标 | |
| chunk | 分块 | |
| delta | delta (保留) | `agent_reply_delta` 字段名 |
| attachment | 附件 | |
| presign | 预签名 | |
| upload / download | 上传 / 下载 | |

## 限流 / 错误

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| rate limit | 限流 | |
| quota | 配额 | |
| tier | 等级 | rate-limit tier |
| 4xx / 5xx | 4xx / 5xx (保留) | |

## 工具 / MCP

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| tool | 工具 | |
| tools/list | tools/list (保留) | MCP 方法名 |
| tools/call | tools/call (保留) | |
| resources | 资源 | MCP resources |
| DCR (Dynamic Client Registration) | DCR / 动态客户端注册 | 首次出现注全称 |

## A2A

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| JSON-RPC | JSON-RPC (保留) | |
| message/send | message/send (保留) | A2A v1.0 方法名 |
| tasks/get | tasks/get (保留) | |
| tasks/cancel | tasks/cancel (保留) | |
| SendMessage (legacy) | SendMessage (保留，标注 "兼容旧名") | |
| skill | 技能 | agent card 内部字段 |

## 协议过滤器 / 渲染

| 英文 | 中文 (锁定) | 备注 |
|---|---|---|
| protocol filter | 协议过滤器 | webhook 注册时的字段 |
| renderer | 渲染器 | |
| renderer key | 渲染器键 | |
| service / surface | 服务 / 接入面 | service 偏向内部进程，surface 偏向接入面 |

## 修改历史

- 2026-05-19: 首版，锁定 50+ 词条。
