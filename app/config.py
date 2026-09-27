"""Application settings, read from environment variables with safe defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


def _path(name: str, default: str) -> Path:
    return PROJECT_ROOT / os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    log_level: str = "INFO"
    seed: int = 42
    corpus_dir: Path = PROJECT_ROOT / "corpus"
    chroma_dir: Path = PROJECT_ROOT / ".chroma"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 400
    chunk_overlap: int = 60
    top_k: int = 5
    groq_api_key: str = field(default="", repr=False)
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.1-8b-instant"
    judge_model: str = "llama-3.3-70b-versatile"
    max_question_chars: int = 1000
    max_answer_words: int = 200

    @classmethod
    def from_env(cls) -> Settings:
        defaults = cls()
        return cls(
            log_level=os.getenv("LOG_LEVEL", defaults.log_level),
            seed=_int("SEED", defaults.seed),
            corpus_dir=_path("CORPUS_DIR", "corpus"),
            chroma_dir=_path("CHROMA_DIR", ".chroma"),
            embedding_model=os.getenv("EMBEDDING_MODEL", defaults.embedding_model),
            chunk_size=_int("CHUNK_SIZE", defaults.chunk_size),
            chunk_overlap=_int("CHUNK_OVERLAP", defaults.chunk_overlap),
            top_k=_int("TOP_K", defaults.top_k),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            llm_base_url=os.getenv("LLM_BASE_URL", defaults.llm_base_url),
            llm_model=os.getenv("LLM_MODEL", defaults.llm_model),
            judge_model=os.getenv("JUDGE_MODEL", defaults.judge_model),
            max_question_chars=_int("MAX_QUESTION_CHARS", defaults.max_question_chars),
            max_answer_words=_int("MAX_ANSWER_WORDS", defaults.max_answer_words),
        )
