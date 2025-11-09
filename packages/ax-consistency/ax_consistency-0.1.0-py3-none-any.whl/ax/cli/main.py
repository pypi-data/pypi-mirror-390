import typer
import json
import time
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..services.ai_config import AIConfig
from ..services.llm_service import AIService

app = typer.Typer(help="AX - AI-powered code consistency checker")
console = Console()

@app.command()
def setup():
    """Set up AX with your AI provider configuration."""
    console.print("[bold cyan]Welcome to AX Setup![/bold cyan]")
    console.print("Let's configure your AI provider for code analysis.\n")
    
    ai_config = AIConfig()
    
    # Show available providers
    console.print("[bold]Available AI Providers:[/bold]")
    providers = ["openai", "anthropic", "qwen", "gemini"]
    for i, provider in enumerate(providers, 1):
        console.print(f"  {i}. {provider.title()}")
    
    # Get provider choice
    while True:
        try:
            choice = typer.prompt("\nSelect provider (1-4)")
            provider_idx = int(choice) - 1
            if 0 <= provider_idx < len(providers):
                provider = providers[provider_idx]
                break
            else:
                console.print("[red]Invalid choice. Please select 1-4.[/red]")
        except ValueError:
            console.print("[red]Please enter a number between 1-4.[/red]")
    
    # Get API key
    api_key = typer.prompt("Enter your API key", hide_input=True)
    
    # Set defaults based on provider
    defaults = {
        "openai": {
            "endpoint": "https://api.openai.com/v1",
            "model": "gpt-5"
        },
        "anthropic": {
            "endpoint": "https://api.anthropic.com/v1",
            "model": "claude-4.5-sonnet-20240229"
        },
        "qwen": {
            "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-coder-plus"
        },
        "gemini": {
            "endpoint": "https://generativelanguage.googleapis.com/v1",
            "model": "gemini-pro"
        }
    }
    
    # Allow custom endpoint and model
    default_endpoint = defaults[provider]["endpoint"]
    endpoint = typer.prompt("API endpoint", default=default_endpoint)
    
    default_model = defaults[provider]["model"]
    model = typer.prompt("Model name", default=default_model)
    
    # Save configuration
    config = {
        "provider": provider,
        "api_key": api_key,
        "endpoint": endpoint,
        "model": model
    }
    
    ai_config.save_config(config)
    console.print(f"\n[green]Setup complete! AX is now configured to use {provider.title()}.[/green]")
    console.print("You can now run 'ax check' to analyze your code.")

@app.command()
def check(
    path: str = typer.Argument(".", help="Path to check"),
    recursive: bool = typer.Option(True, "-r", "--recursive", help="Check directories recursively"),
    include: Optional[List[str]] = typer.Option(None, "--include", help="File patterns to include"),
    exclude: Optional[List[str]] = typer.Option(None, "--exclude", help="File patterns to exclude"),
    json_output: bool = typer.Option(False, "--json", help="Output results in JSON format"),
    use_ai: bool = typer.Option(True, "--ai/--no-ai", help="Use AI for analysis (default: True)"),
    interactive: bool = typer.Option(True, "-i/-I", "--interactive/--no-interactive", help="Ask to fix issues after analysis"),
):
    """Check code for consistency and quality issues."""
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            console.print(f"[red]Error: Path '{path}' does not exist[/red]")
            raise typer.Exit(1)
        
        from .commands import analyze_project, display_analysis_results, fix_project_files, display_fix_results
        
        results = analyze_project(path_obj, recursive, include, exclude, use_ai=use_ai)
        
        if json_output:
            console.print(json.dumps(results, indent=2, default=str))
        else:
            should_fix = display_analysis_results(results, interactive=interactive and use_ai)
            
            if should_fix:
                console.print("\n[cyan]Starting AI-powered fixes...[/cyan]\n")
                fix_results = fix_project_files(path_obj, recursive, include, exclude, auto=True, use_ai=use_ai)
                display_fix_results(fix_results)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def fix(
    path: str = typer.Argument(".", help="Path to fix"),
    recursive: bool = typer.Option(True, "-r", "--recursive", help="Fix directories recursively"),
    include: Optional[List[str]] = typer.Option(None, "--include", help="File patterns to include"),
    exclude: Optional[List[str]] = typer.Option(None, "--exclude", help="File patterns to exclude"),
    auto: bool = typer.Option(False, "--auto", help="Automatically apply all high-confidence fixes"),
    use_ai: bool = typer.Option(True, "--ai/--no-ai", help="Use AI for fixing (default: True)"),
):
    """Fix code issues automatically using AI."""
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            console.print(f"[red]Error: Path '{path}' does not exist[/red]")
            raise typer.Exit(1)
        
        from .commands import fix_project_files, display_fix_results
        
        results = fix_project_files(path_obj, recursive, include, exclude, auto=auto, use_ai=use_ai)
        display_fix_results(results)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def config(
    action: str = typer.Argument(..., help="Action: show, set"),
    key: Optional[str] = typer.Argument(None, help="Configuration key"),
    value: Optional[str] = typer.Argument(None, help="Configuration value"),
):
    """Manage AX configuration."""
    ai_config = AIConfig()
    
    if action == "show":
        if not ai_config.is_configured():
            console.print("[yellow]AX is not configured. Run 'ax setup' to get started.[/yellow]")
            return
            
        config_data = ai_config.load_config()
        
        table = Table(title="AX Configuration")
        table.add_column("Setting", style="cyan", width=20)
        table.add_column("Value", style="green")
        
        for k, v in config_data.items():
            if k == 'api_key' and v:
                v = f"{v[:8]}..." if len(v) > 8 else v
            table.add_row(k, str(v))
            
        console.print(table)

    elif action == "set":
        if not key or value is None:
            console.print("[red]Usage: ax config set <key> <value>[/red]")
            raise typer.Exit(1)
            
        config_data = ai_config.load_config() if ai_config.is_configured() else {}
        config_data[key] = value
        ai_config.save_config(config_data)
        console.print(f"[green]Set {key} = {value}[/green]")

    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Available actions: show, set")
        raise typer.Exit(1)

