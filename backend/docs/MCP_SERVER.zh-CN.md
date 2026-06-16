# MCP（Model Context Protocol）配置

DeerFlow 支持通过可配置的 MCP 服务器和技能扩展能力。这些扩展配置从项目根目录下独立的 `extensions_config.json` 文件加载。

## 设置

1. 将 `extensions_config.example.json` 复制为项目根目录下的 `extensions_config.json`。

   ```bash
   cp extensions_config.example.json extensions_config.json
   ```

2. 将需要启用的 MCP 服务器或技能设置为 `"enabled": true`。
3. 根据需要配置每个服务器的命令、参数和环境变量。
4. 重启应用以加载并注册 MCP 工具。

## Filesystem MCP 服务器

DeerFlow 已经提供了按 thread 隔离的内置文件工具。
不要为同一个 DeerFlow 工作区额外添加 MCP filesystem server。

重叠的文件工具会使用不同的路径语义，可能导致 LLM 的工具选择和文件访问行为不稳定。

DeerFlow 当前没有为 filesystem server 适配 MCP Roots 模式。具体来说，它不会发布按 thread 收窄的 MCP roots，也不会把 `/mnt/user-data/...` 这类 DeerFlow 沙箱路径映射为 `@modelcontextprotocol/server-filesystem` 可接受的路径。

请优先使用 DeerFlow 内置文件工具处理 DeerFlow 工作区文件。

## OAuth 支持（HTTP/SSE MCP 服务器）

对于 `http` 和 `sse` 类型的 MCP 服务器，DeerFlow 支持 OAuth token 获取和自动刷新。

- 支持的授权类型：`client_credentials`、`refresh_token`
- 在 `extensions_config.json` 中为每个 server 配置 `oauth` 块
- 密钥建议通过环境变量提供，例如 `$MCP_OAUTH_CLIENT_SECRET`

示例：

```json
{
  "mcpServers": {
    "secure-http-server": {
      "enabled": true,
      "type": "http",
      "url": "https://api.example.com/mcp",
      "oauth": {
        "enabled": true,
        "token_url": "https://auth.example.com/oauth/token",
        "grant_type": "client_credentials",
        "client_id": "$MCP_OAUTH_CLIENT_ID",
        "client_secret": "$MCP_OAUTH_CLIENT_SECRET",
        "scope": "mcp.read",
        "refresh_skew_seconds": 60
      }
    }
  }
}
```

## 自定义工具拦截器

可以注册自定义拦截器，在每次 MCP 工具调用前执行。它适合用于注入按请求变化的 header，例如从 LangGraph 执行上下文中读取用户鉴权 token，也可以用于日志和指标采集。

在 `extensions_config.json` 中通过 `mcpInterceptors` 声明拦截器：

```json
{
  "mcpInterceptors": [
    "my_package.mcp.auth:build_auth_interceptor"
  ],
  "mcpServers": { }
}
```

每个条目是 `module:variable` 格式的 Python 导入路径，并通过 `resolve_variable` 解析。该变量必须是一个无参数 builder 函数，返回兼容 `MultiServerMCPClient` 的 `tool_interceptors` 接口的异步拦截器；也可以返回 `None` 表示跳过。

从 LangGraph metadata 注入鉴权 header 的示例：

```python
def build_auth_interceptor():
    async def interceptor(request, handler):
        from langgraph.config import get_config
        metadata = get_config().get("metadata", {})
        headers = dict(request.headers or {})
        if token := metadata.get("auth_token"):
            headers["X-Auth-Token"] = token
        return await handler(request.override(headers=headers))
    return interceptor
```

- 支持传入单个字符串，会自动规范化为单元素列表。
- 无效路径或 builder 执行失败只会记录 warning，不会阻塞其他拦截器。
- builder 返回值必须是 `callable`；如果返回非 callable 且非 `None`，会记录 warning 并跳过。

## 工作方式

MCP 服务器会暴露工具，这些工具会在运行时自动发现并集成到 DeerFlow 的 Agent 系统中。启用后，Agent 可以直接使用这些工具，无需额外修改代码。

## 示例能力

MCP 服务器可以提供以下能力：

- **数据库**，例如 PostgreSQL
- **外部 API**，例如 GitHub、Brave Search
- **浏览器自动化**，例如 Puppeteer
- **自定义 MCP Server 实现**

## 了解更多

MCP 官方文档：
https://modelcontextprotocol.io
