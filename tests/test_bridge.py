import json
import unittest
from pathlib import Path

from ca_aws_bridge.client import CisoAssistantClient
from ca_aws_bridge.evaluate import evaluate
from ca_aws_bridge.normalize import normalize_checkov, normalize_config, normalize_security_hub
from ca_aws_bridge.normalize import security_control_id
from ca_aws_bridge.plan import build_plan

ROOT = Path(__file__).resolve().parents[1]


class BridgeTests(unittest.TestCase):
    def load(self, path): return json.loads((ROOT / path).read_text(encoding="utf-8"))
    def mappings(self): return self.load("config/control-mappings.json")

    def test_security_hub_failure_dominates(self):
        observations = normalize_security_hub(self.load("examples/security-hub-findings.json"))
        result = evaluate(observations, self.mappings())[0]
        self.assertEqual(2, len(observations)); self.assertEqual("not_satisfied", result.status)

    def test_config_non_compliance_maps_to_failure(self):
        observations = normalize_config(self.load("examples/aws-config-results.json"))
        self.assertEqual("not_satisfied", evaluate(observations, self.mappings())[0].status)

    def test_checkov_plan_and_api_reference_are_stable(self):
        observations = normalize_checkov(self.load("examples/checkov.json"), "2026-09-05T10:00:00Z")
        results = evaluate(observations, self.mappings()); first = build_plan(observations, results)
        self.assertEqual(first, build_plan(observations, results))
        payload = CisoAssistantClient.evidence_payload(first["operations"][0])
        self.assertTrue(payload["ref_id"].startswith("a2z-aws-")); self.assertNotIn("applied_controls", payload)

    def test_unmapped_signal_is_not_a_control(self):
        source = self.load("examples/security-hub-findings.json"); source["Findings"][0]["Compliance"]["SecurityControlId"] = "UNMAPPED"; source["Findings"] = source["Findings"][:1]
        self.assertEqual([], evaluate(normalize_security_hub(source), self.mappings()))

    def test_full_standards_control_arn_is_normalized(self):
        finding = {"ProductFields": {"StandardsControlArn": "arn:aws:securityhub:us-east-1::control/S3.1"}}
        self.assertEqual("S3.1", security_control_id(finding))


if __name__ == "__main__": unittest.main()