from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import ast


class ConsistencyStrategy(ABC):
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a file and return list of issues
        
        Args:
            file_path: Path to the file being analyzed
            tree: AST of the file
            file_content: Raw file content
            project_context: Context from other project files
            
        Returns:
            List of issue dictionaries
        """
        pass
    
    @abstractmethod
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        """
        Generate a fix for an issue
        
        Args:
            file_path: Path to the file
            issue: Issue dictionary
            file_content: Current file content
            
        Returns:
            Fix dictionary with confidence score
        """
        pass
    
    def confidence_score(self, issue: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a fix
        
        Args:
            issue: Issue dictionary
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        return issue.get('confidence', 0.5)

