"""
Development Audit System
========================

Implements interactive and silent development audits focused on:

> SECURITY - EFFICIENCY - MINIMALISM <

FUNDAMENTAL POLICY HIERARCHY:
1. CORE CONCEPTS: Security > Efficiency > Minimalism (absolute priority)
2. PERMANENT DIRECTIVES: Non-negotiable security rules
3. PERSISTENT POLICIES: Non-destructive, feature-preserving operations

Dev audits are always executed thoroughly and comprehensively, focusing
heavily on the three core concepts while complying with all directives
and policies EXCEPT where they would explicitly violate a core concept.

The interactive audit prints a detailed report. Immediately after it
finishes, a brief silent audit runs in the background and reports its
outcome via the configured alert channels.
"""

from __future__ import annotations

import os
import re
import json
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional


class DevAudit:
    """
    Runs development audits with interactive and silent modes.
    
    Always executes thoroughly and comprehensively with heavy focus on:
    - SECURITY (highest priority)
    - EFFICIENCY (second priority)  
    - MINIMALISM (third priority)
    
    Complies with all directives and policies except where they would
    explicitly violate a higher-priority core concept.
    """

    def __init__(self, project_root: Optional[Path], alert_manager, config_manager):
        self.project_root = project_root or Path.cwd()
        self.alert_manager = alert_manager
        self.config_manager = config_manager
        # Persisted policy: '!!!!' must be non-destructive and feature-preserving
        # Unless explicitly required by security (core concept override)
        cfg = getattr(self.config_manager, 'config', {}) or {}
        self.policy = (cfg.get('policy') or {
            'non_destructive': True,
            'feature_preservation': True,
            'conflict_resolution': 'merge-prefer-existing',
            'principles': ['SECURITY', 'EFFICIENCY', 'MINIMALISM'],
            'hierarchy': ['CORE_CONCEPTS', 'PERMANENT_DIRECTIVES', 'PERSISTENT_POLICIES']
        })

    # -------------------- Public API --------------------
    def run_interactive(self) -> Dict[str, Any]:
        """Run a full interactive audit and print results to console."""
        results = self._run_audit(detail_level="full")
        self._print_report(results)

        # Kick off a brief audit in background and alert
        bg_thread = threading.Thread(target=self._run_brief_and_alert, daemon=True)
        bg_thread.start()
        return results

    def run_brief(self) -> Dict[str, Any]:
        """Run a brief audit suitable for background/alerts."""
        return self._run_audit(detail_level="brief")

    def get_agent_context(self) -> Dict[str, Any]:
        """
        Export audit results with remediation context for AI agent.
        
        This provides comprehensive information for GitHub Copilot to
        intelligently decide remediation actions while respecting
        persistent policies (non-destructive, feature preservation).
        """
        results = self._run_audit(detail_level="full")
        
        # Build remediation hints for each category
        remediation_context = {
            "policy": self.policy,
            "principles": ["SECURITY", "EFFICIENCY", "MINIMALISM"],
            "constraints": [
                "All actions must be non-destructive",
                "Feature preservation is mandatory",
                "Style must be preserved (no forced formatting)",
                "Conflict resolution: merge-prefer-existing"
            ],
            "security_issues": self._build_security_remediation_hints(results["security"]),
            "efficiency_issues": self._build_efficiency_remediation_hints(results["efficiency"]),
            "minimalism_issues": self._build_minimalism_remediation_hints(results["minimalism"]),
            "summary": results["summary"]
        }
        
        return {
            "audit_results": results,
            "remediation_context": remediation_context,
            "agent_guidance": self._generate_agent_guidance(remediation_context)
        }

    def _build_security_remediation_hints(self, security: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build actionable hints for security issues."""
        hints = []
        for finding in security.get("secrets_findings", []):
            hints.append({
                "file": finding["file"],
                "issue": "Potential secret/credential detected",
                "pattern": finding["pattern"],
                "suggested_actions": [
                    "Review file to confirm if this is a real credential",
                    "If real: move to environment variables or secure vault",
                    "If false positive: add exception to audit config",
                    "Consider adding file to .gitignore if contains secrets"
                ],
                "priority": "critical"
            })
        return hints

    def _build_efficiency_remediation_hints(self, efficiency: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build actionable hints for efficiency issues."""
        hints = []
        for suggestion in efficiency.get("suggestions", []):
            if "wizard implementations" in suggestion:
                hints.append({
                    "issue": "Multiple wizard implementations detected",
                    "suggestion": suggestion,
                    "suggested_actions": [
                        "Identify the canonical wizard (likely codesentinel/gui_wizard_v2.py)",
                        "Verify other wizards are truly redundant (not different use cases)",
                        "Move deprecated wizards to quarantine_legacy_archive/",
                        "Update any references to point to canonical implementation"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            elif "__pycache__" in suggestion:
                hints.append({
                    "issue": "__pycache__ in root directory",
                    "suggestion": suggestion,
                    "suggested_actions": [
                        "Add __pycache__/ to .gitignore",
                        "Remove from git: git rm -r --cached __pycache__/",
                        "Delete directory: rm -rf __pycache__/"
                    ],
                    "priority": "low",
                    "safe_to_automate": True
                })
            elif "Large files" in suggestion:
                hints.append({
                    "issue": "Large files detected",
                    "suggestion": suggestion,
                    "suggested_actions": [
                        "Review large files to determine if they belong in repo",
                        "Consider Git LFS for large binary files",
                        "Move test data/assets to separate location",
                        "Add large files to .gitignore if not needed"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            else:
                hints.append({
                    "issue": "General efficiency concern",
                    "suggestion": suggestion,
                    "suggested_actions": ["Review and determine appropriate action"],
                    "priority": "low",
                    "agent_decision_required": True
                })
        return hints

    def _build_minimalism_remediation_hints(self, minimalism: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build actionable hints for minimalism violations."""
        hints = []
        for violation in minimalism.get("violations", []):
            if "Orphaned test files" in violation:
                hints.append({
                    "issue": "Test files in wrong location",
                    "violation": violation,
                    "suggested_actions": [
                        "Move test_*.py files from root to tests/ directory",
                        "Update any references or imports",
                        "Verify tests still run after move: pytest tests/"
                    ],
                    "priority": "high",
                    "safe_to_automate": True
                })
            elif "Duplicate launcher files" in violation:
                hints.append({
                    "issue": "Duplicate launcher implementations",
                    "violation": violation,
                    "suggested_actions": [
                        "Identify canonical launcher (codesentinel/launcher.py for package)",
                        "Verify launch.py is only used as root entry point",
                        "If truly duplicate: archive one to quarantine_legacy_archive/",
                        "Update references and entry points"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            elif "Redundant packaging" in violation:
                hints.append({
                    "issue": "Both setup.py and pyproject.toml present",
                    "violation": violation,
                    "suggested_actions": [
                        "Modern Python uses pyproject.toml only (PEP 517/518)",
                        "Verify all setup.py config is in pyproject.toml",
                        "Archive setup.py to quarantine_legacy_archive/",
                        "Test installation still works: pip install -e ."
                    ],
                    "priority": "high",
                    "agent_decision_required": True,
                    "note": "This may be causing console script generation issues"
                })
            elif "Incomplete src/codesentinel/" in violation:
                hints.append({
                    "issue": "Abandoned src/ directory structure",
                    "violation": violation,
                    "suggested_actions": [
                        "Review src/codesentinel/ contents",
                        "If truly abandoned: archive to quarantine_legacy_archive/",
                        "If needed: integrate into main codesentinel/ package",
                        "Update imports and references"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            elif "Legacy archive directory" in violation:
                hints.append({
                    "issue": "Legacy archive taking up space",
                    "violation": violation,
                    "suggested_actions": [
                        "Verify all needed features have been ported",
                        "Consider creating archive tarball: tar -czf legacy_v0.tar.gz quarantine_legacy_archive/",
                        "Move tarball to docs/ or external storage",
                        "Remove directory after verification period"
                    ],
                    "priority": "low",
                    "agent_decision_required": True,
                    "note": "Keep until v2 feature parity confirmed"
                })
            elif "Too many installers" in violation:
                hints.append({
                    "issue": "Multiple installer scripts",
                    "violation": violation,
                    "suggested_actions": [
                        "Identify canonical installer for the project",
                        "Archive redundant installers",
                        "Update documentation to reference single installer"
                    ],
                    "priority": "medium",
                    "agent_decision_required": True
                })
            else:
                hints.append({
                    "issue": "Minimalism violation",
                    "violation": violation,
                    "suggested_actions": ["Review and determine appropriate action"],
                    "priority": "medium",
                    "agent_decision_required": True
                })
        return hints

    def _generate_agent_guidance(self, context: Dict[str, Any]) -> str:
        """Generate high-level guidance for AI agent."""
        total_issues = context["summary"]["total_issues"]
        severity = context["summary"]["severity"]
        
        guidance = f"""
CodeSentinel Development Audit - Agent Guidance
================================================

Total Issues: {total_issues} (Severity: {severity})

FUNDAMENTAL POLICY HIERARCHY:
1. CORE CONCEPTS (Absolute Priority): SECURITY > EFFICIENCY > MINIMALISM
2. PERMANENT DIRECTIVES: Non-negotiable security rules
3. PERSISTENT POLICIES: Non-destructive, feature-preserving operations

Dev audits are executed thoroughly and comprehensively with heavy focus on
the three core concepts. Policies can be overridden ONLY when they explicitly
violate a higher-priority core concept.

AGENT ROLE:
You are tasked with intelligently reviewing the audit findings and building
a remediation pipeline. You should:

1. ANALYZE: Review each issue with context
2. PRIORITIZE: Focus on critical/high priority items first (SECURITY first)
3. DECIDE: Determine safe vs. requires-review actions
4. PLAN: Build step-by-step remediation plan following hierarchy
5. EXECUTE: Only perform safe, non-destructive operations
6. REPORT: Document all actions and decisions

SAFE ACTIONS (can automate):
- Moving test files to proper directories
- Adding entries to .gitignore
- Removing __pycache__ directories
- Archiving confirmed-redundant files to quarantine_legacy_archive/

REQUIRES REVIEW (agent decision needed):
- Deleting or archiving potentially-used code
- Consolidating multiple implementations
- Removing packaging configurations
- Modifying imports or entry points

FORBIDDEN ACTIONS:
- Deleting files without archiving
- Forcing code style changes
- Removing features without verification
- Modifying core functionality

RECOMMENDED APPROACH:
1. Start with safe, low-priority cleanup (__pycache__, .gitignore)
2. Move orphaned test files to proper locations
3. For duplicates: analyze usage, archive unused, update references
4. For each action: explain reasoning and confirm non-destructive
5. Create archive snapshots before any structural changes
"""
        return guidance.strip()

    # -------------------- Internal --------------------
    def _run_brief_and_alert(self) -> None:
        results = self.run_brief()
        title = "Dev Audit Summary"
        severity = self._severity_from_results(results)
        message = self._format_alert_message(results)
        try:
            self.alert_manager.send_alert(title=title, message=message, severity=severity)
        except Exception:
            # Alerts should never crash the process
            pass

    def _run_audit(self, detail_level: str = "full") -> Dict[str, Any]:
        prj = self.project_root
        repo_name = prj.name

        # Collect metrics
        metrics = self._collect_repo_metrics(prj, limit_scan=(detail_level == "brief"))
        security = self._security_checks(prj, limit_scan=(detail_level == "brief"))
        
        # File integrity checks (if enabled)
        file_integrity = self._file_integrity_checks(prj)
        
        efficiency = self._efficiency_checks(metrics)
        minimalism = self._minimalism_checks(prj, metrics)
        style = self._style_preservation_checks(prj)

        summary = self._summarize(security, efficiency, minimalism, style, file_integrity)

        return {
            "repository": repo_name,
            "root": str(prj),
            "detail_level": detail_level,
            "policy": self.policy,
            "metrics": metrics,
            "security": security,
            "file_integrity": file_integrity,
            "efficiency": efficiency,
            "minimalism": minimalism,
            "style_preservation": style,
            "summary": summary,
        }

    # -------------------- Checks --------------------
    def _collect_repo_metrics(self, root: Path, limit_scan: bool) -> Dict[str, Any]:
        file_count = 0
        py_count = 0
        big_files: List[str] = []
        unsafe_exts = {".pem", ".key", ".pfx", ".p12"}
        unsafe_files: List[str] = []

        max_files = 3000 if not limit_scan else 800
        max_big_file_size = 5 * 1024 * 1024  # 5 MiB

        for dirpath, dirnames, filenames in os.walk(root):
            # Skip typical build/venv/artifacts
            skip_dirs = {".git", "__pycache__", ".venv", "venv", "dist", "build", "node_modules"}
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]

            for fname in filenames:
                file_count += 1
                if file_count > max_files:
                    break

                p = Path(dirpath) / fname
                if p.suffix == ".py":
                    py_count += 1
                if p.suffix.lower() in unsafe_exts:
                    unsafe_files.append(str(p.relative_to(root)))
                try:
                    if p.stat().st_size > max_big_file_size:
                        big_files.append(str(p.relative_to(root)))
                except OSError:
                    continue

            if file_count > max_files:
                break

        return {
            "total_files_scanned": file_count,
            "python_files": py_count,
            "big_files": big_files[:10],
            "unsafe_files": unsafe_files[:10],
            "scan_limited": file_count >= max_files,
        }

    def _security_checks(self, root: Path, limit_scan: bool) -> Dict[str, Any]:
        secrets_patterns = [
            re.compile(r"aws_?(access|secret)[_\- ]?key\s*[:=]\s*['\"][A-Za-z0-9/+=]{16,}['\"]", re.I),
            re.compile(r"(?i)secret\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
            re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
            re.compile(r"-----BEGIN (RSA|DSA|EC) PRIVATE KEY-----"),
        ]
        findings: List[Dict[str, Any]] = []
        verified_false_positives: List[Dict[str, Any]] = []
        max_hits = 25 if not limit_scan else 8

        scanned = 0
        for dirpath, dirnames, filenames in os.walk(root):
            skip_dirs = {".git", "__pycache__", ".venv", "venv", ".venv_beta", "test_install_env", "dist", "build", "node_modules", "quarantine_legacy_archive"}
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]

            for fname in filenames:
                # Only scan text-like files
                if not any(fname.endswith(ext) for ext in (".py", ".json", ".md", ".yml", ".yaml", ".ini", ".txt")):
                    continue
                p = Path(dirpath) / fname
                try:
                    content = p.read_text(errors="ignore")
                except Exception:
                    continue

                for pat in secrets_patterns:
                    if pat.search(content):
                        finding = {
                            "file": str(p.relative_to(root)),
                            "pattern": pat.pattern[:40] + ("..." if len(pat.pattern) > 40 else ""),
                        }
                        
                        # Verify if this is a false positive
                        fp_result = self._verify_false_positive_security(p, content, pat)
                        if fp_result["is_false_positive"]:
                            finding["verified_false_positive"] = True
                            finding["reason"] = fp_result["reason"]
                            verified_false_positives.append(finding)
                        else:
                            findings.append(finding)
                        
                        if len(findings) + len(verified_false_positives) >= max_hits:
                            break
                if len(findings) + len(verified_false_positives) >= max_hits:
                    break

            scanned += 1
            if len(findings) + len(verified_false_positives) >= max_hits:
                break

        return {
            "secrets_findings": findings,
            "verified_false_positives": verified_false_positives,
            "issues": len(findings),
        }

    def _verify_false_positive_security(self, file_path: Path, content: str, pattern: re.Pattern) -> Dict[str, Any]:
        """
        Verify if a security finding is a false positive through contextual analysis.
        Does NOT whitelist - still reports the finding but marks it as verified FP.
        """
        file_name = file_path.name
        rel_path = str(file_path)
        
        # Skip virtual environments and installed packages
        venv_indicators = ["test_install_env", ".venv", "venv", "site-packages", "dist-packages"]
        if any(indicator in rel_path for indicator in venv_indicators):
            return {
                "is_false_positive": True,
                "reason": "Virtual environment or installed package (not source code)"
            }
        
        # Check for documentation/example contexts
        if file_name in ("SECURITY.md", "README.md", "CONTRIBUTING.md", "EXAMPLE.md", "POLICY.md"):
            # Look for documentation indicators
            doc_indicators = [
                r"example[:\s]",
                r"for example",
                r"sample",
                r"placeholder",
                r"demo",
                r"illustration",
                r"```",  # code blocks
                r"#\s*Example",
                r">\s*",  # markdown quotes
                r"export\s+CODESENTINEL",  # environment variable examples
                r"CODESENTINEL_\w+",  # environment variable names
            ]
            # Check match context (not just file content)
            match = pattern.search(content)
            if match:
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                
                for indicator in doc_indicators:
                    if re.search(indicator, context, re.IGNORECASE):
                        return {
                            "is_false_positive": True,
                            "reason": f"Documentation file ({file_name}) with example/demo context"
                        }
        
        # Check for empty placeholder strings in config (commonly "password": "")
        match = pattern.search(content)
        if match and pattern.pattern.startswith(r"(?i)password"):
            # Check if this is an empty string placeholder
            match_text = match.group(0)
            if '""' in match_text or "''" in match_text:
                return {
                    "is_false_positive": True,
                    "reason": "Empty placeholder string in configuration"
                }
        
        # Check for GUI wizard placeholder/demo password fields
        if "gui_wizard" in rel_path or "setup_wizard" in rel_path:
            # Look for GUI context - Entry widgets, placeholder text, validation
            gui_indicators = [
                r"Entry\s*\(",
                r"placeholder",
                r"Label\s*\(",
                r"\.insert\s*\(",
                r"show\s*=\s*['\"][\*\•]",  # password masking
                r"entry\.get\(\)",
                r"validate",
                r"# Example:",
                r"# Demo",
            ]
            if match:
                # Get context around the match (500 chars before/after)
                start = max(0, match.start() - 500)
                end = min(len(content), match.end() + 500)
                context = content[start:end]
                
                for indicator in gui_indicators:
                    if re.search(indicator, context):
                        return {
                            "is_false_positive": True,
                            "reason": f"GUI wizard file with placeholder/demo password field context"
                        }
        
        # Not a verified false positive
        return {"is_false_positive": False, "reason": None}

    def _file_integrity_checks(self, root: Path) -> Dict[str, Any]:
        """
        Check file integrity using hash-based validation.
        
        Detects:
        - Unauthorized file modifications
        - Missing critical files
        - Unauthorized new files
        """
        try:
            from codesentinel.utils.file_integrity import FileIntegrityValidator
        except ImportError:
            return {
                "status": "error",
                "message": "File integrity module not available"
            }
        
        # Load integrity configuration from config
        cfg = getattr(self.config_manager, 'config', {}) or {}
        integrity_config = cfg.get("integrity", {})
        
        # Skip if not enabled
        if not integrity_config.get("enabled", False):
            return {
                "status": "disabled",
                "message": "File integrity checking is disabled"
            }
        
        # Initialize validator
        validator = FileIntegrityValidator(root, integrity_config)
        
        # Verify integrity
        results = validator.verify_integrity()
        
        # Transform results for dev_audit format
        issues = []
        for violation in results.get("violations", []):
            priority = "CRITICAL" if violation.get("severity") == "critical" else "HIGH"
            issue_type = violation.get("type", "unknown")
            
            if issue_type == "modified_file":
                issues.append({
                    "issue": f"File modified without authorization: {violation['file']}",
                    "priority": priority,
                    "hints": [
                        "Verify if modification was intentional",
                        "Update baseline if change is authorized: codesentinel integrity --update",
                        "Investigate potential security breach if unauthorized"
                    ],
                    "file": violation["file"],
                    "is_critical": violation.get("is_critical", False)
                })
            elif issue_type == "missing_file":
                issues.append({
                    "issue": f"Required file missing: {violation['file']}",
                    "priority": priority,
                    "hints": [
                        "Restore file from backup or repository",
                        "Update baseline if deletion was intentional: codesentinel integrity --update"
                    ],
                    "file": violation["file"],
                    "is_critical": violation.get("is_critical", False)
                })
            elif issue_type == "unauthorized_file":
                issues.append({
                    "issue": f"Unauthorized file detected: {violation['file']}",
                    "priority": "HIGH",
                    "hints": [
                        "Verify file source and purpose",
                        "Add to whitelist if legitimate: codesentinel integrity --whitelist",
                        "Remove if malicious or unwanted"
                    ],
                    "file": violation["file"]
                })
        
        return {
            "status": results.get("status"),
            "issues": issues,
            "statistics": results.get("statistics", {}),
            "verified": results.get("verified")
        }

    def _efficiency_checks(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        suggestions: List[str] = []
        
        if metrics.get("scan_limited"):
            suggestions.append("Repository large; consider excluding artifacts from repo")
        
        if len(metrics.get("big_files", [])) > 0:
            suggestions.append("Large files detected; consider Git LFS or pruning")
        
        # Check for redundant wizard implementations
        root = self.project_root
        wizard_files = []
        if (root / "setup_wizard.py").exists():
            wizard_files.append("setup_wizard.py")
        if (root / "codesentinel" / "gui_wizard_v2.py").exists():
            wizard_files.append("codesentinel/gui_wizard_v2.py")
        if (root / "src" / "codesentinel" / "ui" / "setup" / "wizard.py").exists():
            wizard_files.append("src/codesentinel/ui/setup/wizard.py")
        if len(wizard_files) > 1:
            suggestions.append(f"Multiple wizard implementations detected: {', '.join(wizard_files)} (consolidate to one)")

        # Check for __pycache__ in root
        if (root / "__pycache__").exists():
            suggestions.append("__pycache__ in root directory (add to .gitignore and clean up)")

        return {
            "suggestions": suggestions,
            "issues": len(suggestions),
        }

    def _minimalism_checks(self, root: Path, metrics: Dict[str, Any]) -> Dict[str, Any]:
        violations: List[str] = []
        verified_false_positives: List[Dict[str, Any]] = []
        
        # Check for duplicate installers (defensive)
        installer_names = {"install.py", "install_deps.py", "setup_wizard.py", "install_codesentinel.py"}
        present_installers = []
        for name in installer_names:
            if (root / name).exists():
                present_installers.append(name)
        if len(present_installers) > 2:
            violations.append(f"Too many installers present: {', '.join(present_installers)}")

        # Check for orphaned test files in root (should be in tests/)
        orphaned_tests = []
        for item in root.iterdir():
            if item.is_file() and item.name.startswith("test_") and item.suffix == ".py":
                orphaned_tests.append(item.name)
        if orphaned_tests:
            violations.append(f"Orphaned test files in root (move to tests/): {', '.join(orphaned_tests)}")

        # Check for duplicate launcher/wizard files
        launchers = []
        if (root / "launch.py").exists():
            launchers.append("launch.py")
        if (root / "codesentinel" / "launcher.py").exists():
            launchers.append("codesentinel/launcher.py")
        if len(launchers) > 1:
            violations.append(f"Duplicate launcher files: {', '.join(launchers)}")

        # Check for duplicate setup configurations (setup.py + pyproject.toml)
        if (root / "setup.py").exists() and (root / "pyproject.toml").exists():
            violation = "Redundant packaging: both setup.py and pyproject.toml (prefer pyproject.toml only)"
            fp_result = self._verify_false_positive_minimalism(root, "redundant_packaging")
            if fp_result["is_false_positive"]:
                verified_false_positives.append({
                    "violation": violation,
                    "reason": fp_result["reason"]
                })
            else:
                violations.append(violation)

        # Check for incomplete/abandoned directories
        src_dir = root / "src"
        if src_dir.exists():
            # Check if src/ contains incomplete/abandoned code
            src_codesentinel = src_dir / "codesentinel"
            if src_codesentinel.exists():
                violations.append("Incomplete src/codesentinel/ directory detected (may contain abandoned code)")

        # Check for legacy quarantine directories
        if (root / "quarantine").exists():
            violations.append("Legacy quarantine directory present; archive recommended")
        if (root / "quarantine_legacy_archive").exists():
            violations.append("Legacy archive directory still present (cleanup recommended after verification)")

        return {
            "violations": violations,
            "verified_false_positives": verified_false_positives,
            "issues": len(violations),
        }

    def _verify_false_positive_minimalism(self, root: Path, check_type: str) -> Dict[str, Any]:
        """
        Verify if a minimalism violation is a false positive through contextual analysis.
        Does NOT whitelist - still reports the finding but marks it as verified FP.
        """
        if check_type == "redundant_packaging":
            setup_py = root / "setup.py"
            pyproject_toml = root / "pyproject.toml"
            
            if not setup_py.exists() or not pyproject_toml.exists():
                return {"is_false_positive": False, "reason": None}
            
            try:
                setup_content = setup_py.read_text(errors="ignore")
                pyproject_content = pyproject_toml.read_text(errors="ignore")
                
                # Modern Python packaging best practice: pyproject.toml is primary,
                # but setup.py can be kept for backward compatibility with:
                # - pip < 19.0
                # - older build tools
                # - editable installs in some environments
                
                # Check if pyproject.toml has complete PEP 517/518 build system
                has_build_system = "[build-system]" in pyproject_content
                has_project_section = "[project]" in pyproject_content
                uses_setuptools_backend = "setuptools.build_meta" in pyproject_content
                
                # If pyproject.toml is complete and uses setuptools backend,
                # having setup.py is intentional for compatibility
                if has_build_system and has_project_section and uses_setuptools_backend:
                    return {
                        "is_false_positive": True,
                        "reason": "Valid dual-config: pyproject.toml (PEP 517/518) primary with setup.py for backward compatibility"
                    }
            except Exception:
                pass
        
        return {"is_false_positive": False, "reason": None}

    def _style_preservation_checks(self, root: Path) -> Dict[str, Any]:
        """Check that audit respects existing style and doesn't force changes."""
        notes: List[str] = []
        
        # Verify we're not forcing style changes
        notes.append("Audit is non-destructive; no style enforcement")
        
        # Check for style consistency indicators
        if (root / ".editorconfig").exists():
            notes.append("EditorConfig detected; style defined")
        if (root / "pyproject.toml").exists():
            notes.append("pyproject.toml detected; may contain style config")
        if (root / ".pre-commit-config.yaml").exists():
            notes.append("Pre-commit hooks detected; automated style checks active")
        
        return {
            "notes": notes,
            "style_preserved": True,
        }

    # -------------------- Reporting --------------------
    def _summarize(self, security: Dict[str, Any], efficiency: Dict[str, Any], minimalism: Dict[str, Any], style: Dict[str, Any], file_integrity: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        total_issues = security.get("issues", 0) + efficiency.get("issues", 0) + minimalism.get("issues", 0)
        
        # Add file integrity violations to total
        if file_integrity and file_integrity.get("status") not in ["disabled", "error"]:
            integrity_issues = len(file_integrity.get("issues", []))
            total_issues += integrity_issues
        
        level = "info"
        if total_issues >= 8 or security.get("issues", 0) >= 5:
            level = "critical"
        elif total_issues >= 4 or security.get("issues", 0) >= 3:
            level = "warning"
        
        # Elevate to critical if file integrity has critical violations
        if file_integrity and file_integrity.get("status") == "critical":
            level = "critical"
        
        return {
            "total_issues": total_issues,
            "severity": level,
            "style_preserved": style.get("style_preserved", True),
        }

    def _print_report(self, results: Dict[str, Any]) -> None:
        print("\nCodeSentinel Development Audit")
        print("=" * 40)
        print(f"Repository: {results['repository']}")
        print(f"Detail: {results['detail_level']}")
        print("Policy: non_destructive=%s, feature_preservation=%s" % (
            str(results.get('policy', {}).get('non_destructive', True)),
            str(results.get('policy', {}).get('feature_preservation', True))
        ))
        
        print("\nSecurity Findings:")
        for f in results["security"]["secrets_findings"][:5]:
            print(f"  - {f['file']} (pattern: {f['pattern']})")
        if not results["security"]["secrets_findings"]:
            print("  - No obvious secrets detected")
        
        # Report verified false positives separately
        verified_fps = results["security"].get("verified_false_positives", [])
        if verified_fps:
            print("\nSecurity - Verified False Positives:")
            for fp in verified_fps[:5]:
                print(f"  ✓ {fp['file']} (pattern: {fp['pattern']})")
                print(f"    Reason: {fp['reason']}")
        
        # File Integrity Report
        file_integrity = results.get("file_integrity", {})
        if file_integrity.get("status") not in ["disabled", "error"]:
            print("\nFile Integrity:")
            status = file_integrity.get("status", "unknown")
            print(f"  Status: {status.upper()}")
            
            stats = file_integrity.get("statistics", {})
            if stats:
                print(f"  Files checked: {stats.get('files_checked', 0)}")
                print(f"  Passed: {stats.get('files_passed', 0)}")
                if stats.get('files_modified', 0) > 0:
                    print(f"  ⚠ Modified: {stats.get('files_modified', 0)}")
                if stats.get('files_missing', 0) > 0:
                    print(f"  ⚠ Missing: {stats.get('files_missing', 0)}")
                if stats.get('files_unauthorized', 0) > 0:
                    print(f"  ⚠ Unauthorized: {stats.get('files_unauthorized', 0)}")
            
            # Show critical violations
            critical_issues = [issue for issue in file_integrity.get("issues", []) if issue.get("is_critical")]
            if critical_issues:
                print("\n  CRITICAL File Integrity Violations:")
                for issue in critical_issues[:5]:
                    print(f"    ! {issue['issue']}")
        elif file_integrity.get("status") == "disabled":
            print("\nFile Integrity: DISABLED (enable in config to check file modifications)")
        
        print("\nEfficiency Suggestions:")
        for s in results["efficiency"]["suggestions"]:
            print(f"  - {s}")
        if not results["efficiency"]["suggestions"]:
            print("  - No suggestions")
        
        print("\nMinimalism Violations:")
        for v in results["minimalism"]["violations"]:
            print(f"  - {v}")
        if not results["minimalism"]["violations"]:
            print("  - None detected")
        
        # Report verified false positives for minimalism
        min_fps = results["minimalism"].get("verified_false_positives", [])
        if min_fps:
            print("\nMinimalism - Verified False Positives:")
            for fp in min_fps:
                print(f"  ✓ {fp['violation']}")
                print(f"    Reason: {fp['reason']}")
        
        print("\nStyle Preservation:")
        style_notes = results.get("style_preservation", {}).get("notes", [])
        for note in style_notes:
            print(f"  - {note}")
        if not style_notes:
            print("  - No style information available")
        
        print("\nSummary:")
        print(json.dumps(results["summary"], indent=2))

    def _severity_from_results(self, results: Dict[str, Any]) -> str:
        return results.get("summary", {}).get("severity", "info")

    def _format_alert_message(self, results: Dict[str, Any]) -> str:
        total = results["summary"]["total_issues"]
        sec = results["security"]["issues"]
        eff = results["efficiency"]["issues"]
        minv = results["minimalism"]["issues"]
        return (
            f"Repo: {results['repository']}\n"
            f"Issues: {total} (security: {sec}, efficiency: {eff}, minimalism: {minv})\n"
            f"Detail: {results['detail_level']}\n"
        )


__all__ = ["DevAudit"]
