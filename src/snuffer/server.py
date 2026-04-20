import asyncio
from typing import Any

import mcp.server.stdio
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool

from snuffer.formatter import format_report
from snuffer.modes.filter import run_filter
from snuffer.modes.review import run_review
from snuffer.quarantine_writer import write_quarantine

app = Server("snuffer")


@app.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="snuff_review",
            description="Review untrusted text for prompt injection. Returns diagnostic markdown.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Untrusted input text to review"},
                    "chunk_size": {
                        "type": "integer",
                        "default": 400,
                        "description": "Words per chunk",
                    },
                    "overlap_words": {
                        "type": "integer",
                        "default": 40,
                        "description": "Overlap words between chunks",
                    },
                    "input_filename": {
                        "type": "string",
                        "default": "input",
                        "description": "Filename label for quarantine report",
                    },
                    "quarantine_dir": {
                        "type": "string",
                        "default": "quarantine",
                        "description": "Directory to write quarantine files",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="snuff_filter",
            description="Filter untrusted text, removing chunks above certainty threshold.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Untrusted input text to filter"},
                    "certainty_threshold": {
                        "type": "string",
                        "enum": ["CAUTION", "SUSPICIOUS", "CLEARLY_MALICIOUS"],
                        "default": "SUSPICIOUS",
                    },
                    "min_output_chars": {
                        "type": "integer",
                        "default": 100,
                        "description": "Minimum chars in cleaned output",
                    },
                    "chunk_size": {"type": "integer", "default": 400},
                    "overlap_words": {"type": "integer", "default": 40},
                },
                "required": ["text"],
            },
        ),
    ]


@app.call_tool()  # type: ignore[untyped-decorator]
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "snuff_review":
        input_filename: str = arguments.get("input_filename", "input")
        quarantine_dir: str = arguments.get("quarantine_dir", "quarantine")
        result = await run_review(
            text=arguments["text"],
            chunk_size=arguments.get("chunk_size", 400),
            overlap_words=arguments.get("overlap_words", 40),
        )
        report = format_report(result)
        if result.warnings:
            quarantine_path = write_quarantine(
                result,
                result.original_text,
                result.session_id,
                input_filename,
                quarantine_dir,
            )
            report = report + f"\nQuarantine file written: {quarantine_path}"
        return [TextContent(type="text", text=report)]

    if name == "snuff_filter":
        output = await run_filter(
            text=arguments["text"],
            certainty_threshold=arguments.get("certainty_threshold", "SUSPICIOUS"),
            min_output_chars=arguments.get("min_output_chars", 100),
            chunk_size=arguments.get("chunk_size", 400),
            overlap_words=arguments.get("overlap_words", 40),
        )
        import json

        return [TextContent(type="text", text=json.dumps(output))]

    raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(prog="snuffer")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run HTTP API server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8080)
    serve_parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn
        from snuffer.api import app as fastapi_app

        uvicorn.run(fastapi_app, host=args.host, port=args.port, reload=args.reload)
    else:
        async def _run() -> None:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await app.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="snuffer",
                        server_version="0.1.0",
                        capabilities=app.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )

        asyncio.run(_run())


if __name__ == "__main__":
    main()
