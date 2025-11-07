# CodeSentinel v1.0.3.beta1 - Pre-Release for UNC Testing# CodeSentinel v1.0.3.beta1 - Pre-Release for UNC Testing

**Version**: 1.0.3.beta1  **Version**: 1.0.3.beta1  

**Release Date**: November 6, 2025  **Release Date**: November 6, 2025  

**Status**: Pre-release (Local/UNC testing only)  **Status**: Pre-release (Local/UNC testing only)  

**Git Tag**: v1.0.3.beta1-local**Git Tag**: v1.0.3.beta1-local

------

## Overview## Overview

This pre-release includes:This pre-release includes:

- ✅ Infrastructure hardening (documentation reorganization)- ✅ Infrastructure hardening (documentation reorganization)

- ✅ Priority Distribution System (governance framework)- ✅ Priority Distribution System (governance framework)

- ✅ Polymath branding (subtle, professional attribution)- ✅ Polymath branding (subtle, professional attribution)

- ✅ Complete hardened codebase ready for production testing- ✅ Complete hardened codebase ready for production testing

**Not for PyPI**: This is a local pre-release for testing. It's NOT published to PyPI.**Not for PyPI**: This is a local pre-release for testing. It's NOT published to PyPI.

------

## What's Included## What's Included

### Core Package### Core Package

- `codesentinel-1.0.3b1-py3-none-any.whl` (76 KB - binary distribution)- `codesentinel-1.0.3b1-py3-none-any.whl` (76 KB - binary distribution)

- `codesentinel-1.0.3b1.tar.gz` (130 KB - source distribution)- `codesentinel-1.0.3b1.tar.gz` (130 KB - source distribution)

### New in This Pre-Release### New in This Pre-Release

1. **Priority Distribution System**: docs/architecture/PRIORITY_DISTRIBUTION_SYSTEM.md1. **Priority Distribution System**: docs/architecture/PRIORITY_DISTRIBUTION_SYSTEM.md

   - 5-tier governance framework (T0-T4)   - 5-tier governance framework (T0-T4)

   - 30 unique policies covering all aspects   - 30 unique policies covering all aspects

   - Permanent decision-making framework   - Permanent decision-making framework

2. **Hardened Documentation**2. **Hardened Documentation**

   - 6 organized doc folders (installation, guides, architecture, legacy, publication_logs, audit)   - 6 organized doc folders (installation, guides, architecture, legacy, publication_logs, audit)

   - Navigation hub in docs/README.md   - Navigation hub in docs/README.md

   - Clean root folder (5 essential files only)   - Clean root folder (5 essential files only)

3. **Branding**: "A Polymath Project" by joediggidyyy3. **Branding**: "A Polymath Project" by joediggidyyy

   - Subtle, professional attribution   - Subtle, professional attribution

   - Visible in README.md, package metadata, docstrings   - Visible in README.md, package metadata, docstrings

------

## Installation for UNC Testing## Installation for UNC Testing

### Option 1: Install from Wheel (Recommended for Testing)### Option 1: Install from Wheel (Recommended for Testing)

```bash```bash

# Navigate to dist/ folder# Navigate to dist/ folder

cd dist/cd dist/

# Install the wheel# Install the wheel

pip install codesentinel-1.0.3b1-py3-none-any.whlpip install codesentinel-1.0.3b1-py3-none-any.whl

# Verify installation# Verify installation

codesentinel statuscodesentinel status

``````



### Option 2: Install from Source### Option 2: Install from Source



```bash```bash

# Navigate to dist/ folder# Navigate to dist/ folder

cd dist/cd dist/



# Extract and install# Extract and install

tar -xzf codesentinel-1.0.3b1.tar.gztar -xzf codesentinel-1.0.3b1.tar.gz

cd codesentinel-1.0.3b1/cd codesentinel-1.0.3b1/

pip install .pip install .



# Verify installation# Verify installation

codesentinel statuscodesentinel status

``````

### Option 3: Install Directly from Development### Option 3: Install Directly from Development

```bash```bash

# From project root# From project root

pip install -e .pip install -e .

# Verify installation# Verify installation

codesentinel statuscodesentinel status

``````



------



