#!/usr/bin/env python3
"""Merge host MCP server definitions into Codex TOML or Cursor/Claude JSON configs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


SERVERS = ("gitnexus", "recallium", "mem0")
LOOPBACK_HOSTS = frozenset(("localhost", "127.0.0.1", "::1"))
TOML_URL = re.compile(r"^\s*url\s*=\s*([\"'])(.*?)\1\s*(?:#.*)?$", re.M)


class McpUrlError(ValueError):
    """Raised when an MCP URL would use an unsafe transport."""


def validate_mcp_url(url: object, location: str) -> None:
    """Allow HTTPS everywhere and plain HTTP only for loopback development."""

    if not isinstance(url, str) or not url.strip():
        raise McpUrlError(f"{location} must use a non-empty URL")
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
    except ValueError as error:
        raise McpUrlError(f"invalid MCP URL for {location}: {url}") from error

    if parsed.scheme == "https" and hostname:
        return
    if parsed.scheme == "http" and hostname in LOOPBACK_HOSTS:
        return
    if parsed.scheme == "http":
        raise McpUrlError(
            f"insecure remote HTTP URL for {location}: {url}; "
            "use HTTPS or a loopback host"
        )
    raise McpUrlError(
        f"unsupported MCP URL for {location}: {url}; "
        "use HTTPS or loopback HTTP"
    )


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def section_exists_toml(text: str, server: str) -> bool:
    return bool(re.search(rf"^\[mcp_servers\.{re.escape(server)}\]\s*$", text, re.M))


def section_url_toml(text: str, server: str) -> str | None:
    header = re.search(rf"^\[mcp_servers\.{re.escape(server)}\]\s*$", text, re.M)
    if not header:
        return None
    remainder = text[header.end() :]
    next_section = re.search(r"^\[", remainder, re.M)
    body = remainder[: next_section.start()] if next_section else remainder
    match = TOML_URL.search(body)
    return match.group(2) if match else None


def remove_toml_section(text: str, server: str) -> str:
    pattern = re.compile(
        rf"^\[mcp_servers\.{re.escape(server)}\][^\n]*\n(?:(?!^\[).*\n)*",
        re.M,
    )
    return pattern.sub("", text)


def prompt_yes_no(question: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    print(question + suffix, end="", file=sys.stderr, flush=True)
    reply = sys.stdin.readline().strip()
    if not reply:
        return default
    return reply.lower().startswith("y")


def prompt_mcp_url(host: str, server: str) -> str:
    print(f"New {host} {server} URL: ", end="", file=sys.stderr, flush=True)
    url = sys.stdin.readline().strip()
    if not url:
        raise McpUrlError(f"{host} {server} replacement URL must not be empty")
    return url


def choose_existing_url(
    host: str,
    server: str,
    current_url: str,
    replacement_url: str | None,
) -> tuple[bool, str | None]:
    print(f"Existing {host} {server} URL: {current_url}", file=sys.stderr)
    if replacement_url:
        question = f"Replace {host} {server} URL with {replacement_url}?"
    else:
        question = f"Replace {host} {server} URL?"
    if not prompt_yes_no(question):
        return False, replacement_url
    if replacement_url is None:
        replacement_url = prompt_mcp_url(host, server)
    return True, replacement_url


def load_fragment(path: Path, mem0_url: str | None) -> str | None:
    text = path.read_text(encoding="utf-8")
    if "__MEM0_URL__" in text:
        if not mem0_url:
            print("SKIP: mcp_servers.mem0 (pass --mem0-url or answer TTY prompt)")
            return None
        text = text.replace("__MEM0_URL__", mem0_url)
    for _, url in TOML_URL.findall(text):
        validate_mcp_url(url, f"mcp_servers.{path.stem}")
    return text.rstrip() + "\n"


def merge_codex_toml(
    target: Path,
    fragments_dir: Path,
    policy: str,
    mem0_url: str | None,
    interactive: bool,
    dry_run: bool,
) -> int:
    text = read_text(target)
    changed = False
    for server in SERVERS:
        frag_path = fragments_dir / f"{server}.toml"
        if not frag_path.exists():
            continue
        exists = section_exists_toml(text, server)
        current_url = section_url_toml(text, server) if exists else None
        replacement_url = mem0_url if server == "mem0" else section_url_toml(read_text(frag_path), server)
        if exists and current_url and interactive:
            replace, replacement_url = choose_existing_url(
                "Codex", server, current_url, replacement_url
            )
            if not replace:
                print(f"KEEP: mcp_servers.{server}")
                continue
            if server == "mem0":
                mem0_url = replacement_url
        elif exists and policy == "keep":
            print(f"KEEP: mcp_servers.{server}")
            continue
        elif exists and policy == "ask":
            print(f"CONFLICT: mcp_servers.{server} (use --mcp-keep or --mcp-overwrite)", file=sys.stderr)
            return 2
        if not exists and server == "mem0" and not mem0_url and interactive:
            if prompt_yes_no("Add Codex mem0 URL now?"):
                mem0_url = prompt_mcp_url("Codex", server)
        fragment = load_fragment(frag_path, mem0_url if server == "mem0" else None)
        if fragment is None:
            continue
        if exists:
            text = remove_toml_section(text, server)
            print(f"OVERWRITE: mcp_servers.{server}")
        else:
            print(f"ADD: mcp_servers.{server}")
        if text and not text.endswith("\n"):
            text += "\n"
        if "[mcp_servers]" not in text:
            text = (text + "\n" if text else "") + "[mcp_servers]\n"
        text = text.rstrip() + "\n\n" + fragment
        changed = True
    if dry_run:
        print(f"DRY-RUN: would update {target}")
        return 0
    if changed:
        write_atomic(target, text if text.endswith("\n") else text + "\n")
        print(f"UPDATED: {target}")
    else:
        print(f"UNCHANGED: {target}")
    return 0


def merge_json_mcp_servers(
    target: Path,
    fragment_file: Path,
    policy: str,
    mem0_url: str | None,
    interactive: bool,
    dry_run: bool,
    host_label: str,
) -> int:
    """Merge managed servers into a JSON document's mcpServers object (Cursor/Claude)."""
    raw = read_text(target).strip()
    data = json.loads(raw) if raw else {"mcpServers": {}}
    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        data["mcpServers"] = {}
    servers = json.loads(fragment_file.read_text(encoding="utf-8"))
    changed = False
    for name in SERVERS:
        if name not in servers:
            continue
        entry = dict(servers[name])
        existing_entry = data["mcpServers"].get(name)
        current_url = existing_entry.get("url") if isinstance(existing_entry, dict) else None
        replacement_url = entry.get("url")
        interactive_url_replaced = False
        if replacement_url == "__MEM0_URL__":
            replacement_url = mem0_url
        if isinstance(current_url, str) and current_url and interactive:
            replace, replacement_url = choose_existing_url(
                host_label, name, current_url, replacement_url
            )
            if not replace:
                print(f"KEEP: mcpServers.{name}")
                continue
            interactive_url_replaced = True
            if name == "mem0":
                mem0_url = replacement_url
        if name == "mem0":
            url = entry.get("url", "")
            if url == "__MEM0_URL__":
                if not mem0_url and interactive and not current_url:
                    if prompt_yes_no(f"Add {host_label} mem0 URL now?"):
                        mem0_url = prompt_mcp_url(host_label, name)
                if not mem0_url:
                    print("SKIP: mcpServers.mem0 (pass --mem0-url or answer TTY prompt)")
                    continue
                entry["url"] = mem0_url
        if "url" in entry:
            validate_mcp_url(entry["url"], f"mcpServers.{name}")
        exists = name in data["mcpServers"]
        if exists and not interactive_url_replaced and policy == "keep":
            print(f"KEEP: mcpServers.{name}")
            continue
        elif exists and not interactive_url_replaced and policy == "ask":
            print(f"CONFLICT: mcpServers.{name} (use --mcp-keep or --mcp-overwrite)", file=sys.stderr)
            return 2
        data["mcpServers"][name] = entry
        print(("OVERWRITE" if exists else "ADD") + f": mcpServers.{name}")
        changed = True
    if dry_run:
        print(f"DRY-RUN: would update {target}")
        return 0
    if changed:
        write_atomic(target, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"UPDATED: {target}")
    else:
        print(f"UNCHANGED: {target}")
    return 0


def merge_cursor_json(
    target: Path,
    fragment_file: Path,
    policy: str,
    mem0_url: str | None,
    interactive: bool,
    dry_run: bool,
) -> int:
    return merge_json_mcp_servers(
        target, fragment_file, policy, mem0_url, interactive, dry_run, "Cursor"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", choices=("codex", "cursor", "claude"), required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--fragments", required=True)
    parser.add_argument("--policy", choices=("keep", "overwrite", "ask"), default="ask")
    parser.add_argument("--mem0-url", default=None)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    target = Path(args.target)
    fragments = Path(args.fragments)
    try:
        if args.host == "codex":
            return merge_codex_toml(
                target, fragments, args.policy, args.mem0_url, args.interactive, args.dry_run
            )
        host_label = "Cursor" if args.host == "cursor" else "Claude"
        return merge_json_mcp_servers(
            target,
            fragments,
            args.policy,
            args.mem0_url,
            args.interactive,
            args.dry_run,
            host_label,
        )
    except McpUrlError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
