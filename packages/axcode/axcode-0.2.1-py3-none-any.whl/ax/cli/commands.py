from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.prompt import Confirm
from ..core import AnalysisPipeline, FixExecutor, ASTParser

console = Console()


def analyze_project(path: Path, recursive: bool, include: Optional[List[str]], exclude: Optional[List[str]]) -> List:
    """Analyze project files for consistency issues using AST-based analysis"""
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
    
    console.print("[cyan]Using AST-based analysis...[/cyan]")
    pipeline = AnalysisPipeline(use_cache=True)
    
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


def display_fix_preview(files_with_fixes: List[Dict[str, Any]]) -> bool:
    """Display a preview of all fixes that will be applied and ask for confirmation"""
    if not files_with_fixes:
        return False
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Fix Preview[/bold cyan]\n"
        "The following changes will be applied to your files:",
        border_style="cyan"
    ))
    console.print()
    
    total_files = len(files_with_fixes)
    total_fixes = sum(len(item['fixes']) for item in files_with_fixes)
    
    # Summary statistics
    console.print(f"[bold]Summary:[/bold]")
    console.print(f"  Files to modify: [cyan]{total_files}[/cyan]")
    console.print(f"  Total fixes: [cyan]{total_fixes}[/cyan]")
    console.print()
    
    # Show details for each file
    for file_info in files_with_fixes[:10]:  # Limit to first 10 files
        file_path = file_info['file']
        fixes = file_info['fixes']
        
        console.print(f"[bold yellow]File:[/bold yellow] {file_path}")
        console.print(f"[dim]  {len(fixes)} fix(es) will be applied[/dim]")
        console.print()
        
        # Show first 5 fixes per file
        for fix in fixes[:5]:
            line_num = fix.get('line_number', 0)
            description = fix.get('description', 'No description')
            confidence = fix.get('confidence', 0)
            original = fix.get('original_line', '')
            fixed = fix.get('fixed_line', '')
            
            console.print(f"  [cyan]Line {line_num}:[/cyan] {description}")
            console.print(f"  [dim]Confidence: {confidence:.0%}[/dim]")
            
            if original and fixed:
                # Show diff-style output
                console.print(f"  [red]- {original.strip()}[/red]")
                console.print(f"  [green]+ {fixed.strip()}[/green]")
            
            console.print()
        
        if len(fixes) > 5:
            console.print(f"  [dim]... and {len(fixes) - 5} more fix(es)[/dim]")
            console.print()
    
    if len(files_with_fixes) > 10:
        console.print(f"[dim]... and {len(files_with_fixes) - 10} more file(s)[/dim]")
        console.print()
    
    # Ask for confirmation
    console.print("[bold yellow]Warning:[/bold yellow] This will modify your files.")
    console.print()
    
    return Confirm.ask("[bold cyan]Do you want to proceed with these fixes?[/bold cyan]", default=False)


