"""
CMake template manager for isolated test environments.

This module manages CMake templates for running Google Tests independently
of the generated project's build system.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pytemplify.renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class CMakeTemplateManager:
    """
    Manages CMake templates for isolated test environments (SOLID: SRP).

    Responsibilities:
        - Load CMake templates
        - Render CMake files with test configuration
        - Manage template versions
        - Auto-detect project structure

    DRY Principle:
        - Reuses pytemplify's TemplateRenderer for rendering
    """

    # Template files (DRY: single source of truth)
    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates" / "gtest"
    MAIN_TEMPLATE = "CMakeLists.txt.j2"

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize CMake template manager.

        Args:
            template_dir: Custom template directory (default: built-in)

        Raises:
            FileNotFoundError: If template directory doesn't exist
        """
        self.template_dir = template_dir or self.DEFAULT_TEMPLATE_DIR

        if not self.template_dir.exists():
            raise FileNotFoundError(f"CMake template directory not found: {self.template_dir}")

        self._logger = logging.getLogger(f"{__name__}.CMakeTemplateManager")
        self._logger.debug("CMakeTemplateManager initialized with template dir: %s", self.template_dir)

    def render_cmake_file(self, test_name: str, test_file: Path, output_path: Path, **template_vars) -> None:
        """
        Render CMakeLists.txt for a test.

        DRY: Reuses existing TemplateRenderer.

        Args:
            test_name: Name of the test
            test_file: Path to test file (can be relative to output_path parent)
            output_path: Where to write CMakeLists.txt
            **template_vars: Additional template variables

        Raises:
            FileNotFoundError: If template file doesn't exist
            TemplateRendererException: If rendering fails
        """
        # Prepare template data
        data = {
            "test_name": test_name,
            "test_file": str(test_file),
            **template_vars,
        }

        # Render template (DRY: reuse TemplateRenderer)
        renderer = TemplateRenderer(data)
        template_path = self.template_dir / self.MAIN_TEMPLATE

        if not template_path.exists():
            raise FileNotFoundError(f"CMake template not found: {template_path}")

        self._logger.debug("Rendering CMake template: %s", template_path)
        rendered = renderer.render_file(template_path)

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")

        self._logger.info("Generated CMakeLists.txt: %s", output_path)

    def create_test_config(self, test_dir: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create test configuration from options and test directory structure.

        This method auto-detects common project structures and builds
        the configuration for CMake template rendering.

        Args:
            test_dir: Test directory (where test file is located)
            options: Validator options from YAML config

        Returns:
            Template variables for CMake rendering
        """
        # Auto-detect source patterns
        source_patterns = self._detect_source_patterns(test_dir, options)

        # Auto-detect include directories
        include_dirs = self._detect_include_dirs(test_dir, options, source_patterns)

        # Build configuration
        config = {
            # C++ settings
            "cxx_standard": options.get("cxx_standard", 17),
            "policy_cmp0135": True,  # GoogleTest FetchContent policy
            "policy_cmp0105": True,  # Suppress cmake_minimum_required warnings
            # GoogleTest settings
            "gtest_version": options.get("gtest_version", "v1.15.2"),
            # Platform settings
            "disable_windows": options.get("disable_windows", False),
            # CMake definitions
            "cmake_definitions": options.get("cmake_definitions", ["UNIT_TEST_BUILD=1"]),
            # Source files and includes
            "source_patterns": source_patterns,
            "include_dirs": include_dirs,
            # Linking
            "link_libraries": options.get("link_libraries", ["dl"]),
            # Compiler flags
            "extra_compile_flags": options.get("compile_flags", []),
            "warnings_as_errors": options.get("warnings_as_errors", False),
            # Coverage
            "enable_coverage": options.get("enable_coverage", True),
        }

        self._logger.debug(
            "Created test config: %d source patterns, %d include dirs",
            len(source_patterns),
            len(include_dirs),
        )

        return config

    def _detect_source_patterns(self, test_dir: Path, options: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Auto-detect source file patterns based on common project structures.

        Common patterns:
            - test/stub/*.cpp (stub implementations)
            - ../src/*.cpp (source files relative to test dir)
            - ../../../src/*.cpp (nested test structure)

        Args:
            test_dir: Test directory
            options: User options (can override auto-detection)

        Returns:
            List of source pattern dictionaries with 'name' and 'path' keys
        """
        patterns = []

        # User-specified patterns take precedence
        if "source_patterns" in options:
            patterns.extend(options["source_patterns"])
            self._logger.debug("Using %d user-specified source patterns", len(patterns))
            return patterns

        # Auto-detect common patterns
        # Pattern 1: stub directory (common in test structures)
        # Can be either sibling (../stub) or child (stub)
        stub_dir_sibling = test_dir.parent / "stub"
        stub_dir_child = test_dir / "stub"

        if stub_dir_child.exists():
            patterns.append({"name": "STUB", "path": "stub/*.cpp"})
            self._logger.debug("Detected stub directory (child): %s", stub_dir_child)
        elif stub_dir_sibling.exists():
            patterns.append({"name": "STUB", "path": "../stub/*.cpp"})
            self._logger.debug("Detected stub directory (sibling): %s", stub_dir_sibling)

        # Pattern 2: src directory at same level as test
        src_dir = test_dir.parent / "src"
        if src_dir.exists():
            patterns.append({"name": "SRC", "path": "../src/*.cpp"})
            self._logger.debug("Detected src directory: %s", src_dir)

        # Pattern 3: src directory two levels up (test/unit/stub structure)
        src_dir_up2 = test_dir.parent.parent / "src"
        if src_dir_up2.exists() and not src_dir.exists():
            patterns.append({"name": "SRC", "path": "../../src/*.cpp"})
            self._logger.debug("Detected src directory (2 levels up): %s", src_dir_up2)

        # Pattern 4: src directory three levels up (test/unit/test_X structure)
        src_dir_up3 = test_dir.parent.parent.parent / "src"
        if src_dir_up3.exists() and not src_dir.exists() and not src_dir_up2.exists():
            patterns.append({"name": "SRC", "path": "../../../src/*.cpp"})
            self._logger.debug("Detected src directory (3 levels up): %s", src_dir_up3)

        # Pattern 5: source files in same directory as test files
        # Look for *.cpp files in the test directory (but not *_test.cpp files)
        test_cpp_files = list(test_dir.glob("*.cpp"))
        test_files_to_exclude = {"test_", "*_test"}

        for cpp_file in test_cpp_files:
            exclude = False
            for exclude_pattern in test_files_to_exclude:
                if exclude_pattern in cpp_file.name:
                    exclude = True
                    break
            if not exclude:
                # Add specific file pattern relative to build directory
                rel_path = f"../{cpp_file.name}"
                patterns.append({"name": cpp_file.stem.upper(), "path": rel_path})
                self._logger.debug("Detected source file: %s", rel_path)

        if not patterns:
            self._logger.warning("No source files detected for %s", test_dir)

        return patterns

    def _detect_include_dirs(
        self, test_dir: Path, options: Dict[str, Any], source_patterns: Optional[List[Dict[str, str]]] = None
    ) -> List[str]:
        """
        Auto-detect include directories based on common project structures.

        Common patterns:
            - ../inc or ../include (headers relative to test dir)
            - ../stub (stub headers)
            - ../../../inc (nested structure)

        Args:
            test_dir: Test directory
            options: User options (can override auto-detection)

        Returns:
            List of include directory paths (relative to build directory)
        """
        include_dirs = []

        # User-specified includes take precedence
        if "include_dirs" in options:
            include_dirs.extend(options["include_dirs"])
            self._logger.debug("Using %d user-specified include directories", len(include_dirs))
            return include_dirs

        # Auto-detect common patterns
        # Pattern 1: stub directory (can be child or sibling)
        stub_dir_child = test_dir / "stub"
        stub_dir_sibling = test_dir.parent / "stub"

        if stub_dir_child.exists():
            include_dirs.append("stub")
            self._logger.debug("Detected stub include (child): %s", stub_dir_child)
        elif stub_dir_sibling.exists():
            include_dirs.append("../stub")
            self._logger.debug("Detected stub include (sibling): %s", stub_dir_sibling)

        # Pattern 2: inc directory at same level as test
        inc_dir = test_dir.parent / "inc"
        if inc_dir.exists():
            include_dirs.append("../inc")
            self._logger.debug("Detected inc directory: %s", inc_dir)

        # Pattern 3: include directory at same level as test
        include_dir = test_dir.parent / "include"
        if include_dir.exists():
            include_dirs.append("../include")
            self._logger.debug("Detected include directory: %s", include_dir)

        # Pattern 4: inc directory two levels up
        inc_dir_up2 = test_dir.parent.parent / "inc"
        if inc_dir_up2.exists() and not inc_dir.exists():
            include_dirs.append("../../inc")
            self._logger.debug("Detected inc directory (2 levels up): %s", inc_dir_up2)

        # Pattern 5: inc directory three levels up
        inc_dir_up3 = test_dir.parent.parent.parent / "inc"
        if inc_dir_up3.exists() and not inc_dir.exists() and not inc_dir_up2.exists():
            include_dirs.append("../../../inc")
            self._logger.debug("Detected inc directory (3 levels up): %s", inc_dir_up3)

        # Pattern 6: header files in same directory as test files
        test_h_files = list(test_dir.glob("*.h")) + list(test_dir.glob("*.hpp"))
        if test_h_files:
            include_dirs.append("..")
            self._logger.debug("Detected header files in parent directory, adding '..' to includes")

        # If no include dirs detected but source files were found in parent, add parent
        if not include_dirs and source_patterns:
            # Check if any pattern points to parent directory
            for pattern in source_patterns:
                if pattern["path"].startswith("../"):
                    include_dirs.append("..")
                    self._logger.debug("Adding parent directory to includes for source files")
                    break

        if not include_dirs:
            self._logger.warning("No include directories detected for %s", test_dir)

        return include_dirs

    def validate_template(self, template_name: str = MAIN_TEMPLATE) -> bool:
        """
        Validate that a template exists and is readable.

        Args:
            template_name: Name of the template file

        Returns:
            True if template is valid

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        if not template_path.is_file():
            raise ValueError(f"Template is not a file: {template_path}")

        # Try to read template
        try:
            template_path.read_text(encoding="utf-8")
            return True
        except Exception as e:
            raise ValueError(f"Cannot read template {template_path}: {e}") from e
