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

**InnerLoop requires the OpenCode CLI and httpjail.** Install them and ensure both are on your PATH:

```bash
opencode --version
httpjail --version
```

Quick install (from repository root):

```bash
make install
```

This installs Python dependencies, OpenCode CLI, and httpjail in the correct order.

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

loop = Loop(model="anthropic/claude-haiku-4-5")
response = loop.run("Say hello, one short line.")
```

```text
Output: Hello! How can I help you with your code today?
Duration: 4130 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef23b44ffeZmFgxLa3I3TdM6",
    "input": "Say hello, one short line.",
    "output": "Hello! How can I help you with your code today?",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296450555,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296450586,
            "type": "text",
            "text": "Hello! How can I help you with your code today?"
        },
        {
            "seq": 3,
            "timestamp": 1762296450633,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296447869,
        "end": 1762296451999
    },
    "event_count": 3
}
```
</details>

### Asynchronous Run

```python
import asyncio
from innerloop import Loop

async def main():
    loop = Loop(model="anthropic/claude-haiku-4-5")
    async with loop.asession() as s:
        await s("Remember this number: 42")
        response = await s("What was the number?")

asyncio.run(main())
```

```text
Output: The number was **42**.
Duration: 4325 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef22b71ffelg8VEnUr5vtJwc",
    "input": "What was the number?",
    "output": "The number was **42**.",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296457533,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296457689,
            "type": "text",
            "text": "The number was **42**."
        },
        {
            "seq": 3,
            "timestamp": 1762296457720,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296455904,
        "end": 1762296460229
    },
    "event_count": 3
}
```
</details>

### Tool Use (with workdir)

```python
from innerloop import Loop, allow

loop = Loop(
    model="anthropic/claude-haiku-4-5",
    perms=allow("bash"),
)
loop.default_workdir = "src/innerloop"
response = loop.run("Use bash: ls -1\nReturn only the raw command output.")
```

```text
Output: __init__.py
__pycache__
api.py
config.py
errors.py
events.py
helper.py
invoke.py
mcp.py
output.py
p…
Duration: 5711 ms
Events: 6
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef20b54ffele3CQIsA4pPlWB",
    "input": "Use bash: ls -1\nReturn only the raw command output.",
    "output": "__init__.py\n__pycache__\napi.py\nconfig.py\nerrors.py\nevents.py\nhelper.py\ninvoke.py\nmcp.py\noutput.py\npermissions.py\nproc.py\nproviders.py\nrequest.py\nresponse.py\nstructured.py\nusage.py",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296462447,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296462977,
            "type": "tool_use",
            "output": "__init__.py\n__pycache__\napi.py\nconfig.py\nerrors.py\nevents.py\nhelper.py\ninvoke.py\nmcp.py\noutput.py\npe… (truncated)",
            "status": "completed",
            "tool": "bash"
        },
        {
            "seq": 3,
            "timestamp": 1762296462989,
            "type": "step_finish"
        },
        {
            "seq": 4,
            "timestamp": 1762296464490,
            "type": "step_start"
        },
        {
            "seq": 5,
            "timestamp": 1762296464515,
            "type": "text",
            "text": "__init__.py\n__pycache__\napi.py\nconfig.py\nerrors.py\nevents.py\nhelper.py\ninvoke.py\nmcp.py\noutput.py\npermissions.py\nproc.py\nproviders.py\nrequest.py\nresponse.py\nstructured.py\nusage.py"
        },
        {
            "seq": 6,
            "timestamp": 1762296464555,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296460229,
        "end": 1762296465940
    },
    "event_count": 6
}
```
</details>

### Synchronous Session

```python
from innerloop import Loop

loop = Loop(model="anthropic/claude-haiku-4-5")
with loop.session() as s:
    s("Please remember this word for me: avocado")
    response = s("What was the word I asked you to remember?")
```

```text
Output: The word you asked me to remember was **avocado**.
Duration: 4167 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef1f501ffet0jQMRAi7DTrSp",
    "input": "What was the word I asked you to remember?",
    "output": "The word you asked me to remember was **avocado**.",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296471689,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296471886,
            "type": "text",
            "text": "The word you asked me to remember was **avocado**."
        },
        {
            "seq": 3,
            "timestamp": 1762296472020,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296469798,
        "end": 1762296473965
    },
    "event_count": 3
}
```
</details>

### Asynchronous Session

```python
import asyncio
from innerloop import Loop

