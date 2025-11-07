# CodeSentinel Publication Logs

Comprehensive cache of all CodeSentinel package publications across versions.

## Overview

This directory maintains a well-organized archive of publication events, validation reports, and deployment logs. Publication logging is a **Tier 3 Priority** in CodeSentinel's distribution policy.

### Tier 3 Priority: Publication Log Caching

**Policy Definition**: A well-organized cache of publication logs is essential infrastructure for:

1. **Audit Trail**: Complete historical record of all package versions released to PyPI
2. **Validation History**: Test results, validation reports, and pre-publication checks
3. **Deployment Tracking**: Production upload confirmations and repository references
4. **Recovery Reference**: Quick access to publication procedures and token management for future releases
5. **Policy Enforcement**: Evidence of adherence to security and release procedures

### Directory Structure

Each version gets its own versioned subdirectory containing all related publication artifacts:

```
publication_logs/
├── README.md (this file)
├── v1.0.0/
│   ├── v1.0.0_publication_log.md
│   ├── TEST_PYPI_VALIDATION_PASSED.md
│   └── PRODUCTION_PYPI_PUBLISHED.md
├── v1.0.1/
│   ├── v1.0.1_publication_log.md
│   ├── TEST_PYPI_VALIDATION_PASSED.md
│   └── PRODUCTION_PYPI_PUBLISHED.md
└── v1.0.3_beta/
    ├── v1.0.3_beta_publication_log.md
    ├── TEST_PYPI_VALIDATION_PASSED.md
    └── PRODUCTION_PYPI_PUBLISHED.md
```

### Document Types

#### `v[VERSION]_publication_log.md`

- **Purpose**: Step-by-step publication workflow and results
- **Contents**: Commands executed, upload confirmations, PyPI URLs
- **Generated**: During publication process
- **Audience**: Developers, maintainers, auditors

#### `TEST_PYPI_VALIDATION_PASSED.md`

- **Purpose**: Test PyPI validation results
- **Contents**: Distribution verification, installation tests, CLI functionality verification
- **Generated**: Before production upload
- **Audience**: QA, release managers, auditors
- **Policy**: Must pass before production upload allowed

#### `PRODUCTION_PYPI_PUBLISHED.md`

- **Purpose**: Production PyPI publication confirmation
- **Contents**: Upload success confirmation, PyPI URLs, installation verification
- **Generated**: After successful production upload
- **Audience**: Release managers, auditors, users

### Publication Workflow

```
[Package Ready]
    ↓
[Test PyPI Upload] → TEST_PYPI_VALIDATION_PASSED.md
    ↓
[Validation Tests] → Test results logged
    ↓
[Production PyPI Upload] → PRODUCTION_PYPI_PUBLISHED.md
    ↓
[v[VERSION]_publication_log.md created]
    ↓
[Archive in versioned directory]
```

### Version History

| Version | Date | Status | Test PyPI | Production PyPI | Notes |
|---------|------|--------|-----------|-----------------|-------|
| 1.0.3b0 (beta) | 2025-11-06 | ✅ Published | ✅ Passed | ✅ Live | File integrity system, GUI installers |
| [Future] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

### Maintenance Policy

1. **Retention**: All publication logs retained indefinitely for audit trail
2. **Organization**: Each version gets its own subdirectory
3. **Naming**: Consistent naming convention: `v[VERSION]_*.md`
4. **Archiving**: Completed versions remain in subdirectories as reference
5. **Automation**: `tools/codesentinel/publisher.py` generates logs automatically

### Security Notes

- ⚠️ **Never commit PyPI tokens** to this directory
- ⚠️ **Tokens passed via environment variables** during publication
- ✅ **URLs and validation results** safe to log and version control
- ✅ **Timestamps and error messages** helpful for debugging

### Related Policies

- **Tier 1**: Security-first principle (no hardcoded credentials)
- **Tier 2**: Distribution validation (all tests passing)
- **Tier 3**: Publication log caching (this policy) ← You are here
- **Tier 4**: Cross-platform verification
- **Tier 5**: Post-publication documentation

### Accessing Publication Logs

```bash
# View all publications
ls docs/publication_logs/

# View specific version
cat docs/publication_logs/v1.0.3_beta/v1.0.3_beta_publication_log.md

# Check test validation
cat docs/publication_logs/v1.0.3_beta/TEST_PYPI_VALIDATION_PASSED.md

# Check production status
cat docs/publication_logs/v1.0.3_beta/PRODUCTION_PYPI_PUBLISHED.md
```

### Contributing

When publishing a new version:

1. Create new version directory: `v[VERSION]/`
2. Place publication workflow in: `v[VERSION]/v[VERSION]_publication_log.md`
3. Place test validation in: `v[VERSION]/TEST_PYPI_VALIDATION_PASSED.md`
4. Place production confirmation in: `v[VERSION]/PRODUCTION_PYPI_PUBLISHED.md`
5. Update this README.md with version history entry
6. Commit all logs to git
7. Create GitHub release with link to publication logs

---

**Policy Version**: 1.0  
**Last Updated**: 2025-11-06  
**Maintained By**: CodeSentinel Team  
**Next Review**: 2026-05-06
