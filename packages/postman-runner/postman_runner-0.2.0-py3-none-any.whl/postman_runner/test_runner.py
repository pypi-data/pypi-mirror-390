from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

import requests

from .assertions import AssertionResult, run_assertions


def execute_tests(response: requests.Response, assertion_spec: Dict[str, Any]) -> Tuple[Iterable[AssertionResult], bool]:
    """Run assertions and return the result list along with an overall pass flag."""

    results = run_assertions(response, assertion_spec)
    passed = all(result.passed for result in results) if results else True
    return results, passed


def render_results(results: Iterable[AssertionResult]) -> str:
    lines = ["Assertions:"]
    for result in results:
        prefix = "PASS" if result.passed else "FAIL"
        lines.append(f"  {prefix} {result.name}: {result.message}")
    return "\n".join(lines)
