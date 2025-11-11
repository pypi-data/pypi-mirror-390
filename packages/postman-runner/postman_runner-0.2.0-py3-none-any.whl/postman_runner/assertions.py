from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence

import requests


@dataclass
class AssertionResult:
    name: str
    passed: bool
    message: str


class AssertionErrorCollection(Exception):
    """Raised when one or more assertions fail."""

    def __init__(self, results: Sequence[AssertionResult]):
        self.results = results
        super().__init__("One or more assertions failed")


def run_assertions(response: requests.Response, assertions: Dict[str, Any]) -> List[AssertionResult]:
    """Execute the simple assertion rules against the response."""

    results: List[AssertionResult] = []
    json_cache: Any = None
    text_cache: str = ""

    for name, rule in assertions.items():
        try:
            if name == "status_code":
                expected = int(rule)
                actual = response.status_code
                passed = actual == expected
                message = f"expected {expected}, got {actual}"
            elif name.startswith("json:"):
                path = name.split(":", 1)[1]
                if json_cache is None:
                    json_cache = response.json()
                actual = _extract_json_value(json_cache, path)
                passed = actual == rule
                message = f"expected {rule!r}, got {actual!r}"
            elif name.startswith("header:"):
                header_name = name.split(":", 1)[1]
                actual = response.headers.get(header_name)
                passed = actual == rule
                message = f"expected {rule!r}, got {actual!r}"
            elif name == "text_contains":
                if not isinstance(rule, (list, tuple, set)):
                    expected_values: Iterable[str] = [str(rule)]
                else:
                    expected_values = [str(value) for value in rule]
                if not text_cache:
                    text_cache = response.text
                missing = [value for value in expected_values if value not in text_cache]
                passed = not missing
                message = "missing: " + ", ".join(missing) if missing else "all substrings present"
            elif name == "elapsed_ms_lt":
                threshold = float(rule)
                actual_ms = response.elapsed.total_seconds() * 1000
                passed = actual_ms < threshold
                message = f"elapsed {actual_ms:.2f} ms < {threshold:.2f} ms"
            else:
                passed = False
                message = "unsupported assertion key"
        except Exception as exc:  # noqa: BLE001
            passed = False
            message = f"error while evaluating assertion: {exc}"
        results.append(AssertionResult(name=name, passed=passed, message=message))
    return results


def _extract_json_value(document: Any, path: str) -> Any:
    value = document
    for token in _tokenize_path(path):
        if isinstance(token, int):
            if not isinstance(value, list):
                raise KeyError(f"Index {token} not available on non-list value")
            value = value[token]
        else:
            if not isinstance(value, dict):
                raise KeyError(f"Key '{token}' not available on non-dict value")
            value = value[token]
    return value


def _tokenize_path(path: str) -> List[Any]:
    tokens: List[Any] = []
    buffer = []
    i = 0
    while i < len(path):
        char = path[i]
        if char == '.':
            if buffer:
                tokens.append(''.join(buffer))
                buffer.clear()
            i += 1
        elif char == '[':
            if buffer:
                tokens.append(''.join(buffer))
                buffer.clear()
            i += 1
            index_buffer = []
            while i < len(path) and path[i] != ']':
                index_buffer.append(path[i])
                i += 1
            if i >= len(path) or path[i] != ']':
                raise ValueError(f"Unmatched '[' in json path: {path}")
            index_value = ''.join(index_buffer)
            if not index_value.isdigit():
                raise ValueError(f"Array index must be numeric in path segment: {index_value}")
            tokens.append(int(index_value))
            i += 1
        else:
            buffer.append(char)
            i += 1
    if buffer:
        tokens.append(''.join(buffer))
    return tokens
