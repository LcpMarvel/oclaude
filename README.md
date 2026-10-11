# oclaude

**English** | [简体中文](README.zh-CN.md)

[![Offline tests](https://github.com/LcpMarvel/oclaude/actions/workflows/tests.yml/badge.svg)](https://github.com/LcpMarvel/oclaude/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A lightweight community launcher that lets Claude Code use a Codex / ChatGPT subscription login through a local [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) instance. The default model is **GPT-6.1-Sol / High**, with Claude Code's interactions, tools, and session management retained.

```text
oclaude → Claude Code → CLIProxyAPI (127.0.0.1:18317) → Codex subscription endpoint
```

This project is not affiliated with OpenAI, Anthropic, or CLIProxyAPI. It is a community integration; account permissions, model availability, subscription limits, and terms of service are determined by the providers. It does not imply official provider support for third-party Claude Code workflows.

## Features

- Starts a local proxy on demand and supports multiple sessions; the proxy keeps running after Claude exits.
- Reuses a Codex ChatGPT login without modifying it, or supports independent OAuth login through CLIProxyAPI.
- Configurable default model, model aliases, subagent model, and reasoning effort.
- Appends an engineering prompt to regular sessions, with explicit custom prompts taking precedence.
- Implemented with the Python standard library; the installer does not download dependencies, log in, or modify shell configuration.
- No separately billed API key fallback, bundled credentials, or third-party binaries.

## Requirements and compatibility

Requires Python 3.10+, a `claude` command on `PATH`, and a CLIProxyAPI executable. See the [official Claude Code quickstart](https://code.claude.com/docs/en/quickstart) for installation instructions. Subscription requests require a ChatGPT account with the relevant access.

Validation environment: macOS ARM64, Python 3.14, and Claude Code 2.1.295. CLIProxyAPI 8.0.23 passed the isolated OAuth and model-catalog tests; those tests do not exercise live model inference or tool round trips. Offline CI covers macOS and Linux, but live proxy/model use on Linux remains unverified. Native Windows is unsupported because the launcher uses `fcntl` and Unix process interfaces. Verify compatibility after upgrading the proxy or Claude Code.

## Installation

1. Get the source:

   ```sh
   git clone https://github.com/LcpMarvel/oclaude.git
   cd oclaude
   python3 --version
   claude --version
   ```

2. From the CLIProxyAPI [official releases](https://github.com/router-for-me/CLIProxyAPI/releases), select the **latest stable release** (excluding drafts and prereleases). Download the package for your operating system and CPU architecture, together with `checksums.txt` from the **same version**. The tested version is available at [v8.0.23](https://github.com/router-for-me/CLIProxyAPI/releases/tag/v8.0.23). Source archives are not executable release packages.

   Before extracting, check that the package's SHA-256 matches its entry in `checksums.txt`:

   ```sh
   # macOS: replace with the actual downloaded filename
   shasum -a 256 /path/to/downloaded-archive.tar.gz
   # Linux
   sha256sum /path/to/downloaded-archive.tar.gz
   ```

   After verification, extract the package and locate the `cli-proxy-api` executable. Keep the upstream `LICENSE` in the same directory; the installer copies it when present.

3. Run the installer from the source directory, passing the path to the verified and extracted executable:

   ```sh
   python3 install.py /path/to/cli-proxy-api
   export PATH="$HOME/.local/bin:$PATH"
   oclaude --version
   ```

   To make the command available in future terminals, add the `export PATH=...` line above to your shell startup file, such as `~/.zshrc` for zsh or `~/.bashrc` for bash. The installer does not edit those files.

Installed files:

| File | Installation location |
| --- | --- |
| Launcher | `~/.local/bin/oclaude` |
| CLIProxyAPI | `~/.local/lib/oclaude/cli-proxy-api` |
| Default appended prompt | `~/.local/lib/oclaude/openai-system-prompt.md` |
| Upstream license (when the source file exists) | `~/.local/lib/oclaude/CLIProxyAPI-LICENSE` |

After updating the source or default prompt, rerun the installer and start a new session. Before updating the proxy, finish any related tasks and run `oclaude --oclaude-stop`.

## Login and usage

If you already have a Codex ChatGPT login, run:

```sh
oclaude
oclaude -p 'Explain the entry point of this project'
oclaude --model gpt-6.1-sol --effort high
oclaude --model fable
oclaude --model sonnet
oclaude --model haiku
oclaude --continue
```

The launcher reads `~/.codex/auth.json` by default, or `auth.json` under `CODEX_HOME` when set. The login mode must be `chatgpt`. On each launch, it syncs a valid access token into the proxy's private directory. **It does not modify the Codex login file or copy the Codex refresh token.**

If no usable Codex login is available, or you want the proxy to refresh its own tokens:

```sh
oclaude --oclaude-stop
oclaude --oclaude-login
oclaude
```

CLIProxyAPI initiates login, usually opening a browser. Choose the ChatGPT account whose allowance you want to use. The proxy saves and refreshes this independent authorization, which takes precedence over reusing a Codex login. `--oclaude-setup` is an alias for the same login entry point. See the [CLIProxyAPI Codex OAuth documentation](https://help.router-for.me/configuration/provider/codex).

Reuse mode holds only the current access token. When it expires, open Codex to refresh the login, then restart `oclaude`. Independent OAuth login is available for long-running background tasks. It uses the selected account's permissions and allowance; check the account and workspace you select.

### Model mapping

| Slot / alias | Default model |
| --- | --- |
| Main session, `sonnet`, `opus` | `gpt-6.1-sol` |
| `fable` | `gpt-6-astra` |
| `haiku`, fast tasks | `gpt-6-luna` |
| Subagents without an explicit model | `gpt-6.1-sol` |

Regular sessions receive `high` when `--effort` is not specified. `--model` and `--effort` override the current session; environment variables change the default slots. Explicit models in subagent definitions or invocations still take precedence. Model availability depends on the proxy catalog and account permissions.

### Appended engineering prompt

Regular interactive and `-p` sessions append [openai-system-prompt.md](openai-system-prompt.md) by default, preserving Claude Code's native system prompt and tool rules. The prompt emphasizes inspecting actual inputs and the full behavior chain, proceeding autonomously with routine decisions, focused verification, and accurate reporting of results and blockers. It does not change login, model mapping, or permission mode, and does not guarantee model compliance.

When any of the following flags is explicitly supplied, the launcher skips default prompt injection and preserves the user's setting. The `--flag=value` form is supported:

- `--system-prompt`
- `--system-prompt-file`
- `--append-system-prompt`
- `--append-system-prompt-file`

For example:

```sh
oclaude --append-system-prompt-file ./my-prompt.md
```

To apply both the default policy and a custom policy, combine them in one file and pass it explicitly. Running from source reads the prompt in the source directory; the installed command reads the installed copy. Reinstall after changing the source prompt.

`--continue` / `--resume` may retain the system prompt recorded when the session first started, until compaction updates it. Prefer a new session when verifying prompt changes; the launcher does not change snapshot settings. See [Claude Code's notes on resumed conversations](https://code.claude.com/docs/en/cli-reference#system-prompt-flags-in-resumed-conversations).

## Configuration

Set environment variables in your terminal, or create `~/.config/oclaude/env` (under `oclaude/env` in `XDG_CONFIG_HOME` when set). Environment variables take precedence over the file. The file supports only simple `NAME=value` entries and does not execute shell expressions. It must be readable and writable only by the current user:

```sh
mkdir -p "$HOME/.config/oclaude"
(umask 077; touch "$HOME/.config/oclaude/env")
chmod 600 "$HOME/.config/oclaude/env"
```

A configuration file is optional, and no key is required. Example contents:

```dotenv
OCLAUDE_MODEL=gpt-6.1-sol
OCLAUDE_EFFORT=high
OCLAUDE_PORT=18317
```

| Variable | Default / purpose |
| --- | --- |
| `OCLAUDE_MODEL` | `gpt-6.1-sol` |
| `OCLAUDE_FABLE_MODEL` | `gpt-6-astra` |
| `OCLAUDE_OPUS_MODEL` | `gpt-6.1-sol` |
| `OCLAUDE_SONNET_MODEL` | `gpt-6.1-sol` |
| `OCLAUDE_HAIKU_MODEL` | `gpt-6-luna` |
| `OCLAUDE_FAST_MODEL` | Same as the Haiku mapping |
| `OCLAUDE_SUBAGENT_MODEL` | Same as the Sonnet mapping |
| `OCLAUDE_EFFORT` | `high` |
| `OCLAUDE_CONTEXT_WINDOW` | `272000`; a positive integer controlling Claude Code's context window setting, with automatic compaction retained |
| `OCLAUDE_CODEX_AUTH_FILE` | `$CODEX_HOME/auth.json`, defaulting to `~/.codex/auth.json` |
| `OCLAUDE_PROXY_URL` | Optional upstream network proxy |
| `OCLAUDE_PORT` | `18317`, bound only to `127.0.0.1` |
| `OCLAUDE_API_TIMEOUT_MS` | `3000000` |
| `OCLAUDE_STATE_DIR` | `~/.local/state/oclaude`; set only through the terminal environment |
| `OCLAUDE_KEYS_FILE` | Preferences file path, retaining the legacy name; set only through the terminal environment |
| `OCLAUDE_PROXY_BIN` | Custom CLIProxyAPI path; otherwise searches `PATH`, then the installed copy |

`272000` is a configurable default, **not a hard API limit for all OpenAI models**. Before increasing it, check the limits of the actual subscription endpoint, model, and proxy. Before changing the port, upstream network proxy, or login method, finish related tasks and stop the proxy. Existing sessions must restart to load new settings.

## Management and troubleshooting

```sh
oclaude agents --json       # Pass through a Claude Code management command
oclaude --oclaude-status    # Check local proxy status
oclaude --oclaude-stop      # Stop the proxy, keeping the OAuth login
```

The proxy does not exit automatically with a Claude session, and no startup service is installed. Stopping the proxy interrupts ongoing requests. `--help` / `--version` are passed directly to Claude Code. Other recognized management commands receive no session effort or prompt flags, but still go through login and proxy preparation.

| Problem | What to do |
| --- | --- |
| `oclaude: command not found` | Add `~/.local/bin` to `PATH`, or use the full command path |
| `claude` / CLIProxyAPI not found | Check `PATH`; use `OCLAUDE_PROXY_BIN` to point to an installed proxy executable |
| Login missing, wrong login mode, or expired token | Use `--oclaude-login`, or let Codex refresh its ChatGPT login first |
| Configuration file permissions are too broad | Run `chmod 600` on the configuration file |
| Port already in use | Check the process using it first; set `OCLAUDE_PORT` to a free port if needed |
| Proxy startup fails, model catalog missing, or `unknown provider for model` | Inspect `proxy.log` in the state directory locally; finish tasks, stop and restart the proxy, and check versions, network, and model names |
| GPT model not in Claude Code's built-in catalog warning | It may be a catalog recognition warning; use an actual request to check success, and check the context window setting |
| Default prompt file missing | Rerun the installer from the source directory |
| Old `OCLAUDE_API_KEY` / `OCLAUDE_BASE_URL` rejected | Remove the old configuration; this project supports subscription login only |

On startup, the proxy fetches its maintainer's public model catalog and waits for the default model to register. Initial startup needs network access; upstream or model name changes may require a proxy restart. When reporting an issue, provide only versions, sanitized errors, and reproduction steps. Do not upload login files, the entire state directory, or unchecked logs.

## Development and tests

The source directory contains the Python launcher `oclaude`, installer `install.py`, shared prompt, and focused tests. Run from source with `python3 ./oclaude`; dependencies must already be available, or specify the proxy with `OCLAUDE_PROXY_BIN`.

```sh
# Offline unit tests: argument passthrough, prompt overrides, installed copies, etc.
python3 -m unittest -v test_prompt.py

# Integration tests: require a real proxy binary and network; use fictional tokens to fetch the public model catalog
python3 test_oclaude.py /path/to/cli-proxy-api
```

Integration tests use a temporary state directory and a fake Claude command. They do not run model inference or use a real account. They check subscription configuration, API key isolation, read-only token sync, refresh tokens not being copied, the model catalog, effort, prompt flags, and management arguments. They cannot establish real account allowance, tool-call compatibility, or support for every Claude Code feature.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributions and [SECURITY.md](SECURITY.md) for reporting security issues.

## Privacy and limitations

The default state directory is `~/.local/state/oclaude`, with mode `700`; generated configuration and token files have mode `600`. The Claude process uses a random local proxy token, and the launcher removes inherited OpenAI, Anthropic, and related credential variables. Proxy remote management, the management panel, usage statistics, and request logging are disabled. Proxy process output is still saved, and Claude Code may also save session records.

Request content goes through the local proxy to the subscription service; inference is not offline. The launcher does not rewrite the global configuration or permission mode of regular `claude`. Manage Claude Code permissions, project settings, and external tools according to your use. Independent OAuth login stores credentials locally so the proxy can refresh tokens; reuse mode does not copy the Codex refresh token.

`OPENAI_API_KEY` is not used as a request credential, and there is no separately billed API fallback. Actual allowance deductions and model access are determined by the subscription service. Claude's dollar cost estimate does not represent an OpenAI API bill. Changes to upstream subscription endpoints, model catalogs, or Claude Code behavior may affect compatibility.

## License

This project uses the [MIT License](LICENSE). CLIProxyAPI and Claude Code each remain subject to their upstream licenses and terms of service. This repository does not distribute their binaries or login credentials.
