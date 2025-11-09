from pathlib import Path
from rich.console import Console

from stackloop.cli.display import display_message
from stackloop.models.corrected_code import CorrectedCode
from stackloop.models.error_analysis import ErrorAnalysis, FileFix
from stackloop.models.session_config import SessionConfig


class CodeFixer:
    def __init__(self, ai_agent, console: Console, session: SessionConfig):
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
            if file_fix.file_path:
                file_updated = self._apply_file_fix(file_fix, relative_path)
            else:
                display_message(self.console, f"\n[yellow]💡 {file_fix.suggested_fix}[/yellow]\n")       
        return file_updated
    
    def _apply_file_fix(self, file_fix: FileFix, relative_path: str) -> bool:
        """Apply fix to a specific file."""
        # Normalize and fix target file path
        raw_path = str(file_fix.file_path)
        work_dir = self.session.working_directory.resolve()

        target_file = None

        if relative_path in raw_path:
            # Strip work_dir prefix if duplicated
            relative_part = raw_path.split(relative_path, 1)[-1].lstrip("/\\")
            # # Keep refernce to file for syncing
            if relative_part not in self.session.modified_files:
                self.session.modified_files.add(relative_part)
                config_path = (self.session.working_directory / "stackloop.config.json").resolve()
                config_path.write_text(self.session.to_json(indent=2))
    
            target_file = work_dir / relative_part
        else:
            # Assume the fixer returned a relative path
            target_file = (work_dir / raw_path).resolve()

        # Validate the resolved path
        if not target_file.exists():
            display_message(self.console, f"\n[yellow] ⚠️ File not found: {target_file}[/yellow]\n")
            return False
        
        # Debug logging (optional)
        display_message(self.console, f"\n[dim] 🔍 Applying fix to: {target_file}[/dim]\n")

        # Validation
        if not target_file.is_file():
            display_message(self.console, f"\n[yellow] ⚠️ File not found: {target_file}[/yellow]\n")
            return False

        try:
            original_code = target_file.read_text()
        except Exception as e:
            display_message(self.console, f"\n[red] ❌ Failed to read {file_fix.file_path}: {e}[/red]\n")
            return False

        # Generate the corrected code
        corrected = self._get_corrected_code(original_code, file_fix.suggested_fix)

        if not corrected or not getattr(corrected, "code", None):
            display_message(self.console, f"\n[red] ❌ Invalid fix output for {target_file.name}[/red]\n")
            return False

        # Backup and apply fix
        self._backup_file(target_file)

        try:
            new_code = corrected.code
        except AttributeError:
            # fallback in case structure is simpler
            new_code = getattr(corrected, "code", "")

        target_file.write_text(new_code)
        display_message(self.console, f"\n[green] ✅ Applied fix to {target_file.name}[/green]\n")

        return True

    def _build_analysis_prompt(self, stderr: str) -> str:
        return f""" The application failed with the following stacktrace: 
            {stderr} 
            Analyze the stacktrace and return a JSON object with the following fields: 
            - "message": a clear description of the error 
            - "fixes": a list of objects, each containing: 
                - "file_path": the relative path to the file that needs to be fixed, or null if the fix is not file-specific (e.g., env issue) 
                - "suggested_fix": either a code patch (if file exists) or instructions to fix the error 
                
            Constraints: 
                - Only consider actual errors for fixing. 
                - Ignore warnings, notes, or non-fatal messages.
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
            display_message(self.console, f"[red] ❌ Failed to create backup for {file_path}: {e}[/red]\n")
