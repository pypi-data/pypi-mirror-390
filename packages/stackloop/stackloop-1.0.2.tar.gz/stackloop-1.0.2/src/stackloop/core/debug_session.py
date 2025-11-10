from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import shutil
import json

from stackloop.cli.display import display_message
from stackloop.models.session_config import SessionConfig
from stackloop.utils.constants import IGNORED_DIRS
from rich.console import Console

class DebugSession:
    def __init__(self, root_dir: Path, runtime: str, script: str):
        self.root_dir = root_dir.resolve()
        self.runtime = runtime
        self.script = script
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.relative_path = f".stackloop/session_{self.timestamp}"
        self.work_dir = root_dir / f"{self.relative_path}"
        
    def setup(self, console: Console) -> SessionConfig:
        """Create working directory and copy files"""
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        display_message(console, f"\n[dim]📂 Copying project files to {self.work_dir}[/dim]\n")
        self._copy_project_files()
        self._update_git_ignore_file(console)
        
        config = SessionConfig(
            runtime=self.runtime,
            script=self.script,
            root_directory=self.root_dir,
            working_directory=self.work_dir,
            timestamp=self.timestamp,
            relative_path=self.relative_path
        )
        
        self._save_config(config, console)
        return config
        
    def _copy_project_files(self):
        for item in self.root_dir.iterdir():
            if item.name in IGNORED_DIRS:
                continue
            dest = self.work_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
                
    def _update_git_ignore_file(self, console: Console):
        """Ensure .stackloop is ignored in .gitignore if this is a git repo."""
        git_dir = self.root_dir / ".git"
        if not git_dir.exists():
            return  # not a git repository

        gitignore_path = self.root_dir / ".gitignore"

        # Read current contents (if file exists)
        if gitignore_path.exists():
            content = gitignore_path.read_text()
        else:
            content = ""

        # Check if ".stackloop" is already ignored
        if ".stackloop" not in content:
            display_message(console, f"\n[blue]🧹 Adding .stackloop to .gitignore[/blue]\n")
            lines = []
            if not content.endswith("\n"):
                lines.append("\n")
            lines.append("# StackLoop \n")
            lines.append(".stackloop\n")

            gitignore_path.write_text(content + "".join(lines))

    
    def _save_config(self, config: SessionConfig, console: Console):
        config_path = self.work_dir / "stackloop.config.json"
        config_path.write_text(json.dumps(config.to_dict(), indent=2))
        display_message(console, f"\n[dim]💾 Config saved to {config_path}[/dim]\n")
        
    def sync_back_to_root(self, console: Console, config: SessionConfig):
        """Copy fixed files back to root directory"""
        display_message(console, f"\n[bold cyan]📝 Syncing fixes back to root directory...[/bold cyan]\n")

        # Load session config from file (in case it's been updated)
        config_path = Path(config.working_directory) / "stackloop.config.json"
        if config_path.exists():
            session = SessionConfig.from_json(config_path)
        else:
            session = config

        synced_files = []

        for item in session.modified_files:
            source = (config.working_directory / item).resolve()
            dest = (config.root_directory / item).resolve()

            try:
                dest.parent.mkdir(parents=True, exist_ok=True)  # ✅ ensure directories exist
                shutil.copy2(source, dest)
                synced_files.append(item)
            except Exception as e:
                display_message(console, f"\n[yellow] ⚠️ Could not sync {item}: {e}[/yellow]\n")

        if synced_files:
            display_message(console, f"\n[green]✅ Synced {len(synced_files)} files back to root[/green]\n")
            display_message(console, f"\n[dim]Files: {', '.join(synced_files[:5])}{'...' if len(synced_files) > 5 else ''}[/dim]\n")

        return synced_files


    def create_backup_for_root(self, console: Console, config: SessionConfig):
        """Create a backup of the modified files in the root directory before syncing"""
        config_path = Path(config.working_directory) / "stackloop.config.json"
        if config_path.exists():
            session = SessionConfig.from_json(config_path)
        else:
            session = config

        for item in session.modified_files:
            file_path = (config.root_directory / item).resolve()
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")

            try:
                backup_path.parent.mkdir(parents=True, exist_ok=True)  # ✅ ensure dir exists
                if file_path.exists():  # ✅ only backup existing files
                    backup_path.write_text(file_path.read_text())
                    display_message(console, f"\n[dim]💾 Backup created at {backup_path}[/dim]\n")
                else:
                    display_message(console, f"\n[yellow]⚠️ Skipping missing file: {file_path}[/yellow]\n")
            except Exception as e:
                display_message(console, f"\n[red]❌ Failed to create backup for {file_path}: {e}[/red]\n")
