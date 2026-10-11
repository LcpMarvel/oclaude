# oclaude

[English](README.md) | **简体中文**

[![Offline tests](https://github.com/LcpMarvel/oclaude/actions/workflows/tests.yml/badge.svg)](https://github.com/LcpMarvel/oclaude/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

一个轻量的社区启动器，让 Claude Code 通过本地 [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) 使用 Codex / ChatGPT 订阅登录。默认模型为 **GPT-6.1-Sol / High**，保留 Claude Code 的交互、工具和会话管理方式。

```text
oclaude → Claude Code → CLIProxyAPI (127.0.0.1:18317) → Codex 订阅端点
```

本项目与 OpenAI、Anthropic 或 CLIProxyAPI 无隶属关系。这是社区集成方式；账号权限、模型可用性、订阅额度及服务条款由服务方决定，不代表服务方官方支持第三方 Claude Code 工作流。

## 特性

- 按需启动本地代理，支持多个会话；Claude 退出后代理继续运行。
- 只读复用 Codex 的 ChatGPT 登录，或通过 CLIProxyAPI 独立 OAuth 登录。
- 配置默认模型、模型别名、子代理模型和推理强度。
- 为普通会话附加一份工程提示词，显式自定义提示词优先。
- Python 标准库实现；安装器不下载依赖、不登录、不修改 shell 配置。
- 无独立 API Key 计费回退，也不附带凭据或第三方二进制。

## 依赖与兼容性

需要 Python 3.10+、可在 `PATH` 中找到的 `claude` 命令，以及 CLIProxyAPI 可执行文件。Claude Code 的安装方式见其[官方快速开始](https://code.claude.com/docs/en/quickstart)。订阅调用需要具有相应访问权的 ChatGPT 账号。

验证环境：macOS ARM64、Python 3.14、Claude Code 2.1.295。CLIProxyAPI 8.0.23 已通过隔离 OAuth 与模型目录测试，这些测试不覆盖真实模型推理或工具调用往返。离线 CI 覆盖 macOS 和 Linux，Linux 上的实际代理与模型调用仍未验证。原生 Windows 不支持，因为启动器使用 `fcntl` 和 Unix 进程接口。代理或 Claude Code 升级后，请核对兼容性。

## 安装

1. 获取源码：

   ```sh
   git clone https://github.com/LcpMarvel/oclaude.git
   cd oclaude
   python3 --version
   claude --version
   ```

2. 从 CLIProxyAPI [官方 Releases](https://github.com/router-for-me/CLIProxyAPI/releases) 选择**最新稳定版**（排除 draft 和 prerelease），下载适合系统和 CPU 架构的发行包，以及**同一版本**的 `checksums.txt`。已实测版本可从 [v8.0.23](https://github.com/router-for-me/CLIProxyAPI/releases/tag/v8.0.23) 获取。不要把源码压缩包当作可执行发行包。

   解压前核对发行包的 SHA-256 与 `checksums.txt` 对应条目一致：

   ```sh
   # macOS：替换为实际下载文件名
   shasum -a 256 /path/to/downloaded-archive.tar.gz
   # Linux
   sha256sum /path/to/downloaded-archive.tar.gz
   ```

   核对成功后解压，找到其中的 `cli-proxy-api` 可执行文件。保留同目录的上游 `LICENSE`，安装器会在存在时一并复制。

3. 在源码目录运行安装器，传入刚核对并解压得到的文件路径：

   ```sh
   python3 install.py /path/to/cli-proxy-api
   export PATH="$HOME/.local/bin:$PATH"
   oclaude --version
   ```

   如需后续终端也能找到命令，把上面的 `export PATH=...` 加入自己的 shell 启动文件，例如 zsh 的 `~/.zshrc` 或 bash 的 `~/.bashrc`。安装器不会自动写入这些文件。

安装结果：

| 文件 | 安装位置 |
| --- | --- |
| 启动命令 | `~/.local/bin/oclaude` |
| CLIProxyAPI | `~/.local/lib/oclaude/cli-proxy-api` |
| 默认附加提示词 | `~/.local/lib/oclaude/openai-system-prompt.md` |
| 上游许可证（源文件存在时） | `~/.local/lib/oclaude/CLIProxyAPI-LICENSE` |

更新源码或默认提示词后重新运行安装器，再开启新会话。更新代理前先结束相关任务并运行 `oclaude --oclaude-stop`。

## 登录与使用

已有 Codex 的 ChatGPT 登录时，直接运行：

```sh
oclaude
oclaude -p '解释这个项目的入口'
oclaude --model gpt-6.1-sol --effort high
oclaude --model fable
oclaude --model sonnet
oclaude --model haiku
oclaude --continue
```

默认读取 `~/.codex/auth.json`；设置 `CODEX_HOME` 时读取该目录的 `auth.json`。要求登录模式为 `chatgpt`。每次启动同步有效访问令牌到代理私有目录，**不修改 Codex 登录文件，不复制 Codex 的刷新令牌**。

没有可用的 Codex 登录，或希望代理独立刷新令牌时：

```sh
oclaude --oclaude-stop
oclaude --oclaude-login
oclaude
```

登录由 CLIProxyAPI 发起，通常会打开浏览器；选择希望使用额度的 ChatGPT 账号。代理保存并刷新这次独立授权，该登录优先于复用 Codex 登录。`--oclaude-setup` 是同一登录入口的别名。参见 [CLIProxyAPI Codex OAuth 文档](https://help.router-for.me/configuration/provider/codex)。

复用模式只持有当前访问令牌。令牌过期时，先打开 Codex 刷新登录，再重启 `oclaude`；长期后台任务可使用独立 OAuth 登录。独立登录使用所选账号的权限和额度，请留意账号及工作区。

### 模型映射

| 槽位 / 别名 | 默认模型 |
| --- | --- |
| 主会话、`sonnet`、`opus` | `gpt-6.1-sol` |
| `fable` | `gpt-6-astra` |
| `haiku`、快速任务 | `gpt-6-luna` |
| 未显式指定模型的子代理 | `gpt-6.1-sol` |

普通会话未指定 `--effort` 时补上 `high`。`--model`、`--effort` 覆盖当前会话，环境变量改变默认槽位；子代理定义或调用中的显式模型仍优先。模型是否可用由代理目录和账号权限决定。

### 附加工程提示词

普通交互和 `-p` 会话默认附加 [openai-system-prompt.md](openai-system-prompt.md)，保留 Claude Code 原生 system prompt 和工具规则。它强调检查真实输入与完整行为链路、常规决策自主推进、聚焦验证，以及如实报告结果与阻塞；不改变登录方式、模型映射或权限模式，也不保证模型始终遵循。

显式传入以下任一参数时，启动器跳过默认提示词注入，保留用户设置；支持 `--flag=value` 写法：

- `--system-prompt`
- `--system-prompt-file`
- `--append-system-prompt`
- `--append-system-prompt-file`

例如：

```sh
oclaude --append-system-prompt-file ./my-prompt.md
```

需要默认策略与自定义策略同时生效时，把两者合并到一个文件并传入。源码运行读取源码目录的提示词；安装后的命令读取安装副本，修改源码后需要重新安装。

`--continue` / `--resume` 可能沿用旧会话首次记录的 system prompt，直到压缩后才更新。验证提示词变化时优先开启新会话；启动器不主动改变快照设置。参见 [Claude Code 关于恢复会话的说明](https://code.claude.com/docs/en/cli-reference#system-prompt-flags-in-resumed-conversations)。

## 配置

可以从终端传入环境变量，或创建 `~/.config/oclaude/env`（设置 `XDG_CONFIG_HOME` 时使用该目录下的 `oclaude/env`）。环境变量优先于文件。文件只支持简单 `NAME=value`，不执行 shell 表达式；文件必须仅当前用户可读写：

```sh
mkdir -p "$HOME/.config/oclaude"
(umask 077; touch "$HOME/.config/oclaude/env")
chmod 600 "$HOME/.config/oclaude/env"
```

无需创建配置文件，也无需填写 Key。示例内容：

```dotenv
OCLAUDE_MODEL=gpt-6.1-sol
OCLAUDE_EFFORT=high
OCLAUDE_PORT=18317
```

| 变量 | 默认值 / 用途 |
| --- | --- |
| `OCLAUDE_MODEL` | `gpt-6.1-sol` |
| `OCLAUDE_FABLE_MODEL` | `gpt-6-astra` |
| `OCLAUDE_OPUS_MODEL` | `gpt-6.1-sol` |
| `OCLAUDE_SONNET_MODEL` | `gpt-6.1-sol` |
| `OCLAUDE_HAIKU_MODEL` | `gpt-6-luna` |
| `OCLAUDE_FAST_MODEL` | 与 Haiku 映射相同 |
| `OCLAUDE_SUBAGENT_MODEL` | 与 Sonnet 映射相同 |
| `OCLAUDE_EFFORT` | `high` |
| `OCLAUDE_CONTEXT_WINDOW` | `272000`；正整数，控制 Claude Code 的上下文窗口设置，保留自动压缩 |
| `OCLAUDE_CODEX_AUTH_FILE` | `$CODEX_HOME/auth.json`，默认 `~/.codex/auth.json` |
| `OCLAUDE_PROXY_URL` | 可选的上游网络代理 |
| `OCLAUDE_PORT` | `18317`，仅绑定 `127.0.0.1` |
| `OCLAUDE_API_TIMEOUT_MS` | `3000000` |
| `OCLAUDE_STATE_DIR` | `~/.local/state/oclaude`；仅从终端环境设置 |
| `OCLAUDE_KEYS_FILE` | 偏好配置文件路径，沿用旧命名；仅从终端环境设置 |
| `OCLAUDE_PROXY_BIN` | 自定义 CLIProxyAPI 路径；否则先查 `PATH`，再查安装副本 |

`272000` 是可配置默认值，**不是 OpenAI 全型号 API 的硬上限**。增大前核对实际订阅端点、模型和代理的限制。改变端口、上游网络代理或登录方式前，先结束相关任务并停止代理；已有会话需要重新启动才能载入新设置。

## 管理与故障排查

```sh
oclaude agents --json       # 透传 Claude Code 管理命令
oclaude --oclaude-status    # 检查本地代理状态
oclaude --oclaude-stop      # 停止代理，保留 OAuth 登录
```

代理退出不会随 Claude 会话自动发生，没有安装开机服务。停止代理会中断进行中的请求。`--help` / `--version` 直接交给 Claude Code；其他已识别的管理命令不插入会话 effort 或提示词参数，但仍会走登录与代理准备流程。

| 问题 | 处理方式 |
| --- | --- |
| `oclaude: command not found` | 把 `~/.local/bin` 加入 `PATH`，或使用完整命令路径 |
| 找不到 `claude` / CLIProxyAPI | 检查 `PATH`；代理可用 `OCLAUDE_PROXY_BIN` 指向已安装文件 |
| 未找到登录、登录模式不符或令牌过期 | 使用 `--oclaude-login`，或先让 Codex 刷新 ChatGPT 登录 |
| 配置文件权限过宽 | 对配置文件执行 `chmod 600` |
| 端口被占用 | 先检查占用进程；可设置 `OCLAUDE_PORT` 使用空闲端口 |
| 代理启动失败、模型目录缺失、`unknown provider for model` | 在本机检查状态目录的 `proxy.log`；结束任务并停止代理后重启，检查版本、网络和模型名称 |
| GPT 模型不在 Claude Code 内置目录的提示 | 可能只是目录识别提示；用实际请求结果判断是否调用成功，检查上下文窗口设置 |
| 默认提示词文件缺失 | 在源码目录重新运行安装器 |
| 旧 `OCLAUDE_API_KEY` / `OCLAUDE_BASE_URL` 被拒绝 | 移除旧配置；本项目只支持订阅登录 |

代理启动会获取维护方的公开模型目录，并等待默认模型注册完成。首次启动需要网络；更新上游或模型名称后可能需要重启代理。提交问题时仅提供版本、脱敏错误和复现步骤，勿上传登录文件、整个状态目录或未经检查的日志。

## 开发与测试

源码目录包含 Python 启动器 `oclaude`、安装器 `install.py`、共享提示词和聚焦测试。源码运行可使用 `python3 ./oclaude`；需已有依赖，或通过 `OCLAUDE_PROXY_BIN` 指定代理。

```sh
# 离线单元测试：参数透传、提示词覆盖、安装副本等
python3 -m unittest -v test_prompt.py

# 集成测试：需要真实代理二进制及网络，以虚构令牌获取公开模型目录
python3 test_oclaude.py /path/to/cli-proxy-api
```

集成测试使用临时状态目录和假的 Claude 命令，不执行模型推理，不使用真实账号。它检查订阅配置、API Key 隔离、只读令牌同步、刷新令牌不复制、模型目录、effort、提示词参数和管理参数；不能证明真实账号的额度、工具调用兼容性或全部 Claude Code 功能可用。

贡献方式见 [CONTRIBUTING.md](CONTRIBUTING.md)，安全问题报告方式见 [SECURITY.md](SECURITY.md)。

## 隐私与限制

状态目录默认是 `~/.local/state/oclaude`，权限为 `700`；生成的配置和令牌文件权限为 `600`。Claude 进程使用随机本地代理令牌，启动器移除继承的 OpenAI、Anthropic 等相关凭据变量。代理的远程管理、管理面板、使用统计及请求日志关闭；仍会保存代理进程输出，Claude Code 自身也可能保存会话记录。

请求内容经本地代理发送给订阅服务，不是离线推理。普通 `claude` 的全局配置和权限模式不会被此启动器改写；Claude Code 的权限、项目设置与外部工具仍需按实际使用管理。独立 OAuth 登录会在本机保存供代理刷新的凭据；复用模式不复制 Codex 刷新令牌。

`OPENAI_API_KEY` 不会作为调用凭据，也没有独立 API 计费回退。实际额度扣减和模型访问权由订阅服务端决定；Claude 显示的美元成本估算不代表 OpenAI API 账单。上游订阅端点、模型目录及 Claude Code 行为变化可能影响兼容性。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。CLIProxyAPI 和 Claude Code 各自遵循其上游许可证与服务条款；本仓库不分发它们的二进制或登录凭据。
