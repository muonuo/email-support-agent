"""图的组装 —— 最小边原则。

节点内部已通过 Command 声明路由，图上只需定义固定跳转和起点/终点：
START -> read_email -> classify_intent（之后全靠 Command 分流）
human_review -> send_reply -> END
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from email_agent.nodes import (
    bug_tracking,
    classify_intent,
    draft_response,
    human_review,
    read_email,
    search_documentation,
    send_reply,
)
from email_agent.state import EmailAgentState


def build_graph():
    """构建并编译客户支持 Agent 图。

    - interrupt 需要持久化，compile 时挂 InMemorySaver（生产换持久化存储）
    - 易失败的检索节点挂 RetryPolicy（指数退避，最多 3 次）
    """
    workflow = StateGraph(EmailAgentState)

    workflow.add_node("read_email", read_email)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node(
        "search_documentation",
        search_documentation,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0),
    )
    workflow.add_node("bug_tracking", bug_tracking)
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("human_review", human_review)
    workflow.add_node("send_reply", send_reply)

    workflow.add_edge(START, "read_email")
    workflow.add_edge("read_email", "classify_intent")
    workflow.add_edge("human_review", "send_reply")
    workflow.add_edge("send_reply", END)

    return workflow.compile(checkpointer=InMemorySaver())
