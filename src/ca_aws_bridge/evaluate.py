from collections import defaultdict
from typing import Any

from .models import ControlResult, Observation


def evaluate(observations: list[Observation], document: dict[str, Any]) -> list[ControlResult]:
    mappings = {item["source_id"]: item for item in document.get("mappings", [])}
    grouped: dict[str, list[Observation]] = defaultdict(list)
    for item in observations:
        if item.source_id in mappings:
            grouped[item.source_id].append(item)
    output = []
    for source_id, items in sorted(grouped.items()):
        mapping = mappings[source_id]
        statuses = {item.normalized_status for item in items}
        status = "not_satisfied" if "fail" in statuses else "satisfied" if statuses == {"pass"} else "unknown"
        output.append(ControlResult(mapping["control_ref"], status, tuple(sorted(item.digest for item in items)), tuple(mapping.get("framework_refs", [])), str(mapping.get("rationale", "")), mapping.get("remediation") if status == "not_satisfied" else None))
    return output
