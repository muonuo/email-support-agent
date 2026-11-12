"""路由决策与图结构的单元测试 —— 不依赖真实 LLM 调用。"""

import pytest

from email_agent.routing import needs_human_review, route_by_classification
from email_agent.state import EmailClassification


def make_classification(
    intent: str = "question",
    urgency: str = "low",
) -> EmailClassification:
    return {"intent": intent, "urgency": urgency, "topic": "t", "summary": "s"}  # type: ignore[typeddict-item]


@pytest.mark.parametrize(
    ("intent", "expected"),
    [
        ("question", "search_documentation"),  # 简单问题查文档
        ("feature", "search_documentation"),   # 功能咨询查文档
        ("bug", "bug_tracking"),               # Bug 建工单
        ("billing", "draft_response"),         # 账单直接出稿
        ("complex", "draft_response"),         # 复杂问题直接出稿
    ],
)
def test_route_by_classification(intent: str, expected: str) -> None:
    assert route_by_classification(make_classification(intent=intent)) == expected


@pytest.mark.parametrize(
    ("intent", "urgency", "expected"),
    [
        ("question", "low", False),     # 简单问题：直接发送
        ("feature", "medium", False),   # 普通功能请求：直接发送
        ("question", "high", True),     # 紧急：必须人工
        ("billing", "low", True),       # 账单：必须人工
        ("complex", "low", True),       # 复杂：必须人工
        ("bug", "critical", True),      # 紧急 Bug：必须人工
    ],
)
def test_needs_human_review(intent: str, urgency: str, expected: bool) -> None:
    assert (
        needs_human_review(make_classification(intent=intent, urgency=urgency))
        is expected
    )


def test_graph_contains_all_nodes() -> None:
    """图能编译且包含全部 7 个节点（无需 API Key）。"""
    from email_agent.graph import build_graph

    app = build_graph()
    node_names = set(app.get_graph().nodes)
    expected = {
        "read_email",
        "classify_intent",
        "search_documentation",
        "bug_tracking",
        "draft_response",
        "human_review",
        "send_reply",
    }
    assert expected <= node_names


def test_ticket_id_is_idempotent() -> None:
    """Action 节点幂等性：同一封邮件重复建单，工单号不变。"""
    from email_agent.nodes.bug_tracking import make_ticket_id

    assert make_ticket_id("email-002") == make_ticket_id("email-002")
