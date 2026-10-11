# 参与贡献

欢迎提交问题和小范围改进。较大的行为变化请先开 Issue，说明使用场景、当前行为和期望结果。

## 本地开发

需要 Python 3.10+；只使用标准库，无需安装 Python 依赖。代码依赖 POSIX，面向 macOS 和 Linux。

```sh
git clone https://github.com/LcpMarvel/oclaude.git
cd oclaude
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_prompt.py
```

离线测试不需要 Claude Code、CLIProxyAPI 或账号，覆盖参数传递、提示词覆盖规则和临时 HOME 下的安装。

如果修改登录同步、代理配置或启动流程，再运行隔离集成测试：

```sh
python3 test_oclaude.py /path/to/cli-proxy-api
```

它使用假 Claude、虚构 OAuth 凭据和临时状态目录，需要本机回环端口及公开模型目录的网络访问；不会调用模型。实际模型调用、额度和提示词效果需要另行验证，不能用这些测试替代。

## 改动约定

- 保持启动器小而直接，优先标准库，不改普通 `claude` 的全局配置。
- 明确参数覆盖、模型映射、兼容性和凭据隔离的行为变化，并更新相关测试及 README。
- 修改提示词时沿用 `openai-system-prompt.md` 这一份源码，避免重复或互相冲突的规则。
- 提交信息说明改了什么、为什么；PR 中列出实际执行的验证和未验证部分。
- 不提交真实令牌、登录文件、环境配置、运行日志、会话快照或第三方二进制。

Issue 和 PR 请使用 [GitHub 项目页](https://github.com/LcpMarvel/oclaude)。安全漏洞请按 [SECURITY.md](SECURITY.md) 私下报告。

提交贡献表示你有权将该内容按本项目的 [MIT 许可证](LICENSE) 发布。
