from typing import List, Dict, Any
from pathlib import Path
import ast
import re
from .base import ConsistencyStrategy


class LogicalErrorStrategy(ConsistencyStrategy):
    """Detect logical errors and code smells in code"""
    
    def __init__(self):
        super().__init__()
        
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect logical errors in code"""
        issues = []
        
        # Detect missing operators (+=, -=, etc.)
        issues.extend(self._check_missing_augmented_operators(tree, file_content))
        
        # Detect incorrect comparisons
        issues.extend(self._check_incorrect_comparisons(tree, file_content))
        
        # Detect unreachable code
        issues.extend(self._check_unreachable_code(tree, file_content))
        
        # Detect infinite loops
        issues.extend(self._check_infinite_loops(tree, file_content))
        
        # Detect incorrect loop variables
        issues.extend(self._check_loop_variable_issues(tree, file_content))
        
        # Detect missing return statements
        issues.extend(self._check_missing_returns(tree, file_content))
        
        # Detect unused variables
        issues.extend(self._check_unused_variables(tree, file_content))
        
        # Detect off-by-one errors
        issues.extend(self._check_off_by_one(tree, file_content))
        
        return issues
    
    def _check_missing_augmented_operators(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect cases like x = x + 1 instead of x += 1"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    target_name = node.targets[0].id
                    
                    # Check if value is BinOp with target as left operand
                    if isinstance(node.value, ast.BinOp):
                        if isinstance(node.value.left, ast.Name) and node.value.left.id == target_name:
                            op_map = {
                                ast.Add: '+=',
                                ast.Sub: '-=',
                                ast.Mult: '*=',
                                ast.Div: '/=',
                                ast.Mod: '%=',
                                ast.FloorDiv: '//=',
                            }
                            
                            op_symbol = op_map.get(type(node.value.op))
                            if op_symbol:
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'warning',
                                    'type': 'logical_error',
                                    'message': f"Use augmented assignment '{op_symbol}' instead of '{target_name} = {target_name} + ...'",
                                    'suggestion': f"Replace with '{target_name} {op_symbol} ...'",
                                    'fixable': True
                                })
        
        return issues
    
    def _check_incorrect_comparisons(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect incorrect comparison patterns"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for assignment in conditions (= instead of ==)
            if isinstance(node, (ast.If, ast.While)) and isinstance(node.test, ast.NamedExpr):
                issues.append({
                    'line': node.lineno,
                    'column': node.col_offset,
                    'severity': 'error',
                    'type': 'logical_error',
                    'message': 'Assignment in condition may be unintended. Use == for comparison',
                    'fixable': False
                })
            
            # Check for chained comparisons that might be incorrect
            if isinstance(node, ast.Compare):
                if len(node.ops) > 1:
                    # Check if mixing equality and inequality
                    has_eq = any(isinstance(op, (ast.Eq, ast.NotEq)) for op in node.ops)
                    has_ineq = any(isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for op in node.ops)
                    
                    if has_eq and has_ineq:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'logical_error',
                            'message': 'Mixed equality and inequality in chained comparison may be confusing',
                            'fixable': False
                        })
        
        return issues
    
    def _check_unreachable_code(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unreachable code after return/raise/break/continue"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.For, ast.While, ast.If)):
                body = node.body if hasattr(node, 'body') else []
                
                for i, stmt in enumerate(body):
                    if isinstance(stmt, (ast.Return, ast.Raise)):
                        # Check if there's code after this
                        if i < len(body) - 1:
                            next_stmt = body[i + 1]
                            issues.append({
                                'line': next_stmt.lineno,
                                'column': next_stmt.col_offset,
                                'severity': 'warning',
                                'type': 'logical_error',
                                'message': 'Unreachable code after return/raise statement',
                                'fixable': False
                            })
        
        return issues
    
    def _check_infinite_loops(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect potential infinite loops"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                # Check for while True without break
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                    
                    if not has_break:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'logical_error',
                            'message': 'Potential infinite loop: while True without break statement',
                            'fixable': False
                        })
        
        return issues
    
    def _check_loop_variable_issues(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect issues with loop variables"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                loop_var = node.target
                
                # Check if loop variable is modified in body
                for body_node in ast.walk(node):
                    if isinstance(body_node, ast.Assign):
                        for target in body_node.targets:
                            if isinstance(target, ast.Name) and isinstance(loop_var, ast.Name):
                                if target.id == loop_var.id:
                                    issues.append({
                                        'line': body_node.lineno,
                                        'column': body_node.col_offset,
                                        'severity': 'warning',
                                        'type': 'logical_error',
                                        'message': f"Loop variable '{loop_var.id}' is modified in loop body, which may cause unexpected behavior",
                                        'fixable': False
                                    })
        
        return issues
    
    def _check_missing_returns(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect functions that might be missing return statements"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip __init__ and other special methods
                if node.name.startswith('__') and node.name.endswith('__'):
                    continue
                
                # Check if function has return type hint but no return statement
                if node.returns and node.returns is not None:
                    has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
                    
                    if not has_return and not isinstance(node.returns, ast.Constant):
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'logical_error',
                            'message': f"Function '{node.name}' has return type hint but no return statement",
                            'fixable': False
                        })
        
        return issues
    
    def _check_unused_variables(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unused variables"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assigned_vars = set()
                used_vars = set()
                
                # Collect assigned variables
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Name):
                                assigned_vars.add(target.id)
                    
                    # Collect used variables
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                        used_vars.add(child.id)
                
                # Find unused variables
                unused = assigned_vars - used_vars
                
                for var_name in unused:
                    if not var_name.startswith('_'):  # Allow intentional unused vars with _
                        # Find the line where variable was assigned
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assign):
                                for target in child.targets:
                                    if isinstance(target, ast.Name) and target.id == var_name:
                                        issues.append({
                                            'line': child.lineno,
                                            'column': child.col_offset,
                                            'severity': 'info',
                                            'type': 'dead_code',
                                            'message': f"Variable '{var_name}' is assigned but never used",
                                            'suggestion': f"Remove unused variable or prefix with '_' if intentional",
                                            'fixable': True
                                        })
        
        return issues
    
    def _check_off_by_one(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect potential off-by-one errors"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for range(len(x)) followed by indexing
            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                        if len(node.iter.args) == 1:
                            if isinstance(node.iter.args[0], ast.Call):
                                if isinstance(node.iter.args[0].func, ast.Name) and node.iter.args[0].func.id == 'len':
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'info',
                                        'type': 'code_smell',
                                        'message': 'Consider using "for item in items:" instead of "for i in range(len(items)):"',
                                        'suggestion': 'Use direct iteration or enumerate() for better readability',
                                        'fixable': False
                                    })
        
        return issues
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        """Generate fix for logical errors where possible"""
        
        if not issue.get('fixable', False):
            return {}
        
        lines = file_content.split('\n')
        line_idx = issue['line'] - 1
        
        if line_idx >= len(lines):
            return {}
        
        original_line = lines[line_idx]
        
        # Fix augmented operators
        if 'augmented assignment' in issue.get('message', ''):
            # Extract variable name and operator
            match = re.search(r"Use augmented assignment '(.+?)' instead", issue['message'])
            if match:
                aug_op = match.group(1)
                
                # Find the pattern "var = var OP expr"
                var_match = re.search(r'(\w+)\s*=\s*\1\s*([+\-*/%]|//)\s*(.+)', original_line)
                if var_match:
                    var_name = var_match.group(1)
                    expr = var_match.group(3)
                    indent = len(original_line) - len(original_line.lstrip())
                    fixed_line = ' ' * indent + f"{var_name} {aug_op} {expr}"
                    
                    return {
                        'line_number': issue['line'],
                        'original_line': original_line,
                        'fixed_line': fixed_line,
                        'description': f"Changed to augmented assignment {aug_op}",
                        'confidence': 0.95
                    }
        
        # Fix unused variables (by adding _ prefix)
        if issue.get('type') == 'dead_code' and 'never used' in issue.get('message', ''):
            var_match = re.search(r"Variable '(\w+)' is assigned", issue['message'])
            if var_match:
                var_name = var_match.group(1)
                fixed_line = original_line.replace(var_name, f'_{var_name}', 1)
                
                return {
                    'line_number': issue['line'],
                    'original_line': original_line,
                    'fixed_line': fixed_line,
                    'description': f"Prefixed unused variable with '_'",
                    'confidence': 0.85
                }
        
        return {}

