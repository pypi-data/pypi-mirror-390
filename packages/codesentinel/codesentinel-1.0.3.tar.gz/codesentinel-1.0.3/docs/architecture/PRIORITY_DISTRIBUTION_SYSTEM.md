# CodeSentinel Priority Distribution System (PDS)

**Version**: 1.0  
**Effective Date**: November 6, 2025  
**Status**: PERMANENT POLICY  
**Governance**: Non-negotiable system directive

## Overview

The Priority Distribution System (PDS) is CodeSentinel's governance framework for decision-making, resource allocation, and conflict resolution. It establishes a hierarchical priority structure where **higher-tier policies always supersede lower-tier policies** when conflicts arise.

**Core Principle**: When multiple policies conflict, resolve by priority tier, then by severity level within that tier.

---

## Priority Tier Structure

### ⚔️ TIER 0: CONSTITUTIONAL (Irreversible)

**Definition**: Immutable principles that define CodeSentinel's identity. Violations constitute existential threats.

**Characteristics**:

- Cannot be overridden, suspended, or negotiated
- Apply universally across all versions and branches
- Changes require extraordinary consensus (project architect approval)
- Violations result in immediate rollback + investigation

**Tier 0 Policies**:

- **T0-1: Security-First Principle**: No hardcoded credentials, ever. Environment variables or config files only.
- **T0-2: Non-Destructive Operations**: Never delete code without archiving to `quarantine_legacy_archive/`
- **T0-3: Feature Preservation**: All existing functionality must persist across versions
- **T0-4: Open Source License**: MIT license, copyright maintained, attribution required
- **T0-5: Framework Compliance Review**: Every package release (pre-release and production) must include comprehensive framework compliance review verifying SECURITY > EFFICIENCY > MINIMALISM alignment, persistent policies compliance, technical debt assessment, and long-term sustainability evaluation. Compliance review is a release-blocking requirement.

**Consequences of Violation**: Immediate branch rollback, security audit, rebuild plan

---

### 🔴 TIER 1: CRITICAL (Business Logic)

**Definition**: Core functionality, security measures, and system reliability. Violations create serious operational risks.

**Characteristics**:

- Can be modified ONLY with explicit justification and documented review
- Require comprehensive testing before implementation
- Need maintainer approval for changes
- Violations create immediate debt that must be resolved

**Tier 1 Policies**:

- **T1-1: Security Validation**: All code changes vetted for security before merge
- **T1-2: Test Coverage**: 100% of new functionality must have passing tests
- **T1-3: Cross-Platform Compatibility**: Windows/macOS/Linux parity required
- **T1-4: Dependency Management**: No unmaintained or conflicting dependencies
- **T1-5: Version Consistency**: All version numbers (code, config, packaging) must match

**Resolution Process**:

1. Document the deviation reason
2. Get explicit approval from maintainer
3. Create tracking issue for remediation
4. Schedule fix in sprint planning

---

### 🟠 TIER 2: HIGH (Quality & Architecture)

**Definition**: System design, code organization, performance standards, and integration patterns.

**Characteristics**:

- Should be followed but can be suspended for legitimate reasons
- Require documentation of exceptions
- Should be addressed within current sprint/release cycle
- Violations accumulate technical debt

**Tier 2 Policies**:

- **T2-1: Single Source of Truth**: No duplicate implementations of same functionality
- **T2-2: Performance Standards**: Response times <2s for standard operations, <5s for intensive
- **T2-3: Modular Architecture**: Clear separation of concerns (CLI, Core, Utils, GUI)
- **T2-4: Configuration Validation**: Auto-creation of missing configs with secure defaults
- **T2-5: Audit Logging**: All operations logged with timestamps, no PII in logs
- **T2-6: API Stability**: Public interfaces don't change without major version bump

**Resolution Process**:

1. Document the deviation
2. Create a tracking issue
3. Plan remediation in next sprint
4. Communicate to team

---

### 🟡 TIER 3: MEDIUM (Operational Efficiency)

**Definition**: Well-organized codebase, maintainability, documentation standards, and publishing procedures.

**Characteristics**:

- Should be maintained for long-term codebase health
- Can be deferred if critical path items demand attention
- Good candidates for "cleanup sprints"
- Violations cause friction and slow development

