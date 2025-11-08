"""
Project scanner for auto-detection of source files and dependencies.

This module provides intelligent auto-detection of:
- C++ source files (*.cpp, *.cc, *.cxx)
- Header files (*.h, *.hpp)
- Include directories
- Project dependencies

Used by validators to reduce configuration burden on users.
"""

import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProjectScanner:
    """
    Scans project directories to auto-detect source files and dependencies.

    Uses heuristics to find related source files, headers, and include paths
    without requiring manual specification in most cases.
    """

    # Default source file patterns to search for
    SOURCE_PATTERNS = ["*.cpp", "*.cc", "*.cxx"]

    # Default header file patterns
    HEADER_PATTERNS = ["*.h", "*.hpp"]

    # Common include directory names
    INCLUDE_DIR_NAMES = ["include", "inc", "src", "source", "lib"]

    def __init__(self):
        """Initialize the project scanner."""
        self._logger = logging.getLogger(f"{__name__}.ProjectScanner")

    def scan_project(self, test_file_path: Path, search_depth: int = 3) -> Dict[str, List[str]]:
        """
        Scan project structure around a test file to find related sources.

        Args:
            test_file_path: Path to the test file
            search_depth: How many directory levels to search (default: 3)

        Returns:
            Dictionary with 'sources', 'headers', and 'includes' keys
        """
        self._logger.debug("Scanning project around: %s", test_file_path)

        test_dir = test_file_path.parent
        project_root = self.find_project_root(test_dir, search_depth)

        # Extract the base name from test file (e.g., "test_auth.cpp" -> "auth")
        test_base_name = self._extract_base_name(test_file_path)

        # Find source files (limit search to prevent infinite loops)
        source_files = self._find_source_files(project_root, test_dir, test_base_name)

        # Find header files (limit search to prevent infinite loops)
        header_files = self._find_header_files(project_root, test_dir, test_base_name)

        # Find include directories
        include_dirs = self._find_include_directories(project_root, test_dir)

        result = {
            "sources": [str(f.relative_to(project_root)) for f in source_files[:10]],  # Limit to 10 files max
            "headers": [str(f.relative_to(project_root)) for f in header_files[:10]],  # Limit to 10 files max
            "includes": list(set(str(d.relative_to(project_root)) for d in include_dirs)),
        }

        self._logger.debug(
            "Scan results: %d sources, %d headers, %d include dirs",
            len(result["sources"]),
            len(result["headers"]),
            len(result["includes"]),
        )

        return result

    def find_project_root(self, start_dir: Path, max_depth: int) -> Path:
        """
        Find the project root by looking for common project markers.

        Args:
            start_dir: Directory to start searching from
            max_depth: Maximum depth to search

        Returns:
            Path to project root directory
        """
        current = start_dir

        # Look for project markers (but don't search too far)
        for _ in range(min(max_depth, 5)):  # Limit search depth
            # Check for common project root indicators
            if (
                (current / "CMakeLists.txt").exists()
                or (current / "Makefile").exists()
                or (current / "pyproject.toml").exists()
                or (current / "setup.py").exists()
                or (current / ".git").exists()
            ):
                return current

            if current.parent == current:
                break
            current = current.parent

        # Fallback to test file's parent directory (but not higher than 3 levels)
        fallback = start_dir
        for _ in range(3):
            if fallback.parent == fallback:
                break
            fallback = fallback.parent

        return fallback

    def _extract_base_name(self, test_file_path: Path) -> str:
        """
        Extract the base name from a test file.

        Handles common test naming patterns:
        - test_auth.cpp -> auth
        - auth_test.cpp -> auth
        - TestAuth.cpp -> Auth

        Args:
            test_file_path: Path to the test file

        Returns:
            Base name without test prefix/suffix
        """
        filename = test_file_path.stem  # e.g., "test_auth" from "test_auth.cpp"

        # Remove common test prefixes
        if filename.startswith("test_"):
            return filename[5:]  # Remove "test_" prefix
        if filename.startswith("Test"):
            return filename[4:]  # Remove "Test" prefix

        # Remove common test suffixes
        if filename.endswith("_test"):
            return filename[:-5]  # Remove "_test" suffix
        if filename.endswith("Test"):
            return filename[:-4]  # Remove "Test" suffix

        # If no pattern matched, return the filename as-is
        return filename

    def _should_skip_source_file(self, source_file: Path, test_base_name: str = None) -> bool:
        """Check if a source file should be skipped during scanning."""
        filename = source_file.stem
        filepath_str = str(source_file)

        # Skip test files
        test_patterns = ["test_", "*_test", "*Test"]
        if any(pattern.replace("*", "") in filename for pattern in test_patterns if "*" not in pattern):
            return True

        # Skip framework files
        framework_patterns = ["gtest", "gmock", "googletest"]
        if any(framework in filepath_str.lower() for framework in framework_patterns):
            return True

        # Skip build directories and dependencies
        if any(skip_dir in filepath_str for skip_dir in ["build/", "deps/", "_deps/", "cmake-build-"]):
            return True

        # If test_base_name is provided, only include files matching that base name
        if test_base_name and filename != test_base_name:
            self._logger.debug(
                "Skipping source file '%s' (doesn't match test base name '%s')", filename, test_base_name
            )
            return True

        return False

    def _find_source_files(self, project_root: Path, test_dir: Path, test_base_name: str = None) -> List[Path]:
        """
        Find C++ source files in the project.

        Args:
            project_root: Project root directory
            test_dir: Test file directory
            test_base_name: Base name extracted from test file (e.g., "auth" from "test_auth.cpp")
                           If provided, only source files matching this base name are included

        Returns:
            List of source file paths
        """
        source_files = []

        # Only search in the immediate test directory (no subdirectories)
        for pattern in self.SOURCE_PATTERNS:
            source_files.extend(test_dir.glob(pattern))

        # Search in project root and common source directories (limit depth)
        search_dirs = [project_root]
        for dir_name in self.INCLUDE_DIR_NAMES:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                search_dirs.append(dir_path)

        for search_dir in search_dirs:
            # Only search in the immediate directory to avoid finding framework files
            for pattern in self.SOURCE_PATTERNS:
                source_files.extend(search_dir.glob(pattern))

        # Filter files and remove duplicates
        filtered_files = []
        for source_file in source_files:
            if not self._should_skip_source_file(source_file, test_base_name):
                if source_file not in filtered_files:
                    filtered_files.append(source_file)

        return sorted(filtered_files)

    def _find_header_files(self, project_root: Path, test_dir: Path, test_base_name: str = None) -> List[Path]:
        """
        Find header files in the project.

        Args:
            project_root: Project root directory
            test_dir: Test file directory
            test_base_name: Base name extracted from test file (e.g., "auth" from "test_auth.cpp")
                           If provided, only header files matching this base name are included

        Returns:
            List of header file paths
        """
        header_files = []

        # Only search in the immediate test directory (no subdirectories)
        for pattern in self.HEADER_PATTERNS:
            header_files.extend(test_dir.glob(pattern))

        # Search in project root and common include directories (limit depth)
        search_dirs = [project_root]
        for dir_name in self.INCLUDE_DIR_NAMES:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                search_dirs.append(dir_path)

        for search_dir in search_dirs:
            for pattern in self.HEADER_PATTERNS:
                header_files.extend(search_dir.glob(pattern))

        # Filter out framework headers and duplicates
        filtered_files = []
        framework_patterns = ["gtest", "gmock", "googletest"]

        for header_file in header_files:
            filename = header_file.stem
            filepath_str = str(header_file)

            # Skip framework files
            if any(framework in filepath_str.lower() for framework in framework_patterns):
                continue

            # Skip build directories and dependencies
            if any(skip_dir in filepath_str for skip_dir in ["build/", "deps/", "_deps/", "cmake-build-"]):
                continue

            # If test_base_name is provided, only include files matching that base name
            # E.g., for test_auth.cpp (base_name="auth"), only include auth.h
            if test_base_name:
                if filename != test_base_name:
                    self._logger.debug(
                        "Skipping header file '%s' (doesn't match test base name '%s')", filename, test_base_name
                    )
                    continue

            if header_file not in filtered_files:
                filtered_files.append(header_file)

        return sorted(filtered_files)

    def _find_include_directories(self, project_root: Path, test_dir: Path) -> List[Path]:
        """
        Find include directories in the project.

        Args:
            project_root: Project root directory
            test_dir: Test file directory

        Returns:
            List of include directory paths
        """
        include_dirs = []

        # Always include current test directory
        include_dirs.append(test_dir)

        # Look for common include directory names
        for dir_name in self.INCLUDE_DIR_NAMES:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # Skip framework directories
                if not any(framework in str(dir_path).lower() for framework in ["gtest", "gmock", "googletest"]):
                    include_dirs.append(dir_path)

        # Look for include directories in parent directories
        current = test_dir
        for _ in range(3):  # Search up to 3 levels
            current = current.parent
            if current == project_root:
                break

            for dir_name in self.INCLUDE_DIR_NAMES:
                dir_path = current / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    # Skip framework directories
                    if not any(framework in str(dir_path).lower() for framework in ["gtest", "gmock", "googletest"]):
                        include_dirs.append(dir_path)

        return sorted(list(set(include_dirs)))
