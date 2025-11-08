from __future__ import annotations

import json
import base64
import hashlib
from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Any, TypedDict

from fastmcp.exceptions import ToolError
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from pydantic import Field

from ._dispatcher import invoke_viewer_command
from ._viewers import forget, is_focus_only, remember


ViewerId = Annotated[str, Field(description='Identifier returned by validate_simulation')]
ViewerDirection = Annotated[
    str,
    Field(description='One of TOP, BOTTOM, LEFT, RIGHT, FRONT, BACK (case-insensitive)'),
]


class SlicePayload(TypedDict, total=False):
    code: str
    requirements: list[str]


class ValidationPayload(TypedDict, total=False):
    viewer_id: str
    status: str
    error: str
    window_id: str
    warnings: list[str]
    slice: SlicePayload


class RotatePayload(TypedDict):
    viewer_id: str
    direction: str
    status: str


class VisibilityPayload(TypedDict, total=False):
    viewer_id: str
    status: str
    visibility: list[bool]


VisibilityInput = Annotated[
    list[object],
    Field(description='Structure visibility flags; truthiness normalized per entry'),
]


def _normalize_visibility(entry: object) -> bool:
    if isinstance(entry, bool):
        return entry
    if entry is None:
        return False
    if isinstance(entry, (int, float)):
        return entry != 0
    if isinstance(entry, str):
        value = entry.strip().lower()
        if value in {'true', '1', 'yes', 'on'}:
            return True
        if value in {'false', '0', 'no', 'off', ''}:
            return False
    return bool(entry)


def _normalize_warnings(raw: object) -> list[str] | None:
    if not raw:
        return None
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, Iterable):
        normalized = [str(item) for item in raw if item]
        return normalized or None
    return [str(raw)]


async def rotate_viewer(
    viewer_id: ViewerId,
    direction: ViewerDirection,
) -> ToolResult:
    """Align the viewer camera to the requested orientation."""
    if not viewer_id:
        raise ValueError('viewer_id is required')
    if not direction:
        raise ValueError('direction is required')
    normalized = direction.upper()
    allowed = {'TOP', 'BOTTOM', 'LEFT', 'RIGHT', 'FRONT', 'BACK'}
    if normalized not in allowed:
        raise ValueError(f'direction must be one of {sorted(allowed)}')
    params: dict[str, object | None] = {'viewer': viewer_id, 'direction': normalized}
    result = invoke_viewer_command('rotate', 'rotate', params, timeout=10.0)
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        if is_focus_only(viewer_id):
            forget(viewer_id)
        raise ToolError(f'rotation failed: {error_msg}')
    status = result.get('status', 'ok')
    payload: RotatePayload = {'viewer_id': viewer_id, 'direction': normalized, 'status': status}
    return ToolResult(
        content=[TextContent(type='text', text=f'Viewer aligned to {normalized}')],
        structured_content=payload,
    )


async def show_structures(
    viewer_id: ViewerId,
    visibility: VisibilityInput,
) -> ToolResult:
    """Toggle structure visibility with _normalize_visibility coercion."""
    if not viewer_id:
        raise ValueError('viewer_id is required')
    flags = [_normalize_visibility(entry) for entry in visibility]
    payload = json.dumps(flags)
    params: dict[str, object | None] = {'viewer': viewer_id, 'visibility': payload}
    result = invoke_viewer_command('visibility', 'visibility', params, timeout=10.0)
    error_msg = result.get('error')
    if isinstance(error_msg, str) and error_msg:
        if is_focus_only(viewer_id):
            forget(viewer_id)
        raise ToolError(f'visibility update failed: {error_msg}')
    response: VisibilityPayload = {'viewer_id': viewer_id, 'status': result.get('status', 'ok')}
    returned_flags = result.get('visibility')

    if isinstance(returned_flags, list):
        response['visibility'] = [_normalize_visibility(entry) for entry in returned_flags]
    return ToolResult(
        content=[TextContent(type='text', text=f'Updated visibility for {viewer_id}')],
        structured_content=response,
    )


def _build_inline_payload(file: str) -> dict[str, str]:
    """Read file content and prepare inline viewer payload."""
    candidate = Path(file).expanduser()
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ToolError(f'viewer source not found: {candidate}') from exc
    try:
        data = resolved.read_bytes()
    except FileNotFoundError as exc:
        raise ToolError(f'viewer source not found: {resolved}') from exc
    encoded = base64.b64encode(data).decode('ascii')
    payload: dict[str, str] = {
        'inline_content': encoded,
        'inline_encoding': 'base64',
        'inline_name': resolved.name,
    }
    token = hashlib.sha256(str(resolved).encode('utf-8')).hexdigest()
    payload['inline_token'] = token[:16]
    try:
        payload['source_uri'] = resolved.as_uri()
    except ValueError:
        pass
    try:
        stat = resolved.stat()
    except OSError:
        return payload
    payload['inline_mtime'] = str(stat.st_mtime_ns)
    return payload


