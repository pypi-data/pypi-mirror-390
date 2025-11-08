"""Manual section management for template rendering.

This module provides centralized functionality for handling MANUAL SECTION markers
in generated files. Manual sections allow users to preserve hand-written code between
template regenerations.

The ManualSectionManager class provides:
- Extraction of manual sections from content
- Validation of manual section structure and IDs
- Restoration of manual sections into newly generated content
"""

import re
from typing import Dict, List, Optional

from pytemplify.exceptions import ManualSectionError


class RenderContext:  # pylint: disable=too-few-public-methods
    """Context for tracking filename and line number during rendering operations.

    This is a minimal version for use in manual section operations.
    The full RenderContext is defined in renderer.py.
    """

    def __init__(self, filename: str = "", lineno: int = 1):
        self.filename = filename
        self.lineno = lineno

    def update(self, filename: Optional[str] = None, lineno: Optional[int] = None) -> None:
        """Update context with new filename or line number."""
        if filename is not None:
            self.filename = filename
        if lineno is not None:
            self.lineno = lineno


class ManualSectionManager:
    """Manager for manual section preservation in template rendering.

    This class provides a centralized implementation of manual section handling,
    eliminating code duplication between TemplateRenderer and CodeFormatter.

    Manual sections are marked with:
        MANUAL SECTION START: section_id
        ... user content ...
        MANUAL SECTION END

    The manager ensures:
    - Section IDs are valid (alphanumeric, underscore, hyphen only)
    - No duplicate section IDs
    - Proper nesting (no nested sections)
    - Complete structure (matching START/END pairs)
    - Section preservation across regenerations
    """

    # Pattern constants
    MANUAL_SECTION_START = "MANUAL SECTION START"
    MANUAL_SECTION_END = "MANUAL SECTION END"
    MANUAL_SECTION_ID = "[a-zA-Z0-9_-]+"

    # Regex patterns
    MANUAL_SECTION_PATTERN = re.compile(
        rf"{MANUAL_SECTION_START}: ({MANUAL_SECTION_ID}(?:\s|$))(.*?){MANUAL_SECTION_END}",
        re.DOTALL,
    )

    # Pattern to check for section markers (used for validation)
    MANUAL_SECTION_CHECK_PATTERN = re.compile(
        rf"{MANUAL_SECTION_START}.*?{MANUAL_SECTION_END}",
        re.DOTALL,
    )

    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extract manual sections from content.

        Args:
            content: Content to extract sections from

        Returns:
            Dictionary mapping section IDs to their full section content
            (including markers)
        """
        sections = {}
        for match in self.MANUAL_SECTION_PATTERN.finditer(content):
            section_id = match.group(1).strip()
            # Store the full match (including markers)
            sections[section_id] = match.group(0)
        return sections

    def restore_sections(self, content: str, sections: Dict[str, str]) -> str:
        """Restore manual sections into content.

        Args:
            content: Content to restore sections into
            sections: Dictionary of section ID to section content

        Returns:
            Content with manual sections restored
        """
        if not sections:
            return content

        result = content
        for section_id, original_section in sections.items():
            # Create pattern that matches the section with any content
            section_pattern = re.compile(
                rf"{self.MANUAL_SECTION_START}: {re.escape(section_id)}.*?{self.MANUAL_SECTION_END}",
                re.DOTALL,
            )
            # Replace with the original section
            result = section_pattern.sub(original_section, result)

        return result

    def check_section_ids(
        self, content: str, content_name: str = "content", context: Optional[RenderContext] = None
    ) -> List[str]:
        """Check manual section IDs for validity and duplicates.

        Args:
            content: Content to check
            content_name: Name of content for error messages
            context: Render context for error reporting

        Returns:
            List of valid section IDs found

        Raises:
            ManualSectionError: If sections have invalid IDs or duplicates
        """
        filename = context.filename if context else content_name

        # Find all possible sections (may include invalid ones)
        possible_matches = list(self.MANUAL_SECTION_CHECK_PATTERN.finditer(content))
        valid_matches = list(self.MANUAL_SECTION_PATTERN.finditer(content))

        # Check for invalid section IDs
        if len(possible_matches) != len(valid_matches):
            # Find the first invalid section
            bad_match = None
            for match in possible_matches:
                span_text = content[match.start() : match.end()]
                if not self.MANUAL_SECTION_PATTERN.search(span_text):
                    bad_match = match
                    break

            lineno = 1
            if bad_match is not None:
                lineno = content[: bad_match.start()].count("\n") + 1
            if context:
                context.update(lineno=lineno)

            raise ManualSectionError(filename, lineno, f"{content_name} has invalid section")

        # Extract section IDs
        section_ids = [match.group(1).strip() for match in valid_matches]

        # Check for duplicates
        duplicates = {sid for sid in section_ids if section_ids.count(sid) > 1}
        if duplicates:
            # Find first duplicate for error reporting
            dup_id = next(iter(duplicates))
            dup_match = None
            for match in valid_matches:
                if match.group(1).strip() == dup_id:
                    dup_match = match
                    break

            lineno = 1
            if dup_match is not None:
                lineno = content[: dup_match.start()].count("\n") + 1
            if context:
                context.update(lineno=lineno)

            raise ManualSectionError(filename, lineno, f"{content_name} has duplicated id: {duplicates}")

        return section_ids

    def check_section_structure(
        self, content: str, content_name: str = "content", context: Optional[RenderContext] = None
    ) -> None:
        """Check manual section structure for completeness and proper nesting.

        Args:
            content: Content to check
            content_name: Name of content for error messages
            context: Render context for error reporting

        Raises:
            ManualSectionError: If sections are improperly nested or incomplete
        """
        filename = context.filename if context else content_name

        # Check for nested sections
        matches = list(self.MANUAL_SECTION_CHECK_PATTERN.finditer(content))
        for match in matches:
            section = content[match.start() : match.end()]
            start_count_in_section = section.count(self.MANUAL_SECTION_START)
            end_count_in_section = section.count(self.MANUAL_SECTION_END)

            if start_count_in_section > 1 or end_count_in_section > 1:
                lineno = content[: match.start()].count("\n") + 1
                if context:
                    context.update(lineno=lineno)
                raise ManualSectionError(filename, lineno, f"Nested section in {content_name}")

        # Check for matching START/END pairs
        start_count = content.count(self.MANUAL_SECTION_START)
        end_count = content.count(self.MANUAL_SECTION_END)

        if start_count != end_count:
            # Find the position of the unmatched marker
            lineno = 1
            start_positions = [m.start() for m in re.finditer(re.escape(self.MANUAL_SECTION_START), content)]
            end_positions = [m.start() for m in re.finditer(re.escape(self.MANUAL_SECTION_END), content)]

            if start_count > end_count and start_positions:
                lineno = content[: start_positions[-1]].count("\n") + 1
            elif end_count > start_count and end_positions:
                lineno = content[: end_positions[-1]].count("\n") + 1

            if context:
                context.update(lineno=lineno)

            raise ManualSectionError(
                filename,
                lineno,
                f"Incomplete section in {content_name}: start={start_count}, end={end_count}",
            )

    def validate_sections(
        self,
        template: str,
        rendered: str,
        previous: str = "",
        context: Optional[RenderContext] = None,
    ) -> None:
        """Validate manual sections across template, rendered, and previous content.

        This performs comprehensive validation including:
        - Structure validation for all content
        - ID validation for rendered and previous content
        - Checking that no sections were lost from previous to current

        Args:
            template: Template string
            rendered: Newly rendered content
            previous: Previously rendered content (optional)
            context: Render context for error reporting

        Raises:
            ManualSectionError: If validation fails
        """
        # Validate structure of all content
        self.check_section_structure(template, "template", context)
        self.check_section_structure(rendered, "rendered", context)

        # Validate IDs in rendered content
        curr_ids = self.check_section_ids(rendered, "rendered", context)

        # If there's previous content, validate it and check for lost sections
        if previous:
            self.check_section_structure(previous, "prev_rendered", context)
            prev_ids = self.check_section_ids(previous, "prev_rendered", context)

            # Check for lost sections
            for section_id in prev_ids:
                if section_id not in curr_ids:
                    # Try to locate the missing section for better error reporting
                    lineno = 1
                    match = re.search(rf"{self.MANUAL_SECTION_START}: {re.escape(section_id)}", previous)
                    if match:
                        lineno = previous[: match.start()].count("\n") + 1
                    else:
                        # Fallback to template location
                        match2 = re.search(rf"{self.MANUAL_SECTION_START}: {re.escape(section_id)}", template)
                        if match2:
                            lineno = template[: match2.start()].count("\n") + 1

                    if context:
                        context.update(lineno=lineno)

                    filename = context.filename if context else "template"
                    raise ManualSectionError(filename, lineno, f"New template lost manual section: {section_id}")
