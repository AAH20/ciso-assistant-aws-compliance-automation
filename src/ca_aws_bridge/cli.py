import argparse
import json
from pathlib import Path
from typing import Any

from .client import CisoAssistantClient
from .evaluate import evaluate
from .models import Observation
from .normalize import normalize_checkov, normalize_config, normalize_security_hub
from .plan import build_plan


def read(path: str) -> Any: return json.loads(Path(path).read_text(encoding="utf-8"))
def write(path: str, value: Any) -> None:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="AWS/IaC evidence bridge for CISO Assistant")
    commands = parser.add_subparsers(dest="command", required=True)
    norm = commands.add_parser("normalize"); norm.add_argument("--source", choices=("security-hub", "aws-config", "checkov"), required=True); norm.add_argument("--input", required=True); norm.add_argument("--output", required=True)
    plan = commands.add_parser("plan"); plan.add_argument("--evidence", required=True); plan.add_argument("--mappings", required=True); plan.add_argument("--output", required=True)
    sync = commands.add_parser("sync"); sync.add_argument("--plan", required=True); sync.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.command == "normalize":
        adapters = {"security-hub": normalize_security_hub, "aws-config": normalize_config, "checkov": normalize_checkov}
        observations = adapters[args.source](read(args.input))
        write(args.output, {"schema_version": "1.0", "observations": [item.to_dict() for item in observations]}); return 0
    if args.command == "plan":
        observations = [Observation(**item) for item in read(args.evidence).get("observations", [])]
        write(args.output, build_plan(observations, evaluate(observations, read(args.mappings)))); return 0
    document = read(args.plan)
    if not args.apply:
        print(json.dumps(document, indent=2, sort_keys=True)); return 0
    print(json.dumps(CisoAssistantClient.from_environment().apply(document), indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
