"""
Google Test validator for pytemplify.

This validator discovers C++ test files, builds them in an isolated environment
using pytemplify's CMake templates, runs the tests, and generates coverage reports.

SOLID Principles:
    - SRP: Single responsibility - validate Google Tests
    - OCP: Open for extension through options
    - LSP: Substitutable for BaseValidator
    - DIP: Depends on abstractions (BaseValidator, CMakeTemplateManager)

DRY Principle:
    - Reuses CMakeTemplateManager for CMake rendering
    - Reuses BaseValidator pattern matching logic
"""

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pytemplify.validation.base import BaseValidator, ValidationResult
from pytemplify.validation.cmake_manager import CMakeTemplateManager
from pytemplify.validation.project_scanner import ProjectScanner

logger = logging.getLogger(__name__)


class GTestValidator(BaseValidator):
    """
    Validates generated C++ code using Google Test (SOLID: SRP, LSP).

    Responsibilities:
        - Discover test files (test_*.cpp, *_test.cpp)
        - Build tests in isolated environment
        - Run tests with CTest
        - Generate coverage reports
        - Clean up build artifacts

    DRY: Reuses CMakeTemplateManager for CMake template rendering.
    """

    # Default patterns for test file discovery (DRY: single source of truth)
    DEFAULT_TEST_PATTERNS = ["test_*.cpp", "*_test.cpp", "test_*.cc", "*_test.cc"]

    # Default workspace directory name (can be configured via options)
    DEFAULT_WORKSPACE_DIR = ".pytemplify_gtest"

    # Profile definitions with sensible defaults
    PROFILES = {
        "basic": {
            "build_type": "Debug",
            "cxx_standard": 17,
            "gtest_version": "release-1.12.1",
            "enable_coverage": False,
            "test_timeout": 300,
            "build_parallel_jobs": "auto",
            "keep_build_artifacts": True,
            "warnings_as_errors": False,
            "cmake_definitions": [],
            "compile_flags": [],
            "link_libraries": ["dl"],
            "disable_windows": False,
            "clean_build": False,  # Use incremental builds for better performance
            "verbose": False,  # Suppress output, show only errors (gwgen2 pattern)
        },
        "coverage": {
            "build_type": "Debug",
            "cxx_standard": 17,
            "gtest_version": "release-1.12.1",
            "enable_coverage": True,
            "test_timeout": 300,
            "build_parallel_jobs": "auto",
            "keep_build_artifacts": True,
            "warnings_as_errors": False,
            "cmake_definitions": [],
            "compile_flags": [],
            "link_libraries": ["dl"],
            "disable_windows": False,
            "clean_build": False,  # Use incremental builds for better performance
            "verbose": False,  # Suppress output, show only errors (gwgen2 pattern)
        },
        "strict": {
            "build_type": "Debug",
            "cxx_standard": 17,
            "gtest_version": "release-1.12.1",
            "enable_coverage": True,
            "test_timeout": 300,
            "build_parallel_jobs": "auto",
            "keep_build_artifacts": True,
            "warnings_as_errors": True,
            "cmake_definitions": [],
            "compile_flags": ["-Wall", "-Wextra", "-Wpedantic"],
            "link_libraries": ["dl"],
            "disable_windows": False,
            "clean_build": False,  # Use incremental builds for better performance
            "verbose": False,  # Suppress output, show only errors (gwgen2 pattern)
        },
        "custom": {
            # Custom profile allows full control - no defaults set
        },
    }

    def __init__(self, config):
        """
        Initialize Google Test validator with profile-based configuration.

        Args:
            config: ValidatorConfig instance

        Configuration profiles:
            - basic: Minimal configuration, just run tests
            - coverage: Basic + code coverage reports
            - strict: Coverage + warnings as errors + strict compilation
            - custom: Full control over all options

        User options override profile defaults. For example:
            profile: "coverage"
            options:
              timeout: 600  # Only override timeout
        """
        super().__init__(config)
        self._cmake_manager = CMakeTemplateManager()
        self._logger = logging.getLogger(f"{__name__}.GTestValidator")
        self._project_scanner = ProjectScanner()

        # Get profile name from config
        # Profile can be in options dict OR as a top-level config attribute
        # Debug: log what we receive
        self._logger.debug("Received config.options: %s", self.config.options)
        self._logger.debug("Hasattr profile: %s", hasattr(self.config, "profile"))

        # Try to get profile from config object first, then from options dict
        if hasattr(self.config, "profile") and self.config.profile:
            profile_name = self.config.profile
        else:
            profile_name = self.config.options.get("profile", "basic")

        # Get profile defaults
        if profile_name not in self.PROFILES:
            raise ValueError(f"Unknown profile '{profile_name}'. Available profiles: {list(self.PROFILES.keys())}")

        profile_defaults = self.PROFILES[profile_name].copy()

        # Merge user options with profile defaults (DON'T mutate config.options!)
        # Store merged options in separate instance variable for runtime use
        self._runtime_options = profile_defaults.copy()

        # User options override profile defaults
        # If user provided nested "options" key, merge those
        if "options" in self.config.options:
            user_options = self.config.options["options"]
            self._runtime_options.update(user_options)
        else:
            # Otherwise merge all user options (except "profile")
            user_options = {k: v for k, v in self.config.options.items() if k != "profile"}
            self._runtime_options.update(user_options)

        # Debug: log final coverage setting
        self._logger.info(
            "Profile: %s, enable_coverage: %s", profile_name, self._runtime_options.get("enable_coverage")
        )

        # Set default patterns if not specified
        if not self.config.patterns:
            self.config.patterns.extend(self.DEFAULT_TEST_PATTERNS)

    def discover(self, output_dir: Path) -> List[Path]:
        """
        Discover test files in the output directory.

        Args:
            output_dir: Directory to search for test files

        Returns:
            List of test file paths
        """
        self._logger.info("Discovering Google Test files in %s", output_dir)

        test_files = []
        for pattern in self.config.patterns:
            # Search recursively for test files
            matches = list(output_dir.rglob(pattern))
            test_files.extend(matches)
            self._logger.debug("Pattern '%s' found %d files", pattern, len(matches))

        # Filter out files in build/validation directories to avoid endless loops
        filtered_files = []
        skip_dir_names = [
            self.DEFAULT_WORKSPACE_DIR,
            "build",
            "_deps",
            "CMakeFiles",
            ".cmake",
            "googletest",
            "pytemplify_validation",  # Legacy name for backward compatibility
        ]
        for file_path in test_files:
            # Check if any parent directory matches our skip list
            skip = False
            for parent in file_path.parents:
                if parent.name in skip_dir_names or parent.name.startswith(".pytemplify"):
                    self._logger.debug("Skipping test file in build/framework directory: %s", file_path)
                    skip = True
                    break
            if not skip:
                filtered_files.append(file_path)

        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for file_path in filtered_files:
            if file_path not in seen:
                seen.add(file_path)
                unique_files.append(file_path)

        self._logger.info("Discovered %d test files", len(unique_files))
        return unique_files

    def _handle_coverage(self, build_dir: Path, test_name: str, target: Path, start_time: float) -> Optional[str]:
        """
        Handle coverage generation with configurable failure tolerance.

        Args:
            build_dir: Build directory
            test_name: Name of the test
            target: Test file path
            start_time: Validation start time

        Returns:
            Coverage summary string if successful, None otherwise

        Raises:
            ValidationResult: If coverage fails and tolerate_coverage_failures is False
        """
        enable_cov = self._runtime_options.get("enable_coverage", False)
        self._logger.debug("Coverage enabled: %s", enable_cov)
        if not enable_cov:
            return None

        coverage_result = self._generate_coverage(build_dir)
        if coverage_result["success"]:
            return coverage_result.get("summary")

        # Coverage generation failures are warnings by default
        tolerate = self._runtime_options.get("tolerate_coverage_failures", True)
        self._logger.warning("Coverage generation result: %s", coverage_result.get("summary") or "failed")

        if not tolerate:
            duration = time.time() - start_time
            details = coverage_result.get("summary") or "Coverage generation failed"
            result = self._create_failure_result(
                test_name=test_name,
                target=target,
                message="Coverage generation failed",
                details=details,
                duration=duration,
            )
            # Raise the result as an exception to break out of validation flow
            raise RuntimeError(result)

        return None

    def validate(self, target: Path, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a single test file by building and running it.

        Args:
            target: Test file path
            context: Optional context (can contain 'output_dir' for relative path calculation)

        Returns:
            ValidationResult with test execution results
        """
        start_time = time.time()
        test_name = target.stem

        self._logger.info("Validating Google Test: %s", test_name)

        try:
            # Setup isolated build environment
            build_dir = self._setup_isolated_env(target, context)

            # Build and run test
            build_result = self._build_test(build_dir)
            if not build_result["success"]:
                return self._create_failure_result(
                    test_name=test_name,
                    target=target,
                    message="Build failed",
                    details=build_result["output"],
                    duration=time.time() - start_time,
                )

            test_result = self._run_test(build_dir, test_name)
            if not test_result["success"]:
                return self._create_failure_result(
                    test_name=test_name,
                    target=target,
                    message="Test execution failed",
                    details=test_result["output"],
                    duration=time.time() - start_time,
                )

            # Handle coverage generation
            coverage_info = self._handle_coverage(build_dir, test_name, target, start_time)

            # Build success result
            duration = time.time() - start_time
            message = f"Test '{test_name}' passed"
            details = f"Build time: {build_result['duration']:.2f}s, Test time: {test_result['duration']:.2f}s"

            if coverage_info:
                details += f"\nCoverage: {coverage_info}"

            return self.create_success_result(
                target_name=test_name, message=message, details=details, file_path=target, duration_seconds=duration
            )

        except RuntimeError as e:
            # Coverage failure raised as RuntimeError with ValidationResult
            if isinstance(e.args[0], ValidationResult):
                return e.args[0]
            raise
        except Exception as e:  # pylint: disable=broad-exception-caught
            duration = time.time() - start_time
            self._logger.error("Validation failed for %s: %s", test_name, e)
            return self._create_failure_result(
                test_name=test_name, target=target, message="Validation error", details=str(e), duration=duration
            )

    def _find_git_root(self, reference_path: Path) -> Path:
        """
        Find the root of the git repository by traversing up from the start path.

        This is inspired by gwgen2's find_git_root() utility function.

        Args:
            reference_path: Starting path (typically a test file or output directory)

        Returns:
            Path to git root, or the resolved reference_path if not in a git repo
        """
        path = reference_path.resolve()
        while path != path.parent:
            if (path / ".git").is_dir():
                self._logger.debug("Found git root at: %s", path)
                return path
            path = path.parent

        # Not in a git repository - return resolved reference path as fallback
        self._logger.debug("No git root found, using reference path: %s", reference_path.resolve())
        return reference_path.resolve()

    def _setup_isolated_env(self, test_file: Path, _context: Optional[Dict[str, Any]]) -> Path:
        """
        Setup isolated build environment for the test.

        Creates directory structure in workspace (auto-detected from git root):
            <git_root>/.pytemplify_gtest/<test_name>/
                CMakeLists.txt (rendered from template)
                build/ (CMake build directory)

        If not in a git repository, uses the test file's directory as workspace base.

        Args:
            test_file: Path to test file
            _context: Optional context (reserved for future use)

        Returns:
            Path to build directory

        Raises:
            RuntimeError: If environment setup fails
        """
        # Auto-detect workspace location based on git root (gwgen2 pattern)
        # Pass the parent directory, not the file itself, for consistent behavior
        test_dir = test_file.parent
        git_root = self._find_git_root(test_dir)

        # If git root is the same as test directory, we're not in a git repo
        # Use the test directory itself as workspace base
        if git_root == test_dir.resolve():
            workspace_base = test_dir
            self._logger.debug("Not in git repository, using test directory: %s", workspace_base)
        else:
            workspace_base = git_root
            self._logger.debug("Using git root for workspace: %s", workspace_base)

        # Create workspace under git root (or test dir)
        isolated_dir = workspace_base / self.DEFAULT_WORKSPACE_DIR / test_file.stem
        build_dir = isolated_dir / "build"

        self._logger.debug("Setting up isolated environment: %s", isolated_dir)

        # Clean and recreate build directory if clean_build is enabled (gwgen2 pattern)
        if self._runtime_options.get("clean_build", True):
            if build_dir.exists():
                self._logger.debug("Cleaning existing build directory: %s", build_dir)
                shutil.rmtree(build_dir)

        # Create directories
        isolated_dir.mkdir(parents=True, exist_ok=True)
        build_dir.mkdir(parents=True, exist_ok=True)

        # Auto-detect source files and include directories if not specified
        config_options = self._auto_detect_project_structure(test_file)

        # Create test configuration with auto-detected options
        test_config = self._cmake_manager.create_test_config(test_file.parent, config_options)

        # Use absolute path for test_file since workspace may be outside project
        absolute_test_file = test_file.absolute()

        # Render CMakeLists.txt
        cmake_path = isolated_dir / "CMakeLists.txt"
        self._cmake_manager.render_cmake_file(
            test_name=test_file.stem, test_file=absolute_test_file, output_path=cmake_path, **test_config
        )

        self._logger.debug("Isolated environment ready: %s", build_dir)
        return build_dir

    def _auto_detect_project_structure(self, test_file: Path) -> Dict[str, Any]:
        """
        Auto-detect source files and include directories if not manually specified.

        Args:
            test_file: Path to the test file

        Returns:
            Updated configuration options with auto-detected values (with absolute paths)
        """
        config_options = self._runtime_options.copy()

        # Only scan once and cache results to avoid infinite loops
        if not config_options.get("source_patterns") or not config_options.get("include_dirs"):
            self._logger.info("Auto-detecting project structure for %s", test_file.name)
            scan_results = self._project_scanner.scan_project(test_file)

            # Get project root to convert relative paths to absolute
            test_dir = test_file.parent
            project_root = self._project_scanner.find_project_root(test_dir, 3)

            # Set source patterns if not manually specified
            if not config_options.get("source_patterns"):
                if scan_results["sources"]:
                    # Convert to absolute paths for the format expected by CMake template
                    source_patterns = [
                        {"name": f"SRC{i}", "path": str((project_root / src).absolute())}
                        for i, src in enumerate(scan_results["sources"])
                    ]
                    config_options["source_patterns"] = source_patterns
                    self._logger.info("Auto-detected %d source files", len(scan_results["sources"]))
                else:
                    self._logger.warning("No source files auto-detected, using empty list")
                    config_options["source_patterns"] = []

            # Set include directories if not manually specified
            if not config_options.get("include_dirs"):
                if scan_results["includes"]:
                    # Convert to absolute paths
                    config_options["include_dirs"] = [
                        str((project_root / inc).absolute()) for inc in scan_results["includes"]
                    ]
                    self._logger.info("Auto-detected %d include directories", len(scan_results["includes"]))
                else:
                    # Use test directory as fallback
                    config_options["include_dirs"] = [str(test_dir.absolute())]
                    self._logger.info("No include directories auto-detected, using test directory")

        return config_options

    def _build_test(self, build_dir: Path) -> Dict[str, Any]:  # pylint: disable=too-many-branches
        """
        Build the test using CMake.

        Args:
            build_dir: CMake build directory

        Returns:
            Dictionary with 'success', 'output', 'duration'
        """
        self._logger.info("Building test in %s", build_dir)
        start_time = time.time()

        try:
            # Configure with CMake
            configure_cmd = ["cmake", ".."]
            self._logger.info("Running CMake configure: %s", " ".join(configure_cmd))

            # Conditional output capture based on verbose flag (gwgen2 pattern)
            verbose = self._runtime_options.get("verbose", False)
            if verbose:
                # Verbose mode: stream output to console in real-time
                configure_result = subprocess.run(
                    configure_cmd,
                    cwd=build_dir,
                    timeout=min(self._runtime_options.get("test_timeout", 300), 120),
                    check=False,
                )
            else:
                # Non-verbose mode: capture output and only show on error
                configure_result = subprocess.run(
                    configure_cmd,
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                    timeout=min(self._runtime_options.get("test_timeout", 300), 120),
                    check=False,
                )

            if configure_result.returncode != 0:
                self._logger.error("CMake configure failed with exit code %d", configure_result.returncode)
                # Show error output in non-verbose mode
                if not verbose and configure_result.stderr:
                    self._logger.error("CMake errors:\n%s", configure_result.stderr)
                return {
                    "success": False,
                    "output": f"CMake configure failed (exit code {configure_result.returncode})",
                    "duration": time.time() - start_time,
                }

            # Build with make/ninja
            parallel_jobs = self._runtime_options.get("build_parallel_jobs", "auto")
            if parallel_jobs == "auto":
                parallel_jobs = min(os.cpu_count() or 1, 4)  # Limit to 4 jobs max

            build_cmd = ["cmake", "--build", ".", "--parallel", str(parallel_jobs)]
            self._logger.info("Running CMake build: %s", " ".join(build_cmd))

            # Conditional output capture based on verbose flag (gwgen2 pattern)
            if verbose:
                # Verbose mode: stream output to console in real-time
                build_result = subprocess.run(
                    build_cmd,
                    cwd=build_dir,
                    timeout=self._runtime_options.get("test_timeout", 300),
                    check=False,
                )
            else:
                # Non-verbose mode: capture output and only show on error
                build_result = subprocess.run(
                    build_cmd,
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                    timeout=self._runtime_options.get("test_timeout", 300),
                    check=False,
                )

            duration = time.time() - start_time

            if build_result.returncode != 0:
                self._logger.error("Build failed with exit code %d", build_result.returncode)
                # Show error output in non-verbose mode
                if not verbose:
                    # Show last 20 lines of build output for errors
                    if build_result.stderr:
                        stderr_lines = build_result.stderr.strip().split("\n")[-20:]
                        self._logger.error("Build errors:\n%s", "\n".join(stderr_lines))
                    if build_result.stdout:
                        stdout_lines = build_result.stdout.strip().split("\n")[-20:]
                        self._logger.error("Build output:\n%s", "\n".join(stdout_lines))
                return {
                    "success": False,
                    "output": f"Build failed (exit code {build_result.returncode})",
                    "duration": duration,
                }

            self._logger.info("Build successful (%.2fs)", duration)
            return {"success": True, "output": "Build successful", "duration": duration}

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "Build timed out",
                "duration": time.time() - start_time,
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {
                "success": False,
                "output": f"Build error: {str(e)}",
                "duration": time.time() - start_time,
            }

    def _run_test(self, build_dir: Path, test_name: str) -> Dict[str, Any]:
        """
        Run the test using CTest with fallback to direct execution.

        Implements gwgen2-inspired robust execution with CTest fallback.

        Args:
            build_dir: CMake build directory
            test_name: Name of the test

        Returns:
            Dictionary with 'success', 'output', 'duration'
        """
        self._logger.info("Running test: %s", test_name)
        start_time = time.time()

        try:
            # Run with CTest for better output formatting
            test_cmd = ["ctest", "--output-on-failure", "--verbose"]
            self._logger.info("Running GTest: %s", " ".join(test_cmd))

            # Conditional output capture based on verbose flag (gwgen2 pattern)
            verbose = self._runtime_options.get("verbose", False)
            if verbose:
                # Verbose mode: stream output to console in real-time
                test_result = subprocess.run(
                    test_cmd,
                    cwd=build_dir,
                    timeout=self._runtime_options.get("test_timeout", 300),
                    check=False,
                )
            else:
                # Non-verbose mode: capture output and only show on failure
                test_result = subprocess.run(
                    test_cmd,
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                    timeout=self._runtime_options.get("test_timeout", 300),
                    check=False,
                )

            duration = time.time() - start_time

            # CTest returns 0 if all tests pass
            success = test_result.returncode == 0

            if success:
                self._logger.info("✓ Test %s passed (%.2fs)", test_name, duration)
            else:
                self._logger.error("✗ Test %s failed (%.2fs)", test_name, duration)
                # Show test failure output in non-verbose mode
                if not verbose and hasattr(test_result, "stdout") and test_result.stdout:
                    # Show only the relevant test failure output
                    output_lines = test_result.stdout.strip().split("\n")[-30:]  # Last 30 lines
                    self._logger.error("Test failure output:\n%s", "\n".join(output_lines))

            return {"success": success, "output": "Test output shown above", "duration": duration}

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "Test execution timed out",
                "duration": time.time() - start_time,
            }
        except FileNotFoundError:
            # CTest not found - try direct execution (gwgen2 fallback pattern)
            self._logger.warning("CTest not found, trying direct execution")
            return self._run_test_direct(build_dir, test_name, start_time)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {
                "success": False,
                "output": f"Test execution error: {str(e)}",
                "duration": time.time() - start_time,
            }

    def _run_test_direct(self, build_dir: Path, test_name: str, start_time: float) -> Dict[str, Any]:
        """
        Run test executable directly (fallback when CTest unavailable).

        Inspired by gwgen2's robust execution approach.

        Args:
            build_dir: CMake build directory
            test_name: Name of the test
            start_time: Test start time

        Returns:
            Dictionary with 'success', 'output', 'duration'
        """
        try:
            # Find the test executable
            test_executable = build_dir / test_name
            if not test_executable.exists():
                # Try common variations
                for variant in [f"test_{test_name}", f"{test_name}_test"]:
                    candidate = build_dir / variant
                    if candidate.exists() and os.access(candidate, os.X_OK):
                        test_executable = candidate
                        break

            if not test_executable.exists():
                return {
                    "success": False,
                    "output": f"Test executable not found: {test_executable}",
                    "duration": time.time() - start_time,
                }

            # Conditional output capture based on verbose flag (gwgen2 pattern)
            verbose = self._runtime_options.get("verbose", False)
            if verbose:
                # Verbose mode: stream output to console in real-time
                test_result = subprocess.run(
                    [str(test_executable)],
                    cwd=build_dir,
                    timeout=self._runtime_options.get("test_timeout", 300),
                    check=False,
                )
            else:
                # Non-verbose mode: capture output and only show on failure
                test_result = subprocess.run(
                    [str(test_executable)],
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                    timeout=self._runtime_options.get("test_timeout", 300),
                    check=False,
                )

            duration = time.time() - start_time
            success = test_result.returncode == 0

            # Show failure output in non-verbose mode
            if not success and not verbose and hasattr(test_result, "stdout") and test_result.stdout:
                output_lines = test_result.stdout.strip().split("\n")[-30:]
                self._logger.error("Test failure output:\n%s", "\n".join(output_lines))

            return {"success": success, "output": "Test output shown above", "duration": duration}

        except Exception as e:  # pylint: disable=broad-exception-caught
            return {
                "success": False,
                "output": f"Direct execution error: {str(e)}",
                "duration": time.time() - start_time,
            }

    def _generate_coverage(self, build_dir: Path) -> Dict[str, Any]:
        """
        Generate code coverage report using lcov.

        Args:
            build_dir: CMake build directory

        Returns:
            Dictionary with 'success', 'summary', 'report_path'
        """
        self._logger.info("Generating coverage report")

        try:
            # Check if lcov is available
            lcov_check = subprocess.run(["which", "lcov"], capture_output=True, text=True, check=False)
            if lcov_check.returncode != 0:
                self._logger.warning("lcov not found, skipping coverage generation")
                return {"success": False, "summary": "lcov not available"}

            # Run the coverage target (defined in CMakeLists.txt.j2)
            coverage_cmd = ["make", "test_coverage"]
            self._logger.debug("Running: %s", " ".join(coverage_cmd))

            coverage_result = subprocess.run(
                coverage_cmd, cwd=build_dir, capture_output=True, text=True, timeout=300, check=False
            )

            if coverage_result.returncode != 0:
                self._logger.warning("Coverage generation failed: %s", coverage_result.stderr)
                return {"success": False, "summary": "Coverage generation failed"}

            # Extract coverage summary from lcov output
            coverage_summary = self._parse_coverage_output(coverage_result.stdout)

            report_path = build_dir / "coverage_report" / "index.html"
            self._logger.info("Coverage report generated: file://%s", report_path)

            return {"success": True, "summary": coverage_summary, "report_path": str(report_path)}

        except subprocess.TimeoutExpired:
            return {"success": False, "summary": "Coverage generation timed out"}
        except Exception as e:  # pylint: disable=broad-exception-caught
            self._logger.warning("Coverage generation error: %s", e)
            return {"success": False, "summary": str(e)}

    def _parse_coverage_output(self, output: str) -> str:
        """
        Parse lcov output to extract coverage summary.

        Args:
            output: lcov command output

        Returns:
            Coverage summary string (e.g., "Lines: 85.3%, Functions: 92.1%")
        """
        lines_coverage = None
        functions_coverage = None

        for line in output.split("\n"):
            if "lines......" in line:
                # Extract percentage from line like: "  lines......: 85.3% (123 of 144 lines)"
                parts = line.split(":")
                if len(parts) >= 2:
                    lines_coverage = parts[1].strip().split()[0]
            elif "functions.." in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    functions_coverage = parts[1].strip().split()[0]

        if lines_coverage and functions_coverage:
            return f"Lines: {lines_coverage}, Functions: {functions_coverage}"
        if lines_coverage:
            return f"Lines: {lines_coverage}"
        return "Coverage data not available"

    def cleanup(self, output_dir: Path) -> None:
        """
        Clean up validation artifacts.

        This is the public interface for cleanup (implements BaseValidator abstract method).
        Respects the keep_build_artifacts configuration option.

        Uses git root detection to find workspace location (gwgen2 pattern).

        Args:
            output_dir: Directory where validation was run (used to detect git root)
        """
        # Only clean up if keep_build_artifacts is False
        if not self._runtime_options.get("keep_build_artifacts", True):
            # Auto-detect workspace location using git root (same logic as setup)
            git_root = self._find_git_root(output_dir)

            # Determine workspace base (same logic as setup)
            if git_root == output_dir.resolve():
                # Not in a git repo - use output_dir itself as workspace base
                workspace_base = output_dir
            else:
                # In a git repo - use git root as workspace base
                workspace_base = git_root

            # Clean up workspace
            workspace_path = workspace_base / self.DEFAULT_WORKSPACE_DIR
            if workspace_path.exists():
                self._cleanup(workspace_path)

    def _cleanup(self, isolated_dir: Path) -> None:
        """
        Clean up isolated build environment.

        Args:
            isolated_dir: Isolated environment directory to remove
        """
        try:
            if isolated_dir.exists():
                self._logger.debug("Cleaning up: %s", isolated_dir)
                shutil.rmtree(isolated_dir)
        except (OSError, PermissionError) as e:
            self._logger.warning("Failed to clean up %s: %s", isolated_dir, e)

    def _create_failure_result(  # pylint: disable=too-many-arguments
        self, *, test_name: str, target: Path, message: str, details: str, duration: float
    ) -> ValidationResult:
        """
        Create a failure ValidationResult.

        Args:
            test_name: Name of the test
            target: Test file path
            message: Failure message
            details: Detailed error information
            duration: Validation duration

        Returns:
            ValidationResult indicating failure
        """
        return ValidationResult(
            validator_name=self.config.name,
            target_name=test_name,
            success=False,
            message=message,
            details=details,
            file_path=target,
            errors=[message],
            duration_seconds=duration,
        )
