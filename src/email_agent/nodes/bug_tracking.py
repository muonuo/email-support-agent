"""节点4: bug_tracking —— Action 节点，创建 Bug 工单。

幂等性：工单号由 email_id 哈希生成，同一封邮件重复触发得到同一工单号，
天然去重，符合 Action 节点"可安全重试"的要求。
"""

from typing import Literal

from langgraph.types import Command

from email_agent.state import EmailAgentState


def make_ticket_id(email_id: str) -> str:
    """由邮件 ID 确定性地生成工单号（幂等：同邮件 -> 同工单号）。"""
    return f"BUG-{hash(email_id) % 100000:05d}"


def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """为 Bug 报告创建工单，并写入 customer_history 供草稿节点引用。"""
    ticket_id = make_ticket_id(state["email_id"])
    print(f"  [BugTrack] 创建工单 {ticket_id}")

    return Command(
        update={
            "search_results": [f"Bug 工单 {ticket_id} 已创建"],
            "customer_history": {"ticket_id": ticket_id},
        },
        goto="draft_response",
    )
