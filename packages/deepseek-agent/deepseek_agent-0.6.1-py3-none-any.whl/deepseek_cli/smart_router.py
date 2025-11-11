"""Auto-router chat loop with heuristic Tavily search and SSE streaming."""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from textwrap import dedent
from typing import Iterable, List, Optional, Sequence, Tuple

from openai import OpenAI

try:  # pragma: no cover - dependency is installed at runtime
    from tavily import TavilyClient
except Exception:  # pragma: no cover - Keep import optional for tests
    TavilyClient = None  # type: ignore[assignment]

REASONER_MODEL = os.getenv("DEEPSEEK_REASONER_MODEL", "deepseek-reasoner")

RECENT_YEARS = {str(y) for y in range(2023, 2031)}
MONTHS = {
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "jan",
    "feb",
    "mar",
    "apr",
    "jun",
    "jul",
    "aug",
    "sep",
    "sept",
    "oct",
    "nov",
    "dec",
}
FRESH_KEYWORDS = {
    "today",
    "yesterday",
    "this week",
    "this month",
    "latest",
    "breaking",
    "update",
    "recent",
    "currently",
    "right now",
    "price",
    "cost",
    "schedule",
    "opening hours",
    "hours",
    "tickets",
    "score",
    "standings",
    "lineup",
    "fixtures",
    "release date",
    "who is",
    "ceo",
    "cfo",
    "chair",
    "president",
    "prime minister",
    "election",
    "poll",
    "laws",
    "regulation",
    "bill",
    "income limit",
    "deadline",
    "ban",
    "recall",
    "security patch",
    "cve",
    "vulnerability",
    "weather",
    "forecast",
    "visa",
    "entry requirements",
    "travel advisory",
    "changelog",
    "roadmap",
    "version",
    "firmware",
    "driver",
    "kernel",
    "api version",
    "docs update",
    "stock",
    "earnings",
    "revenue",
    "guidance",
    "acquisition",
    "merger",
    "ipo",
    "btc",
    "eth",
    "concert",
    "festival",
    "game",
    "match",
    "tournament",
    "olympics",
    "world cup",
}
VOLATILE_HINTS = [
    r"\b(news|headline|happened|happening|event|controversy|trip|visit)\b",
    r"\b(results|score|trade|transfer|injury)\b",
    r"\b(cv(e)?-\d{4}-\d{4,})\b",
    r"\b(version|v\d+(\.\d+)+)\b",
    r"\bprice of [A-Za-z0-9]+\b",
]


def _contains_date_like(ql: str) -> bool:
    if any(y in ql for y in RECENT_YEARS):
        return True
    if any(m in ql for m in MONTHS):
        return True
    if re.search(r"\b(0?[1-9]|1[0-2])[/-]\d{2,4}\b", ql):
        return True
    if any(
        k in ql
        for k in [
            "today",
            "yesterday",
            "last week",
            "last month",
            "this week",
            "this month",
        ]
    ):
        return True
    return False


def needs_web_search(question: str) -> bool:
    q = question.strip().lower()
    if not q:
        return False
    static_patterns = [
        r"explain (.+)",
        r"teach me (.+)",
        r"write (a |an )?(email|essay|poem|story|sql|regex|function|code)",
        r"debug (.+)",
        r"how to (.+) in (python|javascript|sql|bash|linux)",
        r"what does (.+) mean",
        r"give me ideas|brainstorm|prompt ideas|examples",
    ]
    if any(re.search(p, q) for p in static_patterns):
        if not _contains_date_like(q) and not any(k in q for k in FRESH_KEYWORDS):
            return False

    if _contains_date_like(q):
        return True
    if any(k in q for k in FRESH_KEYWORDS):
        return True
    if any(re.search(p, q) for p in VOLATILE_HINTS):
        return True
    return False


