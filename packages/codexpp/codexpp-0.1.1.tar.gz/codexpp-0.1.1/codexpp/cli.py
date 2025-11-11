"""Command-line interface for Codexpp."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
import tomllib
from importlib import resources
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from . import config as cfg
from . import loader
from .models import (
    CommandDefinition,
    CommandParameter,
    McpServerDefinition,
    PersonaDefinition,
)

PLACEHOLDER_PATTERN = re.compile(r"(?<!\\)\{\{\s*([a-zA-Z0-9_\-]+)\s*\}\}")
PROMPT_TEMPLATE_PACKAGES = [
    "codexpp.resources.prompts.default",
    "codexpp.resources.prompts.extended",
    "codexpp.resources.prompts.ops",
]


def _write_text(path: str, content: str) -> Path:
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"[codexpp] Dosya oluşturuldu: {target}")
    return target


def main(argv: List[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return

    try:
        args.func(args)
    except CodexppError as exc:
        print(f"[codexpp] {exc}", file=sys.stderr)
        sys.exit(1)


class CodexppError(RuntimeError):
    """Raised when the CLI encounters a recoverable error."""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codexpp",
        description="Codex CLI enhancement framework",
    )
    parser.add_argument(
        "-p",
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Çalışılacak proje dizini (varsayılan: mevcut dizin).",
    )

    subparsers = parser.add_subparsers(dest="command")

    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="Proje dizinine örnek komut ve persona setlerini kur.",
    )
    bootstrap_parser.add_argument(
        "--user",
        action="store_true",
        help="Kullanıcı bazlı kurulum (HOME/.codexpp) yapar.",
    )
    bootstrap_parser.add_argument(
        "--force",
        action="store_true",
        help="Var olan dosyaların üzerine yaz (dikkat!).",
    )
    bootstrap_parser.set_defaults(func=_handle_bootstrap)

    commands_parser = subparsers.add_parser("commands", help="Komut yönetimi.")
    commands_sub = commands_parser.add_subparsers(dest="subcommand")

    commands_list = commands_sub.add_parser("list", help="Tüm komutları listele.")
    commands_list.add_argument(
        "--verbose",
        action="store_true",
        help="Komut parametreleri ve açıklamalarını ayrıntılı göster.",
    )
    commands_list.set_defaults(func=_handle_commands_list)

    commands_show = commands_sub.add_parser("show", help="Komut detaylarını görüntüle.")
    commands_show.add_argument("identifier", help="Komut kimliği (örn. cx:analyze).")
    commands_show.set_defaults(func=_handle_commands_show)

    commands_render = commands_sub.add_parser("render", help="Komut istemini üret.")
    commands_render.add_argument("identifier", help="Komut kimliği.")
    commands_render.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Parametre değerleri (birden fazla kullanılabilir).",
    )
    commands_render.set_defaults(func=_handle_commands_render)

    commands_run = commands_sub.add_parser("run", help="Komutu çalıştır ve isteğe göre Codex'e gönder.")
    commands_run.add_argument("identifier", help="Komut kimliği.")
    commands_run.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Parametre değerleri (birden fazla kullanılabilir).",
    )
    commands_run.add_argument(
        "--persona",
        dest="personas",
        action="append",
        default=[],
        metavar="ID",
        help="Persona kimliği (birden fazla kullanılabilir).",
    )
    commands_run.add_argument(
        "--exec",
        dest="invoke_codex",
        action="store_true",
        help="`codex exec` çağırarak istemi doğrudan çalıştır.",
    )
    commands_run.add_argument(
        "--codex-bin",
        default="codex",
        help="Codex CLI ikili dosya adı veya yolu (varsayılan: codex).",
    )
    commands_run.add_argument(
        "--print-only",
        dest="print_only",
        action="store_true",
        help="İstem çıktısını yazdır ve Codex'i çağırma (varsayılan davranış).",
    )
    commands_run.add_argument(
        "--codex-arg",
        dest="codex_args",
        action="append",
        default=[],
        metavar="ARG",
        help="Codex CLI'ye iletilecek ek argüman (örn. --codex-arg=--skip-git-repo-check).",
    )
    commands_run.add_argument(
        "--summary",
        action="store_true",
        help="Komut parametreleri ve persona bilgilerini istemden önce özetle.",
    )
    commands_run.add_argument(
        "--summary-only",
        action="store_true",
        help="Yalnızca özeti göster, istemi üretme veya Codex'i çağırma.",
    )
    commands_run.add_argument(
        "--summary-format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Özet çıktısının formatı (varsayılan: text).",
    )
    commands_run.add_argument(
        "--save-summary",
        metavar="PATH",
        help="Özet çıktısını dosyaya kaydet.",
    )
    commands_run.add_argument(
        "--save-prompt",
        metavar="PATH",
        help="Final istem metnini dosyaya kaydet.",
    )
    commands_run.set_defaults(func=_handle_commands_run)

    commands_packs = commands_sub.add_parser("packs", help="Komut paketlerini yönet.")
    packs_sub = commands_packs.add_subparsers(dest="pack_subcommand")

    packs_list = packs_sub.add_parser("list", help="Yerleşik komut paketlerini listele.")
    packs_list.set_defaults(func=_handle_commands_packs_list)

    packs_install = packs_sub.add_parser("install", help="Belirtilen komut paketini projeye kur.")
    packs_install.add_argument("name", help="Paket adı (örn. extended).")
    packs_install.add_argument(
        "--user",
        action="store_true",
        help="Paketi kullanıcı dizinine kur (HOME/.codexpp).",
    )
    packs_install.add_argument(
        "--force",
        action="store_true",
        help="Var olan paket dosyasının üzerine yaz.",
    )
    packs_install.set_defaults(func=_handle_commands_packs_install)

    personas_parser = subparsers.add_parser("personas", help="Persona yönetimi.")
    personas_sub = personas_parser.add_subparsers(dest="subcommand")

    personas_list = personas_sub.add_parser("list", help="Tüm persona'ları listele.")
    personas_list.set_defaults(func=_handle_personas_list)

    personas_show = personas_sub.add_parser("show", help="Persona detaylarını görüntüle.")
    personas_show.add_argument("identifier", help="Persona kimliği (örn. system-architect).")
    personas_show.set_defaults(func=_handle_personas_show)

    personas_export = personas_sub.add_parser("export", help="Persona yönergelerini markdown olarak dışa aktar.")
    personas_export.add_argument(
        "--output",
        default="AGENTS.md",
        help="Çıktı dosya yolu (varsayılan: AGENTS.md). '-' ile stdout'a yazdırılır.",
    )
    personas_export.add_argument(
        "--persona",
        dest="personas",
        action="append",
        default=[],
        metavar="ID",
        help="Sadece belirtilen persona(lar)ı dahil et (birden fazla kullanılabilir).",
    )
    personas_export.add_argument(
        "--force",
        action="store_true",
        help="Var olan çıktının üzerine yaz.",
    )
    personas_export.set_defaults(func=_handle_personas_export)

    personas_sync = personas_sub.add_parser(
        "sync",
        help="Persona yönergelerini proje AGENTS.md dosyası ve Codex hafızası ile senkronize et.",
    )
    personas_sync.add_argument(
        "--output",
        default="AGENTS.md",
        help="Projede yazdırılacak dosya yolu (varsayılan: AGENTS.md). '-' ile proje dosyası atlanır.",
    )
    personas_sync.add_argument(
        "--codex-output",
        default="~/.codex/AGENTS.md",
        help="Codex hafızasına yazılacak yol (varsayılan: ~/.codex/AGENTS.md). '-' ile atlanır.",
    )
    personas_sync.add_argument(
        "--persona",
        dest="personas",
        action="append",
        default=[],
        metavar="ID",
        help="Sadece belirtilen persona(lar)ı dahil et (birden fazla kullanılabilir).",
    )
    personas_sync.add_argument(
        "--force",
        action="store_true",
        help="Var olan çıktıların üzerine yaz.",
    )
    personas_sync.add_argument(
        "--show-diff",
        action="store_true",
        help="Mevcut dosyalar değişiyorsa özet diff çıktısını göster.",
    )
    personas_sync.add_argument(
        "--diff-color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Diff çıktısı için renk modu (varsayılan: auto).",
    )
    personas_sync.set_defaults(func=_handle_personas_sync)

    codex_parser = subparsers.add_parser("codex", help="Codex CLI entegrasyon araçları.")
    codex_sub = codex_parser.add_subparsers(dest="subcommand")

    codex_status = codex_sub.add_parser("status", help="Codex CLI kurulum durumunu göster.")
    codex_status.add_argument(
        "--codex-bin",
        default="codex",
        help="Codex CLI ikili dosya adı veya yolu (varsayılan: codex).",
    )
    codex_status.add_argument(
        "--codex-agents",
        default="~/.codex/AGENTS.md",
        help="Codex hafıza dosyasının konumu (varsayılan: ~/.codex/AGENTS.md).",
    )
    codex_status.set_defaults(func=_handle_codex_status)

    codex_setup = codex_sub.add_parser("setup", help="Codex CLI için persona ve hafıza dosyalarını hazırla.")
    codex_setup.add_argument(
        "--codex-bin",
        default="codex",
        help="Codex CLI ikili dosya adı veya yolu (varsayılan: codex).",
    )
    codex_setup.add_argument(
        "--output",
        default="AGENTS.md",
        help="Projede yazdırılacak persona dosyası (varsayılan: AGENTS.md).",
    )
    codex_setup.add_argument(
        "--codex-agents",
        default="~/.codex/AGENTS.md",
        help="Codex hafıza dosyasının konumu (varsayılan: ~/.codex/AGENTS.md).",
    )
    codex_setup.add_argument(
        "--persona",
        dest="personas",
        action="append",
        default=[],
        metavar="ID",
        help="Sadece belirtilen persona(lar)ı dahil et (birden fazla kullanılabilir).",
    )
    codex_setup.add_argument(
        "--force",
        action="store_true",
        help="Var olan çıktılar üzerine yaz.",
    )
    codex_setup.add_argument(
        "--show-diff",
        action="store_true",
        help="Dosyalar değişiyorsa diff göster.",
    )
    codex_setup.add_argument(
        "--diff-color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Diff çıktısı için renk modu (varsayılan: auto).",
    )
    codex_setup.set_defaults(func=_handle_codex_setup)

    codex_install = codex_sub.add_parser(
        "install",
        help="Slash komutlarını Codex config dosyasına ekle.",
    )
    codex_install.add_argument(
        "--codex-bin",
        default="codex",
        help="Codex CLI ikili dosya adı veya yolu (varsayılan: codex).",
    )
    codex_install.add_argument(
        "--config",
        default="~/.codex/config.toml",
        help="Güncellenecek Codex config dosyası (varsayılan: ~/.codex/config.toml).",
    )
    codex_install.add_argument(
        "--include-pack",
        action="append",
        default=[],
        metavar="NAME",
        help="Belirtilen komut paketini config'e dahil et (örn. extended).",
    )
    codex_install.add_argument(
        "--force",
        action="store_true",
        help="Mevcut slash komut bloğunu üzerine yaz.",
    )
    codex_install.set_defaults(func=_handle_codex_install)

    codex_init = codex_sub.add_parser("init", help="Codex CLI için tam kurulum gerçekleştir.")
    codex_init.add_argument(
        "--profile",
        choices=["minimal", "full"],
        default="full",
        help="Kurulum profili (full: bootstrap + persona + komut paketleri).",
    )
    codex_init.add_argument(
        "--include-pack",
        action="append",
        default=[],
        metavar="NAME",
        help="Ek komut paketlerini dahil et (örn. ops).",
    )
    codex_init.add_argument(
        "--include-mcp",
        action="append",
        default=[],
        metavar="NAME",
        help="Ek MCP paketlerini dahil et (örn. default).",
    )
    codex_init.add_argument(
        "--force",
        action="store_true",
        help="Var olan dosyaların üzerine yaz.",
    )
    codex_init.add_argument(
        "--skip-bootstrap",
        action="store_true",
        help="Proje bootstrap adımını atla.",
    )
    codex_init.set_defaults(func=_handle_codex_init)

    mcp_parser = subparsers.add_parser(
        "mcp",
        help="Model Context Protocol sunucu profillerini yönet.",
    )
    mcp_sub = mcp_parser.add_subparsers(dest="subcommand")

    mcp_list = mcp_sub.add_parser(
        "list",
        help="Yüklü MCP profillerini listele.",
    )
    mcp_list.add_argument(
        "--verbose",
        action="store_true",
        help="Sunucu komutu, argümanlar ve ortam değişkenlerini göster.",
    )
    mcp_list.set_defaults(func=_handle_mcp_list)

    mcp_setup = mcp_sub.add_parser(
        "setup",
        help="MCP profillerini Codex CLI tarafından kullanılacak dizine senkronize et.",
    )
    mcp_setup.add_argument(
        "--codex-dir",
        default="~/.codex/mcp",
        help="Profillerin yazılacağı hedef dizin (varsayılan: ~/.codex/mcp).",
    )
    mcp_setup.add_argument(
        "--format",
        choices=["json", "toml", "both"],
        default="json",
        help="Çıktı formatı (varsayılan: json).",
    )
    mcp_setup.add_argument(
        "--force",
        action="store_true",
        help="Var olan dosyaların üzerine yaz.",
    )
    mcp_setup.add_argument(
        "--show-diff",
        action="store_true",
        help="Dosya güncellenirken diff çıktısını göster.",
    )
    mcp_setup.add_argument(
        "--diff-color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Diff renklendirme modu (varsayılan: auto).",
    )
    mcp_setup.set_defaults(func=_handle_mcp_setup)

    mcp_packs = mcp_sub.add_parser(
        "packs",
        help="Yerleşik MCP paketlerini yönet.",
    )
    mcp_packs_sub = mcp_packs.add_subparsers(dest="pack_subcommand")

    mcp_packs_list = mcp_packs_sub.add_parser(
        "list",
        help="Kullanılabilir MCP paketlerini listele.",
    )
    mcp_packs_list.set_defaults(func=_handle_mcp_packs_list)

    mcp_packs_install = mcp_packs_sub.add_parser(
        "install",
        help="Belirtilen MCP paketini projeye veya kullanıcı dizinine kur.",
    )
    mcp_packs_install.add_argument("name", help="Paket adı (örn. default).")
    mcp_packs_install.add_argument(
        "--user",
        action="store_true",
        help="Paketi kullanıcı dizinine kur (HOME/.codexpp).",
    )
    mcp_packs_install.add_argument(
        "--force",
        action="store_true",
        help="Var olan dosyanın üzerine yaz.",
    )
    mcp_packs_install.set_defaults(func=_handle_mcp_packs_install)

    tui_parser = subparsers.add_parser(
        "tui",
        help="Etkileşimli komut keşfi için basit metin arayüzünü başlat.",
    )
    tui_parser.add_argument(
        "--exec",
        action="store_true",
        help="Menüden seçili komutları Codex'e göndermeye izin ver.",
    )
    tui_parser.set_defaults(func=_handle_tui)

    return parser


def _handle_bootstrap(args: argparse.Namespace) -> None:
    if args.user:
        base_dir = cfg.user_config_dir()
    else:
        base_dir = (args.project / cfg.APP_DIR_NAME).resolve()

    resource_cmd = resources.files("codexpp.resources") / "commands"
    resource_personas = resources.files("codexpp.resources") / "personas"
    resource_mcp = resources.files("codexpp.resources") / "mcp"

    commands_dir, personas_dir, mcp_dir = cfg.bootstrap_targets(base_dir)

    command_ops = _copy_resource_tree(resource_cmd, commands_dir, overwrite=args.force)
    persona_ops = _copy_resource_tree(resource_personas, personas_dir, overwrite=args.force)
    mcp_ops = _copy_resource_tree(resource_mcp, mcp_dir, overwrite=args.force)

    _print_bootstrap_summary(base_dir, command_ops + persona_ops + mcp_ops)


def _copy_resource_tree(
    source: resources.abc.Traversable, destination: Path, overwrite: bool = False
) -> List[Tuple[str, Path]]:
    destination.mkdir(parents=True, exist_ok=True)
    operations: List[Tuple[str, Path]] = []
    for item in source.iterdir():
        if not item.name.endswith(".toml"):
            continue
        target_path = destination / item.name
        if target_path.exists():
            if not overwrite:
                operations.append(("skipped", target_path))
                continue
            status = "overwritten"
        else:
            status = "created"
        with item.open("rb") as handle:
            data = handle.read()
        target_path.write_bytes(data)
        operations.append((status, target_path))

    return operations


def _print_bootstrap_summary(base_dir: Path, operations: List[Tuple[str, Path]]) -> None:
    print(f"[codexpp] Kurulum tamamlandı: {base_dir}")

    if not operations:
        print("  - Kopyalanacak yeni dosya bulunamadı.")
        return

    groups: Dict[str, List[Path]] = {"created": [], "overwritten": [], "skipped": []}
    for status, path in operations:
        groups.setdefault(status, []).append(path)

    status_labels = {
        "created": "Oluşturulan dosyalar",
        "overwritten": "Üzerine yazılan dosyalar",
        "skipped": "Atlanan dosyalar (mevcut içerik korundu)",
    }

    for status_key, label in status_labels.items():
        paths = groups.get(status_key, [])
        if not paths:
            continue
        print(f"  - {label}:")
        for path in paths:
            try:
                relative = path.relative_to(base_dir)
            except ValueError:
                relative = path
            print(f"      • {relative}")


def _handle_commands_list(args: argparse.Namespace) -> None:
    commands = loader.load_commands(start=args.project)
    if not commands:
        print("Hiç komut bulunamadı. `codexpp bootstrap` çalıştırmayı deneyin.")
        return

    for command in sorted(commands.values(), key=lambda c: c.identifier):
        tags = f" [{', '.join(command.tags)}]" if command.tags else ""
        print(f"- {command.identifier}{tags}\n  {command.title}")
        if command.summary:
            print(f"  {command.summary}")
        if args.verbose and command.parameters:
            print("  Parametreler:")
            for param in command.parameters.values():
                required = "zorunlu" if param.required else "opsiyonel"
                default = f" (varsayılan: {param.default})" if param.default else ""
                print(f"    • {param.name}: {param.description or '-'} — {required}{default}")
        print("")


def _handle_commands_show(args: argparse.Namespace) -> None:
    commands = loader.load_commands(start=args.project)
    command = commands.get(args.identifier)
    if command is None:
        raise CodexppError(f"Komut bulunamadı: {args.identifier}")

    print(f"{command.identifier} — {command.title}")
    if command.tags:
        print(f"Etiketler: {', '.join(command.tags)}")
    if command.summary:
        print(f"Açıklama: {command.summary}")
    if command.parameters:
        print("Parametreler:")
        for param in command.parameters.values():
            required = "zorunlu" if param.required else "opsiyonel"
            default = f" (varsayılan: {param.default})" if param.default else ""
            print(f"  - {param.name}: {param.description} — {required}{default}")
    print("\nİstem şablonu:\n")
    print(command.prompt.strip())


def _handle_commands_render(args: argparse.Namespace) -> None:
    commands = loader.load_commands(start=args.project)
    command = commands.get(args.identifier)
    if command is None:
        raise CodexppError(f"Komut bulunamadı: {args.identifier}")

    overrides = _parse_key_value_pairs(args.overrides)
    _validate_override_keys(command, overrides)
    missing = _required_missing(command, overrides)
    if missing:
        raise CodexppError(f"Eksik zorunlu parametreler: {', '.join(missing)}")

    rendered = _render_prompt(command, overrides)
    print(rendered.strip())


def _handle_commands_run(args: argparse.Namespace) -> None:
    commands = loader.load_commands(start=args.project)
    command = commands.get(args.identifier)
    if command is None:
        raise CodexppError(f"Komut bulunamadı: {args.identifier}")

    overrides = _parse_key_value_pairs(args.overrides)
    _validate_override_keys(command, overrides)
    missing = _required_missing(command, overrides)
    if missing:
        raise CodexppError(f"Eksik zorunlu parametreler: {', '.join(missing)}")

    personas = _resolve_personas(args.personas, start=args.project)
    resolved_values = _resolve_parameter_values(command, overrides)

    if args.summary_only:
        args.summary = True

    rendered_prompt = _render_prompt(command, resolved_values)
    final_prompt = _compose_prompt(rendered_prompt, personas)

    summary_text: Optional[str] = None
    if args.summary:
        summary_text = _build_run_summary(
            command,
            resolved_values,
            personas,
            invoke_codex=args.invoke_codex and not args.print_only,
            print_only=args.print_only or not args.invoke_codex,
            summary_format=args.summary_format,
        )
        print(summary_text)
        print("")
        if args.save_summary:
            text_to_write = summary_text if summary_text.endswith("\n") else summary_text + "\n"
            _write_text(args.save_summary, text_to_write)
        if args.summary_only:
            if args.save_prompt:
                _write_text(
                    args.save_prompt,
                    final_prompt.strip() + ("\n" if not final_prompt.endswith("\n") else ""),
                )
            return

    if args.save_prompt:
        _write_text(
            args.save_prompt,
            final_prompt.strip() + ("\n" if not final_prompt.endswith("\n") else ""),
        )

    if args.invoke_codex and not args.print_only:
        _invoke_codex(final_prompt, args.codex_bin, args.codex_args)
    else:
        print(final_prompt.strip())
        if args.invoke_codex and args.print_only:
            print("\n[codexpp] `--print-only` etkin, Codex çağrılmadı.")


def _handle_commands_packs_list(args: argparse.Namespace) -> None:
    packs = _available_command_packs()
    if not packs:
        print("Yerleşik komut paketi bulunamadı.")
        return

    installed: set[str] = set()
    for directory in cfg.candidate_command_dirs(args.project):
        if directory.exists():
            installed.update(path.stem for path in directory.glob("*.toml"))

    print("Kullanılabilir paketler:")
    for name in sorted(packs):
        marker = " (kurulu)" if name in installed else ""
        print(f"- {name}{marker}")


def _handle_commands_packs_install(args: argparse.Namespace) -> None:
    packs = _available_command_packs()
    resource = packs.get(args.name)
    if resource is None:
        raise CodexppError(f"Paket bulunamadı: {args.name}")

    if args.user:
        base_dir = cfg.user_config_dir()
    else:
        base_dir = cfg.project_config_dir(args.project)

    target_dir = base_dir / cfg.COMMANDS_DIR_NAME
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{args.name}.toml"
    if target_path.exists() and not args.force:
        raise CodexppError(f"Paket zaten mevcut: {target_path}. Üzerine yazmak için `--force` kullanın.")

    with resource.open("rb") as handle:
        data = handle.read()
    target_path.write_bytes(data)

    location = "kullanıcı" if args.user else "proje"
    print(f"[codexpp] {args.name} paketi {location} dizinine kuruldu: {target_path}")


def _parse_key_value_pairs(pairs: Iterable[str]) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for item in pairs:
        if "=" not in item:
            raise CodexppError(f"Geçersiz eşleme, `anahtar=değer` formatı bekleniyor: {item}")
        key, value = item.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _validate_override_keys(command: CommandDefinition, values: Dict[str, str]) -> None:
    unknown = sorted(key for key in values if key not in command.parameters)
    if unknown:
        raise CodexppError(f"Tanımsız parametre(ler): {', '.join(unknown)}")


def _required_missing(command: CommandDefinition, values: Dict[str, str]) -> List[str]:
    missing: List[str] = []
    for name, param in command.parameters.items():
        candidate = values.get(name) or param.default
        if param.required and not candidate:
            missing.append(name)
    return missing


def _render_prompt(command: CommandDefinition, values: Dict[str, str]) -> str:
    placeholders = set(PLACEHOLDER_PATTERN.findall(command.prompt))
    undefined = sorted(placeholders - set(command.parameters))
    if undefined:
        raise CodexppError(f"İstemde tanımlı olmayan placeholder(lar): {', '.join(undefined)}")

    def replacement(match: re.Match[str]) -> str:
        name = match.group(1)
        param = command.parameters[name]
        return values.get(name, param.default or "")

    result = PLACEHOLDER_PATTERN.sub(replacement, command.prompt)

    leftover = PLACEHOLDER_PATTERN.search(result)
    if leftover:
        raise CodexppError(
            f"İstemde işlenmemiş placeholder bulundu: {leftover.group(0)}"
        )

    return result.replace("\\{{", "{{")


def _resolve_parameter_values(command: CommandDefinition, values: Dict[str, str]) -> Dict[str, str]:
    resolved: Dict[str, str] = {}
    for name, param in command.parameters.items():
        value = values.get(name)
        if value is None:
            value = param.default or ""
        resolved[name] = value
    return resolved


def _build_run_summary(
    command: CommandDefinition,
    resolved_values: Dict[str, str],
    personas: List[PersonaDefinition],
    invoke_codex: bool,
    print_only: bool,
    summary_format: str,
) -> str:
    run_mode = "Codex exec" if invoke_codex else ("stdout" if not print_only else "önizleme")
    summary = {
        "command": {
            "id": command.identifier,
            "title": command.title,
            "tags": command.tags,
        },
        "parameters": {name: resolved_values.get(name, "") for name in command.parameters},
        "personas": [
            {"id": persona.identifier, "label": persona.label} for persona in personas
        ],
        "run_mode": run_mode,
    }

    if summary_format == "json":
        return json.dumps(summary, ensure_ascii=False, indent=2)

    if summary_format == "markdown":
        lines = [
            "# Komut Özeti",
            f"## {command.title} (`{command.identifier}`)",
        ]
        if command.tags:
            lines.append(f"_Etiketler:_ {', '.join(command.tags)}")
        lines.append("")
        lines.append("### Parametreler")
        if summary["parameters"]:
            for name, value in summary["parameters"].items():
                rendered_value = value if value else "(boş)"
                lines.append(f"- {name}: {rendered_value}")
        else:
            lines.append("- (Tanımlı parametre yok)")

        lines.append("")
        lines.append("### Persona'lar")
        if summary["personas"]:
            for persona in summary["personas"]:
                lines.append(f"- {persona['id']}: {persona['label']}")
        else:
            lines.append("- (Seçilmedi)")

        lines.append("")
        lines.append(f"**Çalıştırma modu:** {run_mode}")
        return "\n".join(lines)

    # Varsayılan metin formatı
    lines = [
        "== Komut Özeti ==",
        f"Kimlik: {summary['command']['id']}",
        f"Başlık: {summary['command']['title']}",
    ]
    if command.tags:
        lines.append(f"Etiketler: {', '.join(command.tags)}")

    lines.append("\nParametreler:")
    if summary["parameters"]:
        for name, value in summary["parameters"].items():
            rendered_value = value if value else "(boş)"
            lines.append(f"  - {name}: {rendered_value}")
    else:
        lines.append("  - (Tanımlı parametre yok)")

    lines.append("\nPersona'lar:")
    if summary["personas"]:
        for persona in summary["personas"]:
            lines.append(f"  - {persona['id']}: {persona['label']}")
    else:
        lines.append("  - (Seçilmedi)")

    lines.append(f"\nÇalıştırma modu: {run_mode}")
    return "\n".join(lines)


def _handle_personas_list(args: argparse.Namespace) -> None:
    personas = loader.load_personas(start=args.project)
    if not personas:
        print("Hiç persona bulunamadı. `codexpp bootstrap` çalıştırmayı deneyin.")
        return

    for persona in sorted(personas.values(), key=lambda p: p.identifier):
        print(f"- {persona.identifier}: {persona.label} — {persona.summary}")


def _handle_personas_show(args: argparse.Namespace) -> None:
    personas = loader.load_personas(start=args.project)
    persona = personas.get(args.identifier)
    if persona is None:
        raise CodexppError(f"Persona bulunamadı: {args.identifier}")

    print(f"{persona.identifier} — {persona.label}")
    print(persona.summary)
    print("\nDavranış yönergeleri:")
    for directive in persona.directives:
        print(f"- {directive}")


def _handle_personas_export(args: argparse.Namespace) -> None:
    personas_map = loader.load_personas(start=args.project)
    if not personas_map:
        raise CodexppError("Hiç persona kaynağı bulunamadı. `codexpp bootstrap` çalıştırmayı deneyin.")

    personas = _collect_personas(personas_map, args.personas)
    markdown = _render_personas_markdown(personas)

    if args.output == "-":
        print(markdown.rstrip())
        return

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (args.project / output_path).resolve()

    if output_path.exists() and not args.force:
        raise CodexppError(
            f"Çıktı dosyası zaten mevcut: {output_path}. Üzerine yazmak için `--force` ekleyin."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"[codexpp] Persona çıktısı yazıldı: {output_path}")


def _handle_personas_sync(args: argparse.Namespace) -> None:
    personas_map = loader.load_personas(start=args.project)
    if not personas_map:
        raise CodexppError("Hiç persona kaynağı bulunamadı. `codexpp bootstrap` çalıştırmayı deneyin.")

    personas = _collect_personas(personas_map, args.personas)
    markdown = _render_personas_markdown(personas)

    targets: List[Tuple[str, Path, Optional[str]]] = []

    if args.output != "-":
        project_path = Path(args.output)
        if not project_path.is_absolute():
            project_path = (args.project / project_path).resolve()
        previous = project_path.read_text(encoding="utf-8") if project_path.exists() else None
        targets.append(("project", project_path, previous))

    if args.codex_output != "-":
        codex_path = Path(args.codex_output).expanduser()
        codex_path = codex_path.resolve()
        previous = codex_path.read_text(encoding="utf-8") if codex_path.exists() else None
        targets.append(("codex", codex_path, previous))

    if not targets:
        raise CodexppError("Yazılacak hedef bulunamadı. En az bir çıktı seçmelisiniz.")

    conflicts = [
        path for _, path, previous in targets if previous is not None and previous != markdown and not args.force
    ]
    if conflicts:
        conflict_list = ", ".join(str(path) for path in conflicts)
        raise CodexppError(
            f"Aşağıdaki dosyalar zaten mevcut: {conflict_list}. Üzerine yazmak için `--force` ekleyin."
        )

    use_color = args.diff_color == "always" or (
        args.diff_color == "auto" and sys.stdout.isatty()
    )

    for label, path, previous in targets:
        if previous is not None and previous == markdown:
            print(f"[codexpp] Persona çıktısı zaten güncel ({label}): {path}")
            continue

        path.parent.mkdir(parents=True, exist_ok=True)

        if previous is not None and args.show_diff:
            diff_text = _render_diff(path, previous, markdown)
            if diff_text:
                if use_color:
                    diff_text = _colorize_diff(diff_text)
                print(diff_text)
            else:
                print(f"[codexpp] Değişiklik bulunamadı ({label}): {path}")

        path.write_text(markdown, encoding="utf-8")
        print(f"[codexpp] Persona çıktısı yazıldı ({label}): {path}")


def _render_mcp_server_json(server: McpServerDefinition) -> str:
    data: Dict[str, object] = {
        "id": server.identifier,
        "label": server.label,
        "summary": server.summary,
        "command": server.command,
        "transport": server.transport,
        "auto_start": server.auto_start,
    }
    if server.args:
        data["args"] = server.args
    if server.env:
        data["env"] = server.env
    if server.cwd:
        data["cwd"] = server.cwd
    if server.tags:
        data["tags"] = server.tags

    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _render_mcp_server_toml(server: McpServerDefinition) -> str:
    lines: List[str] = ["[server]"]
    lines.append(f"id = {_toml_quote(server.identifier)}")
    lines.append(f"label = {_toml_quote(server.label)}")
    if server.summary:
        lines.append(f"summary = {_toml_multiline(server.summary)}")
    lines.append(f"command = {_toml_quote(server.command)}")
    lines.append(f"transport = {_toml_quote(server.transport)}")
    lines.append(f"auto_start = {_toml_bool(server.auto_start)}")
    if server.args:
        arg_values = ", ".join(_toml_quote(item) for item in server.args)
        lines.append(f"args = [{arg_values}]")
    if server.cwd:
        lines.append(f"cwd = {_toml_quote(server.cwd)}")
    if server.tags:
        tag_values = ", ".join(_toml_quote(item) for item in server.tags)
        lines.append(f"tags = [{tag_values}]")

    if server.env:
        lines.append("")
        lines.append("[server.env]")
        for key, value in sorted(server.env.items()):
            lines.append(f"{key} = {_toml_quote(value)}")

    return "\n".join(lines) + "\n"


def _toml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _toml_multiline(value: str) -> str:
    escaped = value.replace('"""', '\\"\\"\\"')
    return f'"""{escaped}"""'