## Testing Checklist## Testing Checklist



### Installation### Installation



- [ ] Wheel installation successful- [ ] Wheel installation successful

- [ ] No dependency conflicts- [ ] No dependency conflicts

- [ ] `codesentinel status` returns properly- [ ] `codesentinel status` returns properly

- [ ] Version shows as 1.0.3.beta1- [ ] Version shows as 1.0.3.beta1



### CLI Functionality### CLI Functionality



- [ ] `codesentinel --help` displays all commands- [ ] `codesentinel --help` displays all commands

- [ ] `codesentinel status` shows system status- [ ] `codesentinel status` shows system status

- [ ] `codesentinel integrity --help` shows file integrity options- [ ] `codesentinel integrity --help` shows file integrity options

- [ ] `codesentinel maintenance --help` shows scheduler options- [ ] `codesentinel maintenance --help` shows scheduler options



### File Integrity (New Feature)### File Integrity (New Feature)



- [ ] `codesentinel integrity generate` creates baseline (< 2 seconds)- [ ] `codesentinel integrity generate` creates baseline (< 2 seconds)

- [ ] `.codesentinel_integrity.json` file created- [ ] `.codesentinel_integrity.json` file created

- [ ] `codesentinel integrity verify` validates files (< 2 seconds)- [ ] `codesentinel integrity verify` validates files (< 2 seconds)

- [ ] `codesentinel integrity whitelist` works- [ ] `codesentinel integrity whitelist` works

- [ ] `codesentinel integrity critical` shows critical files- [ ] `codesentinel integrity critical` shows critical files



### GUI Installation### GUI Installation



- [ ] `codesentinel setup` launches GUI wizard- [ ] `codesentinel setup` launches GUI wizard

- [ ] Wizard completes successfully- [ ] Wizard completes successfully

- [ ] Configuration saved properly- [ ] Configuration saved properly

- [ ] Can re-open setup without conflicts- [ ] Can re-open setup without conflicts



### Documentation### Documentation



- [ ] `docs/README.md` provides good navigation- [ ] `docs/README.md` provides good navigation

- [ ] docs/ structure is organized and clear- [ ] docs/ structure is organized and clear

- [ ] All links work (no 404s)- [ ] All links work (no 404s)

- [ ] Governance framework accessible- [ ] Governance framework accessible



### Performance### Performance



- [ ] Baseline generation: < 2 seconds (target: 1.2s)- [ ] Baseline generation: < 2 seconds (target: 1.2s)

- [ ] Integrity verification: < 2 seconds (target: 1.4s)- [ ] Integrity verification: < 2 seconds (target: 1.4s)

- [ ] GUI wizard launch: < 1 second- [ ] GUI wizard launch: < 1 second



------



## Distribution Files## Distribution Files



Located in `dist/` folder:Located in `dist/` folder:



```bash```

dist/dist/

├── codesentinel-1.0.3b1-py3-none-any.whl    (76 KB - binary)├── codesentinel-1.0.3b1-py3-none-any.whl    (76 KB - binary)

├── codesentinel-1.0.3b1.tar.gz              (130 KB - source)├── codesentinel-1.0.3b1.tar.gz              (130 KB - source)

├── codesentinel-1.0.1-py3-none-any.whl      (previous version)├── codesentinel-1.0.1-py3-none-any.whl      (previous version)

├── codesentinel-1.0.1.tar.gz                (previous version)├── codesentinel-1.0.1.tar.gz                (previous version)

├── codesentinel-1.0.3b0-py3-none-any.whl    (previous version)├── codesentinel-1.0.3b0-py3-none-any.whl    (previous version)

└── codesentinel-1.0.3b0.tar.gz              (previous version)└── codesentinel-1.0.3b0.tar.gz              (previous version)

``````

**For UNC Testing**: Use the `codesentinel-1.0.3b1-*` files**For UNC Testing**: Use the `codesentinel-1.0.3b1-*` files

------

## Version Information## Version Information

### Changes from v1.0.3.beta (v1.0.3b0)### Changes from v1.0.3.beta (v1.0.3b0)

**Infrastructure**:**Infrastructure**:

- Added Priority Distribution System- Added Priority Distribution System

