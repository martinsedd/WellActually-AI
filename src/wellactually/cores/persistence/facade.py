"""
Persistence facade - High-level API hiding LanceDB, caching, and vectorization
complexity.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path

from wellactually.cores.persistence.cache import CacheManager
from wellactually.cores.persistence.lance_manager import LanceManager
from wellactually.cores.persistence.schemas import IgnoreRecord, ViolationRecord
from wellactually.cores.persistence.vectorizer import Vectorizer


class PersistenceFacade:
    """
    High-level facade for all persistence operations.

    Orchestrator interacts with this class only, without needing to know about LanceDB
    tables, AST normalization, or vectorization pipelines.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self.lance = LanceManager(db_path)
        self.cache = CacheManager(self.lance)
        self.vectorizer = Vectorizer()

    def chech_cache(self, code: str) -> ViolationRecord | None:
        return self.cache.get_cached_violation(code)

    def is_ignored(self, code: str) -> bool:
        return self.cache.is_ignored(code)

    def store_violation(
        self,
        project_path: str,
        file_path: str,
        line_number: int,
        violation_type: str,
        severity: str,
        code: str,
        roast_message: str,
        context: str | None = None,
    ) -> str:
        """
        Store a new violation with semantic vectorization.

        Args:
            project_path: Absolute path to project root
            file_path: Relative path to the file
            line_number: Line number where violation occurs
            violation_type: Type of violation (SRP, DRY, etc.)
            severity: Severity level (low, medium, high, critical)
            code: The code snippet
            roast_message: The snarky feedback
            context: Optional additional context

        Returns:
            The violation ID
        """
        snippet_hash = self.cache.normalize_and_hash(code)

        embedding_text = f"{violation_type}: {roast_message}\n\n{code}"
        embedding = self.vectorizer.vectorize(embedding_text)

        violation = ViolationRecord(
            id=str(uuid.uuid4()),
            project_path=project_path,
            file_path=file_path,
            line_number=line_number,
            violation_type=violation_type,
            severity=severity,
            snippet=code,
            snippet_hash=snippet_hash,
            roast_message=roast_message,
            context=context,
            embedding=embedding,
            timestamp=datetime.now(timezone.utc),
            ignored=False,
        )

        return self.lance.add_violation(violation)

    def ignore_violation(self, violation_id: str, code: str, reason: str) -> str:
        """
        Mark a violation as ignored with user-provided reason.

        Args:
            violation_id: The ID of the violation to ignore
            code: The code snippet being ignored
            reason: User's reason for ignoring

        Returns:
            The ignore record ID
        """
        snippet_hash = self.cache.normalize_and_hash(code)

        ignore = IgnoreRecord(
            id=str(uuid.uuid4()),
            violation_id=violation_id,
            snippet_hash=snippet_hash,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
            invalidated=False,
            invalidation_reason=None,
        )

        return self.lance.add_ignore(ignore)

    def invalidate_ignore_if_changed(self, old_code: str, new_code: str) -> None:
        self.cache.invalidate_if_changed(old_code, new_code)

    def get_project_violations(self, project_path: str) -> list[ViolationRecord]:
        return self.lance.get_project_violations(project_path)
