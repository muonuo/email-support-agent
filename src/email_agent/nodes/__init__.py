"""节点实现 —— 每个节点只做一件事。

按职责分四类：
- Data 节点：read_email、search_documentation（检索外部数据）
- LLM 节点：classify_intent、draft_response（理解/分析/生成）
- Action 节点：bug_tracking、send_reply（执行外部操作）
- Human 节点：human_review（人机交互）
"""

from email_agent.nodes.read_email import read_email
from email_agent.nodes.classify_intent import classify_intent
from email_agent.nodes.search_documentation import search_documentation
from email_agent.nodes.bug_tracking import bug_tracking
from email_agent.nodes.draft_response import draft_response
from email_agent.nodes.human_review import human_review
from email_agent.nodes.send_reply import send_reply

__all__ = [
    "read_email",
    "classify_intent",
    "search_documentation",
    "bug_tracking",
    "draft_response",
    "human_review",
    "send_reply",
]
