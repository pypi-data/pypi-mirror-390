from pathlib import Path
import questionary
from stackloop.utils.constants import DEFAULT_COMMANDS

def get_runtime_choice() -> str:
    """Prompt user to select runtime"""
    try: 
        answer = questionary.select(
            "Select your project runtime:",
            choices=["Python", "Node.js", "Go", "Other"],
            style=get_questionary_style()
        ).ask()
        
        if answer is None:  # User pressed Ctrl+C
            raise KeyboardInterrupt
            
        return answer
    except KeyboardInterrupt:
        raise  # Let it bubble up to main handler

def get_script_command(runtime: str) -> str:
    """Prompt user for script command"""
    try: 
        default = get_default_command(runtime)
        answer = questionary.text(
            "Enter the script or command to run:",
            default=default
        ).ask()
        
        if answer is None:  # User pressed Ctrl+C
            raise KeyboardInterrupt
            
        return answer
    except KeyboardInterrupt:
        raise  # Let it bubble up to main handler

def get_questionary_style():
    """Return consistent questionary styling"""
    return questionary.Style([
        ("qmark", "fg:#00FFFF bold"),
        ("question", "bold"),
        ("selected", "fg:#FF00FF bold"),
        ("pointer", "fg:#00FFFF bold"),
        ("answer", "fg:#00FF00 bold"),
    ])
    
def get_default_command(runtime: str) -> str:
    """Get default command based on runtime"""
    return DEFAULT_COMMANDS.get(runtime, "")

def resolve_directory(directory: Path | None) -> Path:
    """Resolve and validate project directory"""
    root_dir = directory or Path.cwd()
    root_dir = root_dir.resolve()
    return root_dir

def confirm_sync_back() -> bool:
    """Ask user if they want to sync fixes back to root"""
    try: 
        
        answer = questionary.confirm(
            "Sync the fixed files back to your root directory?",
            default=True,
            style=get_questionary_style()
        ).ask()
        
        if answer is None:  # User pressed Ctrl+C
            raise KeyboardInterrupt
            
        return answer
    except KeyboardInterrupt:
        raise  # Let it bubble up to main handler