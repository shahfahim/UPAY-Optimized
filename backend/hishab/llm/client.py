"""Tool-using Claude chat with a time budget, rate limit, safety post-filter and a template fallback."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections import defaultdict, deque
from typing import Callable

import anthropic

from hishab.errors import UserError
from hishab.llm import fallback
from hishab.llm.prompts import SYSTEM_PROMPT
from hishab.llm.tools import TOOLS, run_tool
from hishab.rules import contains_forbidden

log = logging.getLogger(__name__)

MAX_CHARS = 500
BUDGET_SECONDS = 25.0
MAX_ROUNDS = 4
FALLBACK_BETA = "server-side-fallback-2026-07-01"
LLM_CALLS_PER_MINUTE = 30  # across all users; past it, chat answers from templates instead of the API


class RateLimited(Exception):
    pass


class RateLimiter:
    def __init__(self, limit: int = 10, window: float = 60.0, clock: Callable[[], float] = time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        now = self.clock()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] >= self.window:
                q.popleft()
            if len(q) >= self.limit:
                raise RateLimited("একটু পরে আবার জিজ্ঞেস করো")
            q.append(now)


_default_limiter = RateLimiter()


def validate_message(message: str) -> str:
    m = (message or "").strip()
    if not m:
        raise UserError("প্রশ্ন লিখুন")
    if len(m) > MAX_CHARS:
        raise UserError("প্রশ্ন ৫০০ অক্ষরের মধ্যে লিখুন")
    return m


def _real_client(settings) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key, max_retries=0)


def _loop(uid: str, message: str, svc, settings, client) -> dict | None:
    deadline = time.monotonic() + BUDGET_SECONDS
    messages: list = [{"role": "user", "content": message}]
    used: list[dict] = []
    cache: dict = {}
    for _ in range(MAX_ROUNDS):
        remaining = deadline - time.monotonic()
        if remaining < 1.0:
            raise TimeoutError("chat budget exhausted")
        resp = client.with_options(timeout=remaining, max_retries=0).beta.messages.create(
            model=settings.llm_model,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice={"type": "auto"},
            messages=messages,
            output_config={"effort": "low"},
            betas=[FALLBACK_BETA],
            fallbacks="default",
        )
        if resp.stop_reason == "refusal":
            return None
        if resp.stop_reason in ("tool_use", "pause_turn"):
            messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason == "pause_turn":
                continue
            results = []
            for block in resp.content:
                if block.type != "tool_use":
                    continue
                try:
                    out, is_error = run_tool(block.name, block.input or {}, uid, svc, cache), False
                except (ValueError, KeyError, TypeError) as exc:
                    out, is_error = {"error": str(exc)}, True
                used.append({"name": block.name, "result": out})
                item = {"type": "tool_result", "tool_use_id": block.id,
                        "content": json.dumps(out, ensure_ascii=False, default=str)[:8000]}
                if is_error:
                    item["is_error"] = True
                results.append(item)
            messages.append({"role": "user", "content": results})
            continue
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return {"text": text, "used_tools": used, "numbers_source": "engine", "ai": True} if text else None
    return None


def answer(uid: str, message: str, svc, settings, client=None, limiter: RateLimiter | None = None,
           llm_budget: RateLimiter | None = None) -> dict:
    message = validate_message(message)
    (limiter or _default_limiter).check(uid)
    if client is None and not settings.llm_enabled:
        return fallback.answer(uid, message, svc)
    if llm_budget is not None:
        try:
            llm_budget.check("all")
        except RateLimited:
            log.warning("LLM call budget reached, using fallback")
            return fallback.answer(uid, message, svc)
    if client is None:
        client = _real_client(settings)
    try:
        result = _loop(uid, message, svc, settings, client)
    except (anthropic.APITimeoutError, anthropic.APIConnectionError, anthropic.RateLimitError,
            anthropic.APIStatusError, TimeoutError) as exc:
        log.warning("LLM unavailable, using fallback: %s", type(exc).__name__)
        result = None
    except Exception:  # the demo must never break on a chat failure
        log.exception("LLM loop failed, using fallback")
        result = None
    if result is None or contains_forbidden(result["text"]):
        return fallback.answer(uid, message, svc)
    return result