def load_gitignore_patterns(root_path: Path) -> List[str]:
    """Load patterns from .gitignore files."""
    patterns = []
    
    # Look for .gitignore in the root path and parent directories
    current_path = root_path.resolve()
    
    while True:
        gitignore_file = current_path / ".gitignore"
        if gitignore_file.exists():
            try:
                with open(gitignore_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception:
                # Ignore errors reading .gitignore files
                pass
        
        # Stop at filesystem root or when we can't go up further
        parent = current_path.parent
        if parent == current_path:
            break
        current_path = parent
    
    return patterns

def is_gitignored(file_path: Path, root_path: Path, patterns: List[str]) -> bool:
    """Check if a file should be ignored based on .gitignore patterns."""
    if not patterns:
        return False
    
    # Get relative path from root
    try:
        relative_path = file_path.relative_to(root_path.resolve())
        relative_str = str(relative_path)
        relative_posix = relative_str.replace('\\', '/')  # Normalize path separators

    except ValueError:
        # File is not under root_path

        return False
    
    # Debug specific file
    if 'test_should_be_ignored.py' in str(file_path):
        print(f"DEBUG: Checking {len(patterns)} patterns against {relative_posix}")
    
    for pattern in patterns:
        # Handle negation patterns (starting with !)
        if pattern.startswith('!'):
            # TODO: Implement negation properly (requires more complex logic)
            continue
            
        # Simple pattern matching
        if match_gitignore_pattern(relative_posix, pattern):
            if 'test_should_be_ignored.py' in str(file_path):
                print(f"DEBUG: MATCHED pattern '{pattern}'")
            return True
    
    return False

def match_gitignore_pattern(file_path: str, pattern: str) -> bool:
    """Match a file path against a gitignore pattern."""
    import fnmatch
    
    # Debug specific pattern
    if pattern == 'test_*.py':
        print(f"DEBUG: Testing pattern 'test_*.py' against '{file_path}'")
    
    # Handle directory patterns (ending with /)
    if pattern.endswith('/'):
        # This pattern matches directories
        pattern = pattern[:-1]
        # Check if any part of the path matches
        path_parts = file_path.split('/')
        for i in range(len(path_parts)):
            if fnmatch.fnmatch('/'.join(path_parts[:i+1]), pattern):
                return True
        return False
    
    # Handle patterns starting with /
    if pattern.startswith('/'):
        pattern = pattern[1:]
        return fnmatch.fnmatch(file_path, pattern)
    
    # Handle patterns with ** (match any number of directories)
    if '**' in pattern:
        # Convert ** to * for fnmatch
        pattern = pattern.replace('**', '*')
    
    # Check if pattern matches the full path or any suffix
    if fnmatch.fnmatch(file_path, pattern):
        return True
    
    # Check if pattern matches any part of the path
    path_parts = file_path.split('/')
    for i in range(len(path_parts)):
        suffix = '/'.join(path_parts[i:])
        if fnmatch.fnmatch(suffix, pattern):
            return True
    
    return False

def collect_files(path: Path, include: Optional[List[str]], exclude: Optional[List[str]], recursive: bool) -> List[Path]:
    """Collect files to analyze based on configuration."""
    files = []
    
    # Load .gitignore patterns
    gitignore_patterns = load_gitignore_patterns(path)
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    for file_path in path.glob(pattern):
        if file_path.is_file():
            # Check if file is ignored by .gitignore
            if is_gitignored(file_path, path, gitignore_patterns):
                continue
                
            # Check include patterns
            if include:
                if not any(file_path.match(p) for p in include):
                    continue
            
            # Check exclude patterns
            if exclude:
                if any(file_path.match(p) for p in exclude):
                    continue
            
            # Check if it's a supported file type
            if is_supported_file(file_path):
                files.append(file_path)
    
    return files

def is_supported_file(file_path: Path) -> bool:
    """Check if file type is supported for analysis."""
    supported_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj',
        '.hs', '.ml', '.fs', '.vb', '.pl', '.r', '.m', '.sh', '.bash', '.zsh',
        '.fish', '.ps1', '.bat', '.cmd', '.lua', '.dart', '.nim', '.cr', '.jl',
        '.ex', '.exs', '.elm', '.purs', '.re', '.res', '.resi', '.v', '.sv'
    }
    
    return file_path.suffix.lower() in supported_extensions


if __name__ == "__main__":
    app()