async def main():
    loop = Loop(model="anthropic/claude-haiku-4-5")
    async with loop.asession() as s:
        await s("Remember this number: 42")
        response = await s("What was the number?")

asyncio.run(main())
```

```text
Output: The number was **42**.
Duration: 6191 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef1d5a8ffe0OUEnRRKtvBy1P",
    "input": "What was the number?",
    "output": "The number was **42**.",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296479392,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296479534,
            "type": "text",
            "text": "The number was **42**."
        },
        {
            "seq": 3,
            "timestamp": 1762296479580,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296477429,
        "end": 1762296483620
    },
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
    model="anthropic/claude-haiku-4-5",
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
Output: CPUs and GPUs to Become More Expensive After TSMC Price Hike in 2026 — https://www.guru3d.com/story…
Duration: 10236 ms
Events: 7
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef1aff8ffegJ6nGoztbhINiC",
    "input": "Using web search, find the current top 5 stories on Hacker News.\nPrefer news.ycombinator.com (front page or item pages). For each,\nreturn: title, url, points (int), comments (int). Output JSON with\na 'stories' array. If counts are missing, open the item page and\nextract them. Keep titles unmodified.\n",
    "output": {
        "stories": [
            {
                "title": "CPUs and GPUs to Become More Expensive After TSMC Price Hike in 2026",
                "url": "https://www.guru3d.com/story/cpus-and-gpus-to-become-more-expensive-after-tsmc-price-hike-in-2026/",
                "points": 58,
                "comments": 44
            },
            {
                "title": "NoLongerEvil-Thermostat – Nest Generation 1 and 2 Firmware",
                "url": "https://github.com/codykociemba/NoLongerEvil-Thermostat",
                "points": 241,
                "comments": 70
            },
            {
                "title": "This Day in 1988, the Morris worm infected 10% of the Internet within 24 hours",
                "url": "https://www.tomshardware.com/tech-industry/cyber-security/on-this-day-in-1988-the-morris-worm-slithered-out-and-sparked-a-new-era-in-cybersecurity-10-percent-of-the-internet-was-infected-within-24-hours",
                "points": 221,
                "comments": 126
            },
            {
                "title": "Send this article to your friend who still thinks the cloud is a good idea",
                "url": "https://rameerez.com/send-this-article-to-your-friend-who-still-thinks-the-cloud-is-a-good-idea/",
                "points": 25,
                "comments": 12
            },
            {
                "title": "Pg_lake: Postgres with Iceberg and data lake access",
                "url": "https://github.com/Snowflake-Labs/pg_lake",
                "points": 238,
                "comments": 73
            }
        ]
    },
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296486243,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296486444,
            "type": "text",
            "text": "I'll fetch the top stories from Hacker News for you."
        },
        {
            "seq": 3,
            "timestamp": 1762296486923,
            "type": "tool_use",
            "output": "<html lang=\"en\" op=\"news\"><head><meta name=\"referrer\" content=\"origin\"><meta name=\"viewport\" content… (truncated)",
            "status": "completed",
            "tool": "webfetch"
        },
        {
            "seq": 4,
            "timestamp": 1762296486938,
            "type": "step_finish"
        },
        {
            "seq": 5,
            "timestamp": 1762296488138,
            "type": "step_start"
        },
        {
            "seq": 6,
            "timestamp": 1762296492395,
            "type": "text",
            "text": "I've extracted the top 5 stories from the Hacker News front page. All required data (title, URL, points, and comments) is available from the front page, so no additional item page fetches are needed.\n\n```json\n{\n  \"stories\": [\n    {\n      \"title\": \"CPUs and GPUs to Become More Expensive After TSMC Price Hike in 2026\",\n      \"url\": \"https://www.guru3d.com/story/cpus-and-gpus-to-become-more-expensive-after-tsmc-price-hike-in-2026/\",\n      \"points\": 58,\n      \"comments\": 44\n    },\n    {\n      \"title\": \"NoLongerEvil-Thermostat – Nest Generation 1 and 2 Firmware\",\n      \"url\": \"https://github.com/codykociemba/NoLongerEvil-Thermostat\",\n      \"points\": 241,\n      \"comments\": 70\n    },\n    {\n      \"title\": \"This Day in 1988, the Morris worm infected 10% of the Internet within 24 hours\",\n      \"url\": \"https://www.tomshardware.com/tech-industry/cyber-security/on-this-day-in-1988-the-morris-worm-slithered-out-and-sparked-a-new-era-in-cybersecurity-10-percent-of-the-internet-was-infected-within-24-hours\",\n      \"points\": 221,\n      \"comments\": 126\n    },\n    {\n      \"title\": \"Send this article to your friend who still thinks the cloud is a good idea\",\n      \"url\": \"https://rameerez.com/send-this-article-to-your-friend-who-still-thinks-the-cloud-is-a-good-idea/\",\n      \"points\": 25,\n      \"comments\": 12\n    },\n    {\n      \"title\": \"Pg_lake: Postgres with Iceberg and data lake access\",\n      \"url\": \"https://github.com/Snowflake-Labs/pg_lake\",\n      \"points\": 238,\n      \"comments\": 73\n    }\n  ]\n}\n```"
        },
        {
            "seq": 7,
            "timestamp": 1762296492458,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296483623,
        "end": 1762296493859
    },
    "event_count": 7
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
Output: Coding is like sculpting with logic, chipping away at the unknown until a functional masterpiece em…
Duration: 4905 ms
Events: 3
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef18801ffedGoXu4DjlR8Laa",
    "input": "In one concise sentence, say something creative about coding.",
    "output": "Coding is like sculpting with logic, chipping away at the unknown until a functional masterpiece emerges.",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296497731,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296498089,
            "type": "text",
            "text": "Coding is like sculpting with logic, chipping away at the unknown until a functional masterpiece emerges."
        },
        {
            "seq": 3,
            "timestamp": 1762296498109,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296493859,
        "end": 1762296498764
    },
    "event_count": 3
}
```
</details>

### MCP — Remote server (Context7)

```python
from innerloop import Loop, mcp