def _toml_bool(value: bool) -> str:
    return "true" if value else "false"


def _available_mcp_packs() -> Dict[str, resources.abc.Traversable]:
    try:
        base = resources.files("codexpp.resources.mcp")
    except ModuleNotFoundError:
        return {}

    packs: Dict[str, resources.abc.Traversable] = {}
    for item in base.iterdir():
        if item.name.endswith(".toml"):
            packs[item.name[:-5]] = item
    return packs


def _available_command_packs() -> Dict[str, resources.abc.Traversable]:
    try:
        base = resources.files("codexpp.resources.command_packs")
    except ModuleNotFoundError:
        return {}

    packs: Dict[str, resources.abc.Traversable] = {}
    for item in base.iterdir():
        if item.name.endswith(".toml"):
            packs[item.name[:-5]] = item
    return packs


def _strip_codexpp_slash_commands(config_text: str) -> str:
    start_marker = "# >>> codexpp slash commands"
    end_marker = "# <<< codexpp slash commands"
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}\n?",
        re.DOTALL,
    )
    config_text = pattern.sub("", config_text)

    # Remove any leftover cx:* slash commands and associated headers
    config_text = re.sub(
        r"\n?\[slash_commands\.\"cx:[^\"^\]]+\"\][^\[]*",
        "\n",
        config_text,
        flags=re.DOTALL,
    )

    # Remove empty [slash_commands] tables
    config_text = re.sub(
        r"\n?\[slash_commands\]\s*(?=(\n\[)|\Z)",
        "\n",
        config_text,
    )

    # Collapse multiple blank lines
    config_text = re.sub(r"\n{3,}", "\n\n", config_text).strip("\n") + "\n"
    return config_text


