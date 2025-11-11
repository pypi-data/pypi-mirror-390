import argparse
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from codexpp import cli
from codexpp.models import CommandDefinition, CommandParameter, PersonaDefinition
from typing import Dict


class RenderPromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.command = CommandDefinition(
            identifier="demo",
            title="Demo Command",
            summary="",
            prompt="Hello {{ name }}!\nLiteral \\{{ brace }}",
            parameters={
                "name": CommandParameter(
                    name="name",
                    description="Person name",
                    required=True,
                ),
            },
        )

    def test_render_prompt_supports_whitespace_placeholders(self) -> None:
        result = cli._render_prompt(self.command, {"name": "Codex"})
        self.assertIn("Hello Codex!", result)
        self.assertIn("Literal {{ brace }}", result)

    def test_render_prompt_unknown_placeholder_raises(self) -> None:
        bad_command = CommandDefinition(
            identifier="broken",
            title="Broken",
            summary="",
            prompt="Hi {{ missing }}",
            parameters={},
        )
        with self.assertRaises(cli.CodexppError):
            cli._render_prompt(bad_command, {})

    def test_validate_override_keys_detects_unknown(self) -> None:
        with self.assertRaises(cli.CodexppError):
            cli._validate_override_keys(self.command, {"unknown": "value"})


class PersonaUtilitiesTests(unittest.TestCase):
    def test_collect_personas_filters_and_validates(self) -> None:
        personas_map = {
            "alpha": PersonaDefinition(
                identifier="alpha",
                label="Alpha",
                summary="",
                directives=[],
            ),
            "beta": PersonaDefinition(
                identifier="beta",
                label="Beta",
                summary="",
                directives=[],
            ),
        }
        selected = cli._collect_personas(personas_map, ["beta"])
        self.assertEqual(1, len(selected))
        self.assertEqual("beta", selected[0].identifier)

        with self.assertRaises(cli.CodexppError):
            cli._collect_personas(personas_map, ["gamma"])

    def test_render_personas_markdown_contains_directives(self) -> None:
        persona = PersonaDefinition(
            identifier="reviewer",
            label="Reviewer",
            summary="Reviews changes.",
            directives=["Check tests"],
        )
        markdown = cli._render_personas_markdown([persona])
        self.assertIn("## Reviewer (`reviewer`)", markdown)
        self.assertIn("- Check tests", markdown)

    def test_personas_sync_writes_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            agents_path = project_dir / "AGENTS.md"
            codex_path = project_dir / "codex_agents.md"

            args = SimpleNamespace(
                project=project_dir,
                personas=[],
                output="AGENTS.md",
                codex_output=str(codex_path),
                force=True,
                show_diff=False,
                diff_color="auto",
            )
            with redirect_stdout(io.StringIO()):
                cli._handle_personas_sync(args)

            self.assertTrue(agents_path.exists())
            self.assertTrue(codex_path.exists())
            self.assertIn("# Codex Personas", agents_path.read_text())
            self.assertEqual(agents_path.read_text(), codex_path.read_text())

    def test_personas_sync_diff_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            agents_path = project_dir / "AGENTS.md"
            agents_path.write_text("Old personas\n", encoding="utf-8")

            args = SimpleNamespace(
                project=project_dir,
                personas=[],
                output="AGENTS.md",
                codex_output="-",
                force=True,
                show_diff=True,
                diff_color="never",
            )

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                cli._handle_personas_sync(args)

            output = buffer.getvalue()
            self.assertIn("---", output)
            self.assertIn("+++", output)
            self.assertIn("# Codex Personas", agents_path.read_text())
            self.assertNotIn("\033[32m", output)

    def test_personas_sync_color_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            agents_path = project_dir / "AGENTS.md"
            agents_path.write_text("Old personas\n", encoding="utf-8")

            args = SimpleNamespace(
                project=project_dir,
                personas=[],
                output="AGENTS.md",
                codex_output="-",
                force=True,
                show_diff=True,
                diff_color="always",
            )

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                cli._handle_personas_sync(args)

            output = buffer.getvalue()
            self.assertIn("\033[32m", output)


