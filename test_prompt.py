"""Offline checks for prompt injection, launcher dispatch, and installed assets."""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent


def load_launcher(path):
    loader = SourceFileLoader('oclaude_launcher', str(path))
    module = module_from_spec(spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


launcher = load_launcher(ROOT / 'oclaude')


class PromptTests(unittest.TestCase):
    def test_sessions_preserve_args_and_add_defaults(self):
        prefix = ['--effort', 'high', '--append-system-prompt-file', str(launcher.PROMPT_FILE)]
        for args in ([], ['-p', 'hello'], ['--continue'], ['--resume', 'session'],
                     ['--model', 'fable'], ['--', '--append-system-prompt', '--effort']):
            with self.subTest(args=args):
                original = args.copy()
                self.assertEqual(launcher.session_args(args, 'high'), prefix + args)
                self.assertEqual(args, original)
        for args in (['--effort', 'low', '-p', 'hello'], ['--effort=low', '-p', 'hello']):
            self.assertEqual(launcher.session_args(args, 'high'), prefix[2:] + args)

    def test_explicit_prompt_settings_override_default(self):
        for flag in launcher.PROMPT_FLAGS:
            for args in ([flag, 'custom', '-p', 'hello'], [flag + '=custom', '-p', 'hello']):
                with self.subTest(args=args):
                    self.assertEqual(launcher.session_args(args, 'high'), ['--effort', 'high'] + args)
        args = ['--effort=low', '--append-system-prompt-file', 'custom.md']
        self.assertEqual(launcher.session_args(args, 'high'), args)

    def test_management_args_are_untouched(self):
        for command in launcher.MANAGEMENT:
            args = [command, '--help']
            with self.subTest(command=command):
                self.assertEqual(launcher.session_args(args, 'high'), args)
        args = ['--dangerously-skip-permissions', 'daemon', 'status']
        self.assertEqual(launcher.session_args(args, 'high'), args)

    def test_missing_asset_fails_before_auth_or_proxy(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(launcher, 'STATE', Path(tmp) / 'state'), \
                 patch.object(launcher, 'PROMPT_FILE', Path(tmp) / 'missing.md'), \
                 patch.object(launcher, 'settings', return_value={}), \
                 patch.object(launcher.shutil, 'which', return_value='/fake/claude'), \
                 patch.object(launcher, 'sync_codex_login') as auth, \
                 patch.object(launcher, 'ensure_proxy') as proxy, \
                 patch.object(sys, 'argv', ['oclaude', '-p', 'hello']):
                with self.assertRaisesRegex(ValueError, '提示词文件'):
                    launcher.main()
                auth.assert_not_called()
                proxy.assert_not_called()
                args = ['--append-system-prompt', 'custom']
                self.assertEqual(launcher.session_args(args, 'high'), ['--effort', 'high'] + args)

    def test_main_passes_prompt_file_to_claude(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(launcher, 'STATE', Path(tmp) / 'state'), \
                 patch.object(launcher, 'settings', return_value={}), \
                 patch.object(launcher.shutil, 'which', return_value='/fake/claude'), \
                 patch.object(launcher, 'sync_codex_login'), \
                 patch.object(launcher, 'ensure_proxy', return_value={'port': 12345, 'api-keys': ['fake']}), \
                 patch.object(launcher, 'healthy', return_value=True), \
                 patch.object(launcher.os, 'execve') as execute, \
                 patch.object(sys, 'argv', ['oclaude', '-p', 'hello']):
                launcher.main()
                binary, args, env = execute.call_args.args
                self.assertEqual(binary, '/fake/claude')
                self.assertEqual(args, [binary, '--effort', 'high', '--append-system-prompt-file',
                                        str(launcher.PROMPT_FILE), '-p', 'hello'])
                self.assertEqual(env['ANTHROPIC_MODEL'], 'gpt-6.1-sol')

    def test_help_and_version_bypass_prompt_and_auth(self):
        for flag in ('--help', '-h', '--version', '-v'):
            with self.subTest(flag=flag), \
                 patch.object(launcher.shutil, 'which', return_value='/fake/claude'), \
                 patch.object(launcher.os, 'execve', side_effect=SystemExit) as execute, \
                 patch.object(launcher, 'settings') as settings, \
                 patch.object(sys, 'argv', ['oclaude', flag]):
                with self.assertRaises(SystemExit):
                    launcher.main()
                self.assertEqual(execute.call_args.args[1], ['/fake/claude', flag])
                settings.assert_not_called()

    def test_install_copies_prompt_and_installed_launcher_finds_it(self):
        with tempfile.TemporaryDirectory(prefix='oclaude-install-test-') as tmp:
            home = Path(tmp).resolve()
            proxy = home / 'fake-proxy'
            proxy.write_text('#!/bin/sh\nexit 0\n')
            env = {**os.environ, 'HOME': str(home)}
            result = subprocess.run([sys.executable, str(ROOT / 'install.py'), str(proxy)],
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed_prompt = home / '.local/lib/oclaude/openai-system-prompt.md'
            self.assertEqual(installed_prompt.read_bytes(), launcher.PROMPT_FILE.read_bytes())
            with patch.dict(os.environ, HOME=str(home)):
                installed = load_launcher(home / '.local/bin/oclaude')
                self.assertEqual(installed.PROMPT_FILE, installed_prompt)
                self.assertIn(str(installed_prompt), installed.session_args(['-p', 'hello'], 'high'))


if __name__ == '__main__':
    unittest.main()
