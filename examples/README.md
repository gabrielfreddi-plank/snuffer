# Snuffer Examples

Documented examples of prompt injection attacks and expected snuffer output.

## Prerequisites

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uv sync
```

## Running an example

```python
import asyncio
from snuffer.modes.review import run_review
from snuffer.formatter import format_report

text = open("examples/fixtures/direct_injection.txt").read()
result = asyncio.run(run_review(text))
print(format_report(result))
```