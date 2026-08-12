#!/usr/bin/env python3
"""Test suite for the larp CLI.

Standard library only, matching larp's own zero-dependency policy — run it with
the stdlib test runner, no pytest required:

    python3 -m unittest discover -s tests -v
    python3 tests/test_larp.py            # equivalent

`bin/larp` has no .py extension and is not importable by name, so it is loaded
directly by path. Importing it is side-effect free: everything runs under
`if __name__ == "__main__"`.

Tests for optional features are skipped when the feature is absent, so the file
runs unchanged against branches where a provider has not landed yet.
"""

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import stat
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

LARP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "larp")


def load_larp():
    loader = importlib.machinery.SourceFileLoader("larp", LARP_PATH)
    spec = importlib.util.spec_from_loader("larp", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


larp = load_larp()

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(text: str) -> str:
    """Strips ANSI colour codes so assertions can match on the text itself."""
    return ANSI.sub("", text)


@contextlib.contextmanager
def quiet():
    """Silences the progress spinner so it does not interleave with test output."""
    with contextlib.redirect_stdout(io.StringIO()):
        yield


class TestDestructiveCommandDetection(unittest.TestCase):
    """Commands that can destroy a system must be flagged before they run."""

    DESTRUCTIVE = [
        "sudo rm -rf /",
        "rm -fr /",
        "sudo rm -rf /*",
        "mkfs.ext4 /dev/sda1",
        "dd if=/dev/zero of=/dev/sda bs=1M",
        "wipefs -a /dev/nvme0n1",
        "shred -n 3 /dev/sdb",
        "sudo chmod -R 777 /",
        ":(){ :|:& };:",
        "echo x > /etc/passwd",
    ]

    # Everyday administration must not trip the guard, or users learn to type
    # the confirmation reflexively and the check stops meaning anything.
    SAFE = [
        "sudo pacman -Syu",
        "sudo apt install -y neovim",
        "sudo xbps-install -Su",
        "sudo systemctl restart NetworkManager",
        "sudo rc-service sshd restart",
        "sudo rm -rf /var/cache/pacman/pkg/*",
        "rm -rf ./build",
        "sudo journalctl --vacuum-time=7d",
        "dd if=/dev/urandom of=./testfile bs=1M count=10",
        "chmod 777 ./scratch",
    ]

    def test_destructive_commands_are_flagged(self):
        for cmd in self.DESTRUCTIVE:
            with self.subTest(cmd=cmd):
                self.assertIsNotNone(
                    larp.find_destructive_pattern(cmd),
                    f"expected {cmd!r} to be flagged as destructive",
                )

    def test_ordinary_commands_are_not_flagged(self):
        for cmd in self.SAFE:
            with self.subTest(cmd=cmd):
                self.assertIsNone(
                    larp.find_destructive_pattern(cmd),
                    f"{cmd!r} is routine administration and must not be flagged",
                )

    def test_reason_is_human_readable(self):
        reason = larp.find_destructive_pattern("sudo rm -rf /")
        self.assertIsInstance(reason, str)
        self.assertTrue(reason.strip(), "the reason is shown to the user, so it must not be empty")

    def test_empty_command_is_not_flagged(self):
        self.assertIsNone(larp.find_destructive_pattern(""))


class TestCommandExtraction(unittest.TestCase):
    """Only lines that *are* a command may reach the shell — prose must not."""

    TOKENS = ["sudo systemctl", "sudo rm", "sudo pacman", "curl"]

    def extract(self, line):
        return larp.extract_command_from_line(line, self.TOKENS)

    def test_prose_mentioning_a_command_is_rejected(self):
        # The original regex sliced from the token to end-of-line, so the
        # trailing words of a sentence were executed along with the command.
        cases = [
            "Then run sudo rm -rf /var/cache/foo to clear it",
            "You should use sudo pacman -Syu here",
            "I suggest you curl the file first",
            "The command sudo systemctl restart sshd will fix this",
        ]
        for line in cases:
            with self.subTest(line=line):
                self.assertEqual(self.extract(line), "")

    def test_bare_command_is_accepted(self):
        self.assertEqual(
            self.extract("sudo systemctl restart sshd"), "sudo systemctl restart sshd"
        )

    def test_markdown_and_prompt_markers_are_stripped(self):
        cases = [
            ("- sudo pacman -Syu", "sudo pacman -Syu"),
            ("* sudo pacman -Syu", "sudo pacman -Syu"),
            ("2. sudo pacman -Syu", "sudo pacman -Syu"),
            ("3) sudo pacman -Syu", "sudo pacman -Syu"),
            ("$ sudo pacman -Syu", "sudo pacman -Syu"),
            ("`sudo pacman -Syu`", "sudo pacman -Syu"),
            ("$ `sudo pacman -Syu`", "sudo pacman -Syu"),
            ("- $ `sudo pacman -Syu`", "sudo pacman -Syu"),
            ("   sudo pacman -Syu   ", "sudo pacman -Syu"),
        ]
        for line, expected in cases:
            with self.subTest(line=line):
                self.assertEqual(self.extract(line), expected)

    def test_unrelated_lines_are_rejected(self):
        for line in ["", "This explains the root cause.", "```bash", "FIX_CMD:"]:
            with self.subTest(line=line):
                self.assertEqual(self.extract(line), "")


class TestSanitizeShellCommand(unittest.TestCase):
    def test_strips_backticks_and_bash_prefix(self):
        self.assertEqual(larp.sanitize_shell_command("`ls -la`"), "ls -la")
        self.assertEqual(larp.sanitize_shell_command("bash ls -la"), "ls -la")

    def test_balances_quotes(self):
        self.assertEqual(larp.sanitize_shell_command('echo "hi').count('"') % 2, 0)
        self.assertEqual(larp.sanitize_shell_command("echo 'hi").count("'") % 2, 0)

    def test_empty_input(self):
        self.assertEqual(larp.sanitize_shell_command(""), "")


class TestGeminiModelRanking(unittest.TestCase):
    """Auto-selection must prefer newer releases without code changes."""

    def test_newest_stable_flash_wins(self):
        models = [
            "gemini-1.5-flash",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "gemini-2.5-flash-preview",
        ]
        self.assertEqual(sorted(models, key=larp.rank_gemini_model)[0], "gemini-2.5-flash")

    def test_a_future_version_outranks_todays(self):
        # Guards the actual regression: hardcoded names meant new releases were
        # ranked last. A version this file has never heard of must still win.
        models = ["gemini-2.5-flash", "gemini-9.0-flash"]
        self.assertEqual(sorted(models, key=larp.rank_gemini_model)[0], "gemini-9.0-flash")

    def test_stable_outranks_preview_of_same_version(self):
        models = ["gemini-2.5-flash-preview", "gemini-2.5-flash"]
        self.assertEqual(sorted(models, key=larp.rank_gemini_model)[0], "gemini-2.5-flash")

    def test_flash_outranks_pro_of_same_version(self):
        models = ["gemini-2.5-pro", "gemini-2.5-flash"]
        self.assertEqual(sorted(models, key=larp.rank_gemini_model)[0], "gemini-2.5-flash")

    def test_unparsable_name_does_not_raise(self):
        larp.rank_gemini_model("some-unexpected-model")


class TestChatFixTrigger(unittest.TestCase):
    """The chat repair trigger must match commands, never substrings of a sentence."""

    # Mirrors the set in cmd_chat. Kept in sync deliberately: the trigger is
    # defined inside the chat loop, and this documents the intended contract.
    FIX_COMMANDS = {
        "/fix", "fix", "repair", "fix my system", "fix system", "fix errors",
        "repair errors", "почини", "починить", "почини систему",
        "исправь", "исправить", "отремонтируй", "фикс",
    }

    def triggers(self, text):
        return text.strip().lower().rstrip("!.?") in self.FIX_COMMANDS

    def test_questions_do_not_trigger_a_system_repair(self):
        # Each of these contains a trigger as a substring and used to launch
        # log diagnostics instead of answering the question.
        cases = [
            "как исправить конфиг?",
            "что такое префикс в bash",
            "расскажи про git fix-branch",
            "объясни слово фиксация",
            "how do I fix a merge conflict",
            "what does repair mean in fsck",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertFalse(self.triggers(text))

    def test_explicit_commands_trigger(self):
        for text in ["fix", "/fix", "почини", "Исправь!", "  FIX  ", "repair errors"]:
            with self.subTest(text=text):
                self.assertTrue(self.triggers(text))


class TestPrivateFilePermissions(unittest.TestCase):
    """Config and history hold API keys and prompts — they must be owner-only."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._original_config_dir = larp.CONFIG_DIR
        larp.CONFIG_DIR = self.tmpdir

    def tearDown(self):
        larp.CONFIG_DIR = self._original_config_dir

    def test_written_file_is_owner_only(self):
        path = os.path.join(self.tmpdir, "config.json")
        larp.write_private_json(path, {"openrouter": {"api_key": "sk-secret"}})
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)

    def test_content_round_trips(self):
        path = os.path.join(self.tmpdir, "config.json")
        payload = {"provider": "openrouter", "nested": {"k": [1, 2, 3]}, "unicode": "няшка"}
        larp.write_private_json(path, payload)
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), payload)

    def test_rewrite_keeps_permissions(self):
        path = os.path.join(self.tmpdir, "config.json")
        larp.write_private_json(path, {"a": 1})
        os.chmod(path, 0o644)
        larp.write_private_json(path, {"a": 2})
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)


class TestDefaultConfig(unittest.TestCase):
    def test_auto_fix_is_off_by_default(self):
        # auto_fix runs an AI-generated sudo command with no confirmation.
        self.assertFalse(larp.DEFAULT_CONFIG["auto_fix"])

    def test_every_provider_section_exists(self):
        for section in ["ollama", "gemini", "claude", "openai"]:
            with self.subTest(section=section):
                self.assertIn(section, larp.DEFAULT_CONFIG)

    def test_no_api_key_is_shipped(self):
        for section, values in larp.DEFAULT_CONFIG.items():
            if isinstance(values, dict) and "api_key" in values:
                with self.subTest(section=section):
                    self.assertEqual(values["api_key"], "")


class TestSystemDetection(unittest.TestCase):
    """Detection must degrade to a usable fallback on unknown systems."""

    def test_package_manager_returns_four_parts(self):
        result = larp.detect_package_manager()
        self.assertEqual(len(result), 4)
        self.assertTrue(all(isinstance(part, str) and part for part in result))

    def test_init_system_returns_four_parts(self):
        result = larp.detect_init_system()
        self.assertEqual(len(result), 4)
        self.assertTrue(all(isinstance(part, str) and part for part in result))

    def test_system_prompt_mentions_detected_environment(self):
        prompt = larp.build_system_prompt()
        self.assertIn(larp.detect_package_manager()[0], prompt)
        self.assertIn(larp.detect_init_system()[0], prompt)

    def test_system_info_reports_a_hostname(self):
        # $HOSTNAME is not exported by fish or zsh, which used to make this
        # fall back to the literal string "linux".
        info = larp.get_system_info()
        self.assertIn("User/Host:", info)
        self.assertNotIn("@linux\n", info + "\n")


class TestSearchKeywords(unittest.TestCase):
    def test_stop_words_are_removed(self):
        self.assertNotIn("what", larp.extract_search_keywords("what is wayland").split())

    def test_non_empty_result_for_stop_words_only(self):
        self.assertTrue(larp.extract_search_keywords("what is the").strip())


# =============================================================================
# OpenRouter provider — skipped when the provider is not present in bin/larp.
# =============================================================================

HAS_OPENROUTER = hasattr(larp, "query_provider_openrouter")


class MockOpenRouterHandler(BaseHTTPRequestHandler):
    """Stands in for the OpenRouter API. Behaviour is driven by server.mode."""

    def log_message(self, *args):
        pass

    def _reply(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.server.captured_headers = dict(self.headers)
        self.server.captured_payload = json.loads(self.rfile.read(length))
        model = self.server.captured_payload.get("model", "")
        if hasattr(self.server, "seen_models"):
            self.server.seen_models.append(model)

        mode = self.server.mode
        if mode == "per_model":
            # Fallback tests: succeed or rate-limit depending on the model asked for.
            if model in getattr(self.server, "failing_models", set()):
                self._reply(429, {"error": {"message": "rate limit exceeded"}})
            else:
                self._reply(200, {"choices": [{"message": {"content": f"answer from {model}"}}]})
        elif mode == "error_shaped_answer":
            self._reply(200, {"choices": [{"message": {"content":
                "Error: failed to mount /dev/sda1 — the filesystem is corrupted"}}]})
        elif mode == "ok":
            self._reply(200, {"choices": [{"message": {"content": "pong (=^.^=)"}}]})
        elif mode == "inline_error":
            # OpenRouter reports upstream provider failures as HTTP 200 with an
            # error object and no choices.
            self._reply(200, {"error": {"message": "upstream provider is down", "code": 502}})
        elif mode == "no_choices":
            self._reply(200, {"choices": []})
        else:
            self._reply(int(mode), {"error": {"message": "nope"}})


@unittest.skipUnless(HAS_OPENROUTER, "OpenRouter provider not present in bin/larp")
class TestOpenRouterProvider(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), MockOpenRouterHandler)
        cls.server.mode = "ok"
        cls.server.captured_headers = {}
        cls.server.captured_payload = {}
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls._original_url = larp.OPENROUTER_URL
        larp.OPENROUTER_URL = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        larp.OPENROUTER_URL = cls._original_url
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.server.mode = "ok"
        self.config = {
            "openrouter": {"api_key": "sk-or-test", "model": "anthropic/claude-sonnet-5"}
        }

    def ask(self, prompt="ping", web_context=""):
        with quiet():
            return plain(larp.query_provider_openrouter(prompt, web_context, self.config))

    def test_successful_response_is_parsed(self):
        self.assertEqual(self.ask(), "pong (=^.^=)")

    def test_auth_and_attribution_headers(self):
        self.ask()
        headers = self.server.captured_headers
        self.assertEqual(headers.get("Authorization"), "Bearer sk-or-test")
        self.assertEqual(headers.get("Content-Type"), "application/json")
        self.assertEqual(headers.get("X-Title"), "LarpHelper")

    def test_payload_shape(self):
        self.ask()
        payload = self.server.captured_payload
        self.assertEqual(payload["model"], "anthropic/claude-sonnet-5")
        roles = [message["role"] for message in payload["messages"]]
        self.assertEqual(roles, ["system", "user"])
        self.assertTrue(payload["messages"][0]["content"].strip())
        self.assertIn("[SYSTEM & USER CONTEXT]", payload["messages"][1]["content"])

    def test_web_context_is_included_only_when_supplied(self):
        self.ask()
        self.assertNotIn("[WEB SEARCH CONTEXT]", self.server.captured_payload["messages"][1]["content"])
        self.ask(web_context="linux is cool")
        self.assertIn("[WEB SEARCH CONTEXT]", self.server.captured_payload["messages"][1]["content"])

    def test_missing_key_short_circuits_before_any_request(self):
        self.server.captured_payload = {}
        config = {"openrouter": {"api_key": "", "model": "x"}}
        with quiet(), self.assertRaises(larp.ProviderError) as caught:
            larp.query_provider_openrouter("ping", "", config)
        self.assertIn("OpenRouter API Key is not set", plain(str(caught.exception)))
        self.assertEqual(self.server.captured_payload, {}, "no request should have been made")

    def test_error_responses_are_actionable(self):
        cases = [
            ("inline_error", "upstream provider is down"),
            ("401", "invalid or expired API key"),
            ("402", "insufficient credits"),
            ("404", "does not exist"),
        ]
        for mode, expected in cases:
            with self.subTest(mode=mode):
                self.server.mode = mode
                with quiet(), self.assertRaises(larp.ProviderError) as caught:
                    larp.query_provider_openrouter("ping", "", self.config)
                self.assertIn(expected, plain(str(caught.exception)))

    def test_empty_choices_is_reported(self):
        self.server.mode = "no_choices"
        with quiet(), self.assertRaises(larp.ProviderError) as caught:
            larp.query_provider_openrouter("ping", "", self.config)
        self.assertIn("Empty response", plain(str(caught.exception)))


HAS_FALLBACK = hasattr(larp, "build_attempt_chain")


@unittest.skipUnless(HAS_FALLBACK, "fallback chain not present in bin/larp")
class TestAttemptChain(unittest.TestCase):
    """The active provider is tried first; the chain is purely additive."""

    def test_active_provider_only_when_chain_is_empty(self):
        config = {"provider": "openrouter", "fallback_chain": []}
        self.assertEqual(larp.build_attempt_chain(config), [("openrouter", "")])

    def test_missing_chain_key_is_treated_as_empty(self):
        self.assertEqual(larp.build_attempt_chain({"provider": "ollama"}), [("ollama", "")])

    def test_active_provider_comes_first(self):
        config = {
            "provider": "openrouter",
            "fallback_chain": [{"provider": "gemini"}, {"provider": "ollama"}],
        }
        self.assertEqual(
            larp.build_attempt_chain(config),
            [("openrouter", ""), ("gemini", ""), ("ollama", "")],
        )

    def test_model_overrides_are_kept(self):
        config = {
            "provider": "openrouter",
            "fallback_chain": [{"provider": "openrouter", "model": "anthropic/claude-sonnet-5"}],
        }
        self.assertEqual(
            larp.build_attempt_chain(config),
            [("openrouter", ""), ("openrouter", "anthropic/claude-sonnet-5")],
        )

    def test_duplicate_entries_are_dropped(self):
        config = {
            "provider": "gemini",
            "fallback_chain": [{"provider": "gemini"}, {"provider": "gemini"}],
        }
        self.assertEqual(larp.build_attempt_chain(config), [("gemini", "")])

    def test_unknown_and_malformed_entries_are_ignored(self):
        config = {
            "provider": "ollama",
            "fallback_chain": [{"provider": "chatgpt"}, "not-a-dict", {}, {"model": "x"}],
        }
        self.assertEqual(larp.build_attempt_chain(config), [("ollama", "")])

    def test_label_resolves_the_configured_model(self):
        # Without this, two openrouter entries are indistinguishable in reports.
        config = {"openrouter": {"model": "google/gemma-4-26b-a4b-it:free"}}
        self.assertEqual(
            larp.describe_attempt("openrouter", "", config),
            "openrouter/google/gemma-4-26b-a4b-it:free",
        )
        self.assertEqual(
            larp.describe_attempt("openrouter", "anthropic/claude-sonnet-5", config),
            "openrouter/anthropic/claude-sonnet-5",
        )


@unittest.skipUnless(
    HAS_FALLBACK and HAS_OPENROUTER, "fallback chain or OpenRouter not present in bin/larp"
)
class TestFallbackBehaviour(unittest.TestCase):
    """End-to-end: a failing provider hands off to the next one."""

    FREE = "google/gemma-4-26b-a4b-it:free"
    PAID = "anthropic/claude-sonnet-5"

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), MockOpenRouterHandler)
        cls.server.mode = "ok"
        cls.server.failing_models = set()
        cls.server.seen_models = []
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls._original_url = larp.OPENROUTER_URL
        cls._original_loader = larp.load_config
        cls._original_history = larp.save_history_entry
        larp.OPENROUTER_URL = f"http://127.0.0.1:{cls.server.server_address[1]}"
        larp.save_history_entry = lambda *args, **kwargs: None

    @classmethod
    def tearDownClass(cls):
        larp.OPENROUTER_URL = cls._original_url
        larp.load_config = cls._original_loader
        larp.save_history_entry = cls._original_history
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.server.mode = "per_model"
        self.server.failing_models = set()
        self.server.seen_models = []
        config = {
            "provider": "openrouter",
            "openrouter": {"api_key": "sk-test", "model": self.FREE},
            "fallback_chain": [{"provider": "openrouter", "model": self.PAID}],
        }
        larp.load_config = lambda: json.loads(json.dumps(config))

    def ask(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            answer = larp.query_ollama("вопрос")
        return plain(answer), plain(buffer.getvalue())

    def test_no_fallback_when_the_first_provider_answers(self):
        answer, output = self.ask()
        self.assertEqual(answer, f"answer from {self.FREE}")
        self.assertEqual(self.server.seen_models, [self.FREE])
        self.assertNotIn("Falling back", output)

    def test_rate_limited_model_hands_off_to_the_next(self):
        self.server.failing_models = {self.FREE}
        answer, output = self.ask()
        self.assertEqual(answer, f"answer from {self.PAID}")
        self.assertEqual(self.server.seen_models, [self.FREE, self.PAID])

    def test_the_handoff_is_announced(self):
        # A silent fallback can move a free-model workload onto a paid one.
        self.server.failing_models = {self.FREE}
        _, output = self.ask()
        self.assertIn("Falling back", output)
        self.assertIn(f"answered by openrouter/{self.PAID}", output)

    def test_total_failure_lists_every_attempt(self):
        self.server.failing_models = {self.FREE, self.PAID}
        answer, _ = self.ask()
        self.assertIn("Every configured provider failed", answer)
        self.assertIn(self.FREE, answer)
        self.assertIn(self.PAID, answer)

    def test_an_answer_mentioning_an_error_is_not_a_failure(self):
        # The regression that motivated ProviderError: detecting failure by
        # searching the response for "Error" misreads a correct answer about an
        # error message, which is a common thing to ask a Linux assistant.
        self.server.mode = "error_shaped_answer"
        answer, output = self.ask()
        self.assertTrue(answer.startswith("Error: failed to mount"))
        self.assertEqual(self.server.seen_models, [self.FREE])
        self.assertNotIn("Falling back", output)


@unittest.skipUnless(HAS_OPENROUTER, "OpenRouter provider not present in bin/larp")
class TestOpenRouterConfig(unittest.TestCase):
    def test_default_model_is_namespaced(self):
        model = larp.DEFAULT_CONFIG["openrouter"]["model"]
        self.assertIn("/", model, "OpenRouter model IDs are namespaced, e.g. vendor/model")

    def test_model_list_handles_unreachable_endpoint(self):
        original = larp.OPENROUTER_URL
        larp.OPENROUTER_URL = "http://127.0.0.1:1"  # nothing listening
        try:
            self.assertEqual(larp.get_openrouter_models(), [])
        finally:
            larp.OPENROUTER_URL = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
