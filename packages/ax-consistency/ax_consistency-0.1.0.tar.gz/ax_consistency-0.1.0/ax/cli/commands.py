from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from ..core import AIPipeline, HybridPipeline, FixExecutor, ASTParser
from ..services.ai_config import AIConfig
from ..utils.file_utils import backup_file

console = Console()


def analyze_project(path: Path, recursive: bool, include: Optional[List[str]], exclude: Optional[List[str]], use_ai: bool = True) -> List:
    """Analyze project files for consistency issues using AI"""
    from ..cli.main import collect_files, is_supported_file
    
    if path.is_file():
        if not is_supported_file(path):
            console.print(f"[yellow]File type not supported: {path.suffix}[/yellow]")
            return []
        files = [path]
    else:
        files = collect_files(path, include, exclude, recursive)
    
    if not files:
        console.print("[yellow]No files found to analyze[/yellow]")
        return []
    
    ai_config = AIConfig()
    if use_ai and not ai_config.is_configured():
        console.print("[yellow]AI not configured. Using AST-based analysis.[/yellow]")
        console.print("[dim]Run 'ax setup' to enable AI-powered analysis.[/dim]\n")
        use_ai = False
    
    if use_ai:
        console.print("[cyan]Using AI-powered analysis...[/cyan]")
        pipeline = AIPipeline(use_cache=True, use_ai=True)
    else:
        console.print("[cyan]Using AST-based analysis...[/cyan]")
        pipeline = HybridPipeline(use_cache=True, prefer_ai=False)
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Analyzing files...", total=len(files))
        
        for file_path in files:
            progress.update(task, description=f"Analyzing {file_path.name}")
            
            result = pipeline.analyze_file(file_path, files)
            results.append(result)
            
            progress.advance(task)
    
    return results


def fix_project_files(path: Path, recursive: bool, include: Optional[List[str]], exclude: Optional[List[str]], auto: bool = False, use_ai: bool = True) -> List:
    """Fix consistency issues in project files using AI"""
    from ..cli.main import collect_files
    
    if path.is_file():
        files = [path]
    else:
        files = collect_files(path, include, exclude, recursive)
    
    if not files:
        console.print("[yellow]No files found to fix[/yellow]")
        return []
    
    ai_config = AIConfig()
    if use_ai and not ai_config.is_configured():
        console.print("[yellow]AI not configured. Cannot perform automatic fixes.[/yellow]")
        console.print("[dim]Run 'ax setup' to enable AI-powered fixing.[/dim]")
        return []
    
    if use_ai:
        console.print(f"[cyan]Using AI-powered fixing on {len(files)} file(s)...[/cyan]")
        pipeline = AIPipeline(use_cache=False, use_ai=True)
    else:
        console.print(f"[cyan]Using AST-based fixing on {len(files)} file(s)...[/cyan]")
        pipeline = HybridPipeline(use_cache=False, prefer_ai=False)
    
    all_project_files = collect_files(path.parent if path.is_file() else path, None, None, True)
    
    results = []
    files_needing_manual_fix = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Fixing files...", total=len(files))
        
        for file_path in files:
            progress.update(task, description=f"Fixing {file_path.name}")
            
            parser = ASTParser()
            syntax_check = parser.check_syntax(file_path)
            
            if not syntax_check['valid']:
                content = file_path.read_text(encoding='utf-8')
                fix_result = parser.fix_syntax_errors(file_path, content, interactive=not auto)
                
                if fix_result['fixed']:
                    backup_file(str(file_path))
                    file_path.write_text(fix_result['content'], encoding='utf-8')
                    console.print(f"\n[green]Fixed syntax errors in {file_path.name}[/green]")
                    for change in fix_result['changes']:
                        console.print(f"  - {change}")
                    
                    results.append({
                        'file': str(file_path),
                        'fixed': True,
                        'changes': fix_result['changes'],
                        'type': 'syntax'
                    })
                elif fix_result.get('needs_manual'):
                    files_needing_manual_fix.append((file_path, syntax_check['errors']))
                
                progress.advance(task)
                continue
            
            if use_ai:
                try:
                    fix_result = pipeline.fix_file(file_path, all_project_files)
                    
                    if fix_result.get('fixed'):
                        backup_path = backup_file(str(file_path))
                        console.print(f"\n[green]Fixed: {file_path.name}[/green]")
                        
                        for change in fix_result.get('changes', []):
                            console.print(f"  - {change}")
                        
                        results.append({
                            'file': str(file_path),
                            'fixed': True,
                            'changes': fix_result.get('changes', []),
                            'backup': backup_path
                        })
                    elif 'error' in fix_result:
                        console.print(f"[yellow]{file_path.name}: {fix_result['error']}[/yellow]")
                    else:
                        console.print(f"[dim]{file_path.name}: No changes needed[/dim]")
                    
                except Exception as e:
                    console.print(f"[red]Error fixing {file_path.name}: {e}[/red]")
            
            progress.advance(task)
    
    if files_needing_manual_fix and not auto:
        console.print("\n[yellow]Some files have syntax errors that couldn't be fixed automatically.[/yellow]")
        for file_path, errors in files_needing_manual_fix:
            console.print(f"\n[red]Syntax errors in {file_path.name}:[/red]")
            for error in errors:
                console.print(f"  Line {error['line']}: {error['message']}")
            
            console.print(f"\n[cyan]Would you like to open this file in your editor to fix manually?[/cyan]")
            response = input(f"Open {file_path.name} in editor? (y/n): ").strip().lower()
            
            if response == 'y':
                import subprocess
                try:
                    subprocess.run(['open', str(file_path)])
                    console.print(f"[green]Opened {file_path.name} in default editor[/green]")
                    console.print("[dim]Fix the syntax errors and run 'ax fix' again[/dim]")
                except Exception as e:
                    console.print(f"[yellow]Could not open file: {e}[/yellow]")
                    console.print(f"[dim]Please manually edit: {file_path}[/dim]")
    
    return results