- Reorganized documentation (6 folders, clean root)- Reorganized documentation (6 folders, clean root)

- Added Polymath branding- Added Polymath branding

**Features**: No new features (pre-release for testing infrastructure only)**Features**: No new features (pre-release for testing infrastructure only)

**Fixes**: None (infrastructure-focused)**Fixes**: None (infrastructure-focused)

**Breaking Changes**: None**Breaking Changes**: None

------

## Git Information## Git Information

**Commit**: 22e3a18  **Commit**: 22e3a18  

**Branch**: main  **Branch**: main  

**Tag**: v1.0.3.beta1-local**Tag**: v1.0.3.beta1-local

### View Release Info### View Release Info

```bash```bash

git show v1.0.3.beta1-localgit show v1.0.3.beta1-local

git log --oneline main -n 5git log --oneline main -n 5

``````



------



## Deployment to UNC## Deployment to UNC



### Step 1: Copy Distribution### Step 1: Copy Distribution



```bash```bash

# Copy wheel file to UNC repository# Copy wheel file to UNC repository

cp dist/codesentinel-1.0.3b1-py3-none-any.whl \\UNC\path\to\repo\cp dist/codesentinel-1.0.3b1-py3-none-any.whl \\UNC\path\to\repo\

``````

### Step 2: Install on UNC### Step 2: Install on UNC

```bash```bash

# On UNC system# On UNC system

pip install \\path\to\codesentinel-1.0.3b1-py3-none-any.whlpip install \\path\to\codesentinel-1.0.3b1-py3-none-any.whl

``````



### Step 3: Test### Step 3: Test



Run the testing checklist above on UNC systemRun the testing checklist above on UNC system



### Step 4: Report Results### Step 4: Report Results



Document any issues or successes and report backDocument any issues or successes and report back



------



## Troubleshooting## Troubleshooting



### Installation Issues### Installation Issues



```bash```bash

# Clear pip cache if having issues# Clear pip cache if having issues

pip cache purgepip cache purge



# Try installing with --no-cache-dir# Try installing with --no-cache-dir

pip install --no-cache-dir codesentinel-1.0.3b1-py3-none-any.whlpip install --no-cache-dir codesentinel-1.0.3b1-py3-none-any.whl

``````

### Version Conflicts### Version Conflicts

```bash```bash

# Check installed version# Check installed version

python -c "import codesentinel; print(codesentinel.**version**)"python -c "import codesentinel; print(codesentinel.**version**)"

# Uninstall old version if needed# Uninstall old version if needed

pip uninstall codesentinel -ypip uninstall codesentinel -y

pip install codesentinel-1.0.3b1-py3-none-any.whlpip install codesentinel-1.0.3b1-py3-none-any.whl

``````



### Permission Issues on UNC### Permission Issues on UNC



- Request write permissions if needed- Request write permissions if needed

- Use `pip install --user` if system-wide install fails- Use `pip install --user` if system-wide install fails



------



## Support## Support



**Issues or Questions**?**Issues or Questions**?



1. Check docs/README.md for documentation navigation1. Check docs/README.md for documentation navigation

2. Review docs/architecture/PRIORITY_DISTRIBUTION_SYSTEM.md for governance2. Review docs/architecture/PRIORITY_DISTRIBUTION_SYSTEM.md for governance

3. See docs/guides/ for detailed how-to guides3. See docs/guides/ for detailed how-to guides

4. Contact: joediggidyyy4. Contact: joediggidyyy



------



## Next Steps## Next Steps



After successful UNC testing:After successful UNC testing:



1. Feedback on infrastructure changes1. Feedback on infrastructure changes

2. Final validation before v1.0.3.beta production release2. Final validation before v1.0.3.beta production release

3. Potential adjustments based on test results3. Potential adjustments based on test results

4. Publication to PyPI4. Publication to PyPI



------



**Status**: ✅ Ready for UNC deployment  **Status**: ✅ Ready for UNC deployment  

**Pre-Release**: v1.0.3.beta1  **Pre-Release**: v1.0.3.beta1  

**Built**: November 6, 2025  **Built**: November 6, 2025  

**Tested**: Infrastructure validation complete**Tested**: Infrastructure validation complete

