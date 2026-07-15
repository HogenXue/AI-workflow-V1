#!/usr/bin/env python3
"""Merge host MCP server definitions into Codex TOML or Cursor JSON configs."""

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


def remove_toml_section(text: str, server: str) -> str:
    pattern = re.compile(
        rf"^\[mcp_servers\.{re.escape(server)}\][^\n]*\n(?:(?!^\[).*\n)*",
        re.M,
    )
    return pattern.sub("", text)


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
    dry_run: bool,
) -> int:
    text = read_text(target)
    changed = False
    for server in SERVERS:
        frag_path = fragments_dir / f"{server}.toml"
        if not frag_path.exists():
            continue
        exists = section_exists_toml(text, server)
        if exists and policy == "keep":
            print(f"KEEP: mcp_servers.{server}")
            continue
        if exists and policy == "ask":
            print(f"CONFLICT: mcp_servers.{server} (use --mcp-keep or --mcp-overwrite)", file=sys.stderr)
            return 2
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


def merge_cursor_json(
    target: Path,
    fragment_file: Path,
    policy: str,
    mem0_url: str | None,
    dry_run: bool,
) -> int:
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
        if name == "mem0":
            url = entry.get("url", "")
            if url == "__MEM0_URL__":
                if not mem0_url:
                    print("SKIP: mcpServers.mem0 (pass --mem0-url or answer TTY prompt)")
                    continue
                entry["url"] = mem0_url
        if "url" in entry:
            validate_mcp_url(entry["url"], f"mcpServers.{name}")
        exists = name in data["mcpServers"]
        if exists and policy == "keep":
            print(f"KEEP: mcpServers.{name}")
            continue
        if exists and policy == "ask":
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", choices=("codex", "cursor"), required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--fragments", required=True)
    parser.add_argument("--policy", choices=("keep", "overwrite", "ask"), default="ask")
    parser.add_argument("--mem0-url", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    target = Path(args.target)
    fragments = Path(args.fragments)
    try:
        if args.host == "codex":
            return merge_codex_toml(target, fragments, args.policy, args.mem0_url, args.dry_run)
        return merge_cursor_json(target, fragments, args.policy, args.mem0_url, args.dry_run)
    except McpUrlError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