def _strip_codexpp_mcp_servers(config_text: str) -> str:
    start_marker = "# >>> codexpp mcp servers"
    end_marker = "# <<< codexpp mcp servers"
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}\n?",
        re.DOTALL,
    )
    config_text = pattern.sub("", config_text)

    # Remove any leftover mcp_servers entries
    config_text = re.sub(
        r"\n?\[mcp_servers\.[^\]]+\][^\[]*",
        "\n",
        config_text,
        flags=re.DOTALL,
    )

    # Remove empty [mcp_servers] tables
    config_text = re.sub(
        r"\n?\[mcp_servers\]\s*(?=(\n\[)|\Z)",
        "\n",
        config_text,
    )

    # Collapse multiple blank lines
    config_text = re.sub(r"\n{3,}", "\n\n", config_text).strip("\n") + "\n"
    return config_text


def _build_codex_mcp_block(servers: Dict[str, McpServerDefinition], project_path: Path | None = None) -> str:
    if not servers:
        return "# >>> codexpp mcp servers\n# <<< codexpp mcp servers\n"

    lines: List[str] = ["# >>> codexpp mcp servers"]
    for server in sorted(servers.values(), key=lambda s: s.identifier):
        lines.append(f'[mcp_servers."{server.identifier}"]')
        lines.append(f'command = {_toml_quote(server.command)}')
        if server.args:
            # Filesystem sunucusu için proje dizinini argüman olarak ekle
            if server.identifier == "filesystem" and project_path:
                project_dir = str(project_path.resolve())
                args_with_dir = list(server.args) + [project_dir]
                arg_values = ", ".join(_toml_quote(item) for item in args_with_dir)
            else:
                arg_values = ", ".join(_toml_quote(item) for item in server.args)
            lines.append(f"args = [{arg_values}]")
        # Puppeteer için timeout ayarı ekle (tarayıcı başlatma zaman alabilir)
        if server.identifier == "puppeteer":
            lines.append("startup_timeout_sec = 30")
        # auto_start ayarını ekle (Codex CLI otomatik başlatma için)
        if server.auto_start:
            lines.append("auto_start = true")
        # cwd alanını atla - Codex CLI proje dizinini otomatik kullanır
        # filesystem için --root argümanı zaten proje dizinini belirtiyor
        if server.env:
            lines.append("")
            lines.append(f'[mcp_servers."{server.identifier}".env]')
            for key, value in sorted(server.env.items()):
                lines.append(f"{key} = {_toml_quote(value)}")
        lines.append("")
    lines.append("# <<< codexpp mcp servers")
    return "\n".join(lines) + "\n"


