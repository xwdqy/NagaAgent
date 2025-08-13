### NagaPortalAgent

与娜迦官网API交互的MCP服务，专注于充值功能。系统启动时自动登录并保存认证信息。  # 简介 #

- 官网: `https://naga.furina.chat/`  # 参考官网 #
- 自动登录管理，无需手动处理认证  # 功能 #

#### 可用工具
- `naga_recharge`: 额度充值；参数：`amount`（必填，充值金额）、`payment_type`（可选，支付方式，默认wxpay，支持wxpay/alipay）  # 工具说明 #
- `naga_redeem_code`: 兑换码使用；参数：`key`（必填，兑换码）  # 工具说明 #
- `naga_balance`: 余额查询；无需参数  # 工具说明 #
- `naga_apply_token`: 智能申请API令牌；参数：`name`（可选，令牌名称）、`group`（可选，模型组）、`unlimited_quota`（可选，是否无限制额度，默认true）。如果不提供参数，会返回可用模型列表供选择  # 工具说明 #
- `naga_get_tokens`: 获取已配置的API令牌列表；无需参数  # 工具说明 #

#### 示例
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_recharge","amount":"11.00","payment_type":"wxpay"}
```
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_recharge","amount":"50.00","payment_type":"alipay"}
```
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_redeem_code","key":"aaaa"}
```
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_balance"}
```
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_apply_token"}
```
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_apply_token","name":"my_deepseek_token","group":"deepseek","unlimited_quota":true}
```
```json
{"agentType":"mcp","service_name":"NagaPortalAgent","tool_name":"naga_get_tokens"}
```

#### 功能说明
- **自动认证**: 系统启动时自动登录并保存Cookie和用户ID  # 流程说明 #
- **充值功能**: 向 `https://naga.furina.chat/api/user/pay` 发送充值请求  # 流程说明 #
- **支付页面**: 成功后会返回支付页面URL（`https://pay.furina.chat/submit.php`）  # 页面说明 #
- **自动打开**: 工具会自动打开支付页面，支持多种打开方式（webbrowser、系统命令）  # 自动打开说明 #
- **兑换码功能**: 向 `https://naga.furina.chat/api/user/topup` 发送兑换码请求  # 流程说明 #
- **余额查询功能**: 向 `https://naga.furina.chat/api/user/self` 发送GET请求查询用户信息和余额  # 流程说明 #
- **智能API申请功能**: 自动获取模型列表，智能验证参数，申请成功后自动获取最新令牌列表  # 流程说明 #
- **订单管理**: 自动生成唯一订单号，支持微信支付和支付宝  # 订单说明 #

#### 架构说明
- **统一管理**: 使用`portal_login_manager.py`统一管理登录、认证和Cookie存储  # 架构说明 #
- **自动登录**: 系统启动时自动执行登录流程  # 架构说明 #
- **状态同步**: 所有组件通过登录管理器共享认证状态  # 架构说明 #
- **简化调用**: Agent直接使用httpx进行API调用，避免复杂的客户端封装  # 架构说明 #
- **架构简化**: 移除了专门的Cookie管理器，直接在登录管理器中处理Cookie存储  # 架构说明 #
- **代码优化**: 提取了通用的请求上下文准备和HTTP请求方法，减少重复代码  # 架构说明 #

#### 配置说明
- 在 `config.py` 中配置 `naga_portal.username` 和 `naga_portal.password`  # 配置说明 #
- 系统启动时会自动登录并保存认证信息  # 配置说明 #
- 无需手动处理Cookie或用户ID  # 配置说明 #

#### 备注
- 专注于充值功能，移除了多余的通用API工具  # 备注 #
- 自动处理认证，用户无需关心登录细节  # 备注 #
- **自动打开支付页面**: 充值成功后会自动打开支付页面，无需手动操作  # 备注 #
- 架构简化，代码更易维护  # 备注 #
- **Cookie传递优化**: 修复了POST请求中Cookie传递问题，确保认证信息正确传递  # 修复说明 #
- **架构重构**: 完全简化架构，移除了专门的Cookie管理器，直接在登录管理器中处理Cookie存储  # 重构说明 #


