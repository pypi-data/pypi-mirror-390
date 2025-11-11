from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BodySpecification:
    """Represents the supported request body formats."""

    mode: Optional[str] = None
    raw: Optional[str] = None
    formdata: List[Dict[str, Any]] = field(default_factory=list)
    urlencoded: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RequestPayload:
    """Normalized request data ready for execution."""

    name: str
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: BodySpecification = field(default_factory=BodySpecification)
    assertions: Dict[str, Any] = field(default_factory=dict)