async def validate_simulation(
    file: Annotated[str | None, Field(description='Absolute path or workspace URI to evaluate', default=None)] = None,
    symbol: Annotated[str | None, Field(description='Optional variable name selecting a tidy3d.Simulation', default=None)] = None,
    index: Annotated[int | None, Field(description='Zero-based simulation index when multiple exist', ge=0, default=None)] = None,
    viewer_id: Annotated[str | None, Field(description='Existing viewer identifier to revalidate', default=None)] = None,
) -> ToolResult:
    """Validate a simulation file or refresh an existing viewer while merging session warnings."""
    launched = False
    start_result: dict[str, Any] | None = None
    start_warnings: list[str] | None = None
    normalized_viewer = viewer_id.strip() if isinstance(viewer_id, str) else None
    inline_payload: dict[str, str] = {}
    if file:
        inline_payload = _build_inline_payload(file)

    if not normalized_viewer:
        if not file:
            raise ValueError('file is required when viewer_id is not provided')
        params: dict[str, object | None] = dict(inline_payload)
        if symbol:
            params['symbol'] = symbol
        if index is not None:
            params['index'] = index
        start_result = invoke_viewer_command('start', 'ready', params, timeout=10.0)
        error_msg = start_result.get('error') if isinstance(start_result, dict) else None
        if isinstance(error_msg, str) and error_msg:
            raise ToolError(f'viewer reported error: {error_msg}')
        resolved = start_result.get('viewer_id') if isinstance(start_result, dict) else None
        if not isinstance(resolved, str) or not resolved:
            raise ValueError('viewer did not confirm readiness')
        normalized_viewer = resolved
        status = start_result.get('status') if isinstance(start_result, dict) else None
        focusable = isinstance(status, str) and status.lower() == 'focused'
        remember(normalized_viewer, focusable=focusable)
        start_warnings = _normalize_warnings(start_result.get('warnings') or start_result.get('warning')) if isinstance(start_result, dict) else None
        launched = True
    else:
        remember(normalized_viewer)

    if not normalized_viewer:
        raise ValueError('viewer_id is required')

    params: dict[str, object | None] = dict(inline_payload)
    params['viewer'] = normalized_viewer
    check_result = invoke_viewer_command('check', 'check', params, timeout=10.0)
    if not isinstance(check_result, dict):
        raise RuntimeError('viewer returned unsupported payload')

    response: ValidationPayload = {'viewer_id': normalized_viewer}
    status = check_result.get('status')
    if not isinstance(status, str) or not status:
        status = start_result.get('status') if isinstance(start_result, dict) else None
    if isinstance(status, str) and status:
        response['status'] = status
    error_msg = check_result.get('error')
    if isinstance(error_msg, str) and error_msg:
        response['error'] = error_msg
    window_id = check_result.get('window_id')
    if isinstance(window_id, str) and window_id:
        response['window_id'] = window_id

    warnings = _normalize_warnings(check_result.get('warnings') or check_result.get('warning')) or []
    if start_warnings:
        seen = set(warnings)
        for item in start_warnings:
            if item not in seen:
                warnings.append(item)
                seen.add(item)
    if warnings:
        response['warnings'] = warnings

    slice_data = check_result.get('slice')
    if isinstance(slice_data, dict):
        code = slice_data.get('code')
        requirements = slice_data.get('requirements')
        if isinstance(code, str) and code:
            normalized_requirements = requirements if isinstance(requirements, list) else []
            response['slice'] = {
                'code': code,
                'requirements': [str(entry) for entry in normalized_requirements]
            }
    if launched and 'slice' not in response and isinstance(start_result, dict):
        slice_fallback = start_result.get('slice')
        if isinstance(slice_fallback, dict):
            code = slice_fallback.get('code')
            requirements = slice_fallback.get('requirements')
            if isinstance(code, str) and code:
                normalized_requirements = requirements if isinstance(requirements, list) else []
                response['slice'] = {
                    'code': code,
                    'requirements': [str(entry) for entry in normalized_requirements]
                }

    summary_status = response.get('status') or response.get('error') or 'ok'
    return ToolResult(
        content=[TextContent(type='text', text=f'Validation for {normalized_viewer}: {summary_status}')],
        structured_content=response,
    )
