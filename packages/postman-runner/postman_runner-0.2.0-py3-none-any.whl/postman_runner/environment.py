from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, Mapping

from .models import BodySpecification, RequestPayload

_VARIABLE_PATTERN = re.compile(r"{{\s*([A-Za-z0-9_.-]+)\s*}}")


def load_environment(path: Path) -> Dict[str, str]:
    """Load a Postman environment file into a simple key/value mapping."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:  # pragma: no cover - surface as SystemExit in CLI
        raise SystemExit(f"Could not read environment file '{path}': {exc}") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - surface as SystemExit in CLI
        raise SystemExit(f"Environment file '{path}' is not valid JSON: {exc}") from exc

    if isinstance(raw, dict) and "values" in raw and isinstance(raw["values"], list):
        variables = {
            str(entry.get("key")): str(entry.get("value", ""))
            for entry in raw["values"]
            if entry.get("key") and entry.get("enabled", True)
        }
    elif isinstance(raw, dict):
        variables = {str(key): str(value) for key, value in raw.items()}
    else:  # pragma: no cover - defensive guard
        raise SystemExit(f"Environment file '{path}' must contain an object of variables")

    return variables


def apply_environment(payload: RequestPayload, variables: Mapping[str, str]) -> RequestPayload:
    """Return a copy of the payload with environment variables substituted."""

    if not variables:
        return payload

    headers = {
        _replace_template(key, variables): _replace_template(value, variables)
        for key, value in payload.headers.items()
    }

    body_spec = payload.body
    body = BodySpecification(
        mode=body_spec.mode,
        raw=_replace_template(body_spec.raw, variables) if body_spec.raw is not None else None,
        formdata=[_replace_in_data(entry, variables) for entry in body_spec.formdata],
        urlencoded=[_replace_in_data(entry, variables) for entry in body_spec.urlencoded],
    )

    assertions = _replace_in_data(payload.assertions, variables)

    return replace(
        payload,
        name=_replace_template(payload.name, variables),
        method=_replace_template(payload.method, variables),
        url=_replace_template(payload.url, variables),
        headers=headers,
        body=body,
        assertions=assertions,
    )


def apply_environment_to_data(data: Any, variables: Mapping[str, str]) -> Any:
    """Replace variables inside an arbitrary data structure."""

    return _replace_in_data(data, variables)


def _replace_template(value: Any, variables: Mapping[str, str]) -> Any:
    if value is None:
        return None
    if not isinstance(value, str):
        return value

    def _substitute(match: re.Match[str]) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return _VARIABLE_PATTERN.sub(_substitute, value)


def _replace_in_data(data: Any, variables: Mapping[str, str]) -> Any:
    if isinstance(data, dict):
        return {
            _replace_template(key, variables): _replace_in_data(value, variables)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [_replace_in_data(item, variables) for item in data]
    return _replace_template(data, variables)
