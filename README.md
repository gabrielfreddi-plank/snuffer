# Snuffer

Prompt injection detection MCP server for Claude Code. Snuffer reviews untrusted third-party text before it reaches your LLM, flagging or surgically removing malicious chunks.

## Installation

```bash
uv sync
export ANTHROPIC_API_KEY=sk-ant-...
```

## MCP Setup

Add to your Claude Code MCP config (`~/.claude/claude_desktop_config.json` or `.mcp.json`):

```json
{
  "mcpServers": {
    "snuffer": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/snuffer", "snuffer"]
    }
  }
}
```

## Tools

### `snuff_review`

Reviews text and returns a diagnostic markdown report. Use before passing third-party content to your model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | required | Untrusted input to review |
| `chunk_size` | integer | 400 | Words per analysis chunk |
| `overlap_words` | integer | 40 | Overlap between chunks (catches split attacks) |

**Returns:** Markdown report with a warning table, severity breakdown, and recommended action (`REJECT` or no action).

### `snuff_filter`

Removes flagged chunks from the text and returns the cleaned version. Use when the input is mostly legitimate but may contain injected paragraphs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | required | Untrusted input to filter |
| `certainty_threshold` | `CAUTION` \| `SUSPICIOUS` \| `CLEARLY_MALICIOUS` | `SUSPICIOUS` | Minimum certainty to remove a chunk |
| `min_output_chars` | integer | 100 | If cleaned output is shorter than this, returns `COMPLETELY_ROTTEN_INPUT` error |
| `chunk_size` | integer | 400 | Words per chunk |
| `overlap_words` | integer | 40 | Overlap between chunks |

**Returns:** JSON:
```json
{
  "cleaned_text": "...",
  "error": null,
  "report": {
    "removed_chunks": 1,
    "total_chunks": 3,
    "warnings": 2,
    "severity": { "CLEARLY_MALICIOUS": 1, "SUSPICIOUS": 1, "CAUTION": 0 }
  }
}
```

If all chunks are flagged and the remainder is below `min_output_chars`:
```json
{ "error": "COMPLETELY_ROTTEN_INPUT", "cleaned_text": "", "report": { ... } }
```

## How It Works

```
raw input
    │
    ▼
Normalizer          strips zero-width chars, decodes base64/hex/URL/ROT13, maps homoglyphs
    │
    ▼
Bracket sanitizer   removes forged ⟪SNUF:...⟫ delimiters from untrusted text
    │
    ▼
Chunker             splits into overlapping 400-word windows (configurable)
    │
    ▼
Reviewer            wraps each chunk in tamper-evident ⟪SNUF:{session_key}:[BE]⟫ delimiters,
                    sends to claude-haiku-4-5 with a strict detector system prompt,
                    parses JSON warnings with char offsets + damage type labels
    │
    ▼
Deduplicator        merges warnings within 50-char proximity, keeps highest certainty
    │
    ▼
review → markdown report
filter → cleaned text (flagged chunks removed)
```

### Normalizer

Runs before chunking to surface obfuscated attacks:

- **Zero-width characters** (U+200B, U+FEFF, etc.) — stripped
- **Hex escapes** (`\x49\x67\x6e...`) — decoded in-place
- **Base64** (≥20 chars matching pattern) — decoded and annotated `[BASE64:...]`
- **URL encoding** (`%49%67%6e...`) — decoded and annotated `[URL:...]`
- **HTML entities** (`&lt;`, `&#x49;`) — decoded and annotated `[HTML:...]`
- **ROT13** — heuristic word-frequency check, decoded and annotated `[ROT13:...]` if likely
- **Homoglyphs** (Cyrillic е/х/с posing as Latin) — mapped to ASCII via NFKC + unidecode

### Delimiter Security

Each review session generates a random 8-hex-char key. Chunks are wrapped as:

```
⟪SNUF:a3f92b1c:B⟫ ...untrusted text... ⟪SNUF:a3f92b1c:E⟫
```

The bracket sanitizer strips any pre-existing `⟪SNUF:...⟫` patterns from the input before wrapping, preventing delimiter forgery attacks that attempt to escape the review scope.

### Chunking and Overlap

Long inputs are split into 400-word chunks with 40-word overlap. Overlap ensures that multi-step attacks split across a chunk boundary are still visible together in at least one chunk. Each chunk is reviewed sequentially with the tail of the previous chunk passed as `[PRIOR CONTEXT]`, giving the model cross-chunk awareness.

## Threat Taxonomy

| Damage Type | Description |
|-------------|-------------|
| `INSTRUCTION_OVERRIDE` | "Ignore previous instructions", "your new role is..." |
| `REMOTE_CODE_EXECUTION` | Shell commands, `curl \| bash`, `eval()` |
| `DATA_EXFILTRATION` | Sending context/secrets to external URLs |
| `ROLE_MANIPULATION` | Jailbreaks: "DAN mode", "pretend you are..." |
| `ENCODED_PAYLOAD` | Base64/hex/ROT13 hiding malicious instructions |
| `SOCIAL_ENGINEERING` | Authority claims, urgency, fake authorization codes |
| `INDIRECT_INJECTION` | Malicious instructions disguised as data or citations |
| `MULTI_STEP_ATTACK` | Instructions that build on prior steps across chunks |
| `PRIVILEGE_ESCALATION` | Claiming admin/developer/system access |
| `DELIMITER_FORGERY` | Forged `⟪SNUF:...⟫` brackets to escape review scope |
| `HOMOGLYPH_ATTACK` | Unicode lookalikes (Cyrillic, etc.) to evade text matching |
| `PROMPT_LEAKING` | Requests to print system prompt or context window |

## Python API

```python
import asyncio
from snuffer.modes.review import run_review
from snuffer.modes.filter import run_filter
from snuffer.formatter import format_report

# Review
result = asyncio.run(run_review("...untrusted text..."))
print(format_report(result))

# Filter
output = asyncio.run(run_filter("...untrusted text...", certainty_threshold="SUSPICIOUS"))
if output["error"]:
    raise ValueError(output["error"])
clean = output["cleaned_text"]
```

## Examples

The `examples/` directory contains 19 sample inputs covering all attack vectors plus clean false-positive cases. See `examples/examples.yml` for the full index with expected snuffer behavior.

## Development

```bash
uv run pytest
uv run mypy src/
uv run ruff check src/
```
