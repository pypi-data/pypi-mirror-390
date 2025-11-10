"""Manual section backup and restore utility for pytemplify.

This script provides command-line interface for backing up and restoring
manual sections from generated template files, supporting template development
workflows where manual sections need to be preserved across regenerations.

Usage:
    manual-sections backup <source> [--output FILE] [--recursive]
    manual-sections restore <backup> <target> [--preview] [--sections IDS]
    manual-sections view <backup> [--file PATH] [--section ID]
    manual-sections report <backup> [--output FILE] [--format FORMAT]
"""

import argparse
import base64
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from pytemplify.exceptions import ManualSectionError
from pytemplify.manual_sections import ManualSectionManager


class BackupFormat:
    """Handles JSON backup format with base64 encoding."""

    FORMAT_VERSION = "1.0"

    @staticmethod
    def encode_content(content: str) -> str:
        """Encode content to base64."""
        return base64.b64encode(content.encode("utf-8")).decode("ascii")

    @staticmethod
    def decode_content(encoded_content: str) -> str:
        """Decode content from base64."""
        return base64.b64decode(encoded_content.encode("ascii")).decode("utf-8")

    @staticmethod
    def create_backup_structure(
        source_path: Path, source_type: str, recursive: bool, sections_data: Dict[str, List[Dict]]
    ) -> Dict:
        """Create the complete backup structure."""
        total_files = len(sections_data)
        total_sections = sum(len(sections) for sections in sections_data.values())

        # Store source_path as relative to current working directory for portability
        try:
            # Convert to absolute first, then make relative to cwd
            absolute_path = source_path.absolute()
            relative_path = absolute_path.relative_to(Path.cwd())
            source_path_str = str(relative_path)
        except ValueError:
            # If path is not relative to cwd (e.g., on different drive on Windows),
            # fall back to absolute path
            source_path_str = str(source_path.absolute())

        return {
            "format_version": BackupFormat.FORMAT_VERSION,
            "backup": {
                "metadata": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source_type": source_type,
                    "source_path": source_path_str,
                    "recursive": recursive,
                    "total_files": total_files,
                    "total_sections": total_sections,
                    "pytemplify_version": "0.2.2",  # Should be dynamic
                },
                "sections": sections_data,
            },
        }

    @staticmethod
    def save_backup(backup_data: Dict, output_path: Path) -> None:
        """Save backup data to JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_backup(backup_path: Path) -> Dict:
        """Load backup data from JSON file."""
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ManualSectionError(str(backup_path), 0, f"Failed to load backup: {e}")

    @staticmethod
    def validate_backup(backup_data: Dict) -> None:
        """Validate backup structure and format."""
        if "format_version" not in backup_data:
            raise ManualSectionError("backup", 0, "Invalid backup format: missing format_version")

        if backup_data["format_version"] != BackupFormat.FORMAT_VERSION:
            raise ManualSectionError(
                "backup",
                0,
                f"Unsupported format version: {backup_data['format_version']} "
                f"(expected {BackupFormat.FORMAT_VERSION})",
            )

        if "backup" not in backup_data or "sections" not in backup_data["backup"]:
            raise ManualSectionError("backup", 0, "Invalid backup format: missing sections")


class ManualSectionBackup:
    """Core backup and restore functionality."""

    def __init__(self):
        self.manager = ManualSectionManager()

    def _perform_restore(
        self,
        backup_data: Dict,
        target_path: Path,
        section_filters: Optional[List[str]] = None,
        file_filters: Optional[List[str]] = None,
        section_map: Optional[Dict[str, str]] = None,
        verbose: bool = False,
    ) -> None:
        """Perform the actual restoration of manual sections."""
        sections = backup_data["backup"]["sections"]
        restored_count = 0

        for filename, file_sections in sections.items():
            # Apply file filters
            if file_filters and not any(Path(filename).match(pattern) for pattern in file_filters):
                continue

            # If target_path is a file, use it directly; otherwise, construct path using filename
            if target_path.is_file():
                target_file = target_path
            else:
                target_file = target_path / filename
                target_file.parent.mkdir(parents=True, exist_ok=True)

            # Read existing content or create empty file
            try:
                content = target_file.read_text(encoding="utf-8")
            except (IOError, FileNotFoundError):
                content = ""

            # Process each section for this file
            for section in file_sections:
                section_id = section["id"]

                # Apply section filters
                if section_filters and section_id not in section_filters:
                    continue

                # Apply section mapping
                final_section_id = section_map.get(section_id, section_id) if section_map else section_id

                # Decode section content (this is ONLY the content between markers, no markers included)
                section_content = BackupFormat.decode_content(section["content"])

                # Check if section exists in target
                if self.manager.section_exists(content, final_section_id):
                    # Section exists - replace its content while preserving marker formatting
                    # Use content as-is - it already has the proper format including closing markers
                    content = self.manager.replace_section_content(content, final_section_id, section_content)
                else:
                    # Section doesn't exist - add it with plain markers (no comment prefix)
                    # The backup content is already cleaned by extract_section_content() during backup
                    full_section = (
                        f"{self.manager.MANUAL_SECTION_START}: {final_section_id}\n"
                        f"{section_content}\n"
                        f"{self.manager.MANUAL_SECTION_END}"
                    )

                    # Add new section at the end
                    if content and not content.endswith("\n"):
                        content += "\n"
                    content += full_section

                restored_count += 1
                if verbose:
                    logging.info(f"Restored section '{final_section_id}' to {target_file}")

            # Write the updated content back to file
            target_file.write_text(content, encoding="utf-8")

        logging.info(f"Restoration completed: {restored_count} sections restored")

    def backup_file(self, file_path: Path, base_path: Optional[Path] = None) -> List[Dict]:
        """Extract manual sections from a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except (IOError, UnicodeDecodeError) as e:
            logging.warning(f"Skipping {file_path}: {e}")
            return []

        sections = self.manager.extract_sections(content)
        if not sections:
            return []

        result = []
        for section_id, full_content in sections.items():
            # Use the centralized extract_section_content method
            section_content = self.manager.extract_section_content(full_content)
            if section_content and not section_content.isspace():
                # Count actual lines (including empty lines between content)
                actual_lines = len(section_content.split("\n")) if section_content else 0
                result.append(
                    {
                        "id": section_id,
                        "content": BackupFormat.encode_content(section_content),
                        "encoding": "base64",
                        "line_count": actual_lines,
                        "char_count": len(section_content),
                    }
                )

        return result

    def backup_directory(
        self,
        dir_path: Path,
        recursive: bool = True,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict]]:
        """Backup manual sections from directory."""
        sections_data = {}

        def should_include_file(file_path: Path) -> bool:
            """Check if file should be included based on patterns."""
            if include_patterns:
                included = any(file_path.match(pattern) for pattern in include_patterns)
                if not included:
                    return False

            if exclude_patterns:
                excluded = any(file_path.match(pattern) for pattern in exclude_patterns)
                if excluded:
                    return False

            return True

        if recursive:
            files = list(dir_path.rglob("*"))
        else:
            files = list(dir_path.iterdir())

        for item in files:
            if item.is_file() and should_include_file(item):
                sections = self.backup_file(item)
                if sections:
                    # Store just the filename, not the full relative path
                    sections_data[item.name] = sections

        return sections_data

    def create_backup(
        self,
        source: Path,
        output: Path,
        recursive: bool = True,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> None:
        """Create a complete backup."""
        if source.is_file():
            source_type = "file"
            sections_data = {source.name: self.backup_file(source)}
        elif source.is_dir():
            source_type = "folder"
            sections_data = self.backup_directory(source, recursive, include_patterns, exclude_patterns)
        else:
            raise ManualSectionError(str(source), 0, f"Source not found: {source}")

        backup_data = BackupFormat.create_backup_structure(source, source_type, recursive, sections_data)

        BackupFormat.save_backup(backup_data, output)
        logging.info(
            f"Backup created: {output} ({len(sections_data)} files, "
            f"{sum(len(s) for s in sections_data.values())} sections)"
        )


class PreviewEngine:
    """Generates preview of restore operations."""

    def __init__(self, backup_data: Dict):
        self.backup_data = backup_data
        self.sections = backup_data["backup"]["sections"]

    def generate_preview(
        self,
        target_path: Path,
        section_filters: Optional[List[str]] = None,
        file_filters: Optional[List[str]] = None,
        section_map: Optional[Dict[str, str]] = None,
    ) -> str:
        """Generate preview of what would be restored."""
        lines = []
        lines.append("Preview: Restoring manual sections")
        lines.append("=" * 50)

        metadata = self.backup_data["backup"]["metadata"]
        lines.append(f"Source: {metadata['source_path']}")
        lines.append(f"Created: {metadata['created_at']}")
        lines.append(f"Total sections: {metadata['total_sections']}")
        lines.append("")

        # Analyze what will happen
        changes = self._analyze_changes(target_path, section_filters, file_filters, section_map)

        if not changes:
            lines.append("No sections to restore.")
            return "\n".join(lines)

        lines.append("Files to be modified:")
        for file_path, file_changes in changes.items():
            lines.append(f"  {file_path}/")
            for change in file_changes:
                action = "add" if change["action"] == "add" else "replace"
                lines.append(f"    ├── {change['section_id']} ({change['line_count']} lines) -> will {action}")

        total_files = len(changes)
        total_sections = sum(len(changes[f]) for f in changes)
        lines.append("")
        lines.append(f"Summary: {total_files} files, {total_sections} sections will be modified")

        return "\n".join(lines)

    def _analyze_changes(
        self,
        target_path: Path,
        section_filters: Optional[List[str]] = None,
        file_filters: Optional[List[str]] = None,
        section_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, List[Dict]]:
        """Analyze what changes would occur during restore."""
        changes = {}

        for rel_path, sections in self.sections.items():
            # Apply file filters
            if file_filters and not any(Path(rel_path).match(pattern) for pattern in file_filters):
                continue

            target_file = target_path / rel_path
            # For preview, we show what WOULD happen even if target file doesn't exist yet
            # This allows users to see the impact before creating target files

            file_changes = []
            for section in sections:
                section_id = section["id"]

                # Apply section filters
                if section_filters and section_id not in section_filters:
                    continue

                # Apply section mapping
                final_section_id = section_map.get(section_id, section_id) if section_map else section_id

                # Check if section exists in target
                try:
                    content = target_file.read_text(encoding="utf-8")
                    existing_sections = ManualSectionManager().extract_sections(content)
                    action = "replace" if final_section_id in existing_sections else "add"
                except (IOError, UnicodeDecodeError):
                    # If file doesn't exist or can't be read, assume we need to create it
                    action = "add"

                file_changes.append(
                    {"section_id": final_section_id, "line_count": section["line_count"], "action": action}
                )

            if file_changes:
                changes[rel_path] = file_changes

        return changes


class ReportGenerator:
    """Generates human-readable reports from backup data."""

    def __init__(self, backup_data: Dict):
        self.backup_data = backup_data
        self.sections = backup_data["backup"]["sections"]

    def generate_markdown_report(
        self,
        section_filters: Optional[List[str]] = None,
        file_filters: Optional[List[str]] = None,
        max_lines: Optional[int] = None,
        include_content: bool = True,
    ) -> str:
        """Generate markdown report."""
        lines = []
        metadata = self.backup_data["backup"]["metadata"]

        lines.append("# Manual Sections Backup Report")
        lines.append(f"**Created:** {metadata['created_at']}")
        lines.append(
            f"**Source:** {metadata['source_path']} ({'recursive' if metadata['recursive'] else 'non-recursive'})"
        )
        lines.append(f"**Total Sections:** {metadata['total_sections']}")
        lines.append("")

        for file_path, sections in self.sections.items():
            # Apply file filters
            if file_filters and not any(Path(file_path).match(pattern) for pattern in file_filters):
                continue

            lines.append(f"## File: {file_path}")

            for section in sections:
                section_id = section["id"]

                # Apply section filters
                if section_filters and section_id not in section_filters:
                    continue

                lines.append(f"### Section: {section_id} ({section['line_count']} lines)")

                if include_content:
                    try:
                        content = BackupFormat.decode_content(section["content"])
                        if max_lines and section["line_count"] > max_lines:
                            content_lines = content.split("\n")
                            if len(content_lines) > max_lines:
                                content_lines = content_lines[:max_lines]
                                content = (
                                    "\n".join(content_lines) + f"\n... ({section['line_count'] - max_lines} more lines)"
                                )
                    except Exception:
                        content = "[Error decoding content]"

                    lines.append("```")
                    lines.append(content)
                    lines.append("```")

                lines.append("")

        return "\n".join(lines)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manual section backup and restore utility for pytemplify",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup
  manual-sections backup ./generated/ --recursive --output backup.json
  manual-sections backup single_file.py --output backup.json

  # Restore with preview
  manual-sections restore backup.json ./generated/ --preview
  manual-sections restore backup.json ./new_location/ --section-map "old_id:new_id"

  # View sections
  manual-sections view backup.json --summary
  manual-sections view backup.json --file "utils.py" --section "helpers"

  # Generate reports
  manual-sections report backup.json --output report.md
  manual-sections report backup.json --format markdown --sections "imports,constants"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create backup of manual sections")
    backup_parser.add_argument("source", type=Path, help="Source file or directory")
    backup_parser.add_argument(
        "--output", "-o", type=Path, default=Path("manual_sections_backup.json"), help="Output backup file"
    )
    backup_parser.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirectories")
    backup_parser.add_argument("--include", action="append", help="Include file pattern (can be used multiple times)")
    backup_parser.add_argument("--exclude", action="append", help="Exclude file pattern (can be used multiple times)")
    backup_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore manual sections from backup")
    restore_parser.add_argument("backup", type=Path, help="Backup file")
    restore_parser.add_argument("target", type=Path, help="Target file or directory")
    restore_parser.add_argument("--preview", action="store_true", help="Show preview without making changes")
    restore_parser.add_argument("--sections", help="Comma-separated list of section IDs to restore")
    restore_parser.add_argument("--files", help="File pattern to restore")
    restore_parser.add_argument("--section-map", action="append", help="Map old section ID to new ID (format: old:new)")
    restore_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # View command
    view_parser = subparsers.add_parser("view", help="View backup contents")
    view_parser.add_argument("backup", type=Path, help="Backup file")
    view_parser.add_argument("--file", help="Show sections for specific file")
    view_parser.add_argument("--section", help="Show specific section content")
    view_parser.add_argument("--summary", action="store_true", help="Show backup summary only")
    view_parser.add_argument("--list", action="store_true", help="List all files and sections")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate human-readable report")
    report_parser.add_argument("backup", type=Path, help="Backup file")
    report_parser.add_argument("--output", "-o", type=Path, help="Output file (default: stdout)")
    report_parser.add_argument("--format", choices=["markdown", "text"], default="markdown", help="Report format")
    report_parser.add_argument("--sections", help="Include only specific sections (comma-separated)")
    report_parser.add_argument("--files", help="Include only matching files (glob pattern)")
    report_parser.add_argument("--max-lines", type=int, help="Truncate sections longer than N lines")
    report_parser.add_argument("--summary-only", action="store_true", help="Generate summary report only")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Setup logging
    level = logging.DEBUG if getattr(args, "verbose", False) else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    try:
        if args.command == "backup":
            backup = ManualSectionBackup()
            backup.create_backup(args.source, args.output, args.recursive, args.include, args.exclude)

        elif args.command == "restore":
            backup_data = BackupFormat.load_backup(args.backup)
            BackupFormat.validate_backup(backup_data)

            if args.preview:
                preview = PreviewEngine(backup_data)
                section_filters = args.sections.split(",") if args.sections else None
                file_filters = [args.files] if args.files else None
                section_map = {}
                if args.section_map:
                    for mapping in args.section_map:
                        old_id, new_id = mapping.split(":", 1)
                        section_map[old_id] = new_id

                print(preview.generate_preview(args.target, section_filters, file_filters, section_map))
            else:
                # Implement actual restore functionality
                section_filters = args.sections.split(",") if args.sections else None
                file_filters = [args.files] if args.files else None
                section_map = {}
                if args.section_map:
                    for mapping in args.section_map:
                        old_id, new_id = mapping.split(":", 1)
                        section_map[old_id] = new_id

                backup = ManualSectionBackup()
                backup._perform_restore(
                    backup_data, args.target, section_filters, file_filters, section_map, args.verbose
                )

        elif args.command == "view":
            backup_data = BackupFormat.load_backup(args.backup)
            BackupFormat.validate_backup(backup_data)

            if args.summary:
                metadata = backup_data["backup"]["metadata"]
                print(f"Backup Summary:")
                print(f"  Created: {metadata['created_at']}")
                print(f"  Source: {metadata['source_path']}")
                print(f"  Files: {metadata['total_files']}")
                print(f"  Sections: {metadata['total_sections']}")
            elif args.list:
                print("Files with manual sections:")
                for file_path in backup_data["backup"]["sections"]:
                    sections = backup_data["backup"]["sections"][file_path]
                    print(f"  {file_path} ({len(sections)} sections)")
            elif args.file and args.section:
                sections = backup_data["backup"]["sections"].get(args.file, [])
                for section in sections:
                    if section["id"] == args.section:
                        content = BackupFormat.decode_content(section["content"])
                        print(f"Section: {args.section} ({section['line_count']} lines)")
                        print("-" * 50)
                        print(content)
                        break
                else:
                    print(f"Section '{args.section}' not found in file '{args.file}'")
            else:
                print("Use --summary, --list, or specify --file and --section")

        elif args.command == "report":
            backup_data = BackupFormat.load_backup(args.backup)
            BackupFormat.validate_backup(backup_data)

            report_gen = ReportGenerator(backup_data)
            section_filters = args.sections.split(",") if args.sections else None
            file_filters = [args.files] if args.files else None

            if args.format == "markdown":
                report = report_gen.generate_markdown_report(
                    section_filters, file_filters, args.max_lines, not args.summary_only
                )
            else:
                # TODO: Implement text format
                report = "Text format not yet implemented"

            if args.output:
                args.output.write_text(report, encoding="utf-8")
                logging.info(f"Report saved to {args.output}")
            else:
                print(report)

    except ManualSectionError as e:
        logging.error(f"Manual section error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if getattr(args, "verbose", False):
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
