# Security Policy

Do not submit AWS credentials, session tokens, secret values, Terraform state, personal data or unredacted account exports in issues. Collectors should use read-only roles; synchronization tokens must be narrowly scoped and stored in a managed secret store. Remote writes require explicit `--apply`.

Report vulnerabilities privately through the repository owner's GitHub security advisory channel.
