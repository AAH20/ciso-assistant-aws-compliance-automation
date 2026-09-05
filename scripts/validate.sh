#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
python3 -m unittest discover -s tests -v
work_dir="${TMPDIR:-/tmp}/ca-aws-bridge-validation"
mkdir -p "$work_dir"
for source in security-hub aws-config checkov; do
  case "$source" in security-hub) input="examples/security-hub-findings.json" ;; aws-config) input="examples/aws-config-results.json" ;; checkov) input="examples/checkov.json" ;; esac
  python3 -m ca_aws_bridge.cli normalize --source "$source" --input "$input" --output "$work_dir/$source-evidence.json"
  python3 -m ca_aws_bridge.cli plan --evidence "$work_dir/$source-evidence.json" --mappings config/control-mappings.json --output "$work_dir/$source-plan.json"
done
python3 -m compileall -q src
echo "Validation passed; generated plans are in $work_dir"
