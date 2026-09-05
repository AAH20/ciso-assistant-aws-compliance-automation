# Production Roadmap

Implemented: Security Hub ASFF, AWS Config and Checkov adapters; canonical evidence digests; explicit mappings; deterministic aggregation; idempotent review-gated plans; conservative Evidence translation; offline tests and CI.

Next:

1. Pin and contract-test a supported CISO Assistant release.
2. Add paginated boto3 collectors with read-only cross-account roles.
3. Add Organizations, IAM Access Analyzer, GuardDuty, Inspector, CloudTrail and EKS adapters.
4. Add OPA/Conftest, Trivy and GitHub attestations.
5. Add durable state, retries, dead letters, OpenTelemetry and per-account SLOs.
6. Generate Terraform and CloudFormation remediation PR payloads.
7. Recollect effective state and prove remediation results.
8. Package ECS, EKS and Lambda deployment patterns.

Production readiness requires tenant isolation, restore, threat-model, migration and authenticated end-to-end tests. Synthetic fixtures are not live-cloud evidence.
