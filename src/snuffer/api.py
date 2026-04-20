from typing import Any

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel

from snuffer.formatter import format_report
from snuffer.modes.filter import run_filter
from snuffer.modes.review import run_review

app = FastAPI(title="Snuffer API")


class ReviewRequest(BaseModel):
    text: str
    chunk_size: int = 400
    overlap_words: int = 40


class FilterRequest(BaseModel):
    text: str
    certainty_threshold: str = "SUSPICIOUS"
    min_output_chars: int = 100
    chunk_size: int = 400
    overlap_words: int = 40


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/review", response_class=PlainTextResponse)
async def review(req: ReviewRequest) -> str:
    try:
        result = await run_review(
            text=req.text,
            chunk_size=req.chunk_size,
            overlap_words=req.overlap_words,
        )
        return format_report(result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})  # type: ignore[return-value]


@app.post("/filter")
async def filter_text(req: FilterRequest) -> Any:
    try:
        output = await run_filter(
            text=req.text,
            certainty_threshold=req.certainty_threshold,  # type: ignore[arg-type]
            min_output_chars=req.min_output_chars,
            chunk_size=req.chunk_size,
            overlap_words=req.overlap_words,
        )
        return output
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
