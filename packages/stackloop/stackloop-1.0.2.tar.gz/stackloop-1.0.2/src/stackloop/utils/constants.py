IGNORED_DIRS = {".stackloop", ".git", "__pycache__", "venv", "node_modules"}
DEFAULT_COMMANDS = {
    "Python": "python main.py",
    "Node.js": "npm run build",
    "Go": "go run main.go",
}
MAX_ITERATIONS = 5

SUPPORTED_MODELS = {
    "groq": [
        "llama-3.3-70b-versatile",    
        "llama-3.1-8b-instant",        
        "openai/gpt-oss-120b",          
        "openai/gpt-oss-20b" 
    ],
    "google": [
        "gemini-2.5-pro",           # Google's most powerful coding model, excels at reasoning in long contexts
        "gemini-2.5-flash",         # A faster, more cost-effective alternative to Pro
    ],
    "mistral": [
        "codestral",                # A cutting-edge, 256K context model specifically for coding tasks
        "devstral-medium",          # Optimized for agentic software engineering tasks
        "mistral-large-2.1",        # Top-tier model for high complexity tasks
        "mistral-small-3.2",        # A minor update to 3.1, better instruction following and less repetition
    ],
    "openai": [
        "gpt-5",                    # OpenAI's flagship and strongest coding model with high reasoning ability
        "gpt-4o",
        "gpt-4o-mini",              # An efficient model balancing speed and power at a low cost
    ],
    "anthropic": [
        "claude-opus-4.1",          # Anthropic's most powerful model, improves on previous versions
        "claude-sonnet-4.5",        # The best model in the world for agents and coding tasks
    ]
}
