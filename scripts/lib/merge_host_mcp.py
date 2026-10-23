#!/usr/bin/env python3
"""Merge host MCP server definitions into native TOML or JSON configs."""

from __future__ import annotations

import argparse
import copy
import datetime
import ipaddress
import json
import math
import os
import re
import sys
import stat
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

try:
    import tomllib
except ImportError:  # Python 3.10 remains supported when tomli is available.
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


SERVERS = ("gitnexus", "recallium", "mem0")
LOOPBACK_HOSTS = frozenset(("localhost", "127.0.0.1", "::1"))
PRIVATE_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7")
)


class McpUrlError(ValueError):
    """Raised when an MCP URL would use an unsafe transport."""


def validate_mcp_url(url: object, location: str) -> None:
    """Allow HTTPS everywhere and HTTP for loopback or private-network hosts."""

    if not isinstance(url, str) or not url.strip():
        raise McpUrlError(f"{location} must use a non-empty URL")
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
    except ValueError as error:
        raise McpUrlError(f"invalid MCP URL for {location}: {url}") from error

    if parsed.scheme == "https" and hostname:
        return
    if parsed.scheme == "http" and hostname:
        if hostname in LOOPBACK_HOSTS:
            return
        try:
            address = ipaddress.ip_address(hostname)
            if any(address in network for network in PRIVATE_NETWORKS):
                return
        except ValueError:
            pass
    if parsed.scheme == "http":
        raise McpUrlError(
            f"insecure remote HTTP URL for {location}: {url}; "
            "use HTTPS, a loopback host, or a private IP address"
        )
    raise McpUrlError(
        f"unsupported MCP URL for {location}: {url}; "
        "use HTTPS or trusted local-network HTTP"
    )


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    # Preserve CRLF and comments when a keep operation does not require a write.
    with path.open(encoding="utf-8", newline="") as stream:
        return stream.read()


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(temporary)
    try:
        if path.exists():
            os.chmod(tmp, stat.S_IMODE(path.stat().st_mode))
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        tmp.replace(path)
    finally:
        if descriptor != -1:
            os.close(descriptor)
        tmp.unlink(missing_ok=True)


def parse_toml(text: str, location: str) -> dict:
    if tomllib is None:
        raise ValueError(
            "TOML parsing requires Python 3.11+ or the optional tomli package on Python 3.10; "
            "no configuration was changed"
        )
    try:
        return tomllib.loads(text)
    except ValueError as error:
        raise ValueError(f"invalid TOML in {location}: {error}") from error


def toml_servers(data: dict, location: str) -> dict:
    servers = data.get("mcp_servers", {})
    if not isinstance(servers, dict):
        raise ValueError(f"{location}: mcp_servers must be a table")
    for name, entry in servers.items():
        if not isinstance(entry, dict):
            raise ValueError(f"{location}: mcp_servers.{name} must be a server table")
    return servers


def toml_statements(text: str):
    """Split only at real statement boundaries, never inside strings or collections.

    This scanner locates text to preserve; tomllib remains the syntax authority.
    Every edited result is reparsed and compared with the expected full document.
    """
    start = index = depth = 0
    quote = None
    comment = False
    while index < len(text):
        char = text[index]
        if comment:
            if char == "\n":
                comment = False
            else:
                index += 1
                continue
        elif quote:
            if quote.startswith('"') and char == "\\":
                index += 2
                continue
            if text.startswith(quote, index):
                index += len(quote)
                if len(quote) == 3:
                    # Four/five quote endings include one/two literal quotes.
                    while index < len(text) and text[index] == quote[0]:
                        index += 1
                quote = None
                continue
            index += 1
            continue
        elif char in ("'", '"'):
            quote = char * 3 if text.startswith(char * 3, index) else char
            index += len(quote)
            continue
        elif char == "#":
            comment = True
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        if char == "\n" and depth == 0:
            yield text[start:index + 1]
            start = index + 1
        index += 1
    if start < len(text):
        yield text[start:]


def single_toml_path(data: dict) -> tuple[str, ...]:
    """Decode a single header/key with the TOML parser, including quoted dots."""
    path = []
    node = data
    while isinstance(node, dict) and len(node) == 1:
        key, node = next(iter(node.items()))
        path.append(key)
        if isinstance(node, list) and len(node) == 1 and isinstance(node[0], dict):
            node = node[0]
    return tuple(path)


def assignment_path(statement: str) -> tuple[str, ...]:
    quote = None
    index = 0
    while index < len(statement):
        char = statement[index]
        if quote:
            if char == "\\" and quote == '"':
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "=":
            key = statement[:index]
            return single_toml_path(parse_toml(key + " = 0", "assignment key"))
        index += 1
    raise ValueError("unsupported TOML assignment; no configuration was changed")


def toml_key(value: str) -> str:
    return value if re.fullmatch(r"[A-Za-z0-9_-]+", value) else json.dumps(value, ensure_ascii=False)


