from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from dotenv import load_dotenv

from stackloop.agent.setup import get_agent
from stackloop.core.agent_config import select_model, select_provider
from stackloop.utils.constants import MAX_ITERATIONS
from stackloop.core.execution import install_dependencies, run_application
from stackloop.core.debug_session import DebugSession
from stackloop.core.code_fixer import CodeFixer
from stackloop.cli.display import display_message, display_welcome, get_package_version
from stackloop.cli.prompts import (
    confirm_sync_back, get_runtime_choice, get_script_command, resolve_directory
)

app = typer.Typer(help="StackLoop - AI-powered debugging agent", no_args_is_help=True)
console = Console()

def version_callback(value: bool):
    """Display StackLoop version when --version or -v is used."""
    if value:
        v = get_package_version("stackloop")
        if v != "unknown":
            display_message(console, f"\n[bold cyan]StackLoop version {v}[/bold cyan]\n")
        else:
            display_message(console, f"\n[yellow]StackLoop version unknown[/yellow]\n")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, 
        "--version", 
        "-v", 
        callback=version_callback, 
        is_eager=True, 
        help="Show version and exit"
    )
):
    """StackLoop - AI-powered debugging agent"""
    if ctx.invoked_subcommand is None:
        display_message(console, ctx.get_help())
        raise typer.Exit()


@app.command("run")
def run(directory: Optional[Path] = typer.Argument(None, help="Project root directory")):
    """Run StackLoop to debug and fix your app automatically."""
    try:
        
        # Setup
        display_welcome(console)
        
         # Get project configuration
        root_dir = resolve_directory(directory)
        
        # Load .env from the project directory
        env_path = root_dir / ".env"
        load_dotenv(env_path)
        
        if not root_dir.exists():
            display_message(console, f"\n[red] ❌ Directory not found: {root_dir}[/red]\n")
            raise typer.Exit(1)
        
        # AI Agent setup
        provider = select_provider()
        model_name = select_model(provider, console)
        ai_agent = get_agent(provider, model_name, console)
        
        display_message(console, f"\n[dim] 📁 Project directory: {root_dir}[/dim]\n")
        
        runtime = get_runtime_choice()
        script = get_script_command(runtime)
        
        # Create and setup session
        session = DebugSession(root_dir, runtime, script)
        config = session.setup(console)
        
        install_dependencies(runtime, root_dir, console)
        
        # Initialize fixer
        fixer = CodeFixer(ai_agent, console, config)
        
        # Main debugging loop
        display_message(console, f"\n[bold yellow] 🚀 Running your application...[/bold yellow]\n")
        
        iteration = 0
        success = False
        changes_made = False   # 👈 track if fixer made any changes
        
        while not success and iteration < MAX_ITERATIONS:
            iteration += 1
            display_message(console, f"\n[bold magenta] 🔄 Iteration {iteration}[/bold magenta]\n")
            
            # Run the application
            result = run_application(session.work_dir, script, console)
            
            if result.success:
                success = True
                display_message(console, f"\n[green] ✅ Application ran successfully![/green]\n")
            else:
                display_message(console, f"\n[yellow]💡 Application failed, AI will attempt to fix errors...[/yellow]\n")
                
                # Analyze and fix errors
                analysis = fixer.analyze_error(result.stderr)
                changed = fixer.apply_fixes(analysis, session.relative_path)
                if changed:
                    changes_made = True
        
        # Final summary
        if success:
            if changes_made:
                display_message(console, f"\n[bold yellow]🔄 Files were fixed in the working directory.[/bold yellow]\n")
                if confirm_sync_back():
                    session.create_backup_for_root(console, config)
                    session.sync_back_to_root(console, config)
                    display_message(console, f"\n[green]✨ All done! Your files have been updated.[/green]\n")
                else:
                    display_message(console, f"\n[dim]💡 Fixed files are in: {session.work_dir}[/dim]\n")
            else:
                display_message(console, f"\n[green]✅ No changes were needed. Everything is already working![/green]\n")
        else:
            display_message(console, f"\n[red]❌ Maximum iterations reached, application still fails.[/red]\n")
    
    except KeyboardInterrupt:
        display_message(console, f"\n[yellow]⚠️ Cancelled by user[/yellow]\n")
        raise typer.Exit()
    except Exception as e:
        display_message(console, f"\n[red] ❌ Error: {e}[/red]\n")
        raise typer.Exit(1)