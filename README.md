## Minimal ReAct Agent

- **Provider**: OpenAI (tool calling), or `mock` (offline demo)
- **Tools**: Web search (DuckDuckGo HTML)

### Setup
1. (Optional) Copy `.env.example` to `.env` and set your keys.
2. Install dependencies:

```
pip install -r requirements.txt
```

### Run
- Mock provider (no API keys):
```
python -m agent.cli "Who is the CEO of OpenAI?" --provider mock --max-steps 2
```

- OpenAI provider (requires `OPENAI_API_KEY`):
```
python -m agent.cli "Find the latest NVIDIA earnings headline and summarize" --provider openai --max-steps 3
```

### ENV
See `.env.example` for supported variables.