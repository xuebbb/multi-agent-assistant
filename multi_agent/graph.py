"""接图:把四个节点连成一张会自我改进的流水线,编译成可执行的 graph。"""
from langgraph.graph import StateGraph, START, END

from multi_agent.state import State
from multi_agent.agents import planner, worker, critic, synthesizer


def route_after_critic(state: State) -> str:
    """条件边:批判者之后,决定'回炉重做'还是'定稿'。

    要改 且 还没到重做上限(最多 3 次) -> 打回执行者
    否则(通过了 / 或已达上限)       -> 去定稿
    """
    if state["verdict"] == "REVISE" and state.get("attempts", 0) < 3:
        return "worker"
    return "synthesizer"


def build_graph():
    """构建并编译 LangGraph 图。"""
    builder = StateGraph(State)
    builder.add_node("planner", planner)
    builder.add_node("worker", worker)
    builder.add_node("critic", critic)
    builder.add_node("synthesizer", synthesizer)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "worker")
    builder.add_edge("worker", "critic")
    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {"worker": "worker", "synthesizer": "synthesizer"},  # 返回值 -> 去哪个节点
    )
    builder.add_edge("synthesizer", END)

    return builder.compile()
