from typing import List, Dict, Any
from pathlib import Path
import ast
import re
from .base import ConsistencyStrategy


class SecurityStrategy(ConsistencyStrategy):
    """Detect security vulnerabilities and issues"""
    
    def __init__(self):
        super().__init__()
        
        # Common patterns for security issues
        self.hardcoded_secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'aws[_-]?secret\s*=\s*["\'][^"\']+["\']',
        ]
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect security issues in code"""
        issues = []
        
        # Check for hardcoded secrets
        issues.extend(self._check_hardcoded_secrets(tree, file_content))
        
        # Check for SQL injection risks
        issues.extend(self._check_sql_injection(tree, file_content))
        
        # Check for command injection risks
        issues.extend(self._check_command_injection(tree, file_content))
        
        # Check for unsafe file operations
        issues.extend(self._check_unsafe_file_ops(tree, file_content))
        
        # Check for unsafe deserialization
        issues.extend(self._check_unsafe_deserialization(tree, file_content))
        
        # Check for weak crypto
        issues.extend(self._check_weak_crypto(tree, file_content))
        
        # Check for unsafe eval/exec
        issues.extend(self._check_eval_exec(tree, file_content))
        
        return issues
    
    def _check_hardcoded_secrets(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect hardcoded passwords, API keys, and secrets"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        
                        # Check if variable name suggests a secret
                        if any(keyword in var_name for keyword in ['password', 'api_key', 'apikey', 'secret', 'token', 'key']):
                            # Check if assigned a string literal
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                # Exclude common placeholders
                                value = node.value.value
                                if value and value not in ['', 'YOUR_API_KEY', 'YOUR_PASSWORD', 'TODO']:
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'error',
                                        'type': 'security',
                                        'message': f"Hardcoded secret detected: '{target.id}'. Use environment variables instead",
                                        'suggestion': f"Replace with: {target.id} = os.getenv('{target.id.upper()}')",
                                        'fixable': True
                                    })
        
        return issues
    
    def _check_sql_injection(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect potential SQL injection vulnerabilities"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for string formatting in SQL queries
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'executemany', 'raw']:
                        if node.args:
                            query_arg = node.args[0]
                            
                            # Check for f-strings
                            if isinstance(query_arg, ast.JoinedStr):
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'error',
                                    'type': 'security',
                                    'message': 'Potential SQL injection: using f-string in SQL query',
                                    'suggestion': 'Use parameterized queries instead',
                                    'fixable': False
                                })
                            
                            # Check for .format() or % formatting
                            elif isinstance(query_arg, ast.Call):
                                if isinstance(query_arg.func, ast.Attribute) and query_arg.func.attr == 'format':
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'error',
                                        'type': 'security',
                                        'message': 'Potential SQL injection: using .format() in SQL query',
                                        'suggestion': 'Use parameterized queries instead',
                                        'fixable': False
                                    })
                            
                            elif isinstance(query_arg, ast.BinOp) and isinstance(query_arg.op, ast.Mod):
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'error',
                                    'type': 'security',
                                    'message': 'Potential SQL injection: using % formatting in SQL query',
                                    'suggestion': 'Use parameterized queries instead',
                                    'fixable': False
                                })
        
        return issues
    
    def _check_command_injection(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect potential command injection vulnerabilities"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for unsafe shell command execution
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['system', 'popen']:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'security',
                            'message': f"Potential command injection risk with {node.func.attr}()",
                            'suggestion': 'Use subprocess with shell=False instead',
                            'fixable': False
                        })
                
                elif isinstance(node.func, ast.Name):
                    if node.func.id == 'eval':
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'error',
                            'type': 'security',
                            'message': 'eval() is dangerous and can execute arbitrary code',
                            'suggestion': 'Use ast.literal_eval() for safe evaluation',
                            'fixable': False
                        })
                    
                    elif node.func.id == 'exec':
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'error',
                            'type': 'security',
                            'message': 'exec() is dangerous and can execute arbitrary code',
                            'suggestion': 'Avoid dynamic code execution',
                            'fixable': False
                        })
        
        return issues
    
    def _check_unsafe_file_ops(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unsafe file operations"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # Check for missing encoding
                    has_encoding = any(
                        isinstance(kw, ast.keyword) and kw.arg == 'encoding'
                        for kw in node.keywords
                    )
                    
                    if not has_encoding:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'info',
                            'type': 'security',
                            'message': 'File opened without explicit encoding',
                            'suggestion': "Use encoding='utf-8' for consistent behavior",
                            'fixable': True
                        })
        
        return issues
    
    def _check_unsafe_deserialization(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unsafe deserialization"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check for pickle.loads or pickle.load
                    if node.func.attr in ['load', 'loads']:
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'pickle':
                            issues.append({
                                'line': node.lineno,
                                'column': node.col_offset,
                                'severity': 'warning',
                                'type': 'security',
                                'message': 'Unsafe deserialization with pickle can execute arbitrary code',
                                'suggestion': 'Only unpickle data from trusted sources, or use JSON instead',
                                'fixable': False
                            })
        
        return issues
    
    def _check_weak_crypto(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect weak cryptography"""
        issues = []
        
        weak_hash_algorithms = ['md5', 'sha1']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'new' and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'hashlib':
                            # Check first argument for algorithm name
                            if node.args and isinstance(node.args[0], ast.Constant):
                                algo = node.args[0].value
                                if algo in weak_hash_algorithms:
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'warning',
                                        'type': 'security',
                                        'message': f"Weak cryptographic algorithm '{algo}' detected",
                                        'suggestion': 'Use SHA-256 or better',
                                        'fixable': False
                                    })
                
                elif isinstance(node.func, ast.Name):
                    if node.func.id in weak_hash_algorithms:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'security',
                            'message': f"Weak cryptographic algorithm '{node.func.id}' detected",
                            'suggestion': 'Use SHA-256 or better',
                            'fixable': False
                        })
        
        return issues
    
    def _check_eval_exec(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect eval/exec usage"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', '__import__']:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'error',
                            'type': 'security',
                            'message': f"Dangerous function '{node.func.id}()' can execute arbitrary code",
                            'suggestion': 'Avoid dynamic code execution or use safer alternatives',
                            'fixable': False
                        })
        
        return issues
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        """Generate fix for security issues where possible"""
        
        if not issue.get('fixable', False):
            return {}
        
        lines = file_content.split('\n')
        line_idx = issue['line'] - 1
        
        if line_idx >= len(lines):
            return {}
        
        original_line = lines[line_idx]
        
        # Fix hardcoded secrets
        if 'Hardcoded secret' in issue.get('message', ''):
            match = re.search(r"(\w+)\s*=\s*['\"]([^'\"]+)['\"]", original_line)
            if match:
                var_name = match.group(1)
                indent = len(original_line) - len(original_line.lstrip())
                fixed_line = ' ' * indent + f"{var_name} = os.getenv('{var_name.upper()}')"
                
                return {
                    'line_number': issue['line'],
                    'original_line': original_line,
                    'fixed_line': fixed_line,
                    'description': f"Changed to use environment variable",
                    'confidence': 0.90
                }
        
        # Fix missing encoding in file operations
        if 'without explicit encoding' in issue.get('message', ''):
            if 'open(' in original_line and 'encoding=' not in original_line:
                # Add encoding parameter
                fixed_line = original_line.replace('open(', 'open(', 1)
                # Find the closing parenthesis
                close_paren = original_line.rfind(')')
                if close_paren > 0:
                    before_paren = original_line[:close_paren]
                    after_paren = original_line[close_paren:]
                    
                    # Check if there are other parameters
                    if before_paren.count(',') > 0:
                        fixed_line = before_paren + ", encoding='utf-8'" + after_paren
                    else:
                        # Only filename parameter
                        parts = before_paren.split('open(', 1)
                        if len(parts) == 2:
                            fixed_line = parts[0] + 'open(' + parts[1] + ", encoding='utf-8'" + after_paren
                
                return {
                    'line_number': issue['line'],
                    'original_line': original_line,
                    'fixed_line': fixed_line,
                    'description': "Added encoding='utf-8' parameter",
                    'confidence': 0.85
                }
        
        return {}

