from app.agent import EnterpriseCopilotAgent
from app.config import settings


class DummyLLM:
    pass


class DummyMCP:
    pass


def test_filter_low_relevance_search_results(monkeypatch) -> None:
    monkeypatch.setattr(settings, "min_relevance_score", 0.5)
    agent = EnterpriseCopilotAgent(DummyLLM(), DummyMCP())

    tool_result = {
        "tool": "search_hr_knowledge_base",
        "result": {
            "query": "cafeteria menu",
            "results": [
                {"title": "Weak match", "score": 0.49},
                {"title": "Strong match", "score": 0.5},
            ],
        },
    }

    filtered = agent._filter_low_relevance_results(tool_result)

    assert filtered["result"]["results"] == [{"title": "Strong match", "score": 0.5}]
    assert filtered["result"]["min_relevance_score"] == 0.5
