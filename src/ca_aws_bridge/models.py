from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Observation:
    source_kind: str
    source_id: str
    scope: str
    observed_at: str
    raw_status: str
    normalized_status: str
    title: str
    attributes: dict[str, Any]
    digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ControlResult:
    control_ref: str
    status: str
    evidence_digests: tuple[str, ...]
    framework_refs: tuple[str, ...]
    rationale: str
    remediation: str | None
