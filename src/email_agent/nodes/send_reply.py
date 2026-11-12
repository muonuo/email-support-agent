"""节点7: send_reply —— Action 节点，发送回复邮件。"""

from email_agent.state import EmailAgentState


def send_reply(state: EmailAgentState) -> dict:
    """发送邮件。真实业务对接 SMTP / 邮件服务 API。"""
    draft = state.get("draft_response", "")
    print(f"  [Send] 发送回复邮件给 {state['sender_email']} 成功...\n\n{draft}")
    return {}