def display_analysis_results(results: List, interactive: bool = False):
    """Display analysis results with consistency score and optional interactive mode"""
    if not results:
        console.print("[green]No files analyzed[/green]")
        return False
    
    total_issues = sum(r.get('issue_count', 0) for r in results)
    syntax_errors = sum(1 for r in results if not r.get('syntax_valid', True))
    
    total_score = 0.0
    scored_files = 0
    for r in results:
        if 'consistency_score' in r:
            total_score += r['consistency_score']
            scored_files += 1
    
    avg_consistency = (total_score / scored_files * 100) if scored_files > 0 else 100.0
    
    consistency_color = "green" if avg_consistency >= 80 else "yellow" if avg_consistency >= 60 else "red"
    
    console.print(Panel(
        f"Analyzed {len(results)} files\n"
        f"Consistency Score: [{consistency_color}]{avg_consistency:.1f}%[/{consistency_color}]\n"
        f"Found {total_issues} issues\n"
        f"Syntax errors: {syntax_errors} files",
        title="Analysis Summary",
        style="cyan"
    ))
    
    files_with_issues = []
    
    for result in results:
        file_path = result.get('file_path', 'unknown')
        
        if not result.get('syntax_valid', True):
            console.print(f"\n[red]Syntax errors in {file_path}:[/red]")
            for error in result.get('syntax_errors', []):
                console.print(f"  Line {error['line']}: {error['message']}")
            files_with_issues.append(file_path)
            continue
        
        issues = result.get('issues', [])
        if issues:
            score = result.get('consistency_score', 1.0) * 100
            score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
            
            console.print(f"\n[bold]{file_path}[/bold] - Consistency: [{score_color}]{score:.1f}%[/{score_color}]")
            
            if result.get('summary'):
                console.print(f"[dim]{result['summary']}[/dim]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Line", style="cyan", width=6)
            table.add_column("Type", style="yellow", width=20)
            table.add_column("Severity", style="red", width=10)
            table.add_column("Message", style="white")
            
            for issue in issues[:10]:
                table.add_row(
                    str(issue.get('line', 'N/A')),
                    issue.get('type', 'unknown'),
                    issue.get('severity', 'info'),
                    issue.get('message', '')
                )
            
            console.print(table)
            
            if len(issues) > 10:
                console.print(f"[dim]... and {len(issues) - 10} more issues[/dim]")
            
            files_with_issues.append(file_path)
    
    if interactive and files_with_issues:
        console.print("\n" + "="*60)
        console.print("[bold cyan]Would you like to fix these issues automatically?[/bold cyan]")
        console.print("[dim]This will use AI to fix the detected issues.[/dim]")
        response = input("\nFix issues now? (y/n): ").strip().lower()
        return response == 'y'
    
    return False


def display_fix_results(results: List):
    """Display fix results in a formatted way"""
    if not results:
        console.print("[yellow]No fixes applied[/yellow]")
        return
    
    fixed_count = sum(1 for r in results if r.get('fixed', False))
    
    console.print(Panel(
        f"Processed {len(results)} files\n"
        f"Fixed {fixed_count} files",
        title="Fix Summary",
        style="green"
    ))
    
    for result in results:
        if result.get('fixed'):
            console.print(f"\n[green]Fixed: {result['file']}[/green]")
            for change in result.get('changes', []):
                console.print(f"  - {change}")

