from pathlib import Path
from pydantic_ai import Agent
from rich.console import Console

from stackloop.cli.display import display_message
from stackloop.models.corrected_code import CorrectedCode
from stackloop.models.error_analysis import ErrorAnalysis, FileFix
from stackloop.models.session_config import SessionConfig


class CodeFixer:
    def __init__(self, ai_agent: Agent, console: Console, session: SessionConfig):
        self.ai_agent = ai_agent
        self.console = console
        self.session = session
        
    def analyze_error(self, stderr: str) -> ErrorAnalysis:
        """Analyze stacktrace and get AI suggestions"""
        try:
            prompt = self._build_analysis_prompt(stderr)
            analysis = self.ai_agent.run_sync(
                user_prompt=prompt,
                output_type=ErrorAnalysis
            ).output
            return analysis
        except Exception as e:
            display_message(self.console, f"\n[red] ❌ Error during analysis: {e.message}[/red]\n")
            return ErrorAnalysis(message="Analysis failed", fixes=[])
    
    def apply_fixes(self, analysis: ErrorAnalysis, relative_path: str) -> bool:
        """Apply all suggested fixes"""
        file_updated = False
        for file_fix in analysis.fixes:
            if file_fix.file_path and file_fix.can_fix_automatically:
                file_updated = self._apply_file_fix(file_fix, relative_path)
            else:
                display_message(self.console, f"\n[dim yellow]💡 {file_fix.suggested_fix}[/dim yellow]\n")       
        return file_updated
    
    def _apply_file_fix(self, file_fix: FileFix, relative_path: str) -> bool:
        """Apply fix to a specific file."""
        raw_path = str(file_fix.file_path).strip()
        work_dir = Path(self.session.working_directory).resolve()

        # Normalize the path
        target_file = self._normalize_path(raw_path, work_dir, relative_path)
        
        if not target_file:
            display_message(self.console, f"\n[yellow]⚠️ Could not resolve path: {raw_path}[/yellow]\n")
            return False

        # Debug logging
        display_message(self.console, f"\n[dim]📝 AI provided: {raw_path}[/dim]\n")
        display_message(self.console, f"\n[dim]🔍 Resolved to: {target_file}[/dim]\n")

        # Validate
        if not target_file.exists():
            display_message(self.console, f"\n[yellow]⚠️ File not found: {target_file}[/yellow]\n")
            display_message(self.console, f"\n[dim]💡 Fix suggestion: {file_fix.suggested_fix[:100]}...[/dim]\n")
            return False
        
        if not target_file.is_file():
            display_message(self.console, f"\n[yellow]⚠️ Not a file: {target_file}[/yellow]\n")
            return False

        # Read original code
        try:
            original_code = target_file.read_text()
        except Exception as e:
            display_message(self.console, f"\n[red]❌ Failed to read file: {e}[/red]\n")
            return False

        # Get corrected code from AI
        corrected = self._get_corrected_code(original_code, file_fix.suggested_fix)
        if not corrected or not getattr(corrected, "code", None):
            display_message(self.console, f"\n[red]❌ AI returned invalid fix[/red]\n")
            return False

        # Backup original
        self._backup_file(target_file)

        # Write corrected code
        try:
            new_code = corrected.code
            target_file.write_text(new_code)
        except Exception as e:
            display_message(self.console, f"\n[red]❌ Failed to write file: {e}[/red]\n")
            return False

        display_message(self.console, f"\n[green]✅ Applied fix to {target_file.name}[/green]\n")

        # Track the modification
        self._track_modified_file(target_file, work_dir)
        
        return True

    def _normalize_path(self, raw_path: str, work_dir: Path, relative_path: str) -> Path | None:
        """
        Normalize file path from AI response.
        """
        raw_path = raw_path.strip()
        
        # Remove duplicated session path if present
        if relative_path in raw_path:
            raw_path = raw_path.split(relative_path, 1)[-1].lstrip("/\\")
        
        # Convert to Path
        path_obj = Path(raw_path)
        
        # If absolute, try to find relative to work_dir's root
        if path_obj.is_absolute():
            # Get the root directory (parent of .stackloop)
            root_dir = Path(self.session.root_directory)
            
            try:
                # Make it relative to root, then apply to work_dir
                relative_to_root = path_obj.relative_to(root_dir)
                return (work_dir / relative_to_root).resolve()
            except ValueError:
                # Path is outside root - just use the filename
                return (work_dir / path_obj.name).resolve()
        
        # It's relative - just append to work_dir
        return (work_dir / path_obj).resolve()

    def _track_modified_file(self, target_file: Path, work_dir: Path):
        """Track modified file in session config"""
        try:
            relative_file_path = target_file.relative_to(work_dir)
            
            if str(relative_file_path) not in self.session.modified_files:
                self.session.modified_files.add(str(relative_file_path))
                
                # Update config
                config_path = work_dir / "stackloop.config.json"
                config_path.write_text(self.session.to_json(indent=2))
                
                display_message(self.console, f"\n[dim]💾 Tracked: {relative_file_path}[/dim]\n")
        except ValueError:
            display_message(self.console, f"\n[yellow]⚠️ File outside work directory, not tracked[/yellow]\n")
        except Exception as e:
            display_message(self.console, f"\n[yellow]⚠️ Could not update config: {e}[/yellow]\n")

    def _build_analysis_prompt(self, stderr: str) -> str:
        return f""" The application failed with the following stacktrace: 
            {stderr} 
            Analyze the stacktrace and return a JSON object with the following fields: 
            - "message": a clear description of the error 
            - "fixes": a list of objects, each containing: 
                - "file_path": the relative path to the file that needs to be fixed, or null if the fix is not file-specific (e.g., env issue) 
                - "suggested_fix": either a code patch (if file exists) or instructions to fix the error 
                - "can_fix_automatically": a boolean indicating if the fix can be applied automatically (e.g not a package installation issue or not an issue the user must manually resolve)
                
            Constraints: 
                - Only consider actual errors for fixing. 
                - Ignore warnings, notes, or non-fatal messages.
                - Always set can_fix_automatically to true if issue can be resolved by modifying code files and false if the user has to manually fix.
                - If multiple files are involved, include all of them in "fixes". 
                - If the error is environment/config related (no file), set file_path=null. 
                - Always return a valid JSON object that matches the ErrorAnalysis schema. 
        """
        
    def _get_corrected_code(self, original_code: str, suggested_fix: str) -> CorrectedCode:
        try:
            
            """Get corrected code from AI with structured output compliance"""
            fix_prompt = f"""
                You are an AI code fixer. 
                You will be given some original source code and a suggested fix. 
                Apply the suggested fix cleanly and return the complete corrected code.

                Respond ONLY with valid JSON that matches this schema:
                {{
                "code": "string  // the full corrected code"
                }}

                Do NOT include explanations, markdown formatting, or any text outside the JSON.

                ---

                Original code:
                {original_code}

                Suggested fix:
                {suggested_fix}
            """
            corrected = self.ai_agent.run_sync(
                user_prompt=fix_prompt,
                output_type=CorrectedCode
            ).output
            return corrected
        except Exception as e:
            display_message(self.console, f"\n[red] ❌ Error during code correction: {e.message}[/red]\n")
            return CorrectedCode(code="")
        
    def _backup_file(self, file_path: Path):
        """Create a backup copy of the file before modification."""
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        try:
            backup_path.write_text(file_path.read_text())
            display_message(self.console, f"\n[dim] 💾 Backup created at {backup_path}[/dim]\n")
        except Exception as e:
            display_message(self.console, f"\n[red] ❌ Failed to create backup for {file_path}: {e}[/red]\n")
