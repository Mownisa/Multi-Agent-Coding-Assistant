"""
LLM provider chain with automatic fallback.

Order: Google Gemini Flash -> Groq (Llama) -> Anthropic Claude Haiku
       -> Together AI -> Ollama (local).

Why this order:
- Google Gemini Flash is the primary provider - free tier gives generous
  daily request limits with no credit card required.
- Groq is fallback 1 - free tier, extremely fast inference, generous
  rate limits (check https://console.groq.com/docs/rate-limits for
  current numbers since these change).
- Anthropic Claude Haiku is fallback 2 - capable, but requires a funded
  account; will fail fast with BILLING_REQUIRED if credits are empty.
- Together AI is fallback 3, free tier ~60 req/min when the key is valid.
- Ollama is the last resort - works only if running locally, and is
  skipped entirely unless explicitly enabled in config.

Each agent calls `get_llm()` to get a single object that already knows
how to fall back - agents don't need their own try/except logic.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel

from src.settings import config

logger = logging.getLogger(__name__)


class FallbackLLM:
    """
    Wraps multiple LangChain chat models and tries them in order.
    Exposes the same .ainvoke() interface so it's a drop-in replacement
    for any single LangChain chat model.
    """

    def __init__(self, providers: List[tuple[str, BaseChatModel]]):
        if not providers:
            raise RuntimeError(
                "No LLM providers configured. Set GOOGLE_API_KEY, "
                "ANTHROPIC_API_KEY, or TOGETHER_API_KEY in your .env, "
                "or run Ollama locally."
            )
        self.providers = providers

    async def ainvoke(self, messages: List[BaseMessage], *args, **kwargs):
        errors: list[str] = []
        for name, model in self.providers:
            try:
                logger.info("[LLM] Trying provider: %s", name)
                result = await model.ainvoke(messages, *args, **kwargs)

                if not getattr(result, "content", None) or not str(result.content).strip():
                    logger.warning("[LLM] Provider '%s' returned empty content, treating as failure", name)
                    errors.append(f"{name} [EMPTY_RESPONSE]: model returned empty content")
                    continue

                logger.info("[LLM] Provider '%s' succeeded", name)
                return result
            except Exception as exc:
                kind = _classify_error(exc)
                logger.warning("[LLM] Provider '%s' failed (%s): %s", name, kind, exc)
                errors.append(f"{name} [{kind}]: {exc}")
                continue

        summary = "; ".join(errors) if errors else "no providers were configured"
        raise RuntimeError(f"All LLM providers failed. Details: {summary}")

    def bind_tools(self, tools):
        """
        Tool binding (used by create_react_agent). Bind tools to every
        underlying provider so fallback still works when tools are attached.
        """
        bound_providers = [
            (name, model.bind_tools(tools)) for name, model in self.providers
        ]
        return FallbackLLM(bound_providers)


def _classify_error(exc: Exception) -> str:
    """Best-effort classification so logs/errors are actionable at a glance."""
    text = str(exc).lower()
    name = type(exc).__name__.lower()

    if "credit balance is too low" in text or "billing" in text or "purchase credits" in text:
        return "BILLING_REQUIRED"
    if "resource_exhausted" in text or "quota" in text or "rate limit" in text or "429" in text:
        return "QUOTA_EXCEEDED"
    if "invalid_api_key" in text or "invalid api key" in text or "401" in text or "unauthorized" in text or "authentication" in text:
        return "AUTH_FAILED"
    if "connecterror" in name or "connection error" in text or "all connection attempts failed" in text:
        return "CONNECTION_FAILED"
    if "timeout" in text or "timed out" in name:
        return "TIMEOUT"
    if "404" in text or "not found" in text:
        return "NOT_FOUND"
    return "UNKNOWN"


def get_llm(max_tokens: int = 800, temperature: float = 0.0) -> FallbackLLM:
    """
    Builds the fallback chain based on whichever API keys are present.
    Google Gemini Flash first (free tier, ~1,500 req/day, no card),
    Anthropic Claude Haiku second (free tier, generous limits),
    Together AI third (free tier, 60+ req/min),
    Ollama last (local only, skipped entirely if not configured to run).
    """
    providers: List[tuple[str, BaseChatModel]] = []

    if config.has_google:
        providers.append((
            "google-gemini-flash",
            ChatGoogleGenerativeAI(
                api_key=config.google_api_key,
                model=config.google_model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30,
            ),
        ))
    else:
        logger.info("[LLM] Skipping google-gemini-flash: no GOOGLE_API_KEY configured")

    if config.has_groq:
        providers.append((
            "groq",
            ChatOpenAI(
                api_key=config.groq_api_key,
                base_url="https://api.groq.com/openai/v1",
                model=config.groq_model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30,
            ),
        ))
    else:
        logger.info("[LLM] Skipping groq: no GROQ_API_KEY configured")

    if config.has_anthropic:
        providers.append((
            "anthropic-claude-haiku",
            ChatAnthropic(
                api_key=config.anthropic_api_key,
                model=config.anthropic_model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30,
            ),
        ))
    else:
        logger.info("[LLM] Skipping anthropic-claude-haiku: no ANTHROPIC_API_KEY configured")

    if config.has_together:
        providers.append((
            "together-ai",
            ChatOpenAI(
                api_key=config.together_api_key,
                base_url="https://api.together.xyz/v1",
                model=config.together_model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30,
            ),
        ))
    else:
        logger.info("[LLM] Skipping together-ai: no TOGETHER_API_KEY configured")

    if getattr(config, "use_ollama_fallback", False):
        providers.append((
            "ollama",
            ChatOpenAI(
                api_key="ollama",
                base_url=f"{config.ollama_base_url}/v1",
                model=config.ollama_model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=10,
            ),
        ))
    else:
        logger.info("[LLM] Skipping ollama: use_ollama_fallback not enabled")

    return FallbackLLM(providers)
