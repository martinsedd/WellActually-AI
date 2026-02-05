"""
Python parser using Tree-sitter
"""

from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser

from wellactually.cores.structure.graph.schema import ClassNode, FileNode, FunctionNode
from wellactually.cores.structure.parsers.base import BaseParser


class PythonParser(BaseParser):
    """
    Tree-sitter based parser for Python code.
    """

    def __init__(self) -> None:
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def parse_file(self, file_path: Path, content: str) -> tuple[FileNode, list[ClassNode], list[FunctionNode]]:
        """
        Parse a Python file and extract structural information

        Args:
            file_path: Path to the file being parsed
            content: File content as string

        Returns:
            Tuple of (FileNode, list of ClassNodes, list of FunctionNodes)
        """
        tree = self.parser.parse(bytes(content, "utf8"))
        root = tree.root_node

        # Count lines of code (non-empty, non-comment)
        loc = len([line for line in content.split("\n") if line.strip() and not line.strip().startswith("#")])

        file_node = FileNode(
            path=str(file_path),
            language="python",
            lines_of_code=loc,
        )

        classes: list[ClassNode] = []
        functions: list[FunctionNode] = []

        self._extract_classed_and_functions(root, str(file_path), content, classes, functions)

        return file_node, classes, functions

    def _extract_classed_and_functions(
        self,
        node: Node,
        file_path: str,
        content: str,
        classes: list[ClassNode],
        functions: list[FunctionNode],
        parent_class: str | None = None,
    ) -> None:
        """Recursively extract class and function definitions."""
        if node.type == "class_definition":
            class_name_node = node.child_by_field_name("name")
            if class_name_node:
                class_name = content[class_name_node.start_byte : class_name_node.end_byte]

                method_count = sum(1 for child in node.children if child.type == "function_definition")

                is_abstract = self._is_abstract_class(node, content)

                classes.append(
                    ClassNode(
                        name=class_name,
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        is_abstract=is_abstract,
                        method_count=method_count,
                    )
                )

                for child in node.children:
                    self._extract_classed_and_functions(child, file_path, content, classes, functions, class_name)
        elif node.type == "function_definition":
            func_name_node = node.child_by_field_name("name")
            if func_name_node:
                func_name = content[func_name_node.start_byte : func_name_node.end_point]
                func_body = content[node.start_byte : node.end_byte]

                complexity = self.calculate_complexity(func_body)

                functions.append(
                    FunctionNode(
                        name=func_name,
                        file_path=file_path,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        complexity=complexity,
                        parent_class=parent_class,
                    )
                )
        else:
            for child in node.children:
                self._extract_classed_and_functions(child, file_path, content, classes, functions, parent_class)

    def get_imports(self, content: str) -> list[tuple[str, list[str]]]:
        """
        Extract import statements from Python code.

        Args:
            content: File content as string

        Returns:
            List of (module_path, imported_names) tuples
        """
        tree = self.parser.parse(bytes(content, "utf8"))
        root = tree.root_node

        imports: list[tuple[str, list[str]]] = []

        for node in root.children:
            if node.type == "import_statement":
                # import foo, bar
                for child in node.children:
                    if child.type == "dotted_name":
                        module_name = content[child.start_byte : child.end_byte]
                        imports.append((module_name, [module_name]))
            elif node.type == "import_from_statement":
                module_node = node.child_by_field_name("module_name")
                if module_node:
                    module_name = content[module_node.start_byte : module_node.end_byte]
                    imported_names: list[str] = []

                    for child in node.children:
                        if child.type == "dotted_name" or child.type == "identifier":
                            name = content[child.start_byte : child.end_byte]
                            if name != module_name:
                                imported_names.append(name)

                    imports.append((module_name, imported_names))
        return imports

    def calculate_complexity(self, function_body: str) -> int:
        """
        Calculate cyclomatic complexity for a Python function.

        Complexity = 1 + number of decision points (if, for, while, and, or, except)

        Args:
            function_body: Function source code

        Returns:
            Cyclomatic complexity score
        """
        tree = self.parser.parse(bytes(function_body, "utf8"))
        root = tree.root_node

        complexity = 1
        decision_nodes = {"if_statement", "for_statement", "while_statement", "except_clause", "boolean_operator"}

        def count_decisions(node: Node) -> int:
            count = 0
            if node.type in decision_nodes:
                count += 1
            for child in node.children:
                count += count_decisions(child)
            return count

        complexity += count_decisions(root)
        return complexity

    def _is_abstract_class(self, class_node: Node, content: str) -> bool:
        """
        Check if a class is abstract (inherits from ABC or has @abstractmethod).

        Args:
            class_node: The class_definition node
            content: File content

        Returns:
            True if class is abstract, False otherwise
        """
        bases_node = class_node.child_by_field_name("superclasses")
        if bases_node:
            bases_text = content[bases_node.start_byte : bases_node.end_byte]
            if "ABC" in bases_text or "abc.ABC" in bases_text:
                return True

        for child in class_node.children:
            if child.type == "function_definition":
                for func_child in child.children:
                    if func_child.type == "decorator":
                        decorator_text = content[func_child.start_byte : func_child.end_byte]
                        if "abstractmethod" in decorator_text:
                            return True

        return False
