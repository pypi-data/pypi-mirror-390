from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class FixStatus(Enum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    SKIPPED = "skipped"


class FixType(Enum):
    REPLACE = "replace"
    INSERT = "insert"
    DELETE = "delete"
    MOVE = "move"


@dataclass
class Fix:
    file_path: str
    line_number: int
    column: int
    fix_type: FixType
    original_code: str
    new_code: str
    description: str
    confidence_score: float
    status: FixStatus = FixStatus.PENDING
    backup_content: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def is_safe_to_auto_apply(self) -> bool:
        """Determine if this fix is safe to apply automatically"""
        return self.confidence_score >= 0.9
    
    def requires_user_approval(self) -> bool:
        """Determine if this fix requires user approval"""
        return 0.6 <= self.confidence_score < 0.9
    
    def is_low_confidence(self) -> bool:
        """Determine if this fix has low confidence"""
        return self.confidence_score < 0.6
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "fix_type": self.fix_type.value,
            "original_code": self.original_code,
            "new_code": self.new_code,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "status": self.status.value,
            "backup_content": self.backup_content,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Fix":
        return cls(
            file_path=data["file_path"],
            line_number=data["line_number"],
            column=data["column"],
            fix_type=FixType(data["fix_type"]),
            original_code=data["original_code"],
            new_code=data["new_code"],
            description=data["description"],
            confidence_score=data["confidence_score"],
            status=FixStatus(data.get("status", "pending")),
            backup_content=data.get("backup_content"),
            metadata=data.get("metadata", {})
        )