from pydantic_ai import Agent

from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from rich.console import Console
import typer

from stackloop.cli.display import display_message
from stackloop.core.agent_config import get_api_key
# Add other model classes as needed (DeepSeekModel, etc.)

def get_agent(provider: str, model_name: str, console: Console) -> Agent:
    api_key = get_api_key(provider, console)
    model_classes = {
        "groq": GroqModel(model_name, provider=GroqProvider(api_key=api_key)),
        "openai": OpenAIChatModel(model_name, provider=OpenAIProvider(api_key=api_key)),
        "mistral": MistralModel(model_name, provider=MistralProvider(api_key=api_key)),
        "anthropic": AnthropicModel(model_name, provider=AnthropicProvider(api_key=api_key)),
        "google": GoogleModel(model_name, provider=GoogleProvider(api_key=api_key))
    }

    model = model_classes.get(provider)
    if not model:
        display_message(console, f"\n[red]Unsupported provider: {provider}[/red]\n")
        raise typer.Exit(1)

    return Agent(
        model,
        system_prompt="You are a helpful debugging assistant"
    )
    