**Tier 3 Policies**:

- **T3-1: Root Folder Cleanliness**: No orphans, orphaned test files, dead code in root. Maximum 12 essential files.
- **T3-2: Documentation Organization**: Clear folder hierarchy, no duplicates, <5 files per logical section
- **T3-3: Publication Log Caching**: Well-organized archive of all package versions released
- **T3-4: Code Style Consistency**: Follow existing patterns (formatting, naming, structure)
- **T3-5: Redundancy Elimination**: Consolidate multiple versions of similar functionality
- **T3-6: Clean Imports**: Remove unused imports, organize by standard library → third-party → local
- **T3-7: Build Artifact Management**: Keep dist/, build/, *.egg-info/ in .gitignore, never commit
- **T3-8: Legacy Code Archiving**: Deprecated code moved to `quarantine_legacy_archive/` with versioning

**Resolution Process**:

1. Schedule in sprint planning
2. Batch similar improvements together
3. Communicate changes to team
4. Update documentation

---

### 🟢 TIER 4: LOW (Nice-to-Have)

**Definition**: Stylistic improvements, convenience features, and optimization opportunities that don't affect core functionality.

**Characteristics**:

- Nice to have but not required
- Can be addressed opportunistically
- Good for junior developers or learning exercises
- Won't impact project if not done

**Tier 4 Policies**:

- **T4-1: Code Comments**: Helpful comments for complex logic (not required for obvious code)
- **T4-2: Type Hints**: Recommended for function signatures (Python 3.13+ compatible)
- **T4-3: Performance Optimization**: Refactoring for efficiency after proving bottlenecks exist
- **T4-4: UI/UX Polish**: Visual improvements that don't change functionality
- **T4-5: Documentation Examples**: Additional examples in docstrings for public APIs
- **T4-6: Optional Dependencies**: Support for nice-to-have but not critical features

**Resolution Process**:

1. Add to backlog
2. Implement when time permits
3. Include in sprint if capacity available
4. No formal tracking required if deferred indefinitely

---

## Severity Levels (Within Each Tier)

Each tier also contains severity classifications for issue prioritization:

### Severity Ratings

- **CRITICAL**: Blocking, breaks functionality, security/stability risk
- **HIGH**: Significant impact, affects multiple users/systems
- **MEDIUM**: Noticeable issue, workaround exists
- **LOW**: Minor issue, cosmetic or rare edge case

### Conflict Resolution Matrix

When multiple policies conflict:

```
RULE: Resolve by tier first, then by severity within tier.

Example 1: T0 vs T2 policy conflict
→ ALWAYS choose T0 (Constitutional always wins)

Example 2: Two T3 policies conflict
→ Choose by severity level (CRITICAL > HIGH > MEDIUM > LOW)

Example 3: T1-MEDIUM vs T3-CRITICAL  
→ Choose T1-MEDIUM (tier always wins over severity)
```

---

## Application Examples

### Example 1: Root Folder Cleanliness (T3-1)

**Situation**: Root folder has 25 files, causing navigation friction  
**Applicable Policy**: T3-1 (Root Folder Cleanliness)  
**Action**: Consolidate to <12 essential files  
**Priority**: Schedule in sprint, batch with T3-2 improvements  
**Timeline**: Complete this sprint or next  

### Example 2: Security Vulnerability Found

**Situation**: Dependency has critical security vulnerability  
**Applicable Policy**: T1-4 (Dependency Management)  
**Action**: Immediate hotfix, all systems prioritized  
**Timeline**: Within 24 hours  
**Override**: All other work stops until resolved

### Example 3: Code Formatting Inconsistency

**Situation**: Some files use 2-space indent, others use 4-space  
**Applicable Policy**: T3-4 (Code Style Consistency)  
**Action**: Schedule as part of cleanup sprint  
**Priority**: Can be deferred if critical features pending  
**Timeline**: Next available sprint with capacity

### Example 4: Missing Comments in Complex Algorithm

**Situation**: New algorithm lacks explanatory comments  
**Applicable Policy**: T4-2 (Code Comments)  
**Action**: Consider adding, not required  
**Priority**: Optional, good for senior code review  
**Timeline**: Whenever (no deadline)

