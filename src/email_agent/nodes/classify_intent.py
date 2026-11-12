"""节点2: classify_intent —— LLM 节点，意图识别 + 路由决策。

不用条件边：节点内部通过 Command(goto=...) 直接声明下一跳。
失败策略：结构化输出解析失败时重试由调用方/RetryPolicy 处理；
彻底失败则按 complex 兜底，走草稿 -> 人工审核路径。
"""

from typing import Literal

from langgraph.types import Command

from email_agent.llm import get_classifier_llm
from email_agent.routing import route_by_classification
from email_agent.state import EmailAgentState

CLASSIFY_PROMPT = """分析这封客户邮件并分类：
邮件: {email_content}
发件人: {sender_email}
以 JSON 格式输出，字段：
- intent: question/bug/billing/feature/complex 之一
- urgency: low/medium/high/critical 之一
- topic: 邮件主题（短语）
- summary: 邮件内容一句话摘要"""


def _fallback_classification() -> dict:
    """LLM 输出解析彻底失败时的兜底分类：按复杂问题转人工。"""
    return {
        "intent": "complex",
        "urgency": "high",
        "topic": "parse-fallback",
        "summary": "意图识别失败，按复杂问题转人工审核",
    }


def classify_intent(
    state: EmailAgentState,
) -> Command[Literal["search_documentation", "bug_tracking", "draft_response"]]:
    """LLM 结构化分类，并根据意图决定下一节点。"""
    prompt = CLASSIFY_PROMPT.format(
        email_content=state["email_content"],
        sender_email=state["sender_email"],
    )

    try:
        classification = get_classifier_llm().invoke(prompt)
    except Exception as exc:  # noqa: BLE001 —— LLM 调用异常统一兜底，不能让工作流崩溃
        print(f"  [Classify] 意图识别失败({exc.__class__.__name__})，按 complex 兜底转人工")
        classification = _fallback_classification()

    goto = route_by_classification(classification)
    print(f"  [Classify] intent={classification['intent']}, urgency={classification['urgency']}")
    print(f"  [Classify] -> 路由到: {goto}")
    return Command(update={"classification": classification}, goto=goto)
