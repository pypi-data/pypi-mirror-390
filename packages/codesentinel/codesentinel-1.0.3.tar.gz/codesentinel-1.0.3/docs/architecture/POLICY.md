# CodeSentinel Non-Destructive Policy and `!!!!` Trigger

## Fundamental Policy Hierarchy

**Priority Distribution (Descending Importance):**

1. **CORE CONCEPTS** (Absolute Priority)
   - SECURITY > EFFICIENCY > MINIMALISM
   - These three principles guide ALL decisions
   - Higher priority concept always overrides lower priority

2. **PERMANENT DIRECTIVES**
   - Non-negotiable security rules (credential management, audit logging)
   - Cannot be violated under any circumstances
   - Always in effect

3. **PERSISTENT POLICIES**
   - Non-destructive operations, feature preservation, style preservation
   - Can be overridden ONLY when they explicitly violate Core Concepts or Permanent Directives

**This hierarchy is fundamental to CodeSentinel's operating policy.**

## Development Audit Execution

The `!!!!` trigger is a development-audit accelerator that:

- **Executes thoroughly and comprehensively** - Always complete analysis
- **Focuses heavily on the three core concepts** - Security, Efficiency, Minimalism
- **Complies with all directives and policies** - EXCEPT where they would explicitly violate a core concept
- **Never removes features or reduces capability** - Unless security demands it
- **Resolves conflicts and duplications safely** - Following the hierarchy
- **Operates in non-destructive, feature-preserving mode by default**

Implementation details:

- Config carries a persistent `policy` section with:
  - `non_destructive: true`
  - `feature_preservation: true`
  - `conflict_resolution: "merge-prefer-existing"`
  - `principles: ["SECURITY", "EFFICIENCY", "MINIMALISM"]`
  - `hierarchy: ["CORE_CONCEPTS", "PERMANENT_DIRECTIVES", "PERSISTENT_POLICIES"]`
- Config also carries `dev_audit.trigger_tokens` including `!!!!` and `dev_audit.enforce_policy: true`.
- DevAudit reads and reports policy, and does not perform any destructive operations.
- Future automation invoked by `!!!!` MUST respect this policy hierarchy

This policy is persistent and loaded on every run, guaranteeing that `!!!!` never results in feature loss unless absolutely required by security concerns.
