# StackLoop

AI-powered debugging agent that automatically runs, analyzes, and fixes your code.

## Installation
```bash
pip install stackloop
```

## Usage
```bash
# Run in current directory
stackloop run

# Run in specific directory
stackloop run /path/to/your/project
```

## Features

- 🤖 AI-powered error analysis
- 🔧 Automatic code fixes
- 🔄 Iterative debugging
- 💾 Safe backups before modifications
- 🎨 Beautiful CLI interface

## Requirements

- Python 3.9+
- API keys for inference API providers (Groq, OpenAI, Anthropic, etc.)
## Configuration

Create a `.env` file in your project directory with at least one API key:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
```

## License

MIT License