"""路由决策纯函数 —— 从节点中抽出，便于单元测试。

对应方法论"决策定义在节点内部"：节点调用这些函数决定 Command 的 goto，
而不是在图上挂条件边。决策逻辑与节点实现分离，测试时无需真实调用 LLM。
"""

from email_agent.state import EmailClassification

# 意图 -> 分类后的下一跳（question/feature 查文档，bug 建工单，其余直接出稿）
_CLASSIFY_ROUTE = {
    "question": "search_documentation",
    "feature": "search_documentation",
    "bug": "bug_tracking",
}

# 需要人工审核的意图与紧急度
_REVIEW_INTENTS = frozenset({"complex", "billing"})
_REVIEW_URGENCIES = frozenset({"high", "critical"})


def route_by_classification(classification: EmailClassification) -> str:
    """意图识别后的路由：返回下一节点名。"""
    return _CLASSIFY_ROUTE.get(classification["intent"], "draft_response")


def needs_human_review(classification: EmailClassification) -> bool:
    """草稿生成后是否需要人工审核。

    规则：紧急任务（high/critical）或复杂/账单类问题都转人工。
    """
    return (
        classification["intent"] in _REVIEW_INTENTS
        or classification["urgency"] in _REVIEW_URGENCIES
    )
