"""Email Support Agent —— 基于 LangGraph 的客户支持邮件 Agent。

课程来源：《Langchain和LangGraph入门到实战》第5章第3节 Think In LangGraph。
核心思想：路由决策写在节点内部（Command），而不是条件边；图只保留最小边。
"""

from email_agent.graph import build_graph
__all__ = ["build_graph"]
