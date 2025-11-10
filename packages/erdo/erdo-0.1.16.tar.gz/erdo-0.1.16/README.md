# Erdo Agent SDK

Build AI agents and workflows with Python. The Erdo Agent SDK provides a declarative way to create agents that can be executed by the [Erdo platform](https://erdo.ai).

## Installation

```bash
pip install erdo
```

## Quick Start

### Creating Agents

Create agents using the `Agent` class and define steps with actions:

```python
from erdo import Agent, state
from erdo.actions import memory, llm
from erdo.conditions import IsSuccess, GreaterThan

# Create an agent
data_analyzer = Agent(
    name="data analyzer",
    description="Analyzes data files and provides insights",
    running_message="Analyzing data...",
    finished_message="Analysis complete",
)

# Step 1: Search for relevant context
search_step = data_analyzer.step(
    memory.search(
        query=state.query,
        organization_scope="specific",
        limit=5,
        max_distance=0.8
    )
)

# Step 2: Analyze the data with AI
analyze_step = data_analyzer.step(
    llm.message(
        model="claude-sonnet-4-20250514",
        system_prompt="You are a data analyst. Analyze the data and provide insights.",
        query=state.query,
        context=search_step.output.memories,
        response_format={
            "Type": "json_schema",
            "Schema": {
                "type": "object",
                "required": ["insights", "confidence", "recommendations"],
                "properties": {
                    "insights": {"type": "string", "description": "Key insights found"},
                    "confidence": {"type": "number", "description": "Confidence 0-1"},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    ),
    depends_on=search_step,
)
```

### Code Execution with External Files

Use the `@agent.exec` decorator to execute code with external Python files:

```python
from erdo.types import PythonFile

@data_analyzer.exec(
    code_files=[
        PythonFile(filename="analysis_files/analyze.py"),
        PythonFile(filename="analysis_files/utils.py"),
    ]
)
def execute_analysis():
    """Execute detailed analysis using external code files."""
    from analysis_files.analyze import analyze_data
    from analysis_files.utils import prepare_data

    # Prepare and analyze data
    prepared_data = prepare_data(context.parameters.get("dataset", {}))
    results = analyze_data(context)

    return results
```

### Conditional Step Execution

Handle step results with conditions:

```python
from erdo.conditions import IsSuccess, GreaterThan

# Store high-confidence results
analyze_step.on(
    IsSuccess() & GreaterThan("confidence", "0.8"),
    memory.store(
        memory={
            "content": analyze_step.output.insights,
            "description": "High-confidence data analysis results",
            "type": "analysis",
            "tags": ["analysis", "high-confidence"],
        }
    ),
)

# Execute detailed analysis for high-confidence results
analyze_step.on(
    IsSuccess() & GreaterThan("confidence", "0.8"),
    execute_analysis
)
```

### Complex Execution Modes

Use execution modes for advanced workflows:

```python
from erdo import ExecutionMode, ExecutionModeType
from erdo.actions import bot
from erdo.conditions import And, IsAny
from erdo.template import TemplateString

# Iterate over resources
analyze_files = agent.step(
    action=bot.invoke(
        bot_name="file analyzer",
        parameters={"resource": TemplateString("{{resources}}")},
    ),
    key="analyze_files",
    execution_mode=ExecutionMode(
        mode=ExecutionModeType.ITERATE_OVER,
        data="parameters.resource",
        if_condition=And(
            IsAny(key="dataset.analysis_summary", value=["", None]),
            IsAny(key="dataset.type", value=["FILE"]),
        ),
    )
)
```

### Loading Prompts

Use the `Prompt` class to load prompts from files:

```python
from erdo import Prompt

# Load prompts from a directory
prompts = Prompt.load_from_directory("prompts")

# Use in your agent steps
step = agent.step(
    llm.message(
        system_prompt=prompts.system_prompt,
        query=state.query,
    )
)
```

### State and Templating

Access dynamic data using the `state` object and template strings:

```python
from erdo import state
from erdo.template import TemplateString

# Access input parameters
query = state.query
dataset = state.dataset

# Use in template strings
template = TemplateString("Analyzing: {{query}} for dataset {{dataset.id}}")
```

## Core Concepts

### Actions

Actions are the building blocks of your agents. Available action modules:

- `erdo.actions.memory` - Memory storage and search
- `erdo.actions.llm` - Large language model interactions
- `erdo.actions.bot` - Bot invocation and orchestration
- `erdo.actions.codeexec` - Code execution
- `erdo.actions.utils` - Utility functions
- `erdo.actions.resource_definitions` - Resource management

### Conditions

Conditions control when steps execute:

- `IsSuccess()`, `IsError()` - Check step status
- `GreaterThan()`, `LessThan()` - Numeric comparisons
- `TextEquals()`, `TextContains()` - Text matching
- `And()`, `Or()`, `Not()` - Logical operators

### Types

Key types for agent development:

- `Agent` - Main agent class
- `ExecutionMode` - Control step execution behavior
- `PythonFile` - Reference external Python files
- `TemplateString` - Dynamic string templates
- `Prompt` - Prompt management

## Advanced Features

### Multi-Step Dependencies

Create complex workflows with step dependencies:

```python
step1 = agent.step(memory.search(...))
step2 = agent.step(llm.message(...), depends_on=step1)
step3 = agent.step(utils.send_status(...), depends_on=[step1, step2])
```

### Dynamic Data Access

Use the state object to access runtime data:

```python
# Access nested data
user_id = state.user.id
dataset_config = state.dataset.config.type

# Use in actions
step = agent.step(
    memory.search(query=f"data for user {state.user.id}")
)
```

### Error Handling

Handle errors with conditions and fallback steps:

```python
from erdo.conditions import IsError

main_step = agent.step(llm.message(...))

# Handle errors
main_step.on(
    IsError(),
    utils.send_status(
        message="Analysis failed, please try again",
        status="error"
    )
)
```

## Invoking Agents

Use the `invoke()` function to execute agents programmatically:

```python
from erdo import invoke

# Invoke an agent
response = invoke(
    "data-question-answerer",
    messages=[{"role": "user", "content": "What were Q4 sales?"}],
    datasets=["sales-2024"],
    parameters={"time_period": "Q4"},
)

if response.success:
    print(response.result)
else:
    print(f"Error: {response.error}")
```

### Invocation Modes

Control how bot actions are executed for testing and development:

| Mode | Description | Cost |
|------|-------------|------|
| **live** | Execute with real API calls | $$$ per run |
| **replay** | Cache responses, replay on subsequent runs | $$$ first run, FREE after |
| **manual** | Use developer-provided mock responses | FREE always |

```python
# Live mode (default) - real API calls
response = invoke("my-agent", messages=[...], mode="live")

# Replay mode - cache after first run (recommended for testing!)
response = invoke("my-agent", messages=[...], mode="replay")

# Replay with refresh - bypass cache, get fresh response
response = invoke("my-agent", messages=[...], mode={"mode": "replay", "refresh": True})

# Manual mode - use mock responses
response = invoke(
    "my-agent",
    messages=[...],
    mode="manual",
    manual_mocks={
        "llm.message": {
            "status": "success",
            "output": {"content": "Mocked response"}
        }
    }
)
```

**Replay Mode Refresh:**
The `refresh` parameter forces a fresh API call while staying in replay mode:
- First run: Executes and caches the response
- Subsequent runs: Uses cached response (free!)
- With refresh: Bypasses cache, gets fresh response, updates cache

Perfect for updating cached responses after bot changes without switching modes.

## Testing Agents

Write fast, parallel agent tests using `agent_test_*` functions:

```python
from erdo import invoke
from erdo.test import text_contains

def agent_test_csv_sales():
    """Test CSV sales analysis."""
    response = invoke(
        "data-question-answerer",
        messages=[{"role": "user", "content": "What were Q4 sales?"}],
        datasets=["sales-q4-2024"],
        mode="replay",  # Free after first run!
    )

    assert response.success
    result_text = str(response.result)
    assert text_contains(result_text, "sales", case_sensitive=False)
```

Run tests in parallel with the CLI:

```bash
# Run all tests
erdo agent-test tests/test_my_agent.py

# Verbose output
erdo agent-test tests/test_my_agent.py --verbose

# Refresh cached responses (bypass cache for all replay mode tests)
erdo agent-test tests/test_my_agent.py --refresh
```

**Refresh Flag:**
The `--refresh` flag forces all tests using `mode="replay"` to bypass cache and get fresh responses. Perfect for:
- Updating cached responses after bot changes
- Verifying tests with current LLM behavior
- No code changes needed - just add the flag!

### Test Helpers

The `erdo.test` module provides assertion helpers:

```python
from erdo.test import (
    text_contains,      # Check if text contains substring
    text_equals,        # Check exact match
    text_matches,       # Check regex pattern
    json_path_equals,   # Check JSON path value
    json_path_exists,   # Check if JSON path exists
    has_dataset,        # Check if dataset is present
)
```

## CLI Integration

Deploy and manage your agents using the Erdo CLI:

```bash
# Login to your account
erdo login

# Sync your agents to the platform
erdo sync-agent my_agent.py

# Invoke an agent
erdo invoke my-agent --message "Hello!"

# Run agent tests
erdo agent-test tests/test_my_agent.py
```

## Examples

See the `examples/` directory for complete examples:

- `agent_centric_example.py` - Comprehensive agent with multiple steps
- `state_example.py` - State management and templating
- `invoke_example.py` - Agent invocation patterns
- `agent_test_example.py` - Agent testing examples

## API Reference

### Core Classes

- **Agent**: Main agent class for creating workflows
- **ExecutionMode**: Control step execution (iterate, conditional, etc.)
- **Prompt**: Load and manage prompt templates

### Actions

- **memory**: Store and search memories
- **llm**: Interact with language models
- **bot**: Invoke other bots and agents
- **codeexec**: Execute Python code
- **utils**: Utility functions (status, notifications, etc.)

### Conditions

- **Comparison**: `GreaterThan`, `LessThan`, `TextEquals`, etc.
- **Status**: `IsSuccess`, `IsError`, `IsNull`, etc.
- **Logical**: `And`, `Or`, `Not`

### State & Templating

- **state**: Access runtime parameters and data
- **TemplateString**: Dynamic string templates with `{{variable}}` syntax

## License

Commercial License - see LICENSE file for details.