def _load_commands_from_resource(resource: resources.abc.Traversable) -> Dict[str, CommandDefinition]:
    with resource.open("rb") as handle:
        data = tomllib.load(handle)

    commands: Dict[str, CommandDefinition] = {}
    for entry in data.get("commands", []):
        identifier = entry["id"]
        parameters = {
            name: CommandParameter(
                name=name,
                description=value.get("description", ""),
                required=value.get("required", False),
                default=value.get("default"),
                placeholder=value.get("placeholder"),
            )
            for name, value in entry.get("inputs", {}).items()
        }
        commands[identifier] = CommandDefinition(
            identifier=identifier,
            title=entry.get("title", identifier),
            summary=entry.get("summary", ""),
            prompt=entry["prompt"],
            parameters=parameters,
            tags=list(entry.get("tags", [])),
        )
    return commands


def _build_codex_slash_block(commands: Dict[str, CommandDefinition]) -> str:
    if not commands:
        return "# >>> codexpp slash commands\n# <<< codexpp slash commands\n"

    lines: List[str] = ["# >>> codexpp slash commands", "[slash_commands]"]
    for command in sorted(commands.values(), key=lambda c: c.identifier):
        lines.append(f'[slash_commands."{command.identifier}"]')
        description = command.summary or command.title
        description = description.replace('"""', '\\"\\"\\"')
        lines.append(f'description = """{description}"""')
        prompt = command.prompt.strip("\n").replace('"""', '\\"\\"\\"')
        lines.append(f'prompt = """{prompt}"""')
        if command.tags:
            tags = ", ".join(f'"{tag}"' for tag in command.tags)
            lines.append(f"tags = [{tags}]")
        lines.append("")
    lines.append("# <<< codexpp slash commands")
    lines.append("")
    return "\n".join(lines)


