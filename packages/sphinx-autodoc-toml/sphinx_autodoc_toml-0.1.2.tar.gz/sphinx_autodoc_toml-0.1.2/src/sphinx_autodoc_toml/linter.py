"""Linter and formatter for TOML-Doc specification compliance.

.. spec:: The linter tool MUST validate TOML-Doc specification compliance.
   :id: S_LINT_001
   :status: planned
   :tags: linter, validation
   :links: R_LINT_001

.. spec:: The linter MUST check for Separator Rule violations.
   :id: S_LINT_003
   :status: planned
   :tags: linter, validation
   :links: R_LINT_002

.. spec:: The linter MUST check for Attachment Rule violations.
   :id: S_LINT_004
   :status: planned
   :tags: linter, validation
   :links: R_LINT_003

.. spec:: The linter MUST provide auto-formatting to fix spec violations.
   :id: S_LINT_005
   :status: planned
   :tags: linter, formatting
   :links: R_LINT_004
"""

import argparse
import sys
from pathlib import Path
from typing import List


class LintError:
    """Represents a linting error in a TOML file."""

    def __init__(self, line: int, message: str, severity: str = "error"):
        self.line = line
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        return f"L{self.line}: {self.severity.upper()}: {self.message}"


class TomlDocLinter:
    """Linter for TOML-Doc specification compliance."""

    def __init__(self, toml_path: Path):
        self.toml_path = toml_path
        self.errors: List[LintError] = []

    def lint(self) -> List[LintError]:
        """
        Lint the TOML file for TOML-Doc specification compliance.

        Returns:
            List of LintError objects
        """
        # TODO: Implement linting logic
        # This should check:
        # 1. Separator Rule: Doc-comment preceded by empty line
        # 2. Attachment Rule: Doc-comment not separated from item by empty line
        # 3. Doc-comment marker syntax (#:)

        return self.errors

    def format(self) -> str:
        """
        Format the TOML file to comply with TOML-Doc specification.

        Returns:
            Formatted TOML content
        """
        # TODO: Implement formatting logic
        # This should automatically fix common issues:
        # - Add missing empty lines before doc-comments
        # - Remove empty lines between doc-comments and items

        return self.toml_path.read_text()


def main() -> int:
    """Main entry point for the toml-doc-lint CLI tool."""
    parser = argparse.ArgumentParser(
        description="Lint and format TOML files for TOML-Doc specification compliance"
    )
    parser.add_argument("file", type=Path, help="TOML file to lint")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for errors without formatting",
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format the file to fix errors",
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    linter = TomlDocLinter(args.file)

    if args.format:
        formatted = linter.format()
        args.file.write_text(formatted)
        print(f"Formatted {args.file}")
        return 0

    # Default to check mode
    errors = linter.lint()
    if errors:
        for error in errors:
            print(error)
        return 1

    print(f"No errors found in {args.file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