class CommandLineIntegrationTests(unittest.TestCase):
    def test_commands_render_outputs_prompt(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["commands", "render", "cx:analyze", "--set", "target=src/"])

        rendered = buffer.getvalue()
        self.assertIn("Target scope: src/", rendered)

    def test_commands_run_summary_only(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(
                [
                    "commands",
                    "run",
                    "cx:analyze",
                    "--set",
                    "target=src/",
                    "--summary-only",
                ]
            )

        output = buffer.getvalue()
        self.assertIn("== Komut Özeti ==", output)
        self.assertNotIn("Analyze the target scope", output)

    def test_commands_run_json_summary(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(
                [
                    "commands",
                    "run",
                    "cx:analyze",
                    "--set",
                    "target=src/",
                    "--summary",
                    "--summary-only",
                    "--summary-format",
                    "json",
                ]
            )

        data = json.loads(buffer.getvalue())
        self.assertEqual("cx:analyze", data["command"]["id"])
        self.assertEqual("src/", data["parameters"]["target"])
        self.assertEqual("önizleme", data["run_mode"])

    def test_commands_run_markdown_summary(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(
                [
                    "commands",
                    "run",
                    "cx:analyze",
                    "--set",
                    "target=src/",
                    "--summary",
                    "--summary-only",
                    "--summary-format",
                    "markdown",
                ]
            )

        output = buffer.getvalue()
        self.assertIn("### Parametreler", output)
        self.assertIn("- target: src/", output)

    def test_commands_run_save_summary_and_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.txt"
            prompt_path = Path(tmpdir) / "prompt.txt"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                cli.main(
                    [
                        "commands",
                        "run",
                        "cx:analyze",
                        "--set",
                        "target=src/",
                        "--summary",
                        "--summary-format",
                        "text",
                        "--save-summary",
                        str(summary_path),
                        "--save-prompt",
                        str(prompt_path),
                        "--print-only",
                    ]
                )

            self.assertTrue(summary_path.exists())
            self.assertTrue(prompt_path.exists())


class CodexCommandTests(unittest.TestCase):
    @patch("codexpp.cli.shutil.which", return_value=None)
    def test_codex_status_missing(self, mock_which) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["codex", "status"])

        output = buffer.getvalue()
        self.assertIn("Codex CLI bulunamadı", output)
        mock_which.assert_called_once()

    @patch("codexpp.cli.subprocess.run")
    @patch("codexpp.cli.shutil.which", return_value="/usr/bin/codex")
    def test_codex_status_success(self, mock_which, mock_run) -> None:
        mock_run.return_value = SimpleNamespace(stdout="codex 0.56.0\n", stderr="")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["codex", "status"])

        output = buffer.getvalue()
        self.assertIn("/usr/bin/codex", output)
        self.assertIn("codex 0.56.0", output)
        mock_run.assert_called_once()

    @patch("codexpp.cli._handle_personas_sync")
    @patch("codexpp.cli.shutil.which", return_value="/usr/bin/codex")
    def test_codex_setup_invokes_personas_sync(self, mock_which, mock_sync) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(
                [
                    "codex",
                    "setup",
                    "--persona",
                    "system-architect",
                    "--force",
                    "--diff-color",
                    "never",
                ]
            )

        mock_sync.assert_called_once()
        sync_args = mock_sync.call_args[0][0]
        self.assertEqual(["system-architect"], sync_args.personas)
        self.assertTrue(sync_args.force)
        self.assertEqual("never", sync_args.diff_color)
        self.assertIn("Codex CLI ile çalışmaya hazırsınız", buffer.getvalue())


class CommandPackTests(unittest.TestCase):
    def test_commands_packs_list(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["commands", "packs", "list"])

        output = buffer.getvalue()
        self.assertIn("extended", output)
        self.assertIn("ops", output)

    def test_commands_packs_install_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                cli.main(
                    [
                        "-p",
                        str(project_dir),
                        "commands",
                        "packs",
                        "install",
                        "extended",
                        "--force",
                    ]
                )
            pack_path = project_dir / ".codexpp" / "commands" / "extended.toml"
            self.assertTrue(pack_path.exists())

    def test_commands_list_verbose_displays_parameters(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["commands", "list", "--verbose"])

        output = buffer.getvalue()
        self.assertIn("Parametreler:", output)

    @patch("codexpp.cli.shutil.which", return_value="/usr/bin/codex")
    def test_codex_install_updates_config_and_prompts(self, mock_which) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            prompts_dir = Path(tmpdir) / "prompts"

            with patch.object(cli, "_sync_codex_prompts") as mock_sync:
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    cli.main(
                        [
                            "codex",
                            "install",
                            "--config",
                            str(config_path),
                            "--include-pack",
                            "extended",
                            "--force",
                        ]
                    )

                mock_sync.assert_called_once()
                called_prompts_dir = mock_sync.call_args.kwargs.get("prompts_dir")
                if called_prompts_dir is None and len(mock_sync.call_args.args) > 1:
                    called_prompts_dir = mock_sync.call_args.args[1]
                self.assertIsNotNone(called_prompts_dir)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                cli.main(
                    [
                        "codex",
                        "install",
                        "--config",
                        str(config_path),
                        "--include-pack",
                        "extended",
                        "--force",
                        "--codex-bin",
                        "/usr/bin/codex",
                    ]
                )

            text = config_path.read_text()
            self.assertIn("# >>> codexpp slash commands", text)
            self.assertIn('cx:analyze', text)
            self.assertIn('cx:plan', text)


class McpCommandTests(unittest.TestCase):
    def test_mcp_packs_list(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["mcp", "packs", "list"])

        output = buffer.getvalue()
        self.assertIn("default", output)

    def test_mcp_packs_install_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                cli.main(
                    [
                        "-p",
                        str(project_dir),
                        "mcp",
                        "packs",
                        "install",
                        "default",
                        "--force",
                    ]
                )

            pack_path = project_dir / ".codexpp" / "mcp" / "default.toml"
            self.assertTrue(pack_path.exists())

    def test_mcp_list_verbose(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["mcp", "list", "--verbose"])

        output = buffer.getvalue()
        self.assertIn("filesystem", output)
        self.assertIn("Komut:", output)

    def test_mcp_setup_writes_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            target_dir = project_dir / "codex-mcp"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                cli.main(
                    [
                        "-p",
                        str(project_dir),
                        "mcp",
                        "setup",
                        "--codex-dir",
                        str(target_dir),
                        "--format",
                        "both",
                        "--force",
                    ]
                )

            json_path = target_dir / "filesystem.json"
            toml_path = target_dir / "filesystem.toml"
            self.assertTrue(json_path.exists())
            self.assertTrue(toml_path.exists())

            data = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual("filesystem", data["id"])
            self.assertEqual("npx", data["command"])


class CodexInitTests(unittest.TestCase):
    @patch("codexpp.cli._handle_mcp_setup")
    @patch("codexpp.cli._handle_mcp_packs_install")
    @patch("codexpp.cli._handle_codex_install")
    @patch("codexpp.cli._handle_codex_setup")
    @patch("codexpp.cli._handle_commands_packs_install")
    @patch("codexpp.cli._handle_bootstrap")
    @patch("codexpp.cli.shutil.which", return_value="/usr/bin/codex")
    def test_codex_init_full_profile(
        self,
        mock_which,
        mock_bootstrap,
        mock_pack_install,
        mock_codex_setup,
        mock_codex_install,
        mock_mcp_install,
        mock_mcp_setup,
    ) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cli.main(["codex", "init", "--force"])

        mock_bootstrap.assert_called_once()
        installed_names = [call.args[0].name for call in mock_pack_install.call_args_list]
        self.assertIn("extended", installed_names)
        self.assertIn("ops", installed_names)
        mcp_installed = [call.args[0].name for call in mock_mcp_install.call_args_list]
        self.assertIn("default", mcp_installed)
        mock_codex_setup.assert_called_once()
        mock_codex_install.assert_called_once()
        mock_mcp_setup.assert_called_once()


class TuiTests(unittest.TestCase):
    def test_tui_session_basic(self) -> None:
        command = CommandDefinition(
            identifier="demo:hello",
            title="Demo Command",
            summary="",
            prompt="Hello {{name}}",
            parameters={
                "name": CommandParameter(
                    name="name",
                    description="Adınız",
                    required=True,
                    default=None,
                    placeholder="NAME",
                )
            },
        )
        commands = {"demo:hello": command}
        personas: Dict[str, PersonaDefinition] = {}
        inputs = iter(["1", "Codex", "", "q"])

        def fake_input(prompt: str = "") -> str:
            return next(inputs)

        with redirect_stdout(io.StringIO()):
            cli._run_tui_session(
                commands,
                personas,
                Path("."),
                allow_exec=False,
                input_fn=fake_input,
            )


if __name__ == "__main__":
    unittest.main()