loop = Loop(
    model="anthropic/claude-sonnet-4-5",
    mcp=mcp(context7="https://mcp.context7.com/mcp"),
)
prompt = (
    "Use the context7 MCP server to search for FastAPI's latest "
    "async database patterns. Summarize in 2-3 sentences."
)
response = loop.run(prompt)
```

```text
Output: Based on the FastAPI documentation, the latest async database patterns focus on **dependency inject…
Duration: 15206 ms
Events: 10
```

<details>
  <summary>JSON Output</summary>

```json
{
    "session_id": "ses_5aef174d3ffe71UZVFdrHOWf2W",
    "input": "Use the context7 MCP server to search for FastAPI's latest async database patterns. Summarize in 2-3 sentences.",
    "output": "Based on the FastAPI documentation, the latest async database patterns focus on **dependency injection with `yield` for resource management**, using `async def` dependencies to create database sessions that are automatically closed after request completion. FastAPI recommends using SQLModel with session dependencies (e.g., `SessionDep`) that leverage context managers to ensure proper session lifecycle management. For production, patterns include **explicit session closing** for long-running or streaming responses, pagination with `limit`/`offset` parameters, and separating data models (`HeroBase`, `HeroCreate`, `HeroPublic`) to control what data is exposed in API responses versus what's stored in the database.",
    "attempts": 1,
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296500655,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296501560,
            "type": "text",
            "text": "I'll search for FastAPI's latest async database patterns using the Context7 MCP server."
        },
        {
            "seq": 3,
            "timestamp": 1762296502098,
            "type": "tool_use",
            "output": "Available Libraries (top matches):\n\nEach result includes:\n- Library ID: Context7-compatible identifi… (truncated)",
            "status": "completed",
            "tool": "context7_resolve_library_id"
        },
        {
            "seq": 4,
            "timestamp": 1762296502111,
            "type": "step_finish"
        },
        {
            "seq": 5,
            "timestamp": 1762296504938,
            "type": "step_start"
        },
        {
            "seq": 6,
            "timestamp": 1762296506454,
            "type": "tool_use",
            "output": "### FastAPI Dependency with `yield` and `async with` (Python)\n\nSource: https://github.com/fastapi/fa… (truncated)",
            "status": "completed",
            "tool": "context7_get_library_docs"
        },
        {
            "seq": 7,
            "timestamp": 1762296506468,
            "type": "step_finish"
        },
        {
            "seq": 8,
            "timestamp": 1762296507900,
            "type": "step_start"
        },
        {
            "seq": 9,
            "timestamp": 1762296512451,
            "type": "text",
            "text": "Based on the FastAPI documentation, the latest async database patterns focus on **dependency injection with `yield` for resource management**, using `async def` dependencies to create database sessions that are automatically closed after request completion. FastAPI recommends using SQLModel with session dependencies (e.g., `SessionDep`) that leverage context managers to ensure proper session lifecycle management. For production, patterns include **explicit session closing** for long-running or streaming responses, pagination with `limit`/`offset` parameters, and separating data models (`HeroBase`, `HeroCreate`, `HeroPublic`) to control what data is exposed in API responses versus what's stored in the database."
        },
        {
            "seq": 10,
            "timestamp": 1762296512507,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296498764,
        "end": 1762296513970
    },
    "event_count": 10
}
```
</details>

### MCP — Local server (BioMCP)

```python
from innerloop import Loop, mcp

