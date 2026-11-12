"""节点6: human_review —— Human 节点，人工审核（Human-in-the-loop）。

通过 interrupt() 暂停图执行，把待审信息抛给外部调用方（CLI/前端）；
调用方收集人工决策后用 Command(resume=...) 恢复执行。

resume 的数据协议（与前端约定好）：
- {"action": "approve"}                 批准，按原草稿发送
- {"action": "edit", "edited_response": "..."}  修改后发送
"""

from langgraph.types import interrupt

from email_agent.state import EmailAgentState


def human_review(state: EmailAgentState) -> dict:
    """暂停等待人工审批。interrupt 的 payload 会出现在调用方结果的 __interrupt__ 中。"""
    classification = state.get("classification") or {}

    human_decision = interrupt({
        "email_id": state.get("email_id", ""),
        "original_email": state.get("email_content", ""),
        "draft_response": state.get("draft_response", ""),
        "urgency": classification.get("urgency"),
        "intent": classification.get("intent"),
        "action": "请审阅并批准或编辑此回复,输入[approve 或 edit]",
    })

    if human_decision.get("action") == "edit":
        # 人工改写了草稿，更新 State 后继续
        return {"draft_response": human_decision.get("edited_response")}
    # approve：保持原草稿，继续发送
    return {}
