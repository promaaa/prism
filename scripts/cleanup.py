#!/usr/bin/env python3
"""
Cleanup script for Prism repository maintenance.
Removes temporary files, cache directories, old logs, and build artifacts.
"""

import os
import shutil
import glob
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Set


class RepositoryCleaner:
    """Repository cleanup utility."""

    def __init__(self, repo_root: Path, dry_run: bool = False, verbose: bool = False):
        """
        Initialize the cleaner.

        Args:
            repo_root: Root directory of the repository
            dry_run: If True, only show what would be deleted
            verbose: If True, show detailed output
        """
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.removed_files = 0
        self.removed_dirs = 0
        self.saved_space = 0

    def log(self, message: str):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def dry_log(self, message: str):
        """Log what would be done in dry run mode."""
        if self.dry_run:
            print(f"[DRY RUN] {message}")
        else:
            self.log(message)

    def remove_file(self, file_path: Path) -> bool:
        """Remove a file and track statistics."""
        try:
            if self.dry_run:
                self.dry_log(f"Would remove file: {file_path}")
                return True

            size = file_path.stat().st_size
            file_path.unlink()
            self.removed_files += 1
            self.saved_space += size
            self.log(f"Removed file: {file_path}")
            return True
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
            return False

    def remove_directory(self, dir_path: Path) -> bool:
        """Remove a directory and track statistics."""
        try:
            if self.dry_run:
                self.dry_log(f"Would remove directory: {dir_path}")
                return True

            # Calculate size before removal
            size = self.get_directory_size(dir_path)
            shutil.rmtree(dir_path)
            self.removed_dirs += 1
            self.saved_space += size
            self.log(f"Removed directory: {dir_path}")
            return True
        except Exception as e:
            print(f"Error removing directory {dir_path}: {e}")
            return False

    def get_directory_size(self, dir_path: Path) -> int:
        """Calculate the total size of a directory."""
        total_size = 0
        try:
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except:
            pass
        return total_size

    def clean_python_cache(self):
        """Clean Python cache files and directories."""
        self.log("Cleaning Python cache...")

        # Remove __pycache__ directories
        for cache_dir in self.repo_root.rglob("__pycache__"):
            if cache_dir.is_dir():
                self.remove_directory(cache_dir)

        # Remove .pyc files
        for pyc_file in self.repo_root.rglob("*.pyc"):
            self.remove_file(pyc_file)

        # Remove .pyo files
        for pyo_file in self.repo_root.rglob("*.pyo"):
            self.remove_file(pyo_file)

    def clean_test_cache(self):
        """Clean test cache directories."""
        self.log("Cleaning test cache...")

        # pytest cache
        pytest_cache = self.repo_root / ".pytest_cache"
        if pytest_cache.exists():
            self.remove_directory(pytest_cache)

        # coverage files
        for cov_file in self.repo_root.rglob(".coverage*"):
            self.remove_file(cov_file)

        # Remove coverage HTML reports
        coverage_html = self.repo_root / "htmlcov"
        if coverage_html.exists():
            self.remove_directory(coverage_html)

    def clean_build_artifacts(self):
        """Clean build artifacts and distributions."""
        self.log("Cleaning build artifacts...")

        # Common build directories
        build_dirs = ["build", "dist", "*.egg-info", ".eggs"]
        for pattern in build_dirs:
            for build_dir in self.repo_root.glob(pattern):
                if build_dir.is_dir():
                    self.remove_directory(build_dir)

        # PyInstaller artifacts
        for spec_file in self.repo_root.rglob("*.spec"):
            self.remove_file(spec_file)

    def clean_logs(self, max_age_days: int = 30):
        """Clean old log files."""
        self.log(f"Cleaning log files older than {max_age_days} days...")

        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        # Find log directories
        log_dirs = []
        for potential_log_dir in [
            self.repo_root / "logs",
            self.repo_root / "prism" / "logs",
        ]:
            if potential_log_dir.exists():
                log_dirs.append(potential_log_dir)

        for log_dir in log_dirs:
            for log_file in log_dir.rglob("*.log*"):
                if log_file.is_file():
                    try:
                        file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_mtime < cutoff_date:
                            self.remove_file(log_file)
                    except:
                        # If we can't get mtime, skip the file
                        pass

    def clean_temp_files(self):
        """Clean temporary files."""
        self.log("Cleaning temporary files...")

        # Common temporary file patterns
        temp_patterns = [
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.backup",
            "*~",
            "*.swp",
            "*.swo",
            ".DS_Store",
            "Thumbs.db",
            "ehthumbs.db",
            "desktop.ini",
        ]

        for pattern in temp_patterns:
            for temp_file in self.repo_root.rglob(pattern):
                if temp_file.is_file():
                    self.remove_file(temp_file)

    def clean_database_backups(self, keep_recent: int = 5):
        """Clean old database backup files, keeping the most recent ones."""
        self.log(f"Cleaning database backups, keeping {keep_recent} most recent...")

        # Find database files
        db_files = []
        for db_file in self.repo_root.rglob("*.db"):
            if "backup" in db_file.name.lower() or db_file.name.endswith(".db"):
                db_files.append(db_file)

        # Sort by modification time (newest first)
        db_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # Remove old backups
        for old_backup in db_files[keep_recent:]:
            self.remove_file(old_backup)

    def clean_export_files(self, max_age_days: int = 7):
        """Clean old export files."""
        self.log(f"Cleaning export files older than {max_age_days} days...")

        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        # Common export extensions
        export_patterns = ["*.csv", "*.xlsx", "*.pdf", "*.json"]

        for pattern in export_patterns:
            for export_file in self.repo_root.rglob(pattern):
                # Skip files in node_modules, venv, etc.
                if any(
                    part in export_file.parts
                    for part in ["node_modules", "venv", "env", ".git"]
                ):
                    continue

                try:
                    file_mtime = datetime.fromtimestamp(export_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        self.remove_file(export_file)
                except:
                    pass

    def clean_venv_cache(self):
        """Clean virtual environment cache."""
        self.log("Cleaning virtual environment cache...")

        venv_dirs = ["venv", "env", ".venv", ".env"]
        for venv_dir in venv_dirs:
            venv_path = self.repo_root / venv_dir
            if venv_path.exists() and venv_path.is_dir():
                # Only clean cache directories within venv
                for cache_dir in venv_path.rglob("__pycache__"):
                    if cache_dir.is_dir():
                        self.remove_directory(cache_dir)

    def run_full_cleanup(self):
        """Run a full cleanup of the repository."""
        print("Starting repository cleanup...")
        if self.dry_run:
            print("DRY RUN MODE - No files will be actually deleted")

        start_time = datetime.now()

        # Run all cleanup operations
        self.clean_python_cache()
        self.clean_test_cache()
        self.clean_build_artifacts()
        self.clean_logs()
        self.clean_temp_files()
        self.clean_database_backups()
        self.clean_export_files()
        self.clean_venv_cache()

        # Summary
        duration = datetime.now() - start_time
        saved_mb = self.saved_space / (1024 * 1024)

        print(f"\nCleanup completed in {duration.total_seconds():.2f} seconds")
        print(f"Removed {self.removed_files} files and {self.removed_dirs} directories")
        print(".2f")

        if self.dry_run:
            print("This was a dry run - no files were actually deleted")

    def get_cleanup_plan(self) -> dict:
        """Get a plan of what would be cleaned without actually doing it."""
        # This would require implementing dry-run logic for each cleanup method
        # For now, return a summary of what gets cleaned
        return {
            "python_cache": "Removes __pycache__ directories and .pyc/.pyo files",
            "test_cache": "Removes pytest cache and coverage files",
            "build_artifacts": "Removes build/, dist/, and *.egg-info directories",
            "logs": "Removes log files older than 30 days",
            "temp_files": "Removes temporary files (*.tmp, *.bak, etc.)",
            "database_backups": "Removes old database backups (keeps 5 most recent)",
            "export_files": "Removes export files older than 7 days",
            "venv_cache": "Removes __pycache__ from virtual environments",
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up Prism repository by removing temporary files, cache, and build artifacts."
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--repo-root",
        "-r",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--plan", action="store_true", help="Show cleanup plan without running cleanup"
    )

    args = parser.parse_args()

    cleaner = RepositoryCleaner(
        repo_root=args.repo_root, dry_run=args.dry_run, verbose=args.verbose
    )

    if args.plan:
        print("Repository Cleanup Plan:")
        print("=" * 50)
        for category, description in cleaner.get_cleanup_plan().items():
            print(f"• {category}: {description}")
        print("\nRun without --plan to execute cleanup.")
        return

    cleaner.run_full_cleanup()


if __name__ == "__main__":
    main()