def _build_prompt_template_from_command(command: CommandDefinition) -> str:
    lines = [
        "---",
        f"title: {command.title or command.identifier}",
        f'description: {command.summary or command.title or command.identifier}',
    ]
    placeholders = []
    for param in command.parameters.values():
        if param.placeholder:
            placeholders.append(param.placeholder)
        else:
            placeholders.append(param.name.upper())
    if placeholders:
        hint = " ".join(f"{name}=<value>" for name in placeholders)
        lines.append(f"argument_hint: {hint}")
    persona = _infer_persona(command)
    if persona:
        lines.append(f"persona: {persona}")
    lines.extend(["---", ""])
    lines.append(command.prompt.strip("\n"))
    lines.append("")
    return "\n".join(lines)


def _infer_persona(command: CommandDefinition) -> Optional[str]:
    tag_map = {
        "analysis": "system-architect",
        "planning": "implementation-engineer",
        "implementation": "implementation-engineer",
        "quality": "code-reviewer",
        "review": "code-reviewer",
        "debugging": "implementation-engineer",
        "ops": "implementation-engineer",
        "documentation": "implementation-engineer",
    }
    for tag in command.tags:
        persona = tag_map.get(tag)
        if persona:
            return persona
    return None


def _handle_tui(args: argparse.Namespace) -> None:
    commands = loader.load_commands(start=args.project)
    if not commands:
        print("Hiç komut bulunamadı. `codexpp bootstrap` çalıştırmayı deneyin.")
        return
    personas = loader.load_personas(start=args.project)
    project_path = Path(args.project or Path.cwd())
    try:
        _run_tui_session(commands, personas, project_path, allow_exec=args.exec)
    except KeyboardInterrupt:
        print("\n[codexpp] TUI kapatıldı.")


