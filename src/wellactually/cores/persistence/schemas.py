"""
Pydantic schemas for violation and ignore records.
"""

from datetime import datetime

from lancedb.pydantic import LanceModel
from pydantic import Field


class ViolationRecord(LanceModel):
    """
    Record of a code violation detected by WellActually
    """

    id: str = Field(description="Unique identifier (UUID)")
    project_path: str = Field(description="Absolute path to the project root")
    file_path: str = Field(description="Relative path to the file")
    line_number: int = Field(description="Line number where the violation occurs")
    violation_type: str = Field(description="Type of violation (SRP, DRY, GOD_CLASS, etc.)")
    severity: str = Field(description="Severity level (low, medium, high, critical)")
    snippet: str = Field(description="Code snippet that triggered the violation")
    snippet_hash: str = Field(description="SHA-256 hash of normalized AST")
    roast_message: str = Field(description="The snarky feedback message")
    context: str | None = Field(None, description="Additional context from graph/analysis")
    embedding: list[float] | None = Field(None, description="Semantic vector embedding")
    timestamp: datetime = Field(default_factory=datetime.now)
    ignored: bool = Field(default=False, description="Whether this violation has been ignored")


class IgnoreRecord(LanceModel):
    """
    Record of a user ignoring a validation.
    """

    id: str = Field(description="Unique identifier (UUID)")
    violation_id: str = Field(description="ID of the violation being ignored")
    snippet_hash: str = Field(description="Hash of the code block (for invalidation)")
    reason: str = Field(description="User-provided reason for ignoring")
    timestamp: datetime = Field(default_factory=datetime.now)
    invalidated: bool = Field(default=False, description="Whether the ignore has been invalidated")
    invalidation_reason: str | None = Field(None, description="Why the ignore was invalidated")