loop = Loop(
    model="anthropic/claude-sonnet-4-5",
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
    "events": [
        {
            "seq": 1,
            "timestamp": 1762296517158,
            "type": "step_start"
        },
        {
            "seq": 2,
            "timestamp": 1762296517572,
            "type": "text",
            "text": "I'll help you look up information about the BRAF V600E mutation using the biomcp tools."
        },
        {
            "seq": 3,
            "timestamp": 1762296521505,
            "type": "tool_use",
            "output": "{\n  \"domain\": \"thinking\",\n  \"result\": \"Added thought 1 to main sequence. Progress: 1/3 thoughts. Nex… (truncated)",
            "status": "completed",
            "tool": "biomcp_think"
        },
        {
            "seq": 4,
            "timestamp": 1762296521573,
            "type": "step_finish"
        },
        {
            "seq": 5,
            "timestamp": 1762296523099,
            "type": "step_start"
        },
        {
            "seq": 6,
            "timestamp": 1762296525150,
            "type": "tool_use",
            "output": "{\n  \"domain\": \"thinking\",\n  \"result\": \"Added thought 2 to main sequence. Progress: 2/3 thoughts. Nex… (truncated)",
            "status": "completed",
            "tool": "biomcp_think"
        },
        {
            "seq": 7,
            "timestamp": 1762296525193,
            "type": "step_finish"
        },
        {
            "seq": 8,
            "timestamp": 1762296528026,
            "type": "step_start"
        },
        {
            "seq": 9,
            "timestamp": 1762296529676,
            "type": "tool_use",
            "output": "{\n  \"domain\": \"thinking\",\n  \"result\": \"Added thought 3 to main sequence. Progress: 3/3 thoughts. Thi… (truncated)",
            "status": "completed",
            "tool": "biomcp_think"
        },
        {
            "seq": 10,
            "timestamp": 1762296529728,
            "type": "step_finish"
        },
        {
            "seq": 11,
            "timestamp": 1762296531406,
            "type": "step_start"
        },
        {
            "seq": 12,
            "timestamp": 1762296537258,
            "type": "tool_use",
            "output": "\n### OncoKB Gene Summary\n| Gene | Type | Highest Level | Clinical Implications |\n|------|------|----… (truncated)",
            "status": "completed",
            "tool": "biomcp_variant_searcher"
        },
        {
            "seq": 13,
            "timestamp": 1762296551419,
            "type": "tool_use",
            "output": "\n### cBioPortal Summary for BRAF\n- **Mutation Frequency**: 0.0% (0 mutations in 0 samples)\n- **Studi… (truncated)",
            "status": "completed",
            "tool": "biomcp_article_searcher"
        },
        {
            "seq": 14,
            "timestamp": 1762296551431,
            "type": "step_finish"
        },
        {
            "seq": 15,
            "timestamp": 1762296553160,
            "type": "step_start"
        },
        {
            "seq": 16,
            "timestamp": 1762296557294,
            "type": "text",
            "text": "The BRAF V600E mutation is a pathogenic oncogenic variant (ClinVar classification) commonly found in melanoma, thyroid cancer, and colorectal cancer, with clinical significance rated at the highest level (Level 1) by OncoKB. Targeted therapies include BRAF inhibitors (dabrafenib, vemurafenib) and MEK inhibitors (trametinib), often used in combination, particularly for melanoma and BRAF V600E-positive thyroid cancer. The mutation is detectable through both genomic testing and immunohistochemistry, with a very low population frequency (0.000004 in gnomAD), confirming its role as a somatic cancer driver rather than a germline variant."
        },
        {
            "seq": 17,
            "timestamp": 1762296557359,
            "type": "step_finish"
        }
    ],
    "time": {
        "start": 1762296513971,
        "end": 1762296559241
    },
    "event_count": 17
}
```
</details>
<!-- END USAGE -->
