from typing import List, Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from ..utils.file_utils import backup_file
import difflib


class FixExecutor:
    
    def __init__(self, auto_fix_threshold: float = 0.9, interactive_threshold: float = 0.6):
        self.auto_fix_threshold = auto_fix_threshold
        self.interactive_threshold = interactive_threshold
        self.console = Console()
    
    def execute_fixes(self, file_path: Path, fixes: List[Dict[str, Any]], auto: bool = False) -> Dict[str, Any]:
        """Execute fixes on a file"""
        
        if not fixes:
            return {'fixed': False, 'changes': [], 'message': 'No fixes to apply'}
        
        backup_path = backup_file(str(file_path))
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            applied_fixes = []
            
            high_confidence_fixes = [f for f in fixes if f.get('confidence', 0) >= self.auto_fix_threshold]
            medium_confidence_fixes = [f for f in fixes if self.interactive_threshold <= f.get('confidence', 0) < self.auto_fix_threshold]
            low_confidence_fixes = [f for f in fixes if f.get('confidence', 0) < self.interactive_threshold]
            
            if auto or high_confidence_fixes:
                for fix in high_confidence_fixes:
                    if self._apply_fix_to_lines(lines, fix):
                        applied_fixes.append(fix)
            
            if not auto and medium_confidence_fixes:
                for fix in medium_confidence_fixes:
                    if self._prompt_user_for_fix(file_path, fix, lines):
                        if self._apply_fix_to_lines(lines, fix):
                            applied_fixes.append(fix)
            
            if low_confidence_fixes:
                self._show_low_confidence_warnings(low_confidence_fixes)
            
            if applied_fixes:
                new_content = '\n'.join(lines)
                file_path.write_text(new_content, encoding='utf-8')
                
                self._show_diff(content, new_content, file_path)
                
                return {
                    'fixed': True,
                    'changes': [f['description'] for f in applied_fixes],
                    'backup_path': backup_path
                }
            else:
                return {
                    'fixed': False,
                    'changes': [],
                    'message': 'No fixes applied'
                }
                
        except Exception as e:
            return {
                'fixed': False,
                'error': str(e),
                'backup_path': backup_path
            }
    
    def _apply_fix_to_lines(self, lines: List[str], fix: Dict[str, Any]) -> bool:
        """Apply a fix to the lines array"""
        line_num = fix.get('line_number', 0)
        
        if line_num < 1 or line_num > len(lines):
            return False
        
        line_idx = line_num - 1
        original_line = fix.get('original_line', '')
        fixed_line = fix.get('fixed_line', '')
        
        if original_line and lines[line_idx] == original_line:
            lines[line_idx] = fixed_line
            return True
        
        return False
    
    def _prompt_user_for_fix(self, file_path: Path, fix: Dict[str, Any], lines: List[str]) -> bool:
        """Prompt user to approve a fix"""
        self.console.print(f"\n[yellow]Medium confidence fix for {file_path.name}[/yellow]")
        self.console.print(f"Line {fix.get('line_number', 0)}: {fix.get('description', 'No description')}")
        self.console.print(f"Confidence: {fix.get('confidence', 0):.2%}\n")
        
        original = fix.get('original_line', '')
        fixed = fix.get('fixed_line', '')
        
        self.console.print("[red]- " + original + "[/red]")
        self.console.print("[green]+ " + fixed + "[/green]")
        
        response = input("\nApply this fix? (y/n): ").strip().lower()
        return response == 'y'
    
    def _show_low_confidence_warnings(self, fixes: List[Dict[str, Any]]):
        """Show warnings for low confidence fixes"""
        if not fixes:
            return
        
        self.console.print("\n[yellow]Low confidence issues detected (not auto-fixed):[/yellow]")
        for fix in fixes:
            self.console.print(f"  Line {fix.get('line_number', 0)}: {fix.get('description', 'No description')} (confidence: {fix.get('confidence', 0):.2%})")
    
    def _show_diff(self, original: str, modified: str, file_path: Path):
        """Show highlighted diff of changes"""
        original_lines = original.split('\n')
        modified_lines = modified.split('\n')
        
        diff = list(difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"{file_path.name} (original)",
            tofile=f"{file_path.name} (fixed)",
            lineterm=''
        ))
        
        if not diff:
            return
        
        self.console.print(f"\n[bold cyan]Changes applied to {file_path.name}:[/bold cyan]")
        
        for line in diff[2:]:
            if line.startswith('+') and not line.startswith('+++'):
                self.console.print(f"[green]{line}[/green]")
            elif line.startswith('-') and not line.startswith('---'):
                self.console.print(f"[red]{line}[/red]")
            elif line.startswith('@@'):
                self.console.print(f"[cyan]{line}[/cyan]")
            else:
                self.console.print(f"[dim]{line}[/dim]")
        
        self.console.print()

