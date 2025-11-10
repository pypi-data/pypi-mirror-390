# InnerLoop

Python SDK for invoking the [OpenCode](https://opencode.ai/) coding CLI in a headless, non-interactive manner.

Supports:

- Synchronous and Asynchronous modes
- Structured outputs using Pydantic models
- Sessions for multiple invocations with shared context
- Permission configuration for reading, writing, web, and bash tools
- Configurable working directory per loop, session, or call

## Installation

You can install `innerloop` using `uv` (recommended) or `pip`.

```bash
# Using uv
uv pip install innerloop

# Using pip
pip install innerloop
```

## Development setup

We manage dependencies with [uv](https://github.com/astral-sh/uv). After cloning the
repository, create the virtual environment and install the dev dependencies:

```bash
uv sync --extra dev
```

When running commands locally (formatting, linting, or tests), always invoke them
through `uv run` so that the virtual environment is used. Running `pytest` directly
via the system Python will skip the managed environment and lead to import errors
such as `ModuleNotFoundError: No module named 'pydantic'`. Because the package code
lives in `src/`, remember to set `PYTHONPATH=src` (or install the project in editable
mode) when invoking Python tooling.

```bash
# Examples
PYTHONPATH=src uv run pytest tests
uv run ruff check src/innerloop
```

## Prerequisites

**InnerLoop requires the OpenCode CLI.** Install it and ensure it's on your PATH:

```bash
opencode --version
```

Quick install (from repository root):

```bash
make install
```

This installs Python dependencies and OpenCode CLI.

If the commands fail, see [Installing OpenCode](docs/guides/installing-opencode.md) for detailed installation instructions.

### Running end-to-end tests

The end-to-end suite exercises the real CLI. Enable it with:

```bash
INNERLOOP_E2E=1 PYTHONPATH=src uv run pytest tests/e2e
```

We default to the free `openrouter/minimax/minimax-m2:free` model (no extra configuration).
Structured validation tests require a more capable model; set `INNERLOOP_E2E_MODEL` if you
have access to another model (e.g. `anthropic/claude-haiku-4-5`).

## Usage

<!-- BEGIN USAGE -->
We summarize results below each snippet without `print()` in the examples.
Summary shows: Output (first 100 chars), Duration (ms), Events.

To render yourself from a Response object:

```python
def show(resp):
    print('Output:', str(resp.output)[:100])
    dur = (resp.time.end - resp.time.start) if resp.time else 0
    print(f'Duration: {dur} ms')
    print(f'Events: {resp.event_count}')
    print(resp.model_dump_json(by_alias=True, indent=4))
```

See: src/innerloop/response.py


### Synchronous Run

```python
from innerloop import Loop

loop = Loop(model="opencode/big-pickle")
response = loop.run("Say hello, one short line.")
```

```text
Output: Hello!
Duration: 2548 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_596213148ffeaPKT8um8y5wtRx",
    "input": "Say hello, one short line.",
    "output": "\nHello!",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712801979,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712802426,
            "type": "text",
            "text": "\nHello!"
        },
        {
            "seq": 3,
            "timestamp": 1762712802487,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712800029,
        "end": 1762712802577
    },
    "structured_output_file": null,
    "event_count": 3
}
```
</details>

### Simple run() Function

```python
from innerloop import run

# Single function call - no Loop needed
response = run("What is 2+2?", model="opencode/big-pickle")
```

```text
Output: 4
Duration: 2543 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_59621270affeWs7kUmRYV74QPl",
    "input": "What is 2+2?",
    "output": "\n4",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712804641,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712805009,
            "type": "text",
            "text": "\n4"
        },
        {
            "seq": 3,
            "timestamp": 1762712805052,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712802580,
        "end": 1762712805123
    },
    "structured_output_file": null,
    "event_count": 3
}
```
</details>

### Simple LLM (No Tools)

```python
from innerloop import Loop, Permission
from pydantic import BaseModel

class SVGImage(BaseModel):
    svg_content: str

# Deny ALL tools - pure LLM response only
loop = Loop(
    model="opencode/big-pickle",
    perms=Permission(
        bash=Permission.DENY,
        edit=Permission.DENY,
        webfetch=Permission.DENY,
    ),
)

prompt = "Generate an SVG of a pelican riding a bicycle. Return only valid SVG markup."
response = loop.run(prompt, response_format=SVGImage)
```

```text
Output: {"svg_content": "<svg viewBox='0 0 400 300' xmlns='http://www.w3.org/2000/svg'>\n  <!-- Bicycle fra…
Duration: 8347 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_596211d78ffegI9oWA8hxClpue",
    "input": "Generate an SVG of a pelican riding a bicycle. Return only valid SVG markup.",
    "output": {
        "svg_content": "<svg viewBox='0 0 400 300' xmlns='http://www.w3.org/2000/svg'>\n  <!-- Bicycle frame -->\n  <path d='M 150 200 L 200 150 L 250 200 L 200 150 L 180 120' stroke='#333' stroke-width='3' fill='none'/>\n  \n  <!-- Bicycle wheels -->\n  <circle cx='150' cy='200' r='25' stroke='#333' stroke-width='3' fill='none'/>\n  <circle cx='250' cy='200' r='25' stroke='#333' stroke-width='3' fill='none'/>\n  <circle cx='150' cy='200' r='3' fill='#333'/>\n  <circle cx='250' cy='200' r='3' fill='#333'/>\n  \n  <!-- Bicycle handlebars -->\n  <path d='M 180 120 L 170 110' stroke='#333' stroke-width='3'/>\n  <path d='M 165 108 L 175 108' stroke='#333' stroke-width='3'/>\n  \n  <!-- Bicycle seat -->\n  <ellipse cx='200' cy='145' rx='15' ry='5' fill='#8B4513'/>\n  \n  <!-- Pelican body -->\n  <ellipse cx='200' cy='100' rx='35' ry='25' fill='white' stroke='#333' stroke-width='2'/>\n  \n  <!-- Pelican head -->\n  <circle cx='175' cy='95' r='15' fill='white' stroke='#333' stroke-width='2'/>\n  \n  <!-- Pelican beak -->\n  <path d='M 160 95 L 145 93 L 148 97 Z' fill='#FFA500' stroke='#333' stroke-width='1'/>\n  \n  <!-- Pelican eye -->\n  <circle cx='170' cy='93' r='3' fill='black'/>\n  <circle cx='171' cy='92' r='1' fill='white'/>\n  \n  <!-- Pelican wings -->\n  <path d='M 200 100 Q 220 85, 240 90 Q 235 105, 210 110 Z' fill='white' stroke='#333' stroke-width='2'/>\n  <path d='M 200 100 Q 180 85, 160 90 Q 165 105, 190 110 Z' fill='white' stroke='#333' stroke-width='2'/>\n  \n  <!-- Pelican legs on pedals -->\n  <line x1='190' y1='120' x2='185' y2='150' stroke='#FFA500' stroke-width='2'/>\n  <line x1='210' y1='120' x2='215' y2='150' stroke='#FFA500' stroke-width='2'/>\n  \n  <!-- Pedals -->\n  <rect x='180' y='148' width='10' height='4' fill='#333'/>\n  <rect x='210' y='148' width='10' height='4' fill='#333'/>\n</svg>"
    },
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712807659,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712813365,
            "type": "text",
            "text": "\n<json>\n{\n  \"svg_content\": \"<svg viewBox='0 0 400 300' xmlns='http://www.w3.org/2000/svg'>\\n  <!-- Bicycle frame -->\\n  <path d='M 150 200 L 200 150 L 250 200 L 200 150 L 180 120' stroke='#333' stroke-width='3' fill='none'/>\\n  \\n  <!-- Bicycle wheels -->\\n  <circle cx='150' cy='200' r='25' stroke='#333' stroke-width='3' fill='none'/>\\n  <circle cx='250' cy='200' r='25' stroke='#333' stroke-width='3' fill='none'/>\\n  <circle cx='150' cy='200' r='3' fill='#333'/>\\n  <circle cx='250' cy='200' r='3' fill='#333'/>\\n  \\n  <!-- Bicycle handlebars -->\\n  <path d='M 180 120 L 170 110' stroke='#333' stroke-width='3'/>\\n  <path d='M 165 108 L 175 108' stroke='#333' stroke-width='3'/>\\n  \\n  <!-- Bicycle seat -->\\n  <ellipse cx='200' cy='145' rx='15' ry='5' fill='#8B4513'/>\\n  \\n  <!-- Pelican body -->\\n  <ellipse cx='200' cy='100' rx='35' ry='25' fill='white' stroke='#333' stroke-width='2'/>\\n  \\n  <!-- Pelican head -->\\n  <circle cx='175' cy='95' r='15' fill='white' stroke='#333' stroke-width='2'/>\\n  \\n  <!-- Pelican beak -->\\n  <path d='M 160 95 L 145 93 L 148 97 Z' fill='#FFA500' stroke='#333' stroke-width='1'/>\\n  \\n  <!-- Pelican eye -->\\n  <circle cx='170' cy='93' r='3' fill='black'/>\\n  <circle cx='171' cy='92' r='1' fill='white'/>\\n  \\n  <!-- Pelican wings -->\\n  <path d='M 200 100 Q 220 85, 240 90 Q 235 105, 210 110 Z' fill='white' stroke='#333' stroke-width='2'/>\\n  <path d='M 200 100 Q 180 85, 160 90 Q 165 105, 190 110 Z' fill='white' stroke='#333' stroke-width='2'/>\\n  \\n  <!-- Pelican legs on pedals -->\\n  <line x1='190' y1='120' x2='185' y2='150' stroke='#FFA500' stroke-width='2'/>\\n  <line x1='210' y1='120' x2='215' y2='150' stroke='#FFA500' stroke-width='2'/>\\n  \\n  <!-- Pedals -->\\n  <rect x='180' y='148' width='10' height='4' fill='#333'/>\\n  <rect x='210' y='148' width='10' height='4' fill='#333'/>\\n</svg>\"\n}\n</json>"
        },
        {
            "seq": 3,
            "timestamp": 1762712813407,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712805128,
        "end": 1762712813475
    },
    "structured_output_file": "/home/user/InnerLoop/.innerloop/structured_default_1762712805125.json",
    "event_count": 3
}
```
</details>

### Asynchronous Run

```python
import asyncio
from innerloop import Loop

async def main():
    loop = Loop(model="opencode/big-pickle")
    async with loop.asession() as s:
        await s("Remember this number: 42")
        response = await s("What was the number?")

asyncio.run(main())
```

```text
Output: 42
Duration: 2794 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_59620fd19ffed4rMsATeal7B4f",
    "input": "What was the number?",
    "output": "\n42",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712818464,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712818993,
            "type": "text",
            "text": "\n42"
        },
        {
            "seq": 3,
            "timestamp": 1762712819036,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712816308,
        "end": 1762712819102
    },
    "structured_output_file": null,
    "event_count": 3
}
```
</details>

### Tool Use (with workdir)

```python
from innerloop import Loop, allow

loop = Loop(
    model="opencode/big-pickle",
    perms=allow("bash"),
)
loop.default_workdir = "src/innerloop"
response = loop.run("Use bash: ls -1\nReturn only the raw command output.")
```

```text
Output: __init__.py
__pycache__
api.py
capabilities.py
config.py
errors.py
events.py
helper.py
httpjail.py
…
Duration: 5949 ms
Events: 7
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_59620e6faffeDr0K8ZZ02MBqB6",
    "input": "Use bash: ls -1\nReturn only the raw command output.",
    "output": "\n__init__.py\n__pycache__\napi.py\ncapabilities.py\nconfig.py\nerrors.py\nevents.py\nhelper.py\nhttpjail.py\ninvoke.py\nmcp.py\noutput.py\npermissions.py\nproc.py\nproviders.py\nrequest.py\nresponse.py\nstructured.py\nusage.py",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712822042,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712822527,
            "type": "tool_use",
            "output": "__init__.py\n__pycache__\napi.py\ncapabilities.py\nconfig.py\nerrors.py\nevents.py\nhelper.py\nhttpjail.py\ni… (truncated)",
            "status": "completed",
            "tool": "bash"
        },
        {
            "seq": 3,
            "timestamp": 1762712822926,
            "type": "text",
            "text": ""
        },
        {
            "seq": 4,
            "timestamp": 1762712822966,
            "type": "step_finish"
        },
        {
            "seq": 5,
            "timestamp": 1762712823729,
            "type": "step_start"
        },
        {
            "seq": 6,
            "timestamp": 1762712824959,
            "type": "text",
            "text": "\n__init__.py\n__pycache__\napi.py\ncapabilities.py\nconfig.py\nerrors.py\nevents.py\nhelper.py\nhttpjail.py\ninvoke.py\nmcp.py\noutput.py\npermissions.py\nproc.py\nproviders.py\nrequest.py\nresponse.py\nstructured.py\nusage.py"
        },
        {
            "seq": 7,
            "timestamp": 1762712824995,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712819105,
        "end": 1762712825054
    },
    "structured_output_file": null,
    "event_count": 7
}
```
</details>

### Synchronous Session

```python
from innerloop import Loop

loop = Loop(model="opencode/big-pickle")
with loop.session() as s:
    s("Please remember this word for me: avocado")
    response = s("What was the word I asked you to remember?")
```

```text
Output: avocado
Duration: 9132 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_59620cfbeffe2F90DwEBrZpwcc",
    "input": "What was the word I asked you to remember?",
    "output": "\navocado",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712836250,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712836794,
            "type": "text",
            "text": "\navocado"
        },
        {
            "seq": 3,
            "timestamp": 1762712836842,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712827788,
        "end": 1762712836920
    },
    "structured_output_file": null,
    "event_count": 3
}
```
</details>

### Asynchronous Session

```python
import asyncio
from innerloop import Loop

async def main():
    loop = Loop(model="opencode/big-pickle")
    async with loop.asession() as s:
        await s("Remember this number: 42")
        response = await s("What was the number?")

asyncio.run(main())
```

```text
Output: 42
Duration: 2559 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_59620a150ffefqTes7yy6RUHuU",
    "input": "What was the number?",
    "output": "\n42",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712841633,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712842025,
            "type": "text",
            "text": "\n42"
        },
        {
            "seq": 3,
            "timestamp": 1762712842078,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712839595,
        "end": 1762712842154
    },
    "structured_output_file": null,
    "event_count": 3
}
```
</details>

### Structured Output

```python
from innerloop import Loop, allow
from pydantic import BaseModel

class HNStory(BaseModel):
    title: str
    url: str
    points: int
    comments: int

class HNTop(BaseModel):
    stories: list[HNStory]

loop = Loop(
    model="opencode/big-pickle",
    perms=allow(webfetch=True),
)

prompt = (
    "Using web search, find the current top 5 stories on Hacker News.\n"
    "Prefer news.ycombinator.com (front page or item pages). For each,\n"
    "return: title, url, points (int), comments (int). Output JSON with\n"
    "a 'stories' array. If counts are missing, open the item page and\n"
    "extract them. Keep titles unmodified.\n"
)
response = loop.run(prompt, response_format=HNTop)
```

```text
Output: The Manuscripts of Edsger W. Dijkstra — https://www.cs.utexas.edu/~EWD/
Duration: 14913 ms
Events: 11
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_596201786ffeQbrIohyd3aonMZ",
    "input": "Using web search, find the current top 5 stories on Hacker News.\nPrefer news.ycombinator.com (front page or item pages). For each,\nreturn: title, url, points (int), comments (int). Output JSON with\na 'stories' array. If counts are missing, open the item page and\nextract them. Keep titles unmodified.\n",
    "output": {
        "stories": [
            {
                "title": "The Manuscripts of Edsger W. Dijkstra",
                "url": "https://www.cs.utexas.edu/~EWD/",
                "points": 94,
                "comments": 26
            },
            {
                "title": "Marble Fountain",
                "url": "https://willmorrison.net/posts/marble-fountain/",
                "points": 42,
                "comments": 2
            },
            {
                "title": "Montana Becomes First State to Enshrine 'Right to Compute' into Law",
                "url": "https://montananewsroom.com/montana-becomes-first-state-to-enshrine-right-to-compute-into-law/",
                "points": 140,
                "comments": 71
            },
            {
                "title": "The Principles of Diffusion Models",
                "url": "https://arxiv.org/abs/2510.21890",
                "points": 32,
                "comments": 3
            },
            {
                "title": "AI isn't replacing jobs. AI spending is",
                "url": "https://www.fastcompany.com/91435192/chatgpt-llm-openai-jobs-amazon",
                "points": 252,
                "comments": 111
            }
        ]
    },
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712874269,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712874952,
            "type": "tool_use",
            "output": "Hacker News\n\n[![](y18.svg)](https://news.ycombinator.com)\n\n**[Hacker News](news)**[new](newest) | [p… (truncated)",
            "status": "completed",
            "tool": "webfetch"
        },
        {
            "seq": 3,
            "timestamp": 1762712874952,
            "type": "text",
            "text": "\nI'll fetch the top 5 stories from Hacker News and extract the required information."
        },
        {
            "seq": 4,
            "timestamp": 1762712875014,
            "type": "step_finish"
        },
        {
            "seq": 5,
            "timestamp": 1762712876018,
            "type": "step_start"
        },
        {
            "seq": 6,
            "timestamp": 1762712878338,
            "type": "tool_use",
            "output": "",
            "status": "completed",
            "tool": "write"
        },
        {
            "seq": 7,
            "timestamp": 1762712878811,
            "type": "text",
            "text": "\nNow I'll extract the top 5 stories from the front page and create the JSON output:"
        },
        {
            "seq": 8,
            "timestamp": 1762712878855,
            "type": "step_finish"
        },
        {
            "seq": 9,
            "timestamp": 1762712880136,
            "type": "step_start"
        },
        {
            "seq": 10,
            "timestamp": 1762712886981,
            "type": "text",
            "text": "\nSuccessfully fetched the top 5 stories from Hacker News and saved the JSON data to the specified file."
        },
        {
            "seq": 11,
            "timestamp": 1762712887034,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712872203,
        "end": 1762712887116
    },
    "structured_output_file": "/home/user/InnerLoop/.innerloop/structured_default_1762712872201.json",
    "event_count": 11
}
```
</details>

### Providers — LM Studio (local)

```python
from innerloop import Loop

loop = Loop(
    model="lmstudio/google/gemma-3n-e4b",
    providers={
        "lmstudio": {
            "options": {"baseURL": "http://127.0.0.1:1234/v1"}
        },
    },
)

response = loop.run("In one concise sentence, say something creative about coding.")
```

```text
Output: None
Duration: n/a ms
Events: 0
```

<details>
  <summary>JSON Output</summary>

```json
{
    "note": "LM Studio example requires a running server.",
    "how_to": [
        "Start LM Studio and load google/gemma-3n-e4b",
        "Ensure LM Studio is listening at http://127.0.0.1:1234/v1"
    ],
    "error": "Process exited with code 1."
}
```
</details>

### MCP — Remote server (Context7)

```python
from innerloop import Loop, mcp

loop = Loop(
    model="opencode/big-pickle",
    mcp=mcp(context7="https://mcp.context7.com/mcp"),
)
prompt = (
    "Use the context7 MCP server to search for FastAPI's latest "
    "async database patterns. Summarize in 2-3 sentences."
)
response = loop.run(prompt)
```

```text
Output: FastAPI's latest async database patterns emphasize using `async def` endpoints with dependency inje…
Duration: 7989 ms
Events: 11
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5961fd83dffef8t2e5fKkqHyzD",
    "input": "Use the context7 MCP server to search for FastAPI's latest async database patterns. Summarize in 2-3 sentences.",
    "output": "\nFastAPI's latest async database patterns emphasize using `async def` endpoints with dependency injection for database connections, leveraging `yield` with `try/finally` blocks for proper resource cleanup. The framework supports both async database operations with libraries like SQLAlchemy 2.0 and SQLModel, while maintaining compatibility with synchronous code through regular `def` functions when needed.",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762712891038,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762712891528,
            "type": "tool_use",
            "output": "Available Libraries (top matches):\n\nEach result includes:\n- Library ID: Context7-compatible identifi… (truncated)",
            "status": "completed",
            "tool": "context7_resolve-library-id"
        },
        {
            "seq": 3,
            "timestamp": 1762712891626,
            "type": "text",
            "text": ""
        },
        {
            "seq": 4,
            "timestamp": 1762712891675,
            "type": "step_finish"
        },
        {
            "seq": 5,
            "timestamp": 1762712892677,
            "type": "step_start"
        },
        {
            "seq": 6,
            "timestamp": 1762712893368,
            "type": "tool_use",
            "output": "### Create FastAPI App with Async Endpoints\n\nSource: https://github.com/fastapi/fastapi/blob/master/… (truncated)",
            "status": "completed",
            "tool": "context7_get-library-docs"
        },
        {
            "seq": 7,
            "timestamp": 1762712893397,
            "type": "text",
            "text": ""
        },
        {
            "seq": 8,
            "timestamp": 1762712893445,
            "type": "step_finish"
        },
        {
            "seq": 9,
            "timestamp": 1762712895012,
            "type": "step_start"
        },
        {
            "seq": 10,
            "timestamp": 1762712896209,
            "type": "text",
            "text": "\nFastAPI's latest async database patterns emphasize using `async def` endpoints with dependency injection for database connections, leveraging `yield` with `try/finally` blocks for proper resource cleanup. The framework supports both async database operations with libraries like SQLAlchemy 2.0 and SQLModel, while maintaining compatibility with synchronous code through regular `def` functions when needed."
        },
        {
            "seq": 11,
            "timestamp": 1762712896255,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762712888341,
        "end": 1762712896330
    },
    "structured_output_file": null,
    "event_count": 11
}
```
</details>

### MCP — Local server (BioMCP)

```python
from innerloop import Loop, mcp

loop = Loop(
    model="opencode/big-pickle",
    mcp=mcp(biomcp="uvx --from biomcp-python biomcp run"),
)
prompt = (
    "Using ONLY the biomcp MCP server tools, look up the BRAF V600E mutation. "
    "List associated cancer types and targeted drug therapies in 2-3 sentences."
)
response = loop.run(prompt, timeout=60.0)
```

```text
Output: The BRAF V600E mutation is a pathogenic oncogenic variant (ClinVar classification) commonly found i…
Duration: 45270 ms
Events: 17
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef13973ffex1A8iL1TRbnQj4",
    "input": "Using ONLY the biomcp MCP server tools, look up the BRAF V600E mutation. List associated cancer types and targeted drug therapies in 2-3 sentences.",
    "output": "The BRAF V600E mutation is a pathogenic oncogenic variant (ClinVar classification) commonly found in melanoma, thyroid cancer, and colorectal cancer, with clinical significance rated at the highest level (Level 1) by OncoKB. Targeted therapies include BRAF inhibitors (dabrafenib, vemurafenib) and MEK inhibitors (trametinib), often used in combination, particularly for melanoma and BRAF V600E-positive thyroid cancer. The mutation is detectable through both genomic testing and immunohistochemistry, with a very low population frequency (0.000004 in gnomAD), confirming its role as a somatic cancer driver rather than a germline variant.",
    "attempts": 1,
    "time": {
        "start": 1762296517158,
        "end": 1762296562428
    },
    "event_count": 17
}
```
</details>
<!-- END USAGE -->
