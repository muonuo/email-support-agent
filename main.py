"""CLI 演示入口：依次跑三个典型场景，人工审核环节在终端交互。

用法：
    uv run main.py
"""

import sys

from dotenv import load_dotenv
from langgraph.types import Command

from email_agent.graph import build_graph
from email_agent.state import EmailAgentState

# Windows 终端默认 GBK，重配为 UTF-8 以支持 emoji/中文输出
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# 三个典型场景：覆盖 自动回复 / 建工单+审核 / 紧急直接审核 三条路径
SCENARIOS = [
    {
        "id": "email-001",
        "title": "场景1: 普通问题（查文档 -> 自动回复，全程无人工）",
        "content": "Hi，我忘记登录密码了，如何重置？",
        "sender": "jack@example.com",
    },
    {
        "id": "email-002",
        "title": "场景2: Bug 报告（建工单 -> 人工审核）",
        "content": "PDF导出功能每次都会崩溃，急需修复！",
        "sender": "jane@corp.com",
    },
    {
        "id": "vip-email-003",
        "title": "场景3: 紧急账单（跳过检索 -> 人工审核）",
        "content": "我被重复扣款了！这是什么情况！请立刻处理！",
        "sender": "jack@corp.com",
    },
]

BANNER_WIDTH = 60


def print_banner(title: str) -> None:
    print("=" * BANNER_WIDTH)
    print(f"📧 {title}")
    print("=" * BANNER_WIDTH)


def initial_state(scenario: dict) -> EmailAgentState:
    """把演示场景转成图的初始 State。"""
    return {
        "email_content": scenario["content"],
        "sender_email": scenario["sender"],
        "email_id": scenario["id"],
        "classification": None,
        "search_results": None,
        "customer_history": None,
        "draft_response": None,
    }


def show_review_panel(info: dict) -> None:
    """展示人工审核面板：原始邮件 + 分类信息 + AI 草稿。"""
    print("-" * BANNER_WIDTH)
    print(f"待审邮件: {info['email_id']} | intent={info['intent']} | urgency={info['urgency']}")
    print(f"原邮件: {info['original_email']}")
    print()
    print("AI 草稿:")
    print(info["draft_response"])
    print("-" * BANNER_WIDTH)


def collect_human_decision() -> dict:
    """在终端收集人工决策：approve 直接发送 / edit 修改后发送。"""
    while True:
        choice = input("请选择 [approve] 直接发送 / [edit] 修改后发送: ").strip().lower()
        if choice in ("approve", "edit"):
            break
        print("输入无效，请输入 approve 或 edit")

    if choice == "approve":
        return {"action": "approve"}

    print("请输入修改后的回复内容（单独一行输入 END 结束）:")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return {"action": "edit", "edited_response": "\n".join(lines)}


def handle_interrupts(app, config: dict, result: dict) -> None:
    """若执行被 interrupt 暂停（等待人工审核），在终端交互后恢复。"""
    for intr in result.get("__interrupt__") or []:
        print("\n⏸️  触发人工审核（interrupt），图已暂停")
        show_review_panel(intr.value)
        decision = collect_human_decision()
        app.invoke(Command(resume=decision), config)


def run_scenario(app, scenario: dict) -> None:
    """跑单个场景：invoke -> 若有 interrupt 则交互恢复。"""
    config = {"configurable": {"thread_id": f"demo-{scenario['id']}"}}
    print(f"\n=== {scenario['title']} ===\n")
    result = app.invoke(initial_state(scenario), config)
    handle_interrupts(app, config, result)
    print()


def main() -> None:
    app = build_graph()
    for scenario in SCENARIOS:
        run_scenario(app, scenario)
    print("✅ 全部场景执行完成")


if __name__ == "__main__":
    main()
