import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable

from .models import Observation


def timestamp(value: Any) -> str:
    return value if isinstance(value, str) and value else datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def observation(core: dict[str, Any]) -> Observation:
    canonical = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return Observation(**core, digest=hashlib.sha256(canonical.encode()).hexdigest())


def security_control_id(finding: dict[str, Any]) -> str:
    direct = finding.get("Compliance", {}).get("SecurityControlId")
    if direct:
        return str(direct)
    value = str(finding.get("ProductFields", {}).get("StandardsControlArn") or finding.get("GeneratorId") or "unknown-control")
    return value.rstrip("/").rsplit("/", 1)[-1]


def normalize_security_hub(document: dict[str, Any]) -> list[Observation]:
    output = []
    for finding in document.get("Findings", []):
        raw = str(finding.get("Compliance", {}).get("Status", "UNKNOWN"))
        status = {"passed": "pass", "failed": "fail"}.get(raw.lower(), "unknown")
        resources = finding.get("Resources") or [{}]
        source_id = security_control_id(finding)
        for resource in resources:
            output.append(observation({
                "source_kind": "aws-security-hub",
                "source_id": source_id,
                "scope": str(resource.get("Id", "unknown-resource")),
                "observed_at": timestamp(finding.get("UpdatedAt")),
                "raw_status": raw,
                "normalized_status": status,
                "title": str(finding.get("Title", "Security Hub finding")),
                "attributes": {"finding_id": finding.get("Id"), "severity": finding.get("Severity", {}).get("Label"), "resource_type": resource.get("Type")},
            }))
    return output


def normalize_config(document: dict[str, Any]) -> list[Observation]:
    output = []
    for result in document.get("EvaluationResults", []):
        identifier = result.get("EvaluationResultIdentifier", {})
        qualifier = identifier.get("EvaluationResultQualifier", {})
        raw = str(result.get("ComplianceType", "UNKNOWN"))
        status = {"compliant": "pass", "non_compliant": "fail"}.get(raw.lower(), "unknown")
        output.append(observation({
            "source_kind": "aws-config",
            "source_id": str(qualifier.get("ConfigRuleName", "unknown-rule")),
            "scope": str(qualifier.get("ResourceId", "unknown-resource")),
            "observed_at": timestamp(identifier.get("OrderingTimestamp") or result.get("ResultRecordedTime")),
            "raw_status": raw,
            "normalized_status": status,
            "title": "AWS Config evaluation",
            "attributes": {"resource_type": qualifier.get("ResourceType")},
        }))
    return output


def checkov_items(document: dict[str, Any]) -> Iterable[tuple[dict[str, Any], str]]:
    results = document.get("results", {})
    for item in results.get("failed_checks", []): yield item, "fail"
    for item in results.get("passed_checks", []): yield item, "pass"
    for item in results.get("skipped_checks", []): yield item, "unknown"


def normalize_checkov(document: dict[str, Any], observed_at: str | None = None) -> list[Observation]:
    return [observation({
        "source_kind": "checkov",
        "source_id": str(item.get("check_id", "unknown-check")),
        "scope": str(item.get("resource", "unknown-resource")),
        "observed_at": timestamp(observed_at),
        "raw_status": status.upper(),
        "normalized_status": status,
        "title": str(item.get("check_name", "Checkov observation")),
        "attributes": {"file_path": item.get("file_path"), "file_line_range": item.get("file_line_range")},
    }) for item, status in checkov_items(document)]