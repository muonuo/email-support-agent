"""State 设计 —— 所有节点共享的"工作笔记本"。

入 State 原则：下游节点需要用它做决策或处理、无法从其他字段推导、
重新获取成本高的信息才存。能推导的不存，临时变量不存。
"""

from typing import Literal, TypedDict

Intent = Literal["question", "bug", "billing", "feature", "complex"]
Urgency = Literal["low", "medium", "high", "critical"]


class EmailClassification(TypedDict):
    """意图识别的结构化输出（LLM with_structured_output 的目标格式）。"""

    intent: Intent
    urgency: Urgency
    topic: str
    summary: str


class EmailAgentState(TypedDict, total=False):
    """邮件 Agent 的全局 State。

    四类字段：
    - 原始输入：邮件内容与发件人（之后无法重建）
    - 分类结果：被后续多个节点所需
    - 外部数据：搜索结果 / 工单信息（重新获取成本高）
    - 生成内容：回复草稿（人工审核期间要展示）
    """

    # 原始输入
    email_content: str
    sender_email: str
    email_id: str
    # 分类结果
    classification: EmailClassification | None
    # 外部数据
    search_results: list[str] | None
    customer_history: dict | None
    # 生成内容
    draft_response: str | None
