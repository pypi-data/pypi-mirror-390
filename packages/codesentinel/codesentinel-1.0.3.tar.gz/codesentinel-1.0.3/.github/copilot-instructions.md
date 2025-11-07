# CodeSentinel AI Agent Instructions

CodeSentinel is a security-first automated maintenance and monitoring system with the core principle: **SECURITY > EFFICIENCY > MINIMALISM**.

## Architecture Overview

The codebase follows a dual-architecture pattern:

- **`codesentinel/`** - Core Python package with CLI interface (`codesentinel`, `codesentinel-setup`)
- **`tools/codesentinel/`** - Comprehensive maintenance automation scripts
- **`tools/config/`** - JSON configuration files for alerts, scheduling, and policies
- **`tests/`** - Test suite using pytest with unittest fallback

## Key Commands

### Development Audit
```bash
# Run interactive audit
codesentinel !!!!

# Get agent-friendly context for remediation
codesentinel !!!! --agent
```

### Maintenance Operations
```bash
# Daily maintenance workflow
python tools/codesentinel/scheduler.py --schedule daily

# Weekly maintenance (security, dependencies, performance)
python tools/codesentinel/scheduler.py --schedule weekly
```

## Core Principles

### SECURITY
- No hardcoded credentials - Environment variables or config files only
- Audit logging - All operations logged with timestamps
- Configuration validation - Auto-creation of missing configs with secure defaults
- Dependency scanning - Automated vulnerability detection

### EFFICIENCY
- Avoid redundant code and duplicate implementations
- Consolidate multiple versions of similar functionality
- Clean up orphaned test files and unused scripts
- Optimize import structures and module organization

### MINIMALISM
- Remove unnecessary dependencies
- Archive deprecated code to quarantine_legacy_archive/
- Maintain single source of truth for each feature
- Keep codebase focused and maintainable

## Persistent Policies

When working with this codebase:

1. **NON-DESTRUCTIVE**: Never delete code without archiving first
2. **FEATURE PRESERVATION**: All existing functionality must be maintained
3. **STYLE PRESERVATION**: Respect existing code style and patterns
4. **SECURITY FIRST**: Security concerns always take priority
5. **PERMANENT POLICY (T0-5)**: Framework compliance review required with every package release
   - Every pre-release and production release must include comprehensive framework compliance review
   - Review must verify SECURITY > EFFICIENCY > MINIMALISM alignment
   - Review must validate all persistent policies (non-destructive, feature preservation, security-first)
   - Compliance review is a release-blocking requirement, cannot be deferred
   - Classified as Constitutional (Irreversible) tier in governance system
   - Review must assess technical debt impact and long-term sustainability
   - Report must be part of release package and documentation
   - Failure to include compliance review blocks release approval

## Agent-Driven Remediation

When `codesentinel !!!! --agent` is run, you will receive comprehensive audit context with:

- Detected issues (security, efficiency, minimalism)
- Remediation hints with priority levels
- Safe-to-automate vs. requires-review flags
- Step-by-step suggested actions

Your role is to:

1. **ANALYZE**: Review each issue with full context
2. **PRIORITIZE**: Focus on critical/high priority items first  
3. **DECIDE**: Determine safe vs. requires-review actions
4. **PLAN**: Build step-by-step remediation plan
5. **EXECUTE**: Only perform safe, non-destructive operations
6. **REPORT**: Document all actions and decisions

## Safe Actions (can automate)

- Moving test files to proper directories
- Adding entries to .gitignore
- Removing __pycache__ directories
- Archiving confirmed-redundant files to quarantine_legacy_archive/

## Requires Review (agent decision needed)

- Deleting or archiving potentially-used code
- Consolidating multiple implementations
- Removing packaging configurations
- Modifying imports or entry points

## Forbidden Actions

- Deleting files without archiving
- Forcing code style changes
- Removing features without verification
- Modifying core functionality without explicit approval
- Excessive use of emojis in documentation or code comments

## Integration Points

### GitHub Integration
- Repository-aware configuration detection
- Copilot instructions generation (this file)
- PR review automation capabilities

### Multi-Platform Support  
- Python 3.13/3.14 requirement with backward compatibility
- Cross-platform paths using `pathlib.Path` consistently
- PowerShell/Python dual execution support for Windows/Unix

## When Modifying This Codebase

1. **Understand the dual architecture** - Core package vs. tools scripts serve different purposes
2. **Maintain execution order** - Change detection dependency is critical
3. **Preserve configuration structure** - JSON configs have specific schemas
4. **Test both execution paths** - pytest and unittest must both work
5. **Follow security-first principle** - Never compromise security for convenience
6. **Update timeout values carefully** - Task timeouts affect workflow reliability
