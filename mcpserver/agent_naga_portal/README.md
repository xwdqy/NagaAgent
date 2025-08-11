### NagaPortalAgent

与娜迦官网API交互的MCP服务。默认读取 `config.naga_portal.username/password` 用于登录。  # 简介 #

- 官网: `https://naga.furina.chat/`  # 参考官网 #
- 提供登录/GET/POST/登出/获取用户信息等完整功能  # 功能 #

#### 可用工具
- `naga_login`: 使用保存的用户名/密码登录；可选 `username/password/login_path` 覆盖  # 工具说明 #
- `naga_get`: GET测试；参数：`path`（以/开头），`params`（可选）  # 工具说明 #
- `naga_post`: POST测试；参数：`path`（以/开头），`json`（可选）  # 工具说明 #
- `get_user_info`: 获取用户信息（默认请求 `/api/profile`）  # 工具说明 #
- `naga_logout`: 登出并清理本地会话  # 工具说明 #

#### 示例
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_login"}
```
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_get","path":"/api/profile"}
```

#### 配置说明
- 在 `config.py` 中配置 `naga_portal.username` 和 `naga_portal.password`  # 配置说明 #
- 登录API路径默认为 `/api/user/login`，支持turnstile验证参数  # 配置说明 #
- 登录成功后会自动处理set-cookie响应头，保存会话信息  # 配置说明 #

#### 备注
- 支持真实的娜迦官网登录流程，包括cookie会话管理  # 备注 #
- 如需自定义登录路径或添加验证参数，可在配置中设置  # 备注 #


