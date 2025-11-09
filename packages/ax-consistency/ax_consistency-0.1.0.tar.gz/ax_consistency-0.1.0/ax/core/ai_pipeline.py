from typing import List, Dict, Any, Optional
from pathlib import Path
from .parser import ASTParser
from .cache_service import CacheService
from ..services.llm_service import AIService
from ..services.ai_config import AIConfig


class AIPipeline:
    """Pipeline that uses AI for intelligent consistency analysis"""
    
    def __init__(self, use_cache: bool = True, use_ai: bool = True):
        self.parser = ASTParser()
        self.cache_service = CacheService() if use_cache else None
        self.use_ai = use_ai
        
        self.ai_service = None
        if use_ai:
            try:
                ai_config = AIConfig()
                if ai_config.is_configured():
                    self.ai_service = AIService()
                else:
                    print("Warning: AI not configured. Run 'ax setup' to enable AI-powered analysis.")
                    self.use_ai = False
            except Exception as e:
                print(f"Warning: Could not initialize AI service: {e}")
                self.use_ai = False
    
    def analyze_file(self, file_path: Path, project_files: List[Path]) -> Dict[str, Any]:
        """Analyze a file using AI for consistency checking"""
        
        if self.cache_service:
            cached_result = self.cache_service.get_cached_result(file_path)
            if cached_result:
                return cached_result
        
        result = {
            'file_path': str(file_path),
            'issues': [],
            'syntax_valid': True,
            'syntax_errors': [],
            'consistency_score': 1.0,
            'analysis_type': 'ai' if self.use_ai and self.ai_service else 'ast'
        }
        
        syntax_check = self.parser.check_syntax(file_path)
        if not syntax_check['valid']:
            result['syntax_valid'] = False
            result['syntax_errors'] = syntax_check['errors']
            return result
        
        if self.use_ai and self.ai_service:
            try:
                ai_result = self.ai_service.analyze_file_consistency(file_path, project_files)
                
                if 'error' in ai_result:
                    result['error'] = ai_result['error']
                else:
                    result['issues'] = ai_result.get('issues', [])
                    result['consistency_score'] = ai_result.get('consistency_score', 1.0)
                    result['summary'] = ai_result.get('summary', '')
                    
            except Exception as e:
                result['error'] = f"AI analysis failed: {str(e)}"
        else:
            result['error'] = 'AI service not available'
        
        result['issue_count'] = len(result['issues'])
        
        if self.cache_service:
            self.cache_service.cache_result(file_path, result)
        
        return result
    
    def fix_file(self, file_path: Path, project_files: List[Path]) -> Dict[str, Any]:
        """Fix issues in a file using AI"""
        
        if not self.use_ai or not self.ai_service:
            return {
                'fixed': False,
                'error': 'AI service not available. Run ax setup to configure AI.'
            }
        
        syntax_check = self.parser.check_syntax(file_path)
        
        if not syntax_check['valid']:
            content = file_path.read_text(encoding='utf-8')
            fix_result = self.parser.fix_syntax_errors(file_path, content)
            
            if fix_result['fixed']:
                file_path.write_text(fix_result['content'], encoding='utf-8')
                return {
                    'fixed': True,
                    'changes': fix_result['changes'],
                    'type': 'syntax'
                }
        
        try:
            fix_result = self.ai_service.fix_file_issues(file_path, project_files)
            return fix_result
        except Exception as e:
            return {
                'fixed': False,
                'error': f"AI fix failed: {str(e)}"
            }

