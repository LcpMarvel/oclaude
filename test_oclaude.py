"""Isolated OAuth tests (fetch public catalog, no inference): fake Codex tokens, real CLIProxyAPI model catalog."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def main():
    proxy = str(Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory(prefix='oclaude-oauth-test-') as tmp:
        tmp = Path(tmp)
        env = {k: v for k, v in os.environ.items() if not k.startswith(('OPENAI_', 'OCLAUDE_', 'ANTHROPIC_'))}
        env.update(OCLAUDE_STATE_DIR=str(tmp / 'state'), OCLAUDE_KEYS_FILE=str(tmp / 'env'),
                   OCLAUDE_CODEX_AUTH_FILE=str(tmp / 'codex.json'), OCLAUDE_PROXY_BIN=proxy,
                   OPENAI_API_KEY='MUST-NOT-BE-USED')
        import socket
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            env['OCLAUDE_PORT'] = str(sock.getsockname()[1])
        base = [sys.executable, str(ROOT / 'oclaude')]
        payload = base64.urlsafe_b64encode(json.dumps({'exp': int(time.time()) + 86400}).encode()).decode().rstrip('=')
        auth = {'auth_mode': 'chatgpt', 'tokens': {'access_token': f'fake.{payload}.fake',
                'refresh_token': 'NEVER-COPY-THIS', 'account_id': 'offline-test-account'}}
        source = tmp / 'codex.json'
        fakebin = tmp / 'bin'
        fakebin.mkdir()
        fake = fakebin / 'claude'
        fake.write_text('''#!/usr/bin/env python3
import os,sys,json,urllib.request
from pathlib import Path
assert 'OPENAI_API_KEY' not in os.environ
assert 'OCLAUDE_API_KEY' not in os.environ
assert 'ANTHROPIC_API_KEY' not in os.environ
assert os.environ['ANTHROPIC_MODEL']=='gpt-6.1-sol'
assert os.environ['ANTHROPIC_DEFAULT_OPUS_MODEL']=='gpt-6.1-sol'
assert os.environ['ANTHROPIC_DEFAULT_FABLE_MODEL']=='gpt-6-astra'
assert os.environ['ANTHROPIC_DEFAULT_SONNET_MODEL']=='gpt-6.1-sol'
assert os.environ['ANTHROPIC_DEFAULT_HAIKU_MODEL']=='gpt-6-luna'
assert os.environ['ANTHROPIC_SMALL_FAST_MODEL']=='gpt-6-luna'
assert os.environ['CLAUDE_CODE_SUBAGENT_MODEL']=='gpt-6.1-sol'
assert os.environ['CLAUDE_CODE_EFFORT_LEVEL']=='high'
assert os.environ['CLAUDE_CODE_MAX_CONTEXT_TOKENS']=='272000'
if sys.argv[1:] == ['agents','--json']:
 print('MANAGEMENT_OK');sys.exit()
assert sys.argv[1:3]==['--effort','high'],sys.argv
assert sys.argv[3]=='--append-system-prompt-file',sys.argv
prompt=Path(sys.argv[4])
assert prompt.is_absolute() and 'Engineering Decision and Completion Policy' in prompt.read_text()
req=urllib.request.Request(os.environ['ANTHROPIC_BASE_URL']+'/v1/models',
 headers={'Authorization':'Bearer '+os.environ['ANTHROPIC_AUTH_TOKEN']})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=5) as r:
 models=json.load(r)['data'];assert {'gpt-6-astra','gpt-6.1-sol','gpt-6-luna'} <= {m['id'] for m in models},models
print('OAUTH_CATALOG_OK')
''')
        fake.chmod(0o755)
        env['PATH'] = str(fakebin) + os.pathsep + env['PATH']
        run = subprocess.run(base + ['-p', 'hello'], env=env, capture_output=True, text=True, timeout=15)
        assert run.returncode == 1 and 'Codex 登录' in run.stderr, run.stderr
        assert not (tmp / 'state/config.json').exists()
        source.write_text(json.dumps(auth))
        original = source.read_bytes()
        try:
            for args, expected in [(['-p', 'hello'], 'OAUTH_CATALOG_OK'), (['agents', '--json'], 'MANAGEMENT_OK')]:
                run = subprocess.run(base + args, env=env, capture_output=True, text=True, timeout=25)
                assert run.returncode == 0 and expected in run.stdout, (run.stdout, run.stderr)
            config = json.loads((tmp / 'state/config.json').read_text())
            assert 'codex-api-key' not in config and 'openai-compatibility' not in config
            copied = json.loads((tmp / 'state/auth/codex-imported.json').read_text())
            assert copied['access_token'] == auth['tokens']['access_token']
            assert 'refresh_token' not in copied and 'id_token' not in copied
            assert source.read_bytes() == original
            assert (tmp / 'state/auth/codex-imported.json').stat().st_mode & 0o777 == 0o600
            independent = tmp / 'state/auth/codex-own.json'
            independent.write_text(json.dumps({'type': 'codex', 'access_token': 'offline-independent'}))
            source.unlink()
            run = subprocess.run(base + ['agents', '--json'], env=env, capture_output=True, text=True, timeout=15)
            assert run.returncode == 0, run.stderr
            print('PASS: subscription-only config, no API-key fallback, read-only token import, no refresh-token copy, Astra/Sol/Luna catalog, High, prompt argv, management argv, independent OAuth precedence')
        finally:
            stop = subprocess.run(base + ['--oclaude-stop'], env=env, capture_output=True, timeout=15)
            assert stop.returncode == 0
            assert not (tmp / 'state/config.json').exists()


if __name__ == '__main__':
    main()
