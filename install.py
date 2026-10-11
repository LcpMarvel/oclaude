#!/usr/bin/env python3
"""Install reviewed local files; no downloads, credentials or shell changes."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parent
if len(sys.argv) != 2:
    sys.exit('Usage: python3 install.py /path/to/verified/cli-proxy-api')
proxy = Path(sys.argv[1]).resolve()
if not proxy.is_file():
    sys.exit('CLIProxyAPI executable not found')
prompt = root / 'openai-system-prompt.md'
if not prompt.is_file():
    sys.exit('openai-system-prompt.md not found')
dest = Path.home() / '.local/lib/oclaude'
dest.mkdir(parents=True, exist_ok=True)
bin_dir = Path.home() / '.local/bin'
bin_dir.mkdir(parents=True, exist_ok=True)
for source, target in [(proxy, dest / 'cli-proxy-api'), (root / 'oclaude', bin_dir / 'oclaude')]:
    if source != target.resolve():
        shutil.copy2(source, target)
    target.chmod(0o755)
shutil.copy2(prompt, dest / prompt.name)
license_file = proxy.parent / 'LICENSE'
if license_file.exists():
    shutil.copy2(license_file, dest / 'CLIProxyAPI-LICENSE')
print('Installed ~/.local/bin/oclaude (gpt-6.1-sol / high). Uses Codex / ChatGPT subscription login; no API key required.')
print('Next: oclaude (or oclaude --oclaude-login)')
