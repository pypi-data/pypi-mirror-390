#!/usr/bin/env python3
"""
CodeSentinel Path Resolution Utilities

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

Centralized path resolution logic to eliminate duplication across
installer files and maintain consistent project root detection.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List


class PathResolver:
    """Centralized path resolution for CodeSentinel project operations."""
    
    @staticmethod
    def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
        """
        Find CodeSentinel project root by looking for key indicator files.
        
        Args:
            start_path: Path to start search from (defaults to current file location)
            
        Returns:
            Path to project root or None if not found
        """
        if start_path is None:
            start_path = Path(__file__).parent
            
        # Key files that indicate CodeSentinel project root
        indicator_files = [
            "setup.py",
            "pyproject.toml", 
            "launch.py",
            "codesentinel.json"
        ]
        
        # Search upward from start_path
        current = start_path.resolve()
        for _ in range(10):  # Limit search depth
            for indicator in indicator_files:
                if (current / indicator).exists():
                    # Verify it's actually CodeSentinel by checking for package directory
                    if (current / "codesentinel").exists():
                        return current
            
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
                
        return None
    
    @staticmethod
    def find_git_repositories(search_paths: List[Path], max_repos: int = 10) -> List[dict]:
        """
        Find Git repositories in common development directories.
        
        Args:
            search_paths: List of directories to search
            max_repos: Maximum number of repositories to return
            
        Returns:
            List of repository info dictionaries
        """
        repositories = []
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            try:
                # Search up to 3 levels deep
                for root, dirs, files in os.walk(search_path):
                    # Limit depth
                    level = root.replace(str(search_path), '').count(os.sep)
                    if level >= 3:
                        dirs[:] = []  # Don't recurse deeper
                        continue
                    
                    # Check if this directory is a git repository
                    if '.git' in dirs:
                        repo_path = Path(root)
                        repo_name = repo_path.name
                        relative_path = repo_path.relative_to(search_path.parent)
                        
                        repositories.append({
                            'name': repo_name,
                            'path': repo_path,
                            'relative_path': str(relative_path),
                            'display': f"{repo_name} ({relative_path})"
                        })
                        
                        # Don't search inside git repositories
                        dirs[:] = []
                        
                        if len(repositories) >= max_repos:
                            return repositories
                            
            except (OSError, PermissionError):
                continue  # Skip inaccessible directories
                
        return repositories
    
    @staticmethod
    def get_common_dev_paths() -> List[Path]:
        """Get common development directory paths for the current platform."""
        home = Path.home()
        common_paths = [
            home / "Documents",
            home / "Projects", 
            home / "Code",
            home / "Development",
            home / "dev",
            home / "src"
        ]
        
        # Add platform-specific paths
        if sys.platform == "win32":
            common_paths.extend([
                Path("C:/Projects"),
                Path("D:/Projects"),
                home / "source"
            ])
        else:
            common_paths.extend([
                Path("/opt/projects"),
                home / "workspace"
            ])
            
        return [p for p in common_paths if p.exists()]
    
    @staticmethod
    def setup_python_path(project_root: Path) -> None:
        """
        Setup Python path for CodeSentinel project.
        
        Args:
            project_root: Path to CodeSentinel project root
        """
        # Add src directory if it exists
        src_path = project_root / "src"
        if src_path.exists() and str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
            
        # Add project root if not already present
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
    
    @staticmethod
    def validate_codesentinel_structure(project_root: Path) -> dict:
        """
        Validate CodeSentinel project structure.
        
        Args:
            project_root: Path to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'missing': [],
            'warnings': []
        }
        
        # Required files/directories
        required_items = [
            ('setup.py', 'file'),
            ('codesentinel', 'dir'),
            ('tests', 'dir')
        ]
        
        for item_name, item_type in required_items:
            item_path = project_root / item_name
            if not item_path.exists():
                results['missing'].append(f"{item_name} ({item_type})")
                results['valid'] = False
            elif item_type == 'dir' and not item_path.is_dir():
                results['missing'].append(f"{item_name} (should be directory)")
                results['valid'] = False
            elif item_type == 'file' and not item_path.is_file():
                results['missing'].append(f"{item_name} (should be file)")
                results['valid'] = False
        
        # Optional but recommended items
        recommended_items = [
            'README.md',
            'requirements.txt',
            'launch.py'
        ]
        
        for item_name in recommended_items:
            if not (project_root / item_name).exists():
                results['warnings'].append(f"Missing recommended file: {item_name}")
        
        return results


# Convenience functions for common operations
def get_project_root() -> Optional[Path]:
    """Get CodeSentinel project root from current context."""
    return PathResolver.find_project_root()


def setup_project_environment() -> Optional[Path]:
    """Setup Python environment for CodeSentinel project."""
    project_root = get_project_root()
    if project_root:
        PathResolver.setup_python_path(project_root)
    return project_root


def find_dev_repositories(max_count: int = 10) -> List[dict]:
    """Find development repositories in common locations."""
    search_paths = PathResolver.get_common_dev_paths()
    return PathResolver.find_git_repositories(search_paths, max_count)