# Architecture

CISO Assistant remains the GRC system of record. This independent bridge owns technical collection, normalization, deterministic evaluation and synchronization planning.

1. Read-only organization and account collectors export sanitized Security Hub, Config or IaC results.
2. Adapters convert each source to a canonical observation and SHA-256 digest.
3. Reviewed mappings connect technical signals to internal controls.
4. Failure dominates pass during aggregation; ambiguity remains `unknown`.
5. Stable idempotency keys make synchronization retry-safe.
6. Dry-run is the default and every operation requires review.
7. The generic adapter creates conservative Evidence fields. Control UUID linking requires a pinned CISO Assistant release adapter and authenticated contract tests.
8. An approved GitOps change is followed by recollection to verify effective state.

Production deployments should use Security Hub delegated administration, AWS Config aggregators and read-only cross-account roles. Store evidence in customer-controlled encrypted storage, isolate tenants, use private connectivity, redact identifiers, instrument with OpenTelemetry and give remediation automation pull-request—not direct infrastructure—authority.
