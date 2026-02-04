"""
AST hash-based cache for violation lookups.
"""

import ast
import hashlib

from wellactually.cores.persistence.lance_manager import LanceManager
from wellactually.cores.persistence.schemas import ViolationRecord


class CacheManager:
    """
    Manages deterministic AST hashing and cache lookups.
    """

    def __init__(self, lance_manager: LanceManager) -> None:
        self.lance = lance_manager

    def normalize_and_hash(self, code: str) -> str:
        """
        Normalize Python code AST and generate a stable hash.

        Strips local identifiers (variable names) but preserves external
        method calls to maintain the "shape" of architectural violations.

        Args:
            code: The code snippet to normalize

        Returns:
            SHA-256 hash of the normalized AST
        """
        try:
            tree = ast.parse(code)
            normalized = self._normalize_ast(tree)
            normalized_str = ast.dump(normalized, annotate_fields=False)
            return hashlib.sha256(normalized_str.encode()).hexdigest()
        except SyntaxError:
            # If code has syntax errors, hash the raw code
            return hashlib.sha256(code.encode()).hexdigest()

    def _normalize_ast(self, node: ast.AST) -> ast.AST:
        """
        Recursively normalize an AST by stripping local identifiers.

        Preserves:
        - Function/method call names (external dependencies)
        - Structural elements (if/for/while/try)

        Strips:
        - Variable names (replaced with generic names)
        - Comments and docstrings
        - Whitespace differences
        """
        if isinstance(node, ast.Name):
            # Replace variable names with generic placeholder
            node.id = "VAR"
        elif isinstance(node, ast.FunctionDef):
            # Preserve function name for external calls, but normalize local functions
            # For now, keep function names as they indicate architectural intent
            pass
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            # Strip standalone string literals (docstrings)
            if isinstance(node.value.value, str):
                return ast.Pass()

        for child in ast.iter_child_nodes(node):
            self._normalize_ast(child)

        return node

    def get_cached_violation(self, code: str) -> ViolationRecord | None:
        """
        Check if a violation for this code already exists in cache.

        Args:
            code: The code snippet to check

        Returns:
            Cached violation record if found, None otherwise
        """
        snippet_hash = self.normalize_and_hash(code)
        return self.lance.get_violation_by_hash(snippet_hash)

    def is_ignored(self, code: str) -> bool:
        """
        Check if this code snippet is currently ignored.

        Args:
            code: The code snippet to check

        Returns:
            True if ignored, False otherwise
        """
        snippet_hash = self.normalize_and_hash(code)
        ignore_record = self.lance.check_ignore_status(snippet_hash)
        return ignore_record is not None

    def invalidate_if_changed(self, old_code: str, new_code: str) -> None:
        """
        Invalidate ignores if the code logic has changed.

        Args:
            old_code: Previous version of the code
            new_code: New version of the code
        """
        old_hash = self.normalize_and_hash(old_code)
        new_hash = self.normalize_and_hash(new_code)

        if old_hash != new_hash:
            self.lance.invalidate_ignore(old_hash, "Code structure changed")
