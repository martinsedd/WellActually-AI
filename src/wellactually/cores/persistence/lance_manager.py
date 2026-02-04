"""
LanceDB connection and ledger operations.
"""

import uuid
from pathlib import Path

import lancedb

from wellactually.cores.persistence.schemas import IgnoreRecord, ViolationRecord


class LanceManager:
    """
    Manages the global LanceDB ledger for violations and ignores.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        """
        Initialize LanceDB connection.

        Args:
            db_path: Path to LanceDB storage. Defaults to ~/.config/wellactually
        """
        if db_path is None:
            db_path = Path.home() / ".config" / "wellactually" / "ledger"

        self.db_path = db_path
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(str(self.db_path))

        self._init_tables()

    def _init_tables(self) -> None:
        """Create tables if they don't exist."""
        table_names = self.db.table_names()

        if "violations" not in table_names:
            self.db.create_table("violations", schema=ViolationRecord)

        if "ignores" not in table_names:
            self.db.create_table("ignores", schema=IgnoreRecord)

    def add_violation(self, violation: ViolationRecord) -> str:
        """
        Add a violation record to the ledger.

        Args:
            violation: The violation record to store

        Returns:
            The ID of the stored violation
        """
        table = self.db.open_table("violations")

        if not violation.id:
            violation.id = str(uuid.uuid4())

        table.add([violation.model_dump()])
        return violation.id

    def get_violation_by_hash(self, snippet_hash: str) -> ViolationRecord | None:
        """
        Retrieve a cached violation by snippet_hash.

        Args:
            snippet_hash: The normalized AST hash

        Returns:
            The violation record if found, None otherwise
        """
        table = self.db.open_table("violations")
        results = table.search().where(f"snippet_hash = '{snippet_hash}'").limit(1).to_list()

        if results:
            return ViolationRecord(**results[0])
        return None

    def add_ignore(self, ignore: IgnoreRecord) -> str:
        """
        Add an ignore record to the ledger.

        Args:
            ignore: The ignore record to store

        Returns:
            The ID of the stored ignore
        """
        table = self.db.open_table("ignores")

        if not ignore.id:
            ignore.id = str(uuid.uuid4())

        table.add([ignore.model_dump()])

        self._mark_violation_ignored(ignore.violation_id)

        return ignore.id

    def _mark_violation_ignored(self, violation_id: str) -> None:
        violations_table = self.db.open_table("violations")
        violations_table.update(where=f"id = '{violation_id}'", values={"ignored": True})

    def check_ignore_status(self, snippet_hash: str) -> IgnoreRecord | None:
        """
        Check if a code snippet is currently ignored.

        Args:
            snippet_hash: The normalized AST hash

        Returns:
            The ignore record if active, None otherwise
        """
        table = self.db.open_table("ignores")

        results = table.search().where(f"snippet_hash = '{snippet_hash}' AND invalidated = false").limit(1).to_list()

        if results:
            return IgnoreRecord(**results[0])
        return None

    def invalidate_ignore(self, snippet_hash: str, reason: str) -> None:
        """
        Invaldate an ignore when code changes.

        Args:
            snippet_hash: The hash of the changed code
            reason: Why the ignore was invalidated
        """
        ignores_table = self.db.open_table("ignores")
        ignores_table.update(
            where=f"snippet_hash = '{snippet_hash}' AND invalidated = false",
            values={"invalidated": True, "invalidation_reason": reason},
        )

    def get_project_violations(self, project_path: str) -> list[ViolationRecord]:
        """
        Get all violations for a specific project.

        Args:
            project_path: Absolute path to project root

        Returns:
            List of violation records
        """
        table = self.db.open_table("violations")

        results = table.search().where(f"project_path = '{project_path}'").to_list()

        return [ViolationRecord(**record) for record in results]