def fix_project_files(path: Path, recursive: bool, include: Optional[List[str]], exclude: Optional[List[str]], auto: bool = False) -> List:
    """Fix consistency issues in project files using AST-based analysis"""
    from ..cli.main import collect_files
    
    if path.is_file():
        files = [path]
    else:
        files = collect_files(path, include, exclude, recursive)
    
    if not files:
        console.print("[yellow]No files found to fix[/yellow]")
        return []
    
    console.print(f"[cyan]Analyzing {len(files)} file(s) to determine fixes...[/cyan]")
    pipeline = AnalysisPipeline(use_cache=False)
    
    all_project_files = collect_files(path.parent if path.is_file() else path, None, None, True)
    
    # First pass: Collect all potential fixes
    files_with_fixes = []
    files_needing_manual_fix = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Analyzing files...", total=len(files))
        
        for file_path in files:
            progress.update(task, description=f"Analyzing {file_path.name}")
            
            parser = ASTParser()
            syntax_check = parser.check_syntax(file_path)
            
            if not syntax_check['valid']:
                content = file_path.read_text(encoding='utf-8')
                fix_result = parser.fix_syntax_errors(file_path, content, interactive=not auto)
                
                if fix_result.get('needs_manual'):
                    files_needing_manual_fix.append((file_path, syntax_check['errors']))
                elif fix_result['fixed']:
                    # Add to fixes list
                    files_with_fixes.append({
                        'file': str(file_path),
                        'fixes': [{
                            'line_number': 0,
                            'description': 'Syntax error fixes',
                            'confidence': 0.95,
                            'type': 'syntax'
                        }]
                    })
                
                progress.advance(task)
                continue
            
            # Analyze file to find issues
            try:
                analysis_result = pipeline.analyze_file(file_path, all_project_files)
                issues = analysis_result.get('issues', [])
                
                if issues:
                    # Generate fixes for issues
                    fixes = pipeline.generate_fixes(file_path, issues)
                    
                    if fixes:
                        files_with_fixes.append({
                            'file': str(file_path),
                            'fixes': fixes
                        })
                    
            except Exception as e:
                console.print(f"[red]Error analyzing {file_path.name}: {e}[/red]")
            
            progress.advance(task)
    
    # Show preview and ask for confirmation (unless auto mode)
    if files_with_fixes and not auto:
        proceed = display_fix_preview(files_with_fixes)
        if not proceed:
            console.print("\n[yellow]Fix operation cancelled by user.[/yellow]")
            return []
    
    # Second pass: Apply the fixes
    results = []
    
    console.print("\n[cyan]Applying fixes...[/cyan]\n")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Applying fixes...", total=len(files_with_fixes))
        
        for file_info in files_with_fixes:
            file_path = Path(file_info['file'])
            fixes = file_info['fixes']
            
            progress.update(task, description=f"Fixing {file_path.name}")
            
            try:
                if fixes[0].get('type') == 'syntax':
                    # Handle syntax fixes
                    parser = ASTParser()
                    content = file_path.read_text(encoding='utf-8')
                    fix_result = parser.fix_syntax_errors(file_path, content, interactive=False)
                    
                    if fix_result['fixed']:
                        file_path.write_text(fix_result['content'], encoding='utf-8')
                        
                        results.append({
                            'file': str(file_path),
                            'fixed': True,
                            'changes': fix_result['changes'],
                            'type': 'syntax'
                        })
                else:
                    # Handle other fixes
                    executor = FixExecutor(auto_fix_threshold=0.9, interactive_threshold=0.6)
                    fix_result = executor.execute_fixes(file_path, fixes, auto=True)
                    
                    if fix_result.get('fixed'):
                        results.append({
                            'file': str(file_path),
                            'fixed': True,
                            'changes': fix_result.get('changes', [])
                        })
                        
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
    """Display analysis results and optional interactive mode"""
    if not results:
        console.print("[green]No files analyzed[/green]")
        return False
    
    total_issues = sum(r.get('issue_count', 0) for r in results)
    syntax_errors = sum(1 for r in results if not r.get('syntax_valid', True))
    
    # Calculate average consistency score (files with no issues = 100%)
    total_score = 0.0
    for r in results:
        issue_count = r.get('issue_count', 0)
        if issue_count == 0:
            total_score += 1.0
        else:
            # Simple score based on issue severity
            total_score += max(0.0, 1.0 - (issue_count * 0.05))
    
    avg_consistency = (total_score / len(results) * 100) if len(results) > 0 else 100.0
    
    consistency_color = "green" if avg_consistency >= 80 else "yellow" if avg_consistency >= 60 else "red"
    
    console.print(Panel(
        f"Analyzed {len(results)} files\n"
        f"Quality Score: [{consistency_color}]{avg_consistency:.1f}%[/{consistency_color}]\n"
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
            issue_count = len(issues)
            score = max(0.0, 100.0 - (issue_count * 5))
            score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
            
            console.print(f"\n[bold]{file_path}[/bold] - Quality: [{score_color}]{score:.1f}%[/{score_color}]")
            
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
        console.print("[dim]This will use AST-based analysis to fix the detected issues.[/dim]")
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

