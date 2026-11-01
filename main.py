import asyncio
import json
import os
from typing import List, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import AsyncGroq, GroqError
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = FastAPI(
    title="Feedback Analyzer",
    description="Menganalisis feedback pelanggan menjadi insight terstruktur (JSON).",
    version="1.0.0",
)


# ---------- Schema (Pydantic) ----------
class FeedbackRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000, description="Teks feedback pelanggan")
    context: str = Field("produk atau layanan umum", max_length=300, description="Konteks bisnis/produk")


class FeedbackAnalysis(BaseModel):
    sentiment: Literal["positif", "netral", "negatif"]
    summary: str
    key_issues: List[str]
    suggested_actions: List[str]
    priority: Literal["rendah", "sedang", "tinggi"]


class PromptResult(BaseModel):
    prompt: str
    output: str


class ExperimentResponse(BaseModel):
    prompt_a: PromptResult
    prompt_b: PromptResult
    prompt_c: PromptResult


# ---------- Prompt ----------
SYSTEM_PROMPT = (
    "Kamu adalah analis customer experience yang teliti dan objektif. "
    "Kamu hanya menjawab dalam format JSON valid tanpa teks tambahan."
)


def build_prompt(text: str, context: str) -> str:
    """Prompt C: Role (system prompt) + Task + Context + Constraint + Output Format."""
    return f"""
TASK:
Analisis feedback pelanggan berikut dan ubah menjadi insight yang bisa ditindaklanjuti.

CONTEXT:
Konteks bisnis: {context}
Feedback pelanggan:
\"\"\"{text}\"\"\"

CONSTRAINT:
- Gunakan Bahasa Indonesia.
- Jangan mengarang informasi yang tidak ada di feedback.
- summary maksimal 2 kalimat.
- key_issues dan suggested_actions masing-masing 1 sampai 4 item singkat.
- priority "tinggi" jika ada masalah serius/mendesak, "sedang" jika perlu perbaikan, "rendah" jika hanya masukan ringan.
- Perhatikan sarkasme: tentukan sentiment berdasarkan makna sebenarnya, bukan kata-kata positifnya saja.

OUTPUT FORMAT:
Balas HANYA dengan JSON berikut:
{{
  "sentiment": "positif | netral | negatif",
  "summary": "string",
  "key_issues": ["string"],
  "suggested_actions": ["string"],
  "priority": "rendah | sedang | tinggi"
}}
""".strip()


def prompt_a(text: str, context: str) -> str:
    """Prompt A: sederhana."""
    return f"Analyze this feedback: {text}"


def prompt_b(text: str, context: str) -> str:
    """Prompt B: Role + Task + Context."""
    return (
        "Kamu adalah analis customer experience.\n"
        "Tugas: analisis feedback pelanggan berikut.\n"
        f"Konteks bisnis: {context}\n"
        f"Feedback pelanggan: {text}"
    )


# ---------- Helper LLM ----------
async def run_llm(messages: list, json_mode: bool = False) -> str:
    kwargs = {"model": MODEL, "messages": messages, "temperature": 0.2}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    completion = await client.chat.completions.create(**kwargs)
    return completion.choices[0].message.content


# ---------- Endpoints ----------
@app.get("/")
async def health_check():
    return {"status": "ok", "app": "Feedback Analyzer", "model": MODEL}


@app.post("/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(payload: FeedbackRequest):
    if client is None:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY belum diset di file .env")

    try:
        raw = await run_llm(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(payload.text, payload.context)},
            ],
            json_mode=True,
        )
        return FeedbackAnalysis(**json.loads(raw))

    except (json.JSONDecodeError, ValidationError, TypeError):
        raise HTTPException(status_code=502, detail="Output LLM tidak sesuai format JSON yang diharapkan. Coba lagi.")
    except GroqError as e:
        raise HTTPException(status_code=502, detail=f"Gagal menghubungi Groq API: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan server: {e}")


@app.post("/experiment", response_model=ExperimentResponse)
async def run_experiment(payload: FeedbackRequest):
    """Menjalankan prompt A, B, C dengan input yang sama (secara paralel)."""
    if client is None:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY belum diset di file .env")

    pa = prompt_a(payload.text, payload.context)
    pb = prompt_b(payload.text, payload.context)
    pc = build_prompt(payload.text, payload.context)

    try:
        out_a, out_b, out_c = await asyncio.gather(
            run_llm([{"role": "user", "content": pa}]),
            run_llm([{"role": "user", "content": pb}]),
            run_llm(
                [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": pc}],
                json_mode=True,
            ),
        )
    except GroqError as e:
        raise HTTPException(status_code=502, detail=f"Gagal menghubungi Groq API: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan server: {e}")

    return ExperimentResponse(
        prompt_a=PromptResult(prompt=pa, output=out_a),
        prompt_b=PromptResult(prompt=pb, output=out_b),
        prompt_c=PromptResult(prompt=f"[SYSTEM]\n{SYSTEM_PROMPT}\n\n[USER]\n{pc}", output=out_c),
    )