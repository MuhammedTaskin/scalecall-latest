"""
Common types for tools.
"""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class OperationResult:
    """Standard result format for all tools."""
    success: bool
    data: Dict[str, Any] = None
    error: str = None
    
    def to_dict(self) -> Dict:
        result = {"success": self.success}
        if self.data:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
        return result
