"""节点1: read_email —— Data 节点，解析邮件原始信息。"""

from email_agent.state import EmailAgentState


def read_email(state: EmailAgentState) -> dict:
    """读取收件箱新邮件。真实业务在此连接邮件服务器（IMAP/POP3）拉取。"""
    print(f"  [Read] 收到邮件: {state['email_id']}")
    # 无需更新 State：邮件内容由调用方作为初始 State 传入
    return {}
