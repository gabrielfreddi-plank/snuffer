# Example 05 — Clean Text (Zero Warnings)

## Input

```
The quick brown fox jumps over the lazy dog. This is a completely benign piece of text
that contains no malicious instructions whatsoever. It is simply used to verify that
snuffer correctly returns no warnings for legitimate content.
```

## Snuffer Call

```python
import asyncio
from snuffer.modes.review import run_review
from snuffer.formatter import format_report

text = (
    "The quick brown fox jumps over the lazy dog. This is a completely benign piece of text "
    "that contains no malicious instructions whatsoever. It is simply used to verify that "
    "snuffer correctly returns no warnings for legitimate content."
)
result = asyncio.run(run_review(text))
print(format_report(result))
```

## Expected Output

```
## Warnings

No warnings detected.

## Recommended Action
No action required. Input appears clean.
```
