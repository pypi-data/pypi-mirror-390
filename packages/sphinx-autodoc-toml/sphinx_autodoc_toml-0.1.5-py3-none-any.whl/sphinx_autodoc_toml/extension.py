"""Sphinx extension for autodoc-toml directive.

.. spec:: The extension MUST provide an autodoc-toml directive for Sphinx.
   :id: S_EXT_001
   :status: implemented
   :tags: sphinx, directive
   :links: R_SPHINX_001

.. spec:: The autodoc-toml directive MUST accept a file path argument.
   :id: S_EXT_002
   :status: implemented
   :tags: sphinx, directive
   :links: R_SPHINX_002

.. spec:: The extension MUST resolve both relative and absolute file paths.
   :id: S_EXT_003
   :status: implemented
   :tags: sphinx, paths
   :links: R_SPHINX_003

.. spec:: The extension MUST generate proper docutils nodes from doc-comments.
   :id: S_EXT_004
   :status: implemented
   :tags: sphinx, generation
   :links: R_SPHINX_004

.. spec:: The extension MUST use nested_parse to support embedded Sphinx directives.
   :id: S_EXT_005
   :status: implemented
   :tags: sphinx, directives
   :links: R_SPHINX_005

.. spec:: The extension MUST log clear warnings and errors for invalid files.
   :id: S_EXT_006
   :status: implemented
   :tags: sphinx, error-handling
   :links: R_SPHINX_006

.. spec:: The extension MUST display TOML content in collapsible admonitions.
   :id: S_EXT_007
   :status: implemented
   :tags: sphinx, ui
   :links: R_SPHINX_007
"""

from pathlib import Path
from typing import Any, Dict, List

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.util import logging

from sphinx_autodoc_toml.parser import DocComment, parse_toml_file

logger = logging.getLogger(__name__)


class AutodocTomlDirective(Directive):
    """
    Directive to automatically document TOML files with embedded doc-comments.

    Usage:
        .. autodoc-toml:: path/to/file.toml
           :show-all:
           :recursive:
    """

    # Directive configuration
    has_content = False
    required_arguments = 1  # Path to the TOML file
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "show-all": directives.flag,
        "recursive": directives.flag,
    }

    def run(self) -> List[nodes.Node]:
        """
        Execute the directive.

        Returns:
            List of docutils nodes to insert into the document
        """
        # Get the TOML file path from the argument
        toml_path_str = self.arguments[0]

        # Resolve the path relative to the source directory
        env = self.state.document.settings.env
        source_dir = Path(env.srcdir)

        # Handle both absolute and relative paths
        toml_path = Path(toml_path_str)
        if not toml_path.is_absolute():
            toml_path = source_dir / toml_path

        # Verify the file exists
        if not toml_path.exists():
            logger.warning(
                f"TOML file not found: {toml_path}",
                location=(env.docname, self.lineno),
            )
            return []

        # Parse the TOML file and extract doc-comments
        try:
            doc_comments = parse_toml_file(toml_path)
        except Exception as e:
            logger.error(
                f"Failed to parse TOML file {toml_path}: {e}",
                location=(env.docname, self.lineno),
            )
            return []

        if not doc_comments:
            logger.info(
                f"No doc-comments found in {toml_path}",
                location=(env.docname, self.lineno),
            )
            return []

        # Generate the documentation nodes
        result_nodes = []

        for doc_comment in doc_comments:
            # Create a section for this TOML item
            section_nodes = self._create_section_for_doc_comment(doc_comment, toml_path)
            result_nodes.extend(section_nodes)

        return result_nodes

    def _create_section_for_doc_comment(
        self, doc_comment: DocComment, toml_path: Path
    ) -> List[nodes.Node]:
        """
        Create documentation nodes for a single doc-comment.

        Args:
            doc_comment: The DocComment object

        Returns:
            List of docutils nodes
        """
        result: List[nodes.Node] = []

        # Create a section header for the TOML path
        if doc_comment.path:
            # Create a title node for the TOML path
            title_text = doc_comment.toml_path
            section_id = f"toml-{doc_comment.full_path.replace('.', '-')}"

            # Create a rubric (subheading) for the TOML item
            rubric = nodes.rubric(text=title_text)
            rubric["ids"].append(section_id)
            result.append(rubric)

        # Parse the doc-comment content and insert it into the document
        if doc_comment.content or doc_comment.toml_content:
            # Build the combined RST content using ViewList for proper source tracking
            rst_content: ViewList = ViewList()
            source_name = str(toml_path)

            # Add the doc-comment content (split into individual lines)
            if doc_comment.content:
                for i, line in enumerate(doc_comment.content.split("\n")):
                    rst_content.append(line, source_name, doc_comment.line_number + i)

            # Add the collapsible admonition with TOML code
            if doc_comment.toml_content:
                # Calculate the line offset for the admonition content
                current_line = doc_comment.line_number
                if doc_comment.content:
                    current_line += len(doc_comment.content.split("\n"))
                    # Add a blank line before the admonition if there's doc-comment content
                    rst_content.append("", source_name, current_line)
                    current_line += 1

                # Create the admonition block
                rst_content.append(".. admonition:: View Configuration", source_name, current_line)
                current_line += 1
                rst_content.append("   :class: dropdown", source_name, current_line)
                current_line += 1
                rst_content.append("", source_name, current_line)
                current_line += 1
                rst_content.append("   .. code-block:: toml", source_name, current_line)
                current_line += 1
                rst_content.append("      :linenos:", source_name, current_line)
                current_line += 1
                rst_content.append("", source_name, current_line)
                current_line += 1

                # Add the TOML content with proper indentation
                for line in doc_comment.toml_content.split("\n"):
                    rst_content.append(f"      {line}", source_name, current_line)
                    current_line += 1

            # Use the ViewList (no need to create a separate StringList)
            content_string_list = rst_content

            # Create a container node to hold the parsed content
            container = nodes.container()
            container["classes"].append("toml-doc-comment")

            # Use nested_parse to parse the content as reStructuredText
            # This allows Sphinx directives (like .. req:: or .. spec::) to work
            # Note: We pass 0 as the offset since this is generated content
            self.state.nested_parse(content_string_list, 0, container)  # type: ignore[arg-type]

            result.append(container)

        return result


def setup(app: Sphinx) -> Dict[str, Any]:
    """
    Sphinx extension setup function.

    Args:
        app: The Sphinx application instance

    Returns:
        Extension metadata
    """
    # Register the autodoc-toml directive
    app.add_directive("autodoc-toml", AutodocTomlDirective)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