def _run_tui_session(
    commands: Dict[str, CommandDefinition],
    personas: Dict[str, PersonaDefinition],
    project_path: Path,
    allow_exec: bool,
    *,
    input_fn: Callable[[str], str] = input,
) -> None:
    commands_list = sorted(commands.values(), key=lambda c: c.identifier)
    while True:
        print("\n=== Codexpp Komut Merkezi ===")
        for idx, command in enumerate(commands_list, start=1):
            tags = f" ({', '.join(command.tags)})" if command.tags else ""
            print(f"{idx}. {command.identifier}{tags} - {command.title}")
        choice = input_fn("\nSeçim yap (q: çıkış, r: listeyi yenile): ").strip()
        if choice.lower() in {"q", "quit"}:
            print("[codexpp] Çıkılıyor.")
            return
        if choice.lower() == "r":
            commands = loader.load_commands(start=project_path)
            commands_list = sorted(commands.values(), key=lambda c: c.identifier)
            continue
        if not choice.isdigit():
            print("[codexpp] Geçersiz seçim.")
            continue
        index = int(choice)
        if index < 1 or index > len(commands_list):
            print("[codexpp] Geçersiz numara.")
            continue
        command = commands_list[index - 1]
        overrides: Dict[str, str] = {}
        print(f"\nSeçilen komut: {command.identifier} — {command.title}")
        for param in command.parameters.values():
            placeholder = param.placeholder or param.name.upper()
            prompt = f"{param.name} ({param.description or '-'})"
            if param.default:
                prompt += f" [{param.default}]"
            while True:
                value = input_fn(f"{prompt}: ").strip()
                if value:
                    overrides[param.name] = value
                    break
                if param.default is not None:
                    overrides[param.name] = param.default or ""
                    break
                if not param.required:
                    overrides[param.name] = ""
                    break
                print("[codexpp] Bu değer gerekli.")

        if personas:
            persona_input = input_fn(
                "Persona kimlikleri (virgülle ayır, boş bırakmak için Enter): "
            ).strip()
            persona_ids = [item.strip() for item in persona_input.split(",") if item.strip()]
        else:
            persona_ids = []

        try:
            selected_personas = _resolve_personas(persona_ids, start=project_path)
        except CodexppError as exc:
            print(f"[codexpp] {exc}")
            selected_personas = []

        resolved_values = _resolve_parameter_values(command, overrides)
        prompt_body = _render_prompt(command, resolved_values)
        final_prompt = _compose_prompt(prompt_body, selected_personas)

        summary_text = _build_run_summary(
            command,
            resolved_values,
            selected_personas,
            invoke_codex=allow_exec,
            print_only=not allow_exec,
            summary_format="markdown",
        )

        print("\n--- Özet ---\n")
        print(summary_text)
        print("\n--- Prompt ---\n")
        print(final_prompt.strip())

        if allow_exec:
            action = input_fn("\n[e] Codex'e gönder, [enter] menüye dön: ").strip().lower()
            if action.startswith("e"):
                _invoke_codex(final_prompt, "codex", [])