def build_messages(question: str, context: str = "", tavily_answer: str = "") -> Tuple[str, str]:
    if context:
        system_msg = (
            "You are a helpful assistant. Use the numbered web context below to answer. "
            "Cite sources in square brackets like [1], [2] that map to the context list. "
            "If sources conflict or are insufficient, say what's unknown and why."
        )
        user_msg = dedent(
            f"""
            Web context (numbered sources):
            {context}

            Tavily summary (may be incomplete):
            {tavily_answer}

            Task: Answer the user's question and cite sources like [1], [2] that map to the list above.
            If uncertain or if sources conflict, say what’s unknown and why.

            User question:
            {question}
            """
        ).strip()
    else:
        system_msg = (
            "You are a helpful assistant. Answer clearly and concisely. "
            "Do not fabricate citations. If you are uncertain, say so."
        )
        user_msg = question.strip()
    return system_msg, user_msg


def _safe_tavily_client(api_key: Optional[str]) -> Optional[TavilyClient]:
    if not api_key or not api_key.strip():
        return None
    if TavilyClient is None:  # pragma: no cover - dependency guard
        print(
            "(tavily-python is not installed; skipping web search capability.)",
            file=sys.stderr,
        )
        return None
    try:
        return TavilyClient(api_key=api_key.strip())
    except Exception as exc:  # pragma: no cover - init errors are rare
        print(f"(Unable to initialize Tavily client: {exc})", file=sys.stderr)
        return None


def _format_source_line(index: int, payload: dict) -> str:
    title = payload.get("title", "(no title)")
    url = payload.get("url", "")
    published = payload.get("published_date") or payload.get("date") or ""
    if published:
        try:
            parsed = datetime.fromisoformat(str(published).replace("Z", ""))
            published = parsed.date().isoformat()
        except Exception:
            published = str(published)
    line = f"[{index}] {title}"
    if published:
        line += f" — {published}"
    if url:
        line += f" — {url}"
    return line


def do_tavily_search(
    tavily: TavilyClient,
    question: str,
    *,
    max_results: int,
    search_depth: str,
    time_range: Optional[str],
) -> Tuple[str, str]:
    search_kwargs = dict(
        query=question,
        search_depth=search_depth,
        include_answer=True,
        max_results=max_results,
    )
    if time_range:
        search_kwargs["time_range"] = time_range
    search = tavily.search(**search_kwargs)
    sources = search.get("results", []) or []
    context_lines = [
        _format_source_line(index, payload) for index, payload in enumerate(sources, start=1)
    ]
    return "\n".join(context_lines), search.get("answer") or ""


class _ReasonerStreamRenderer:
    def __init__(self, *, stream=None, err_stream=None) -> None:
        self._stream = stream or sys.stdout
        self._err_stream = err_stream or sys.stderr
        self._thinking_active = False
        self._answer_active = False

    def thinking(self, text: str) -> None:
        if not text:
            return
        if not self._thinking_active:
            self._err_stream.write("[thinking] ")
            self._thinking_active = True
        self._err_stream.write(text)
        self._err_stream.flush()

    def answer(self, text: str) -> None:
        if not text:
            return
        if self._thinking_active:
            self._err_stream.write("\n")
            self._err_stream.flush()
            self._thinking_active = False
        if not self._answer_active:
            self._answer_active = True
        self._stream.write(text)
        self._stream.flush()

    def close(self) -> None:
        if self._thinking_active:
            self._err_stream.write("\n")
            self._err_stream.flush()
            self._thinking_active = False
        if self._answer_active:
            self._stream.write("\n")
            self._stream.flush()
            self._answer_active = False


def _extract_text_chunks(payload: object) -> Iterable[str]:
    if isinstance(payload, str):
        yield payload
        return
    if isinstance(payload, Sequence):
        for item in payload:
            if isinstance(item, str):
                yield item
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    yield str(text)


