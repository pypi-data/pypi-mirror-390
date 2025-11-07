"""
File Integrity Validation System

SECURITY > EFFICIENCY > MINIMALISM

Hash-based file integrity checking with whitelist mechanism for detecting
unauthorized modifications in the CodeSentinel workspace.

⚠️ PERMANENT DIRECTIVES:
- NEVER store plain text passwords or tokens
- All sensitive operations must be audited
- Configuration validation with secure defaults
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime
import logging
import time
from threading import Thread

logger = logging.getLogger(__name__)


class FileIntegrityValidator:
    """
    Validates file integrity using SHA256 hashes and whitelist patterns.
    
    Features:
    - Generate baseline hashes for workspace files
    - Verify files against baseline
    - Manage whitelist of approved files
    - Detect unauthorized modifications
    - Support for critical file designation
    """
    
    DEFAULT_HASH_ALGORITHM = "sha256"
    BASELINE_FILENAME = ".codesentinel_integrity.json"
    
    # Files/directories to always exclude from integrity checking
    EXCLUDE_PATTERNS = {
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".venv",
        "venv",
        ".env",
        "node_modules",
        "dist",
        "build",
        "*.egg-info",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "test_env_*",  # Test virtual environments
    }
    
    def __init__(self, workspace_root: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the file integrity validator.
        
        Args:
            workspace_root: Root directory of the workspace
            config: Optional configuration dict with keys:
                - enabled (bool): Whether integrity checking is enabled
                - whitelist_patterns (List[str]): Glob patterns for whitelisted files
                - critical_files (List[str]): Files that must not be modified
                - hash_algorithm (str): Hash algorithm to use (default: sha256)
        """
        self.workspace_root = Path(workspace_root)
        self.baseline_file = self.workspace_root / self.BASELINE_FILENAME
        
        # Load configuration
        self.config = config or {}
        self.enabled = self.config.get("enabled", False)
        self.whitelist_patterns = set(self.config.get("whitelist_patterns", []))
        self.critical_files = set(self.config.get("critical_files", []))
        self.hash_algorithm = self.config.get("hash_algorithm", self.DEFAULT_HASH_ALGORITHM)
        
        # Baseline data
        self.baseline: Dict[str, Any] = {}
        
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate hash of a file."""
        hasher = hashlib.new(self.hash_algorithm)
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash {file_path}: {e}")
            return ""
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from integrity checking."""
        path_str = str(file_path)
        
        # Check exclude patterns
        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith("*."):
                # File extension pattern
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                # Directory or filename pattern
                return True
        
        return False
    
    def _is_whitelisted(self, file_path: Path) -> bool:
        """Check if file matches whitelist patterns."""
        for pattern in self.whitelist_patterns:
            if file_path.match(pattern):
                return True
        return False
    
    def _is_critical(self, file_path: Path) -> bool:
        """Check if file is marked as critical."""
        rel_path = file_path.relative_to(self.workspace_root)
        return str(rel_path) in self.critical_files
    
    def generate_baseline(self, patterns: Optional[List[str]] = None, max_files: int = 10000) -> Dict[str, Any]:
        """
        Generate baseline hashes for workspace files.
        
        Args:
            patterns: Optional list of glob patterns to include. If None, includes all files.
            max_files: Maximum number of files to process (safety limit to prevent infinite loops)
        
        Returns:
            Dict with baseline data including hashes, metadata, and statistics
        """
        logger.info("Generating file integrity baseline...")
        start_time = time.time()
        
        baseline = {
            "version": "1.0.0",
            "algorithm": self.hash_algorithm,
            "generated": datetime.utcnow().isoformat(),
            "workspace_root": str(self.workspace_root),
            "files": {},
            "statistics": {
                "total_files": 0,
                "critical_files": 0,
                "whitelisted_files": 0,
                "excluded_files": 0,
                "skipped_files": 0
            }
        }
        
        # Determine which files to process
        logger.debug(f"Starting file enumeration for {self.workspace_root}")
        try:
            if patterns:
                logger.debug(f"Using glob patterns: {patterns}")
                files_to_process = []
                for pattern in patterns:
                    try:
                        pattern_matches = list(self.workspace_root.rglob(pattern))
                        logger.debug(f"Pattern '{pattern}' matched {len(pattern_matches)} files")
                        files_to_process.extend(pattern_matches)
                    except Exception as e:
                        logger.warning(f"Error globbing pattern '{pattern}': {e}")
                        continue
            else:
                logger.debug("Using default rglob('*') enumeration")
                files_to_process = list(self.workspace_root.rglob("*"))
                logger.debug(f"Enumerated {len(files_to_process)} total items")
        except Exception as e:
            logger.error(f"Failed to enumerate files: {e}")
            raise RuntimeError(f"File enumeration failed: {e}")
        
        # Safety check for infinite loops
        if len(files_to_process) > max_files:
            logger.warning(f"File enumeration returned {len(files_to_process)} items (limit: {max_files})")
            logger.warning("Truncating to safety limit to prevent infinite processing")
            files_to_process = files_to_process[:max_files]
        
        # Process files with progress logging
        files_processed = 0
        logger.info(f"Beginning file processing ({len(files_to_process)} items)")
        
        for idx, file_path in enumerate(files_to_process, 1):
            # Progress logging every 100 files
            if idx % 100 == 0:
                elapsed = time.time() - start_time
                logger.debug(f"Progress: {idx}/{len(files_to_process)} files processed ({elapsed:.2f}s)")
            
            try:
                if not file_path.is_file():
                    continue
            except (OSError, PermissionError) as e:
                logger.debug(f"Skipping {file_path}: cannot stat file ({e})")
                baseline["statistics"]["skipped_files"] += 1
                continue
            
            # Check if should be excluded
            if self._should_exclude(file_path):
                baseline["statistics"]["excluded_files"] += 1
                continue
            
            # Calculate relative path
            try:
                rel_path = str(file_path.relative_to(self.workspace_root))
            except ValueError:
                logger.debug(f"Skipping {file_path}: outside workspace root")
                continue
            
            # Calculate hash with error handling
            try:
                file_hash = self._calculate_hash(file_path)
                if not file_hash:
                    logger.debug(f"Skipping {file_path}: failed to calculate hash")
                    baseline["statistics"]["skipped_files"] += 1
                    continue
            except Exception as e:
                logger.debug(f"Skipping {file_path}: hash calculation error ({e})")
                baseline["statistics"]["skipped_files"] += 1
                continue
            
            # Get file metadata with error handling
            try:
                file_stat = file_path.stat()
                file_info = {
                    "hash": file_hash,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "is_critical": self._is_critical(file_path),
                    "is_whitelisted": self._is_whitelisted(file_path)
                }
            except (OSError, PermissionError) as e:
                logger.debug(f"Skipping {file_path}: cannot stat file for metadata ({e})")
                baseline["statistics"]["skipped_files"] += 1
                continue
            
            baseline["files"][rel_path] = file_info
            baseline["statistics"]["total_files"] += 1
            files_processed += 1
            
            if file_info["is_critical"]:
                baseline["statistics"]["critical_files"] += 1
            if file_info["is_whitelisted"]:
                baseline["statistics"]["whitelisted_files"] += 1
        
        elapsed = time.time() - start_time
        self.baseline = baseline
        logger.info(f"Baseline generated: {baseline['statistics']['total_files']} files in {elapsed:.2f}s")
        logger.info(f"Statistics - Excluded: {baseline['statistics']['excluded_files']}, "
                   f"Skipped: {baseline['statistics']['skipped_files']}, "
                   f"Processed: {files_processed}")
        
        return baseline
    
    def save_baseline(self, output_path: Optional[Path] = None) -> Path:
        """
        Save baseline to JSON file.
        
        Args:
            output_path: Optional custom output path. Defaults to workspace root.
        
        Returns:
            Path to saved baseline file
        """
        if not self.baseline:
            raise ValueError("No baseline data to save. Call generate_baseline() first.")
        
        output_file = output_path or self.baseline_file
        
        with open(output_file, 'w') as f:
            json.dump(self.baseline, f, indent=2)
        
        logger.info(f"Baseline saved to {output_file}")
        return output_file
    
    def load_baseline(self, input_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load baseline from JSON file.
        
        Args:
            input_path: Optional custom input path. Defaults to workspace root.
        
        Returns:
            Loaded baseline data
        """
        input_file = input_path or self.baseline_file
        
        if not input_file.exists():
            raise FileNotFoundError(f"Baseline file not found: {input_file}")
        
        with open(input_file, 'r') as f:
            self.baseline = json.load(f)
        
        # Ensure statistics field exists (for backward compatibility with older baselines)
        if "statistics" not in self.baseline:
            logger.warning("Baseline missing statistics field - regenerating from scratch")
            self.baseline["statistics"] = {
                "total_files": len(self.baseline.get("files", {})),
                "critical_files": 0,
                "whitelisted_files": 0,
                "excluded_files": 0,
                "skipped_files": 0
            }
        
        logger.info(f"Baseline loaded from {input_file}")
        return self.baseline
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify current workspace files against baseline.
        
        Returns:
            Dict with verification results including violations and statistics
        """
        if not self.baseline:
            try:
                self.load_baseline()
            except FileNotFoundError:
                return {
                    "status": "error",
                    "message": "No baseline found. Generate baseline first with --generate flag."
                }
        
        logger.info("Verifying file integrity...")
        
        results = {
            "status": "pass",
            "verified": datetime.utcnow().isoformat(),
            "violations": [],
            "statistics": {
                "files_checked": 0,
                "files_passed": 0,
                "files_modified": 0,
                "files_missing": 0,
                "files_unauthorized": 0,
                "critical_violations": 0
            }
        }
        
        baseline_files = set(self.baseline.get("files", {}).keys())
        current_files = set()
        
        # Check all current files
        for file_path in self.workspace_root.rglob("*"):
            if not file_path.is_file() or self._should_exclude(file_path):
                continue
            
            try:
                rel_path = str(file_path.relative_to(self.workspace_root))
            except ValueError:
                continue
            
            current_files.add(rel_path)
            results["statistics"]["files_checked"] += 1
            
            # Check if file is in baseline
            if rel_path not in baseline_files:
                # Unauthorized new file
                if not self._is_whitelisted(file_path):
                    results["violations"].append({
                        "type": "unauthorized_file",
                        "severity": "high",
                        "file": rel_path,
                        "message": f"Unauthorized file not in baseline: {rel_path}"
                    })
                    results["statistics"]["files_unauthorized"] += 1
                continue
            
            # Verify hash
            baseline_info = self.baseline["files"][rel_path]
            current_hash = self._calculate_hash(file_path)
            
            if current_hash != baseline_info["hash"]:
                # File modified
                severity = "critical" if baseline_info.get("is_critical") else "high"
                results["violations"].append({
                    "type": "modified_file",
                    "severity": severity,
                    "file": rel_path,
                    "message": f"File hash mismatch: {rel_path}",
                    "expected_hash": baseline_info["hash"],
                    "actual_hash": current_hash,
                    "is_critical": baseline_info.get("is_critical", False)
                })
                results["statistics"]["files_modified"] += 1
                
                if baseline_info.get("is_critical"):
                    results["statistics"]["critical_violations"] += 1
            else:
                results["statistics"]["files_passed"] += 1
        
        # Check for missing files
        missing_files = baseline_files - current_files
        for rel_path in missing_files:
            baseline_info = self.baseline["files"][rel_path]
            severity = "critical" if baseline_info.get("is_critical") else "medium"
            results["violations"].append({
                "type": "missing_file",
                "severity": severity,
                "file": rel_path,
                "message": f"File missing from workspace: {rel_path}",
                "is_critical": baseline_info.get("is_critical", False)
            })
            results["statistics"]["files_missing"] += 1
            
            if baseline_info.get("is_critical"):
                results["statistics"]["critical_violations"] += 1
        
        # Update overall status
        if results["violations"]:
            if results["statistics"]["critical_violations"] > 0:
                results["status"] = "critical"
            else:
                results["status"] = "fail"
        
        logger.info(f"Integrity check complete: {results['status']}")
        return results
    
    def update_whitelist(self, patterns: List[str], replace: bool = False) -> None:
        """
        Update whitelist patterns.
        
        Args:
            patterns: List of glob patterns to add
            replace: If True, replace existing patterns. If False, add to existing.
        """
        if replace:
            self.whitelist_patterns = set(patterns)
        else:
            self.whitelist_patterns.update(patterns)
        
        logger.info(f"Whitelist updated: {len(self.whitelist_patterns)} patterns")
    
    def update_critical_files(self, files: List[str], replace: bool = False) -> None:
        """
        Update critical files list.
        
        Args:
            files: List of file paths (relative to workspace root) to mark as critical
            replace: If True, replace existing list. If False, add to existing.
        """
        if replace:
            self.critical_files = set(files)
        else:
            self.critical_files.update(files)
        
        logger.info(f"Critical files updated: {len(self.critical_files)} files")