def _sync_codex_prompts(
    commands: Dict[str, CommandDefinition],
    prompts_dir: Path,
    force: bool = False,
) -> None:
    prompts_dir.mkdir(parents=True, exist_ok=True)

    template_map: Dict[str, str] = {}
    for package in PROMPT_TEMPLATE_PACKAGES:
        try:
            base = resources.files(package)
        except ModuleNotFoundError:
            continue
        for item in base.iterdir():
            if item.name.endswith(".md"):
                command_id = item.name[:-3].replace("-", ":")
                template_map[command_id] = item.read_text(encoding="utf-8")

    for command in commands.values():
        filename = command.identifier.replace(":", "-") + ".md"
        prompt_path = prompts_dir / filename
        if prompt_path.exists() and not force:
            continue

        template = template_map.get(command.identifier)
        if template is None:
            template = _build_prompt_template_from_command(command)

        prompt_path.write_text(template, encoding="utf-8")


def _handle_codex_status(args: argparse.Namespace) -> None:
    codex_path = shutil.which(args.codex_bin)
    if codex_path is None:
        print("[codexpp] Codex CLI bulunamadı.")
        print("  Kurulum için: npm i -g @openai/codex  veya  brew install --cask codex")
        return

    print(f"[codexpp] Codex CLI bulundu: {codex_path}")
    try:
        result = subprocess.run(
            [codex_path, "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version_output = result.stdout.strip() or result.stderr.strip()
        if version_output:
            print(version_output)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"[codexpp] Codex sürüm bilgisi alınamadı: {exc}")

    agents_path = Path(args.codex_agents).expanduser()
    if agents_path.exists():
        size = agents_path.stat().st_size
        print(f"[codexpp] Codex AGENTS dosyası: {agents_path} ({size} bayt)")
    else:
        print(f"[codexpp] Codex AGENTS dosyası bulunamadı: {agents_path}")


def _handle_codex_setup(args: argparse.Namespace) -> None:
    codex_path = shutil.which(args.codex_bin)
    if codex_path is None:
        raise CodexppError(
            "Codex CLI bulunamadı. Kurulum için: npm i -g @openai/codex  veya  brew install --cask codex"
        )

    sync_args = argparse.Namespace(
        project=args.project,
        personas=args.personas,
        output=args.output,
        codex_output=args.codex_agents,
        force=args.force,
        show_diff=args.show_diff,
        diff_color=args.diff_color,
    )
    _handle_personas_sync(sync_args)

    print("\n[codexpp] Codex CLI ile çalışmaya hazırsınız.")
    print("  Örnek: codex exec --prompt \"...\"")
    print("  veya  codexpp commands run <komut> --exec")
    print("  Durumu kontrol etmek için: codexpp codex status")


def _handle_codex_install(args: argparse.Namespace) -> None:
    codex_path = shutil.which(args.codex_bin)
    if codex_path is None:
        raise CodexppError(
            "Codex CLI bulunamadı. Kurulum için: npm i -g @openai/codex  veya  brew install --cask codex"
        )

    commands = loader.load_commands(start=args.project).copy()

    available_packs = _available_command_packs()
    for name in args.include_pack or []:
        resource = available_packs.get(name)
        if resource is None:
            raise CodexppError(f"Komut paketi bulunamadı: {name}")
        commands.update(_load_commands_from_resource(resource))

    config_path = Path(args.config).expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_text = config_path.read_text() if config_path.exists() else ""

    config_text = _strip_codexpp_slash_commands(config_text)
    config_text = _strip_codexpp_mcp_servers(config_text)

    block = _build_codex_slash_block(commands)
    if config_text and not config_text.endswith("\n"):
        config_text += "\n"
    config_text += block

    # MCP profillerini otomatik kur ve config'e ekle
    mcp_servers = loader.load_mcp_servers(start=args.project)
    if not mcp_servers:
        # Varsayılan MCP paketini kur
        mcp_packs = _available_mcp_packs()
        default_pack = mcp_packs.get("default")
        if default_pack:
            project_dir = cfg.project_config_dir(args.project)
            mcp_dir = project_dir / cfg.MCP_DIR_NAME
            mcp_dir.mkdir(parents=True, exist_ok=True)
            default_path = mcp_dir / "default.toml"
            if not default_path.exists() or args.force:
                with default_pack.open("rb") as handle:
                    data = handle.read()
                default_path.write_bytes(data)
                print(f"[codexpp] Varsayılan MCP paketi kuruldu: {default_path}")
            mcp_servers = loader.load_mcp_servers(start=args.project)

    if mcp_servers:
        # Proje dizinini belirle (codex install çalıştırıldığı dizin)
        project_dir = args.project.resolve() if args.project else Path.cwd().resolve()
        mcp_block = _build_codex_mcp_block(mcp_servers, project_path=project_dir)
        config_text += mcp_block

    config_path.write_text(config_text)
    print(f"[codexpp] Codex config güncellendi: {config_path}")
    prompts_dir = Path.home() / ".codex" / "prompts"
    _sync_codex_prompts(commands, prompts_dir, force=args.force)
    print("  Codex CLI içinde slash komutlarını `/` menüsünden görebilirsiniz.")
    if mcp_servers:
        print(f"  MCP sunucuları config'e eklendi: {', '.join(sorted(mcp_servers.keys()))}")


def _handle_codex_init(args: argparse.Namespace) -> None:
    codex_path = shutil.which("codex")
    if codex_path is None:
        raise CodexppError(
            "Codex CLI bulunamadı. Kurulum için: npm i -g @openai/codex  veya  brew install --cask codex"
        )

    packs = set(args.include_pack or [])
    if args.profile == "full":
        packs.update({"extended", "ops"})

    mcp_packs = set(args.include_mcp or [])
    if args.profile == "full":
        mcp_packs.add("default")

    project_path = args.project

    if not args.skip_bootstrap:
        bootstrap_args = argparse.Namespace(
            user=False,
            force=args.force,
            project=project_path,
        )
        _handle_bootstrap(bootstrap_args)

    for pack in sorted(packs):
        pack_args = argparse.Namespace(
            project=project_path,
            name=pack,
            user=False,
            force=True,
        )
        _handle_commands_packs_install(pack_args)

    for mcp_pack in sorted(mcp_packs):
        mcp_args = argparse.Namespace(
            project=project_path,
            name=mcp_pack,
            user=False,
            force=True,
        )
        try:
            _handle_mcp_packs_install(mcp_args)
        except CodexppError as exc:
            print(f"[codexpp] Uyarı: {exc}")

    setup_args = argparse.Namespace(
        project=project_path,
        personas=[],
        output="AGENTS.md",
        codex_agents="~/.codex/AGENTS.md",
        force=args.force,
        show_diff=False,
        diff_color="auto",
        codex_bin="codex",
    )
    _handle_codex_setup(setup_args)

    install_args = argparse.Namespace(
        project=project_path,
        codex_bin="codex",
        config="~/.codex/config.toml",
        include_pack=list(packs),
        force=True,
    )
    _handle_codex_install(install_args)

    mcp_setup_args = argparse.Namespace(
        project=project_path,
        codex_dir="~/.codex/mcp",
        format="json",
        force=True,
        show_diff=False,
        diff_color="auto",
    )
    _handle_mcp_setup(mcp_setup_args)

    print("[codexpp] Codex init tamamlandı.")


def _handle_mcp_list(args: argparse.Namespace) -> None:
    servers = loader.load_mcp_servers(start=args.project)
    if not servers:
        print("MCP profili bulunamadı. `codexpp mcp packs install default` komutunu çalıştırmayı deneyin.")
        return

    for server in sorted(servers.values(), key=lambda item: item.identifier):
        tags = f" [{', '.join(server.tags)}]" if server.tags else ""
        print(f"- {server.identifier}{tags} — {server.label}")
        if server.summary:
            print(f"  {server.summary}")
        if args.verbose:
            arg_list = " ".join(server.args) if server.args else "(parametre yok)"
            print(f"  Komut: {server.command} {arg_list}")
            print(f"  Transport: {server.transport} | Auto-start: {'evet' if server.auto_start else 'hayır'}")
            if server.cwd:
                print(f"  Çalışma dizini: {server.cwd}")
            if server.env:
                print("  Ortam değişkenleri:")
                for key, value in server.env.items():
                    placeholder = value or "(boş değer)"
                    print(f"    • {key}={placeholder}")
        print("")


def _handle_mcp_packs_list(args: argparse.Namespace) -> None:
    packs = _available_mcp_packs()
    if not packs:
        print("Yerleşik MCP paketi bulunamadı.")
        return

    installed: set[str] = set()
    for directory in cfg.candidate_mcp_dirs(args.project):
        if directory.exists():
            installed.update(path.stem for path in directory.glob("*.toml"))

    print("Kullanılabilir MCP paketleri:")
    for name in sorted(packs):
        marker = " (kurulu)" if name in installed else ""
        print(f"- {name}{marker}")


def _handle_mcp_packs_install(args: argparse.Namespace) -> None:
    packs = _available_mcp_packs()
    resource = packs.get(args.name)
    if resource is None:
        raise CodexppError(f"MCP paketi bulunamadı: {args.name}")

    if args.user:
        base_dir = cfg.user_config_dir()
    else:
        base_dir = cfg.project_config_dir(args.project)

    target_dir = base_dir / cfg.MCP_DIR_NAME
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{args.name}.toml"
    if target_path.exists() and not args.force:
        raise CodexppError(
            f"MCP paketi zaten mevcut: {target_path}. Üzerine yazmak için `--force` kullanın."
        )

    with resource.open("rb") as handle:
        data = handle.read()
    target_path.write_bytes(data)

    location = "kullanıcı" if args.user else "proje"
    print(f"[codexpp] {args.name} MCP paketi {location} dizinine kuruldu: {target_path}")


def _handle_mcp_setup(args: argparse.Namespace) -> None:
    servers = loader.load_mcp_servers(start=args.project)
    if not servers:
        print("MCP profili bulunamadı. Önce `codexpp mcp packs install default` çalıştırmayı deneyin.")
        return

    formats: List[Tuple[str, Callable[[McpServerDefinition], str]]] = []
    if args.format in {"json", "both"}:
        formats.append(("json", _render_mcp_server_json))
    if args.format in {"toml", "both"}:
        formats.append(("toml", _render_mcp_server_toml))

    target_dir = Path(args.codex_dir).expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)

    use_color = args.diff_color == "always" or (
        args.diff_color == "auto" and sys.stdout.isatty()
    )

    for server in sorted(servers.values(), key=lambda item: item.identifier):
        for fmt, renderer in formats:
            content = renderer(server)
            filename = f"{server.identifier}.{fmt}"
            path = target_dir / filename
            previous = path.read_text(encoding="utf-8") if path.exists() else None

            if previous is not None and previous == content:
                print(f"[codexpp] MCP profili zaten güncel: {path}")
                continue

            if previous is not None and not args.force:
                print(
                    f"[codexpp] MCP profili mevcut, üzerine yazılmadı: {path}. Güncellemek için `--force` ekleyin."
                )
                continue

            if previous is not None and args.show_diff:
                diff_text = _render_diff(path, previous, content)
                if diff_text:
                    if use_color:
                        diff_text = _colorize_diff(diff_text)
                    print(diff_text)

            path.write_text(content, encoding="utf-8")
            print(f"[codexpp] MCP profili yazıldı: {path}")

    print(f"[codexpp] MCP profilleri senkronize edildi: {target_dir}")


