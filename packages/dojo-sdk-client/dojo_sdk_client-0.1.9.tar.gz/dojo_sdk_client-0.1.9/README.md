# Dojo SDK Client

Python client SDK for interacting with the Dojo API

## Installation

```bash
uv add dojo-sdk-client
```

if you want to use our example agents:

```bash
uv add "dojo-sdk-client[agents]"
```

if you want to use our multi-turn environment with [verifiers](https://github.com/willccbb/verifiers)

```bash
uv add "dojo-sdk-client[multi_turn_env]"
```

if you want to use our browserbase engine:

```bash
uv add "dojo-sdk-client[browserbase]"
```

## Quick Start

### Basic Task Execution

```python
from dojo_sdk_client import BaseDojoClient
from dojo_sdk_client.types import TaskStatus

client = BaseDojoClient(api_key="your-api-key")

# Create and start task
exec_id = await client.create_task(
    task_id="tic-tac-toe",
    state={"board": [[0]*3 for _ in range(3)]}
)
await client.start_task(exec_id)

status = await client.get_task_status(exec_id)
while status.status == TaskStatus.QUEUED:
    await asyncio.sleep(1)
    status = await client.get_task_status(exec_id)

# Submit action
action = {"type": "click", "x": 100, "y": 100}
await client.submit_action(exec_id, action, "Making move")

```

### Agent Evaluation

```python
from dojo_sdk_client import DojoEvalClient

eval_client = DojoEvalClient(agent=your_agent, api_key="your-api-key")

results = await eval_client.evaluate(
    tasks=["tic-tac-toe", "2048"],
    num_runners=2
)
```

### Changing Engines

```python
from dojo_sdk_client.engines.browserbase_engine import BrowserBaseEngine

engine = BrowserBaseEngine(
    api_key="your-browserbase-api-key",
    project_id="your-browserbase-project-id",
    dojo_api_key="your-dojo-api-key"
)

eval_client = DojoEvalClient(agent=your_agent, api_key="your-api-key", engine=engine)
```

BrowserBase engine has a concurrency limit that can be controlled with the `BROWSERBASE_CONCURRENT_LIMIT` environment variable.

## Clients

**BaseDojoClient** - Low-level HTTP client for direct API interactions

**DojoEvalClient** - High-level client for running automated evaluations

**MultiTurnEnv** - Multi-turn environment for running evaluations with Verifiers

## Engines

**DojoEngine** - Default engine for running tasks using Dojo

**BrowserBaseEngine** - Engine for running tasks using BrowserBase

## Documentation

Visit [docs.trydojo.ai](https://docs.trydojo.ai) for complete documentation.
