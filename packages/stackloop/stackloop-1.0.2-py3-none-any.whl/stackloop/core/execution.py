from pathlib import Path
import shlex
import time
import subprocess
from stackloop.cli.display import display_message
from stackloop.models.execution_result import ExecutionResult
from rich.panel import Panel
from rich.console import Console

def run_application(work_dir: Path, script: str, console: Console) -> ExecutionResult:
    """Run the application in the working directory and capture output"""
    display_message(console, f"\n[dim]Working directory: {work_dir}[/dim]\n")
    display_message(console, f"\n[dim]Command: {script}[/dim]\n")
    
    display_message(console, f"\n[yellow]⏳ Executing...[/yellow]\n")
    
    start_time = time.time()
    
    try:
        # Run in a separate process
        start_time = time.time()    
        result = subprocess.Popen(
            shlex.split(script),
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = result.communicate()
        duration = time.time() - start_time
        
        # Create execution result
        exec_result = ExecutionResult(
            success=result.returncode == 0,
            return_code=result.returncode,
            stdout=stdout,
            stderr=stderr,
            execution_time=duration
        )
        
        # Display results
        if exec_result.success:
            display_message(console, f"\n[bold green]✅ Success![/bold green] (executed in {duration:.2f}s)\n")
            
            if exec_result.stdout:
                console.print(Panel(
                    exec_result.stdout,
                    title="[green]Standard Output[/green]",
                    border_style="green",
                    padding=(1, 2)
                ))
        else:
            display_message(console, f"\n[bold red] ❌ Failed with exit code {exec_result.return_code}[/bold red] (executed in {duration:.2f}s)\n")
            
            if exec_result.stderr:
                console.print(Panel(
                    exec_result.stderr,
                    title="[red]Error Output[/red]",
                    border_style="red",
                    padding=(1, 2)
                ))
        
        return exec_result
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        display_message(console, f"\n[bold red]⏱️  Timeout![/bold red] Process exceeded 30 seconds\n")
        
        return ExecutionResult(
            success=False,
            return_code=-1,
            stdout="",
            stderr="Process timed out after 30 seconds",
            execution_time=execution_time
        )
    
    except Exception as e:
        execution_time = time.time() - start_time
        display_message(console, f"\n[bold red]💥 Exception:[/bold red] {str(e)}\n")
        
        return ExecutionResult(
            success=False,
            return_code=-1,
            stdout="",
            stderr=str(e),
            execution_time=execution_time
        )
        

def install_dependencies(runtime: str, work_dir: Path, console: Console):
    display_message(console, f"\n[cyan] 📦 Checking and installing dependencies...[/cyan]\n")
    
    runtime = runtime.lower()
    cmd = []
    skip_install = False

    if runtime == "node.js":
        if (work_dir / "package-lock.json").exists():
            cmd = ["npm", "ci"]
        elif (work_dir / "yarn.lock").exists():
            cmd = ["yarn", "install"]
        elif (work_dir / "package.json").exists():
            cmd = ["npm", "install"]
        else:
            skip_install = True
    
    elif runtime == "python":
        if (work_dir / "requirements.txt").exists():
            cmd = ["pip", "install", "-r", "requirements.txt"]
        elif (work_dir / "pyproject.toml").exists():
            # Standard command to install project in editable mode
            cmd = ["pip", "install", "."] 
        else:
            skip_install = True
    
    elif runtime == "go":
        # Check for go.mod file
        if (work_dir / "go.mod").exists():
            cmd = ["go", "mod", "tidy"]
            # After 'go mod tidy', dependencies are in the cache and ready to use. 
            # No further 'install' command is typically needed unless you want to build.
        else:
            skip_install = True
    
    else:
        display_message(console, f"\n[yellow] ⚠️ No installer defined for runtime '{runtime}'.[/yellow]\n")
        return

    if skip_install:
        display_message(console, f"\n[yellow] ⚠️ No recognized dependency file found for '{runtime}', skipping install.[/yellow]\n")
        return

    display_message(console, f"\n[blue] → Running {' '.join(cmd)}[/blue]\n")
    
    try:
        result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, check=True)
        if result.returncode == 0: 
            display_message(console, f"\n[green] ✅ Dependencies installed successfully![/green]\n") 
        else: 
            display_message(console, "\n[red] ❌ Dependency installation failed![/red]\n")
    except subprocess.CalledProcessError as e:
        display_message(console, "\n[red] ❌ Dependency installation failed![/red]\n")
    except FileNotFoundError:
        display_message(console, f"\n[red] ❌ Error: '{cmd[0]}' command not found. Ensure the runtime environment is installed and in your PATH.[/red]\n")




