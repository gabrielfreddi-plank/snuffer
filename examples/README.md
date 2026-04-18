# Snuffer Examples

Examples demonstrating prompt injection detection with snuffer.

## Running

```bash
uv run python -c "
import asyncio
from snuffer.modes.review import run_review

result = asyncio.run(run_review(open('examples/01_direct_injection.txt').read()))
print(result)
"
```

## Examples

- `01_direct_injection.md` — basic "ignore previous instructions" attack
- `02_base64_payload.md` — base64-encoded malicious instruction
- `03_homoglyph_attack.md` — Cyrillic lookalike chars
- `04_multi_step.md` — distributed multi-chunk attack
