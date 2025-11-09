from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from .issue import Issue
from .fix import Fix


@dataclass
class AnalysisResult:
    file_path: str
    timestamp: datetime
    issues: List[Issue]
    fixes: List[Fix]
    consistency_score: float
    processing_time: float
    file_hash: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)
    
    @property
    def fix_count(self) -> int:
        return len(self.fixes)
    
    @property
    def high_confidence_fixes(self) -> List[Fix]:
        return [fix for fix in self.fixes if fix.is_safe_to_auto_apply()]
    
    @property
    def medium_confidence_fixes(self) -> List[Fix]:
        return [fix for fix in self.fixes if fix.requires_user_approval()]
    
    @property
    def low_confidence_fixes(self) -> List[Fix]:
        return [fix for fix in self.fixes if fix.is_low_confidence()]
    
    def get_issues_by_type(self, issue_type) -> List[Issue]:
        return [issue for issue in self.issues if issue.issue_type == issue_type]
    
    def get_issues_by_severity(self, severity) -> List[Issue]:
        return [issue for issue in self.issues if issue.severity == severity]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "timestamp": self.timestamp.isoformat(),
            "issues": [issue.to_dict() for issue in self.issues],
            "fixes": [fix.to_dict() for fix in self.fixes],
            "consistency_score": self.consistency_score,
            "processing_time": self.processing_time,
            "file_hash": self.file_hash,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        return cls(
            file_path=data["file_path"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            issues=[Issue.from_dict(issue_data) for issue_data in data["issues"]],
            fixes=[Fix.from_dict(fix_data) for fix_data in data["fixes"]],
            consistency_score=data["consistency_score"],
            processing_time=data["processing_time"],
            file_hash=data["file_hash"],
            metadata=data.get("metadata", {})
        )