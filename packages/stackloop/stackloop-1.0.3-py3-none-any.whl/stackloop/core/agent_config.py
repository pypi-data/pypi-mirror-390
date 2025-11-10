import os
import questionary
from rich.console import Console
import typer

from stackloop.cli.display import display_message
from stackloop.utils.constants import SUPPORTED_MODELS


def select_provider() -> str:
    try: 
        models = SUPPORTED_MODELS.keys()

        if len(models) == 1:
            return models[0]

        answer = questionary.select(
            f"Select inference api provider to use:",
            choices=models
        ).ask()
        if answer is None:  # User pressed Ctrl+C
            raise KeyboardInterrupt
            
        return answer
    except KeyboardInterrupt:
        raise  # Let it bubble up to main handler


def get_api_key(provider: str, console: Console) -> str:
    # Pydantic API key mapping
    key_env = {
        "groq": "GROQ_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
    }.get(provider)

    if not key_env:
        display_message(console, f"\n[red]❌ Unsupported provider: {provider}[/red]\n")
        raise typer.Exit(1)

    key = os.getenv(key_env)
    if not key:
        display_message(console, f"\n[bold red]❌ Missing API key for {provider}![/bold red]\n")
        display_message(console, f"\n[dim]Please set [cyan]{key_env}[/cyan] in your .env file.[dim]\n")
        raise typer.Exit(1)
    return key

def select_model(provider: str, console: Console) -> str:
    try:
        models = SUPPORTED_MODELS.get(provider)
        if not models:
            display_message(console, f"\n[red] No models found for provider {provider}[/red]\n")
            raise typer.Exit(1)

        if len(models) == 1:
            return models[0]

        answer = questionary.select(
            f"Select model for {provider}:",
            choices=models
        ).ask()
        
        if answer is None:  # User pressed Ctrl+C
            raise KeyboardInterrupt
            
        return answer
    except KeyboardInterrupt:
        raise  # Let it bubble up to main handler

