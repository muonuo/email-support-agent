"""LLM 初始化 —— 惰性单例，避免 import 阶段就要求 API Key。

模型与分类器全局只初始化一次（lru_cache）；
没有 DEEPSEEK_API_KEY 时仍可 import 本包跑路由单元测试。
"""

from functools import lru_cache

from langchain.chat_models import init_chat_model

from email_agent.state import EmailClassification

MODEL_NAME = "deepseek-flash"


@lru_cache(maxsize=1)
def get_llm():
    """通用对话模型（生成草稿等）。"""
    return init_chat_model(MODEL_NAME)


@lru_cache(maxsize=1)
def get_classifier_llm():
    """绑定结构化输出的分类模型，用于意图识别。

    deepseek-flash 是思考模式模型，不支持 function calling 的
    tool_choice 强制参数，因此用 json_mode（prompt 中约定 JSON 格式）。
    """
    return get_llm().with_structured_output(EmailClassification, method="json_mode")
