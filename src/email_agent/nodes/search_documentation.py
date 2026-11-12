"""节点3: search_documentation —— Data 节点，检索知识库。

失败策略：检索超时由 graph 上的 RetryPolicy 自动重试（指数退避）；
重试耗尽仍失败则降级返回空结果，不阻塞主流程。
"""

from typing import Literal

from langgraph.types import Command

from email_agent.state import EmailAgentState

# 模拟知识库，实际项目可替换为 RAG 向量检索
_KNOWLEDGE_BASE = [
    "密码重置: 登录 -> 设置 -> 安全 -> 修改密码",
    "密码至少12位，包含大小写和特殊字符",
    "两步验证开启方法: 安全设置 -> 两步验证",
]


def knowledge_base_search(query: str) -> list[str]:
    """知识库检索。真实场景此处对接 RAG / ES / API。"""
    if not query.strip():
        raise ValueError("检索词为空")
    # 模拟检索：返回全部文档（demo 不做相关性过滤）
    return list(_KNOWLEDGE_BASE)


def search_documentation(
    state: EmailAgentState,
) -> Command[Literal["draft_response"]]:
    """根据分类结果构建查询并检索知识库，完成后跳去生成草稿。"""
    classification = state.get("classification") or {}
    query = f"{classification.get('intent', '')} {classification.get('topic', '')}"
    print(f"  [Search] 查询: {query}")

    try:
        search_results = knowledge_base_search(query)
    except Exception as exc:  # noqa: BLE001 —— 检索失败降级为空结果，流程继续
        print(f"  [Search] 检索失败({exc.__class__.__name__})，降级为空结果")
        search_results = []

    return Command(update={"search_results": search_results}, goto="draft_response")
