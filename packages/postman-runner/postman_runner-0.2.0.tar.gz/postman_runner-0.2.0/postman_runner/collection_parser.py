from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .models import BodySpecification, RequestPayload


def load_collection(path: Path) -> Dict[str, Any]:
    """Load a Postman collection from disk."""

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_request_names(collection: Dict[str, Any]) -> List[str]:
    """Return the flattened request names within the collection."""

    return [item.get("name", "") for item in _iter_request_entries(collection.get("item", []))]


def find_request(collection: Dict[str, Any], request_name: str) -> RequestPayload:
    """Find a request by its name and normalize it."""

    for item in _iter_request_entries(collection.get("item", [])):
        if item.get("name") == request_name:
            return _parse_request_item(item)
    raise KeyError(f"Request '{request_name}' not found in collection")


def extract_requests(collection: Dict[str, Any]) -> List[RequestPayload]:
    """Return every request in the collection as a RequestPayload."""

    return [_parse_request_item(item) for item in _iter_request_entries(collection.get("item", []))]


def _iter_items(items: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for item in items:
        if "item" in item:
            yield from _iter_items(item["item"])
        else:
            yield item


def _iter_request_entries(items: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for item in _iter_items(items):
        if "request" in item:
            yield item


def _parse_request_item(item: Dict[str, Any]) -> RequestPayload:
    request_block = item.get("request", {})
    headers = _extract_headers(request_block.get("header", []))
    body_spec = _extract_body(request_block.get("body", {}))
    url = _resolve_url(request_block.get("url"))
    method = request_block.get("method", "GET").upper()
    assertions = _extract_assertions(item)
    return RequestPayload(
        name=item.get("name", "Unnamed"),
        method=method,
        url=url,
        headers=headers,
        body=body_spec,
        assertions=assertions,
    )


def _extract_headers(headers: Iterable[Dict[str, Any]]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for header in headers or []:
        if header.get("disabled"):
            continue
        key = header.get("key")
        value = header.get("value")
        if key is None or value is None:
            continue
        result[str(key)] = str(value)
    return result


def _extract_body(body_block: Dict[str, Any]) -> BodySpecification:
    spec = BodySpecification()
    if not body_block:
        return spec

    mode = body_block.get("mode")
    spec.mode = mode

    if mode == "raw":
        spec.raw = body_block.get("raw")
    elif mode == "formdata":
        entries = body_block.get("formdata", [])
        spec.formdata = [entry for entry in entries if not entry.get("disabled")]
    elif mode == "urlencoded":
        entries = body_block.get("urlencoded", [])
        spec.urlencoded = [entry for entry in entries if not entry.get("disabled")]
    return spec


def _resolve_url(url_spec: Any) -> str:
    if isinstance(url_spec, str):
        return url_spec
    if isinstance(url_spec, dict):
        if url_spec.get("raw"):
            return url_spec["raw"]
        protocol = url_spec.get("protocol")
        host = url_spec.get("host")
        if isinstance(host, list):
            host = ".".join(part for part in host if part)
        path = url_spec.get("path")
        if isinstance(path, list):
            path = "/".join(str(part) for part in path if part)
        port = url_spec.get("port")
        base = host or ""
        if protocol:
            base = f"{protocol}://{base}"
        if port:
            base = f"{base}:{port}"
        query = url_spec.get("query")
        query_string = ""
        if isinstance(query, list) and query:
            active = [f"{entry.get('key')}={entry.get('value')}" for entry in query if not entry.get("disabled")]
            if active:
                query_string = "?" + "&".join(active)
        if path:
            if not str(path).startswith("/"):
                base = f"{base}/{path}"
            else:
                base = f"{base}{path}"
        return f"{base}{query_string}"
    raise ValueError("Unsupported URL specification in collection")


def _extract_assertions(item: Dict[str, Any]) -> Dict[str, Any]:
    assertions = item.get("assertions") or item.get("assert", {})
    if isinstance(assertions, dict):
        return assertions
    return {}
