from deepseek_cli.smart_router import AutoRouterOptions, needs_web_search


def test_needs_web_search_detects_time_sensitive_queries():
    assert needs_web_search("What are the latest BTC prices today?")
    assert needs_web_search("Schedule for September 2025 Olympics")


def test_needs_web_search_skips_static_questions():
    assert not needs_web_search("Explain how binary search works in python")


def test_autorouter_options_enforces_ranges():
    options = AutoRouterOptions(max_results=75, search_depth="unknown")
    assert options.max_results == 10
    assert options.search_depth == "advanced"
