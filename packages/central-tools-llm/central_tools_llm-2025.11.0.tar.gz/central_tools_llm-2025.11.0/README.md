# Central Tools for LLM Orchestration

Utilities for routing workloads to the most appropriate LLM, retrying transient failures, and cycling API keys to stay within rate limits. The first provider family supported is Google (Gemini and Gemma), with room to add more providers.

## Features

- Depth-aware routing to the right model family.
- Pluggable retry strategies with exponential backoff for transient errors.
- API key cycling with per-minute and per-day rate limit tracking (supports up to five keys per provider, fewer if not available).
- Reusable abstractions for providers, routing rules, and orchestrator workflows.

## Quickstart

```bash
pip install -e .
```

```python
from central_tools import (
    LLMOrchestrator,
    LLMRequest,
    TaskDepth,
    APIKeyCycler,
    LLMRouter,
    ExponentialBackoffRetry,
    load_env_file,
    load_api_keys_from_placeholders,
    build_cycler,
    GOOGLE_API_KEY_PLACEHOLDERS,
)
from central_tools.providers.google import google_provider_factory
from central_tools.config import RateLimitConfig, build_router

router = LLMRouter()
router.register_model(
    depth=TaskDepth.DEEP,
    model_name="gemini-2.5-pro",
    provider_id="google",
    provider_factory=google_provider_factory("gemini-2.5-pro"),
    metadata={"family": "gemini"}
)

cycler = APIKeyCycler(max_keys=5)

rate_limits = [
    RateLimitConfig(name="per_minute", period_seconds=60, max_calls=15, cooldown_seconds=10),
    RateLimitConfig(name="per_day", period_seconds=24 * 3600, max_calls=1500),
]

load_env_file("config/.env")
api_keys = load_api_keys_from_placeholders(
    GOOGLE_API_KEY_PLACEHOLDERS,
    rate_limits=rate_limits,
)
build_cycler(cycler, api_keys)

retry_strategy = ExponentialBackoffRetry(max_attempts=4)

orchestrator = LLMOrchestrator(router=router, retry_strategy=retry_strategy, api_cycler=cycler)

request = LLMRequest(
    prompt="Summarize the latest research on retrieval-augmented generation.",
    depth=TaskDepth.DEEP,
    metadata={"family": "gemini"},
)
response = orchestrator.generate(request)
print(response.text)
```

See `examples/quickstart.py` for a more complete illustration including custom error handling and `.env` loading.

### Environment File

Copy `config/.env.template` to `config/.env` and fill in your secrets (the repository copy is ignored by `load_env_file` if it is missing). The example script automatically loads this file and falls back to any `GOOGLE_API_KEY_*` variables that are already defined in your shell.

### Cycle test (validate keys & rotation)

We provide a small test script that cycles through configured API keys and asks each registered model for a short confirmation (constrained to ~10 words) to validate both access and the `APIKeyCycler` behaviour.

Run the test from the repository root:

```powershell
python examples/cycle_test.py
```

The script will:

- Load `config/.env` if present (or use `GOOGLE_API_KEY_1..5` environment variables).
- Register keys in the `APIKeyCycler` and then iterate each key once, calling every registered model.
- Report successes (short model-tagged replies) and failures (rate limits or other provider errors). Results are recorded in `examples/cycle_test_results.md` when you run the script locally.

Sample outcome (already executed in this workspace):

- Key `1`: all models returned short confirmation replies (SUCCESS).
- Key `2` & `3`: rate-limited (HTTP 429) — cycler started cooldowns for these keys.
- Key `4`: all models returned short confirmation replies (SUCCESS).

If you see repeated 429s for a key, check billing/quota and either increase quota or remove the key from rotation.

### Discovering Available Models

Model availability changes over time. You can list the current Gemini endpoints exposed to your project:

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_KEY")
for model in genai.list_models():
    print(model.name)
```

## License

MIT
