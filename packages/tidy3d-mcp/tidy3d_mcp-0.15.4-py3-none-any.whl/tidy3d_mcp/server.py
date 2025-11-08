from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
import webbrowser

from fastmcp import FastMCP
from fastmcp.client.auth import BearerAuth
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.server.proxy import ProxyClient
from fastmcp.tools import Tool

from urllib.parse import urlencode
from pathlib import Path

from .tools import (
    configure_dispatcher,
    capture,
    rotate_viewer,
    set_bridge_url,
    show_structures,
    validate_simulation,
)


def _select_free_port() -> int:
    """Return a host-local TCP port that is currently unused."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind(('127.0.0.1', 0))
        _, port = candidate.getsockname()
    return int(port)


def _viewer_bridge_uri(port: int, host: str | None) -> str:
    """Build the deeplink URI used to request a viewer bridge."""
    params: dict[str, str] = {'port': str(port)}
    if host:
        params['host'] = host
    normalized = (host or '').lower()
    scheme: str | None
    if 'cursor' in normalized:
        scheme = 'cursor'
    elif 'vscode' in normalized:
        scheme = 'vscode'
    else:
        scheme = None
    query = urlencode(params)
    extension_id = 'Flexcompute.tidy3d'
    if scheme:
        return f'{scheme}://{extension_id}/bridge?{query}'
    return f'tidy3d://bridge?{query}'


def _open_deeplink(uri: str) -> None:
    """Launch the viewer deeplink or fail if unavailable."""
    launched = webbrowser.open(uri, new=0, autoraise=True)
    if not launched:
        raise RuntimeError('deeplink launch was rejected by the host OS')


def _await_bridge(port: int, timeout: float = 15.0) -> str:
    """Wait for the viewer bridge to bind and return its base URL."""
    deadline = time.monotonic() + timeout
    endpoint = f'http://127.0.0.1:{port}'
    while True:
        payload = json.dumps({}).encode('utf-8')
        request = urllib.request.Request(
            f'{endpoint}/viewer/ping',
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=1.0):
                return endpoint
        except urllib.error.URLError:
            if time.monotonic() >= deadline:
                break
            time.sleep(0.25)
    raise RuntimeError('viewer bridge did not start within the expected window')


def _bootstrap_viewer_bridge(host: str | None) -> None:
    """Activate the viewer bridge via deeplink and persist its location."""
    port = _select_free_port()
    deeplink = _viewer_bridge_uri(port, host)
    _open_deeplink(deeplink)
    bridge_url = _await_bridge(port)
    set_bridge_url(bridge_url)


def _descriptor_path() -> Path:
    return Path.home() / '.tidy3d' / 'tidy3d-extension.json'


def _bridge_url_from_descriptor(host: str | None) -> str | None:
    target_host = host or 'vscode'
    try:
        raw = _descriptor_path().read_text(encoding='utf-8')
    except FileNotFoundError:
        return None
    except OSError:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    candidate = payload.get(target_host)
    if not isinstance(candidate, dict):
        return None
    value = candidate.get('bridge_url')
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _resolve_requested_bridge(host: str | None, explicit: str | None) -> str | None:
    sources = [
        explicit,
        os.getenv('TIDY3D_VIEWER_BRIDGE_URL', '').strip() or None,
        _bridge_url_from_descriptor(host),
    ]
    for entry in sources:
        if entry:
            return entry
    return None


def main(argv: list[str] | None = None):
    """Launch the FastMCP proxy with host-aware bookkeeping."""
    parser = argparse.ArgumentParser(prog='tidy3d-mcp')
    parser.add_argument('--host', choices=('vscode', 'cursor'), default='vscode')
    parser.add_argument('--api-key', required=True)
    parser.add_argument('--viewer-bridge', default=None)
    parser.add_argument('--enable-viewer', action='store_true')
    args = parser.parse_args(argv)

    bridge_arg = _resolve_requested_bridge(args.host, args.viewer_bridge)
    configure_dispatcher(args.host, bridge_arg)
    viewer_enabled = bool(args.enable_viewer)
    if viewer_enabled:
        if bridge_arg:
            set_bridge_url(bridge_arg)
        else:
            try:
                _bootstrap_viewer_bridge(args.host)
            except Exception as exc:
                print(f'Viewer bridge initialization failed: {exc}', file=sys.stderr)
                set_bridge_url(None)
                viewer_enabled = False
    mcp_url = os.getenv('REMOTE_MCP_URL', 'https://flexagent.simulation.cloud/')
    auth = BearerAuth(token=args.api_key)
    # Production WAF blocks non-browser user agents; force a friendly default and allow overrides.
    user_agent = os.getenv('TIDY3D_MCP_USER_AGENT', '').strip() or 'Mozilla/5.0 (compatible; tidy3d-mcp)'
    headers = {'User-Agent': user_agent}
    transport = StreamableHttpTransport(mcp_url, headers=headers, auth=auth)
    proxy = FastMCP.as_proxy(ProxyClient(transport), name="Tidy3D")

    if viewer_enabled:
        proxy.add_tool(Tool.from_function(validate_simulation))
        proxy.add_tool(Tool.from_function(rotate_viewer))
        # Capture/visibility MCP tools are temporarily disabled while the
        # FlexAgent viewer stops responding to their bridge commands.
        # Restore the registrations below once CAPTURE/SWITCH_VISIBILITY
        # replies work again in the hosted viewer.
        # proxy.add_tool(Tool.from_function(capture))
        # proxy.add_tool(Tool.from_function(show_structures))

    proxy.run(show_banner=False)


if __name__ == '__main__':
    main()
