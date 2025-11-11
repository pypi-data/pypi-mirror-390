from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import requests

from .models import BodySpecification, RequestPayload

DEFAULT_TIMEOUT = 30.0


def execute_request(payload: RequestPayload, timeout: float = DEFAULT_TIMEOUT) -> requests.Response:
    """Execute the HTTP request described by the payload."""

    data, json_body, files, resources = _prepare_body(payload)
    try:
        response = requests.request(
            method=payload.method,
            url=payload.url,
            headers=payload.headers or None,
            data=data,
            json=json_body,
            files=files or None,
            timeout=timeout,
        )
    finally:
        for resource in resources:
            try:
                resource.close()
            except Exception:  # noqa: BLE001
                pass
    return response


def _prepare_body(payload: RequestPayload) -> Tuple[Optional[Any], Optional[Any], Optional[Dict[str, Any]], List[Any]]:
    body: BodySpecification = payload.body
    resources: List[Any] = []
    if not body.mode:
        return None, None, None, resources

    if body.mode == "raw":
        if body.raw is None:
            return None, None, None, resources
        content_type = _get_header(payload.headers, "content-type")
        if content_type and "application/json" in content_type.lower():
            try:
                return None, json.loads(body.raw), None, resources
            except json.JSONDecodeError:
                return body.raw, None, None, resources
        return body.raw, None, None, resources

    if body.mode == "formdata":
        data: Dict[str, Any] = {}
        files: Dict[str, Any] = {}
        for entry in body.formdata:
            key = entry.get("key")
            if not key or entry.get("disabled"):
                continue
            if entry.get("type") == "file":
                src = entry.get("src")
                if not src:
                    continue
                file_handle = open(str(src), "rb")  # noqa: SIM115 - requests expects file objects
                resources.append(file_handle)
                files[key] = file_handle
            else:
                data[key] = entry.get("value", "")
        return data or None, None, files or None, resources

    if body.mode == "urlencoded":
        data = {
            entry.get("key"): entry.get("value", "")
            for entry in body.urlencoded
            if entry.get("key") and not entry.get("disabled")
        }
        return data or None, None, None, resources

    return None, None, None, resources


def _get_header(headers: Dict[str, str], name: str) -> Optional[str]:
    name_lower = name.lower()
    for key, value in headers.items():
        if key.lower() == name_lower:
            return value
    return None
