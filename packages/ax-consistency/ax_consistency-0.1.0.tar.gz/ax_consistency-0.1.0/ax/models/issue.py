from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class IssueSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(Enum):
    NAMING_CONVENTION = "naming_convention"
    TYPE_HINT = "type_hint"
    ERROR_HANDLING = "error_handling"
    DOCSTRING = "docstring"
    IMPORT_STYLE = "import_style"
    LOGIC_INCONSISTENCY = "logic_inconsistency"
    DEAD_CODE = "dead_code"
    DUPLICATE_CODE = "duplicate_code"
    VARIABLE_SCOPE = "variable_scope"
    FUNCTION_COMPLEXITY = "function_complexity"
    RETURN_CONSISTENCY = "return_consistency"
    CONDITION_LOGIC = "condition_logic"
    RESOURCE_MANAGEMENT = "resource_management"


@dataclass
class Issue:
    file_path: str
    line_number: int
    column: int
    issue_type: IssueType
    severity: IssueSeverity
    description: str
    current_code: str
    suggested_fix: Optional[str] = None
    confidence_score: float = 0.0
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "current_code": self.current_code,
            "suggested_fix": self.suggested_fix,
            "confidence_score": self.confidence_score,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
        return cls(
            file_path=data["file_path"],
            line_number=data["line_number"],
            column=data["column"],
            issue_type=IssueType(data["issue_type"]),
            severity=IssueSeverity(data["severity"]),
            description=data["description"],
            current_code=data["current_code"],
            suggested_fix=data.get("suggested_fix"),
            confidence_score=data.get("confidence_score", 0.0),
            context=data.get("context", {})
        )