---

## Tier Assignments for Current Codebase

### T0: Constitutional

- Security-first principle ✅
- Non-destructive operations ✅
- Feature preservation ✅
- MIT license ✅

### T1: Critical

- Security validation ✅
- Test coverage (22/22 passing) ✅
- Cross-platform compatibility ✅
- Dependency management ✅
- Version consistency (1.0.3.beta) ✅

### T2: High

- Single source of truth (consolidating now) 🟨
- Performance standards (1.2s-1.4s ✅)
- Modular architecture ✅
- Configuration validation ✅
- Audit logging ✅
- API stability ✅

### T3: Medium

- Root folder cleanliness (25 files → 6 target) 🔧 **CURRENT PRIORITY**
- Documentation organization (21 files → organized) 🔧 **CURRENT PRIORITY**
- Publication log caching ✅
- Code style consistency ✅
- Redundancy elimination 🟨
- Clean imports ✅
- Build artifact management ✅
- Legacy code archiving ✅

### T4: Low

- Code comments (partial)
- Type hints (partial)
- Performance optimization (not needed now)
- UI/UX polish
- Documentation examples
- Optional dependencies

---

## Policy Modification Process

### Adding/Changing a Policy

1. **Identify Tier**: Which tier does this policy belong in?
2. **Document Rationale**: Why is this policy needed?
3. **Check Conflicts**: Could this conflict with existing policies?
4. **Get Approval**:
   - T0: Architect approval required
   - T1: Maintainer approval required
   - T2/T3/T4: Team consensus sufficient
5. **Update This Document**: Add new policy with unique ID
6. **Communicate**: Announce to team, update wiki/docs
7. **Implement**: Begin enforcement on next sprint

### Deprecating a Policy

1. **Document Why**: Explain why policy is no longer needed
2. **Get Approval**: Same approval level as original policy
3. **Transition Period**: Give team notice before enforcement ends
4. **Archive**: Move to `DEPRECATED_POLICIES.md`
5. **Implement**: New policy replaces old one

---

## Monitoring & Enforcement

### Health Checks

- **Weekly**: Review T0 & T1 violations (must be zero)
- **Sprint Review**: Check T2 & T3 debt accumulation
- **Quarterly**: Full policy audit and assessment

### Reporting

```
Priority Distribution Compliance Report
├── T0 Violations: [count] (must be 0)
├── T1 Violations: [count] (max 2 acceptable)
├── T2 Deviations: [count] (must have remediation plan)
├── T3 Backlog: [count] (schedule in upcoming sprint)
└── T4 Wishlist: [count] (no deadline)
```

### Escalation Path

1. Developer identifies issue → Creates tracking issue
2. Issue tagged with tier level
3. If T0/T1: Escalate immediately to maintainer
4. If T2: Plan for current sprint
5. If T3: Add to sprint backlog
6. If T4: Add to wishlist

---

## Current Status: November 6, 2025

**T0 Violations**: ✅ 0  
**T1 Violations**: ✅ 0  
**T2 Deviations**: 🟨 2 (Single source of truth, Redundancy elimination)  
**T3 Violations**: 🔴 2 (Root cleanliness, Documentation organization)  
**T4 Wishlist**: 🟢 3 (Type hints, Performance optimization, Code comments)

**Current Priority**:

1. **URGENT**: Fix T3-1 (Root Folder Cleanliness) - consolidate to <12 files
2. **URGENT**: Fix T3-2 (Documentation Organization) - organize docs/ folder
3. **IMPORTANT**: Address T2-1 (Single Source of Truth) - eliminate redundancy

---

## Implementation Notes

- **This system is permanent** and persists across all future versions
- **Policies are numbered** for unique reference (T0-1, T1-2, T3-5, etc.)
- **Conflicts always resolve by tier** - never override by severity alone
- **Deviation documentation required** - make explicit when deviating
- **Regular review** - quarterly assessment of policy effectiveness

---

**Document Custodian**: CodeSentinel Project Team  
**Last Updated**: November 6, 2025  
**Next Review**: May 6, 2026  
**Approval Status**: ACTIVE - Binding on all contributors
