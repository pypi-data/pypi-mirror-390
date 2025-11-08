# Anthropic API max_tokens Issue

## Issue Description

When using LionAGI QE Fleet agents with Anthropic models (Claude), you may encounter this error:

```python
pydantic_core._pydantic_core.ValidationError: 1 validation error for CreateMessageRequest
max_tokens
  Field required [type=missing]
```

## Root Cause

The issue is in the **LionAGI core library** (not lionagi-qe-fleet):

**File**: `/workspaces/lionagi/lionagi/service/third_party/anthropic_models.py`
**Line**: 72

```python
class CreateMessageRequest(BaseModel):
    """Request model for Anthropic messages API."""

    model: str = Field(..., min_length=1, max_length=256)
    messages: list[Message]
    max_tokens: int = Field(..., ge=1)  # ❌ Required field with no default
```

The `max_tokens` parameter is **required** (indicated by `...`) but LionAGI's `iModel` doesn't automatically provide it when making Anthropic API calls.

## Workaround

**Use OpenAI instead of Anthropic:**

```python
from lionagi import iModel
from lionagi_qe.agents import CoverageAnalyzerAgent

# ✅ WORKS - Use OpenAI
model = iModel(provider="openai", model="gpt-4o-mini")
agent = CoverageAnalyzerAgent("coverage-001", model=model)

# ❌ FAILS - Anthropic has bug
model = iModel(provider="anthropic", model="claude-sonnet-4")
agent = CoverageAnalyzerAgent("coverage-001", model=model)
```

## Affected Components

- **LionAGI Core**: `lionagi.service.third_party.anthropic_models.CreateMessageRequest`
- **Impact**: All LionAGI applications using Anthropic provider
- **Status**: Reported to LionAGI maintainers

## Potential Fixes (for LionAGI Core)

### Option 1: Add Default Value

```python
max_tokens: int = Field(4096, ge=1)  # Default to 4096 tokens
```

### Option 2: Make Optional with Smart Default

```python
max_tokens: int | None = Field(None, ge=1)  # Allow None, handle in endpoint
```

Then in `anthropic_.py`:

```python
def create_payload(self, request: dict | BaseModel, **kwargs):
    payload, headers = super().create_payload(request, **kwargs)

    # Set default max_tokens if not provided
    if "max_tokens" not in payload or payload["max_tokens"] is None:
        payload["max_tokens"] = 4096

    return (payload, headers)
```

### Option 3: Extract from Model Config

Use the model's configuration to determine appropriate max_tokens:

```python
# In iModel or Endpoint
def get_default_max_tokens(model_name: str) -> int:
    """Get default max tokens based on model capabilities"""
    if "claude-3-5-sonnet" in model_name or "claude-sonnet-4" in model_name:
        return 8192  # Sonnet supports up to 8K output
    elif "claude-3-opus" in model_name:
        return 4096  # Opus output limit
    else:
        return 4096  # Conservative default
```

## Testing After Fix

Once LionAGI fixes this, test with:

```python
import asyncio
from lionagi import iModel
from lionagi_qe.core.memory import QEMemory
from lionagi_qe.core.task import QETask
from lionagi_qe.agents import CoverageAnalyzerAgent

async def test_anthropic():
    # Should work after LionAGI fix
    model = iModel(provider="anthropic", model="claude-sonnet-4")
    memory = QEMemory()

    agent = CoverageAnalyzerAgent(
        agent_id="coverage-test",
        model=model,
        memory=memory
    )

    task = QETask(
        task_type="analyze_coverage",
        context={
            "coverage_data": {"overall": 78.5},
            "framework": "pytest"
        }
    )

    result = await agent.execute(task)
    print("Success!", result)

# Run test
asyncio.run(test_anthropic())
```

## Related Issues

- **Reported**: 2025-11-06
- **LionAGI Version**: Latest (as of Nov 2025)
- **Status**: Awaiting LionAGI maintainer response

## Impact on lionagi-qe-fleet

**Current Status**: ✅ No changes needed in lionagi-qe-fleet

All QE agents work correctly with OpenAI models. The issue is isolated to LionAGI's Anthropic provider implementation.

**Recommendation**: Use OpenAI provider until LionAGI fixes the Anthropic integration.

## Cost Comparison (While Using Workaround)

| Model | Provider | Input ($/1M tokens) | Output ($/1M tokens) | Status |
|-------|----------|--------------------:|---------------------:|--------|
| gpt-4o-mini | OpenAI | $0.15 | $0.60 | ✅ Works |
| gpt-4o | OpenAI | $2.50 | $10.00 | ✅ Works |
| claude-sonnet-4 | Anthropic | $3.00 | $15.00 | ❌ Broken |
| claude-3-5-sonnet | Anthropic | $3.00 | $15.00 | ❌ Broken |

**Current Best Choice**: OpenAI `gpt-4o-mini` - cheapest and working perfectly.

---

**Last Updated**: 2025-11-06
**Tracked Issue**: https://github.com/proffesor-for-testing/lionagi-qe-fleet/issues/TBD