def _render_personas_markdown(personas: List[PersonaDefinition]) -> str:
    lines: List[str] = ["# Codex Personas", ""]
    for persona in personas:
        lines.append(f"## {persona.label} (`{persona.identifier}`)")
        if persona.summary:
            lines.append(persona.summary)
        if persona.directives:
            lines.append("")
            lines.append("**Directives**")
            for directive in persona.directives:
                lines.append(f"- {directive}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _render_diff(path: Path, previous: str, updated: str) -> str:
    diff_lines = list(
        difflib.unified_diff(
            previous.splitlines(),
            updated.splitlines(),
            fromfile=f"{path} (önce)",
            tofile=f"{path} (sonra)",
            lineterm="",
        )
    )
    if not diff_lines:
        return ""
    return "\n".join(diff_lines)


def _colorize_diff(diff_text: str) -> str:
    colored_lines: List[str] = []
    for line in diff_text.splitlines():
        if line.startswith("---") or line.startswith("+++"):
            colored_lines.append(f"\033[90m{line}\033[0m")
        elif line.startswith("@@"):
            colored_lines.append(f"\033[36m{line}\033[0m")
        elif line.startswith("+") and not line.startswith("+++"):
            colored_lines.append(f"\033[32m{line}\033[0m")
        elif line.startswith("-") and not line.startswith("---"):
            colored_lines.append(f"\033[31m{line}\033[0m")
        else:
            colored_lines.append(line)
    return "\n".join(colored_lines)


def _collect_personas(
    personas_map: Dict[str, PersonaDefinition], requested: Iterable[str]
) -> List[PersonaDefinition]:
    requested_ids = [identifier for identifier in requested if identifier]
    if requested_ids:
        missing = [identifier for identifier in requested_ids if identifier not in personas_map]
        if missing:
            raise CodexppError(f"Bulunamayan persona(lar): {', '.join(missing)}")
        personas = [personas_map[identifier] for identifier in requested_ids]
    else:
        personas = sorted(personas_map.values(), key=lambda item: item.identifier)
    return personas


def _resolve_personas(identifiers: Iterable[str], start: Path) -> List[PersonaDefinition]:
    requested = [identifier for identifier in identifiers if identifier]
    if not requested:
        return []

    personas = loader.load_personas(start=start)
    missing = [identifier for identifier in requested if identifier not in personas]
    if missing:
        raise CodexppError(f"Bulunamayan persona(lar): {', '.join(missing)}")

    return [personas[identifier] for identifier in requested]


def _compose_prompt(base_prompt: str, personas: List[PersonaDefinition]) -> str:
    if not personas:
        return base_prompt

    blocks: List[str] = []
    for persona in personas:
        directives = "\n".join(f"- {directive}" for directive in persona.directives)
        block = (
            f"[Persona: {persona.label}]\n"
            f"{persona.summary}\n"
            f"Directives:\n{directives}"
        )
        blocks.append(block)

    persona_section = "\n\n".join(blocks)
    return f"{persona_section}\n\n{base_prompt}"


def _invoke_codex(prompt: str, codex_bin: str, extra_args: Iterable[str]) -> None:
    resolved_bin: Optional[str] = shutil.which(codex_bin)
    if resolved_bin is None:
        raise CodexppError(
            f"`{codex_bin}` komutu bulunamadı. Codex CLI kurulu olduğundan emin olun veya `--codex-bin` ile yolu belirtin."
        )

    try:
        subprocess.run(
            [resolved_bin, "exec", *extra_args, "-"],
            input=prompt,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise CodexppError(f"Codex yürütmesi başarısız oldu (kod: {exc.returncode}).") from exc

