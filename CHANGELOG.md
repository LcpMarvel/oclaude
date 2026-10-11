# 更新记录

## Unreleased

- 提供英文 `README.md` 和中文 `README.zh-CN.md`，附双向语言切换。
- 安装说明改为推荐 CLIProxyAPI 最新稳定版，排除 draft / prerelease。
- CLIProxyAPI 8.0.23 已通过 SHA-256 校验及虚构 OAuth 隔离兼容测试。

## 0.1.0 — 2026-10-11

首个公开版本。

- 通过本地 CLIProxyAPI 将 Claude Code 请求连接到 Codex / ChatGPT 订阅端点。
- 支持只读复用 Codex 访问令牌，以及独立 Codex OAuth 登录。
- 提供 GPT-6.1 Sol、GPT-6 Astra 和 GPT-6 Luna 的可配置模型映射。
- 默认附加工程提示词，覆盖完整交付、决策边界、适度验证、指令冲突、并行调查和事实核对。
- 保留显式提示词及 effort 参数，避开管理命令参数注入。
- 提供本地安装器、离线测试和使用虚构凭据的代理集成测试。
- 补齐公开安装说明、MIT 许可证、贡献与安全报告说明。

测试覆盖参数、安装、登录同步和模型目录；尚未提供提示词改善效果的模型对比结果。macOS ARM64 已验证，Linux 的实际代理与模型调用仍需验证。