def toml_value(value) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{toml_key(key)} = {toml_value(item)}" for key, item in value.items()) + " }"
    raise ValueError(f"unsupported TOML value type: {type(value).__name__}")


def same_data(left, right) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(same_data(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same_data(a, b) for a, b in zip(left, right))
    if isinstance(left, float) and isinstance(right, float) and math.isnan(left) and math.isnan(right):
        return True
    return type(left) is type(right) and left == right


def replace_toml_server(text: str, server: str, entry: dict, expected: dict) -> str:
    """Replace only this server's declarations, retaining unrelated source text.

    Table headers, dotted assignments and individual inline server entries work.
    A closed inline mcp_servers parent cannot be safely extended or surgically
    rewritten; reject it explicitly instead of rewriting unrelated user config.
    """
    prefix = ("mcp_servers", server)
    table = ()
    retained = []
    for statement in toml_statements(text):
        trimmed = statement.lstrip()
        if trimmed.startswith("["):
            table = single_toml_path(parse_toml(statement, "table header"))
        elif trimmed and not trimmed.startswith("#"):
            key = table + assignment_path(statement)
            if len(key) < len(prefix) and prefix[:len(key)] == key:
                raise ValueError(
                    "cannot safely update a closed inline mcp_servers table; "
                    "expand it to [mcp_servers.<name>] tables before updating; no configuration was changed"
                )
            if key[:len(prefix)] == prefix:
                continue
        if table[:len(prefix)] != prefix:
            retained.append(statement)
    rendered = f"[mcp_servers.{server}]\n" + "".join(
        f"{toml_key(key)} = {toml_value(value)}\n" for key, value in entry.items()
    )
    result = "".join(retained)
    if result and not result.endswith("\n"):
        result += "\n"
    result += ("\n" if result else "") + rendered
    actual = parse_toml(result, "proposed MCP configuration")
    if not same_data(actual, expected):
        raise ValueError("TOML preservation check failed; no configuration was changed")
    return result


def merged_server_entry(current: dict | None, fragment: dict) -> dict:
    # Preserve host extensions (headers/env/timeouts/enablement); replace only
    # connection selectors so a URL/stdio switch cannot retain both transports.
    retained = copy.deepcopy(current or {})
    for key in ("url", "command", "args", "type", "transport"):
        retained.pop(key, None)
    return {**fragment, **{key: value for key, value in retained.items() if key not in fragment}}


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


def load_fragment(path: Path, mem0_url: str | None) -> dict | None:
    document = parse_toml(read_text(path), str(path))
    servers = toml_servers(document, str(path))
    if set(document) != {"mcp_servers"} or set(servers) != {path.stem}:
        raise ValueError(f"{path}: fragment must define only mcp_servers.{path.stem}")
    entry = copy.deepcopy(servers[path.stem])
    if path.stem == "mem0" and mem0_url:
        entry["url"] = mem0_url
    if entry.get("url") == "__MEM0_URL__":
        if not mem0_url:
            print("SKIP: mcp_servers.mem0 (pass --mem0-url or answer TTY prompt)")
            return None
        entry["url"] = mem0_url
    if "url" in entry:
        validate_mcp_url(entry["url"], f"mcp_servers.{path.stem}")
    return entry


def merge_codex_toml(
    target: Path,
    fragments_dir: Path,
    policy: str,
    mem0_url: str | None,
    interactive: bool,
    dry_run: bool,
) -> int:
    text = read_text(target)
    document = parse_toml(text, str(target))
    servers = toml_servers(document, str(target))
    changed = False
    for server in SERVERS:
        fragment_path = fragments_dir / f"{server}.toml"
        if not fragment_path.exists():
            continue
        exists = server in servers
        current = servers.get(server)
        current_url = current.get("url") if current else None
        # Keeping an existing server never interprets its source spelling or
        # rewrites it just to normalize the file.
        if exists and not (current_url and interactive):
            if policy == "keep":
                print(f"KEEP: mcp_servers.{server}")
                continue
            if policy == "ask":
                print(f"CONFLICT: mcp_servers.{server} (use --mcp-keep or --mcp-overwrite)", file=sys.stderr)
                return 2
        fragment = load_fragment(fragment_path, mem0_url if server == "mem0" else None)
        replacement_url = fragment.get("url") if fragment else None
        if exists and current_url and interactive:
            replace, replacement_url = choose_existing_url("Codex", server, current_url, replacement_url)
            if not replace:
                print(f"KEEP: mcp_servers.{server}")
                continue
            if replacement_url:
                validate_mcp_url(replacement_url, f"mcp_servers.{server}")
                if fragment is None:
                    fragment = {"url": replacement_url}
                else:
                    fragment["url"] = replacement_url
        if not exists and server == "mem0" and fragment is None and interactive:
            if prompt_yes_no("Add Codex mem0 URL now?"):
                mem0_url = prompt_mcp_url("Codex", server)
                fragment = load_fragment(fragment_path, mem0_url)
        if fragment is None:
            continue
        entry = merged_server_entry(current, fragment)
        expected = copy.deepcopy(document)
        expected.setdefault("mcp_servers", {})[server] = entry
        text = replace_toml_server(text, server, entry, expected)
        document = expected
        servers = document["mcp_servers"]
        print(("OVERWRITE" if exists else "ADD") + f": mcp_servers.{server}")
        changed = True
    # Reparse the complete planned transaction before the first filesystem write.
    if changed and not same_data(parse_toml(text, "proposed MCP configuration"), document):
        raise ValueError("TOML preservation check failed; no configuration was changed")
    if dry_run:
        print(f"DRY-RUN: would update {target}")
    elif changed:
        write_atomic(target, text)
        print(f"UPDATED: {target}")
    else:
        print(f"UNCHANGED: {target}")
    return 0


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def parse_json(text: str, *, allow_jsonc: bool = False):
    """Read native WorkBuddy JSONC without altering comment markers in strings.

    Keep mode never writes; a changed JSONC file is serialized as standard JSON,
    retaining all unrelated data values (comments/formatting are not retained).
    """
    if allow_jsonc:
        text = text.removeprefix("\ufeff")
        chars = list(text)
        index = 0
        in_string = False
        while index < len(chars):
            char = chars[index]
            if in_string:
                if char == "\\":
                    index += 2
                    continue
                if char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
            elif text.startswith("//", index):
                end = text.find("\n", index + 2)
                end = len(text) if end == -1 else end
                for offset in range(index, end):
                    if chars[offset] != "\r":
                        chars[offset] = " "
                index = end
                continue
            elif text.startswith("/*", index):
                end = text.find("*/", index + 2)
                if end == -1:
                    raise ValueError("unterminated JSONC block comment")
                end += 2
                for offset in range(index, end):
                    if chars[offset] not in "\r\n":
                        chars[offset] = " "
                index = end
                continue
            index += 1
        index = 0
        in_string = False
        while index < len(chars):
            char = chars[index]
            if in_string:
                if char == "\\":
                    index += 2
                    continue
                if char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
            elif char == ",":
                following = index + 1
                while following < len(chars) and chars[following].isspace():
                    following += 1
                if following < len(chars) and chars[following] in "]}":
                    chars[index] = " "
            index += 1
        text = "".join(chars)
    def invalid_constant(value):
        raise ValueError(f"invalid JSON numeric constant: {value}")
    return json.loads(text, object_pairs_hook=unique_json_object, parse_constant=invalid_constant)


def merge_json_mcp_servers(
    target: Path,
    fragment_file: Path,
    policy: str,
    mem0_url: str | None,
    interactive: bool,
    dry_run: bool,
    host_label: str,
) -> int:
    """Merge managed servers into a host's JSON mcpServers object."""
    raw = read_text(target).strip()
    data = parse_json(raw, allow_jsonc=host_label == "WorkBuddy") if raw else {"mcpServers": {}}
    if not isinstance(data, dict):
        raise ValueError("MCP configuration must be a JSON object")
    if "mcpServers" in data and not isinstance(data["mcpServers"], dict):
        raise ValueError("mcpServers must be a JSON object")
    if "mcpServers" not in data:
        data["mcpServers"] = {}
    servers = parse_json(read_text(fragment_file))
    if not isinstance(servers, dict):
        raise ValueError("MCP fragment must be a JSON object")
    changed = False
    for name in SERVERS:
        if name not in servers:
            continue
        if not isinstance(servers[name], dict):
            raise ValueError(f"MCP fragment entry {name} must be an object")
        entry = dict(servers[name])
        existing_entry = data["mcpServers"].get(name)
        current_url = existing_entry.get("url") if isinstance(existing_entry, dict) else None
        replacement_url = entry.get("url")
        if name == "mem0" and mem0_url:
            replacement_url = mem0_url
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
            if mem0_url:
                entry["url"] = mem0_url
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
        if interactive_url_replaced and replacement_url is not None:
            entry["url"] = replacement_url
            validate_mcp_url(replacement_url, f"mcpServers.{name}")
        data["mcpServers"][name] = merged_server_entry(
            existing_entry if isinstance(existing_entry, dict) else None, entry
        )
        print(("OVERWRITE" if exists else "ADD") + f": mcpServers.{name}")
        changed = True
    if dry_run:
        print(f"DRY-RUN: would update {target}")
        return 0
    if changed:
        content = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if parse_json(content) != data:
            raise ValueError("JSON preservation check failed; no configuration was changed")
        write_atomic(target, content)
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
    parser.add_argument(
        "--host", choices=("codex", "cursor", "claude", "minimax", "workbuddy"), required=True
    )
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
        host_label = {
            "cursor": "Cursor",
            "claude": "Claude",
            "minimax": "MiniMax Code",
            "workbuddy": "WorkBuddy",
        }[args.host]
        return merge_json_mcp_servers(
            target,
            fragments,
            args.policy,
            args.mem0_url,
            args.interactive,
            args.dry_run,
            host_label,
        )
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
