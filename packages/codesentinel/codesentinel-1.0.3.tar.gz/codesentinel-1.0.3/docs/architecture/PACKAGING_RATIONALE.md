# Packaging Configuration Rationale

## Why Both setup.py AND pyproject.toml?

**Decision:** Keep both packaging configurations for maximum compatibility.

### Modern Standard (pyproject.toml)

- PEP 517/518 compliant
- Modern Python packaging standard
- Preferred by pip >= 21.3
- Declarative configuration

### Legacy Support (setup.py)

- Ensures compatibility with older pip versions (<21.3)
- Required by some CI/CD systems
- Enables editable installs on older systems
- Fallback for build systems that don't support PEP 517

### Console Script Generation

Both configurations define the same console scripts:

- `codesentinel` - Main CLI entry point
- `codesentinel-setup` - Interactive configuration wizard

### Build Process

```bash
# Modern build (uses pyproject.toml)
python -m build

# Legacy build (uses setup.py)
python setup.py sdist bdist_wheel

# Both produce compatible distributions
```

### Maintenance Strategy

1. **Primary**: Edit `pyproject.toml` first
2. **Sync**: Update `setup.py` to match
3. **Test**: Verify both produce working installations
4. **Version**: Keep version numbers synchronized

### When to Remove setup.py?

Remove when ALL of these conditions are met:

- [ ] Python 3.8+ is minimum requirement
- [ ] All CI/CD systems support PEP 517
- [ ] No users report compatibility issues for 2+ releases
- [ ] pip >= 21.3 is ubiquitous (Python 3.10+ era)

**Current Status:** Both maintained for compatibility (v1.0.3)

**References:**

- PEP 517: <https://peps.python.org/pep-0517/>
- PEP 518: <https://peps.python.org/pep-0518/>
- Python Packaging User Guide: <https://packaging.python.org/>