def _stream_with_responses(
    client: OpenAI,
    messages: List[dict],
    renderer: _ReasonerStreamRenderer,
    *,
    model: str,
) -> bool:
    responses_api = getattr(client, "responses", None)
    stream_method = getattr(responses_api, "stream", None) if responses_api else None
    if not stream_method:
        return False
    try:
        with client.responses.stream(
            model=model,
            input=messages,
        ) as stream:
            for event in stream:
                event_type = getattr(event, "type", "")
                if event_type == "response.thinking.delta":
                    renderer.thinking(getattr(event, "delta", "") or "")
                elif event_type == "response.output_text.delta":
                    renderer.answer(getattr(event, "delta", "") or "")
                elif event_type == "response.error":
                    error = getattr(event, "error", None)
                    message = getattr(error, "message", None) if error else None
                    raise RuntimeError(message or str(error))
        renderer.close()
        return True
    except Exception as exc:
        renderer.close()
        print(
            f"(Responses streaming failed: {exc}. Falling back to chat completions.)",
            file=sys.stderr,
        )
        return False


def _stream_with_chat_completions(
    client: OpenAI,
    messages: List[dict],
    renderer: _ReasonerStreamRenderer,
    *,
    model: str,
) -> None:
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    try:
        for chunk in stream:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            if not delta:
                continue
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                for piece in _extract_text_chunks(reasoning):
                    renderer.thinking(piece)
            content = getattr(delta, "content", None)
            if content:
                for piece in _extract_text_chunks(content):
                    renderer.answer(piece)
    finally:
        renderer.close()


def stream_reasoner_response(
    client: OpenAI,
    model: str,
    system_msg: str,
    user_prompt: str,
) -> None:
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt},
    ]
    renderer = _ReasonerStreamRenderer()
    streamed = _stream_with_responses(client, messages, renderer, model=model)
    if not streamed:
        _stream_with_chat_completions(client, messages, renderer, model=model)


def print_banner() -> None:
    print("=" * 60)
    print("Interactive chat (auto-router: deepseek-reasoner + Tavily smart search)")
    print("Type your message and press Enter.")
    print("Commands: /exit, /help")
    print("=" * 60)


@dataclass
class AutoRouterOptions:
    force_search: bool = False
    no_search: bool = False
    max_results: int = 8
    search_depth: str = "advanced"
    time_range: Optional[str] = None
    verbose_router: bool = False

    def __post_init__(self) -> None:
        self.max_results = max(1, min(int(self.max_results or 8), 10))
        if self.search_depth not in {"basic", "advanced"}:
            self.search_depth = "advanced"


def run_auto_router(
    client: OpenAI,
    options: AutoRouterOptions,
    *,
    tavily_api_key: Optional[str],
) -> int:
    tavily_client = _safe_tavily_client(tavily_api_key)
    print_banner()
    try:
        while True:
            try:
                question = input("> ").strip()
            except EOFError:
                print("\nGoodbye!")
                return 0

            if not question:
                continue
            lower = question.lower()
            if lower in {"/exit", "exit", "quit", ":q"}:
                print("Goodbye!")
                return 0
            if lower in {"/help", "help"}:
                print("Commands: /exit, /help")
                print(
                    "Tip: pass --force-search or --no-search when launching autorouter to override heuristics."
                )
                continue

            if options.force_search:
                use_search = True
            elif options.no_search:
                use_search = False
            else:
                use_search = needs_web_search(question)
            if options.verbose_router:
                print(f"(Search heuristic) use_search={use_search}", file=sys.stderr)

            context = ""
            tavily_summary = ""
            if use_search:
                if not tavily_client:
                    print(
                        "(Heuristic chose web search, but no Tavily API key is configured — continuing without web context.)",
                        file=sys.stderr,
                    )
                else:
                    try:
                        context, tavily_summary = do_tavily_search(
                            tavily_client,
                            question,
                            max_results=options.max_results,
                            search_depth=options.search_depth,
                            time_range=options.time_range,
                        )
                    except Exception as exc:
                        print(
                            f"(Search failed: {type(exc).__name__}: {exc}. Continuing without web context.)",
                            file=sys.stderr,
                        )

            system_msg, user_prompt = build_messages(
                question, context=context, tavily_answer=tavily_summary
            )
            stream_reasoner_response(client, REASONER_MODEL, system_msg, user_prompt)

            if context:
                print("Sources:")
                print(context)
            else:
                print("(No web sources were used.)")
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        return 0


__all__ = [
    "AutoRouterOptions",
    "needs_web_search",
    "run_auto_router",
    "stream_reasoner_response",
]
