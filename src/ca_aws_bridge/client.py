import json
import os
import urllib.error
import urllib.request
from typing import Any


class ConfigurationError(RuntimeError):
    pass


class CisoAssistantClient:
    def __init__(self, base_url: str, token: str, endpoint: str = "/api/evidences/") -> None:
        self.base_url, self.token, self.endpoint = base_url.rstrip("/"), token, endpoint

    @classmethod
    def from_environment(cls):
        url, token = os.environ.get("CISO_ASSISTANT_URL", ""), os.environ.get("CISO_ASSISTANT_TOKEN", "")
        if not url or not token:
            raise ConfigurationError("CISO_ASSISTANT_URL and CISO_ASSISTANT_TOKEN are required")
        return cls(url, token, os.environ.get("CISO_ASSISTANT_EVIDENCE_ENDPOINT", "/api/evidences/"))

    @staticmethod
    def evidence_payload(operation: dict[str, Any]) -> dict[str, Any]:
        payload, key = operation["payload"], operation["idempotency_key"]
        return {
            "name": f"Automated evidence: {payload['control_ref']}",
            "ref_id": f"a2z-aws-{key[:20]}",
            "description": json.dumps({"producer": "ciso-assistant-aws-compliance-automation", "control_ref": payload["control_ref"], "status": payload["status"], "framework_refs": payload["framework_refs"], "evidence_digests": [item["digest"] for item in payload["evidence"]], "review_required": operation["review_required"]}, sort_keys=True),
        }

    def apply(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        responses = []
        for operation in plan.get("operations", []):
            request = urllib.request.Request(f"{self.base_url}{self.endpoint}", data=json.dumps(self.evidence_payload(operation)).encode(), method="POST", headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "Idempotency-Key": operation["idempotency_key"]})
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    responses.append({"status": response.status, "body": json.loads(response.read() or b"{}")})
            except urllib.error.HTTPError as exc:
                raise RuntimeError(f"CISO Assistant API returned HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc
        return responses
