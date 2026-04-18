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

## Examples

| File | Attack type | Mode |
|------|-------------|------|
| `01_direct_injection.md` | "ignore previous instructions" | review |
| `02_base64_payload.md` | base64-encoded malicious command | review |
| `03_homoglyph_attack.md` | Cyrillic lookalike chars | review |
| `04_multi_step_attack.md` | Distributed 3-part attack across chunks | review |
| `05_clean_text.md` | Benign text — zero warnings expected | review |
| `06_filter_mode.md` | Filter mode removing malicious chunk | filter |
