"""节点5: draft_response —— LLM 节点，生成回复草稿 + 判断是否需人工审核。

上下文格式化在节点内部完成，不污染 State（State 只存下游需要的数据）。
"""

from typing import Literal

from langgraph.types import Command

from email_agent.llm import get_llm
from email_agent.routing import needs_human_review
from email_agent.state import EmailAgentState

# 回复落款，按需改成你的产品/团队名
SIGNATURE = "AI 客服助手"

DRAFT_PROMPT = """起草一封回复邮件：
客户: {sender_email}
原邮件: {email_content}
意图: {intent} | 紧急度: {urgency}
{context}

要求：专业、友好、有针对性地解决用户问题。不超过100字。落款统一写"{signature}"。"""


def _format_context(state: EmailAgentState) -> str:
    """把检索结果、工单信息格式化为 prompt 上下文片段。"""
    parts: list[str] = []
    if state.get("search_results"):
        docs = "\n".join(f"- {r}" for r in state["search_results"])
        parts.append(f"文档:\n{docs}")
    if state.get("customer_history"):
        parts.append(f"工单: {state['customer_history']}")
    return "\n".join(parts)


def draft_response(
    state: EmailAgentState,
) -> Command[Literal["human_review", "send_reply"]]:
    """LLM 生成回复草稿；紧急/复杂/账单类问题转人工审核，其余直接发送。"""
    classification = state.get("classification") or {}
    prompt = DRAFT_PROMPT.format(
        sender_email=state["sender_email"],
        email_content=state["email_content"],
        intent=classification.get("intent"),
        urgency=classification.get("urgency"),
        context=_format_context(state),
        signature=SIGNATURE,
    )

    response = get_llm().invoke(prompt)
    print(f"  [Draft] 回复已生成 ({len(response.content)} 字符)")

    goto = "human_review" if needs_human_review(classification) else "send_reply"
    print(f"  [Draft] -> 路由到: {goto}")
    return Command(update={"draft_response": response.content}, goto=goto)
