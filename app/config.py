"""Application settings, read from environment variables with safe defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def _int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


def _float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value not in (None, "") else default


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _path(name: str, default: str) -> Path:
    return PROJECT_ROOT / os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    log_level: str = "INFO"
    seed: int = 42
    warmup_on_start: bool = False  # load the model and index when the server starts

    # Paths
    corpus_dir: Path = PROJECT_ROOT / "corpus"
    chroma_dir: Path = PROJECT_ROOT / ".chroma"
    model_cache_dir: Path = PROJECT_ROOT / ".cache" / "fastembed"

    # Ingestion
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_threads: int = 0  # 0 lets ONNX Runtime decide; 1 suits a small shared CPU
    query_prefix: str = BGE_QUERY_PREFIX
    collection_name: str = "veridane_policies"
    chunk_strategy: str = "heading"
    chunk_size: int = 350
    chunk_overlap: int = 50

    # Retrieval
    top_k: int = 5
    retrieval_mode: str = "hybrid"
    candidate_pool: int = 30
    relevance_threshold: float = 0.55

    # Generation
    groq_api_key: str = field(default="", repr=False)
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "openai/gpt-oss-20b"
    judge_model: str = "openai/gpt-oss-120b"
    llm_reasoning_effort: str = "low"  # gpt-oss models only; leave empty for other models
    llm_max_tokens: int = 1024  # covers the hidden reasoning tokens plus the answer
    llm_timeout: float = 30.0

    # Guardrails
    max_question_chars: int = 1000
    max_answer_words: int = 200

    @classmethod
    def from_env(cls) -> Settings:
        defaults = cls()
        return cls(
            log_level=os.getenv("LOG_LEVEL", defaults.log_level),
            seed=_int("SEED", defaults.seed),
            warmup_on_start=_bool("WARMUP_ON_START", defaults.warmup_on_start),
            corpus_dir=_path("CORPUS_DIR", "corpus"),
            chroma_dir=_path("CHROMA_DIR", ".chroma"),
            model_cache_dir=_path("MODEL_CACHE_DIR", ".cache/fastembed"),
            embedding_model=os.getenv("EMBEDDING_MODEL", defaults.embedding_model),
            embedding_threads=_int("EMBEDDING_THREADS", defaults.embedding_threads),
            query_prefix=os.getenv("QUERY_PREFIX", defaults.query_prefix),
            collection_name=os.getenv("COLLECTION_NAME", defaults.collection_name),
            chunk_strategy=os.getenv("CHUNK_STRATEGY", defaults.chunk_strategy),
            chunk_size=_int("CHUNK_SIZE", defaults.chunk_size),
            chunk_overlap=_int("CHUNK_OVERLAP", defaults.chunk_overlap),
            top_k=_int("TOP_K", defaults.top_k),
            retrieval_mode=os.getenv("RETRIEVAL_MODE", defaults.retrieval_mode),
            candidate_pool=_int("CANDIDATE_POOL", defaults.candidate_pool),
            relevance_threshold=_float("RELEVANCE_THRESHOLD", defaults.relevance_threshold),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            llm_base_url=os.getenv("LLM_BASE_URL", defaults.llm_base_url),
            llm_model=os.getenv("LLM_MODEL", defaults.llm_model),
            judge_model=os.getenv("JUDGE_MODEL", defaults.judge_model),
            llm_reasoning_effort=os.getenv("LLM_REASONING_EFFORT", defaults.llm_reasoning_effort),
            llm_max_tokens=_int("LLM_MAX_TOKENS", defaults.llm_max_tokens),
            llm_timeout=_float("LLM_TIMEOUT", defaults.llm_timeout),
            max_question_chars=_int("MAX_QUESTION_CHARS", defaults.max_question_chars),
            max_answer_words=_int("MAX_ANSWER_WORDS", defaults.max_answer_words),
        )
