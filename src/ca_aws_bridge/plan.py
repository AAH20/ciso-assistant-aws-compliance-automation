import hashlib
import json
from typing import Any

from .models import ControlResult, Observation


def build_plan(observations: list[Observation], results: list[ControlResult]) -> dict[str, Any]:
    indexed = {item.digest: item for item in observations}
    operations = []
    for result in results:
        payload = {
            "control_ref": result.control_ref, "status": result.status,
            "framework_refs": list(result.framework_refs), "rationale": result.rationale,
            "remediation": result.remediation,
            "evidence": [indexed[digest].to_dict() for digest in result.evidence_digests],
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        operations.append({"operation": "upsert_control_evidence", "idempotency_key": hashlib.sha256(canonical.encode()).hexdigest(), "review_required": True, "payload": payload})
    return {"schema_version": "1.0", "dry_run_default": True, "operations": operations}
