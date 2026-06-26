import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()  # 从 .env 读 key,不硬编码、不进 git

# 连 DeepSeek(它兼容 OpenAI 接口,所以用 ChatOpenAI + 改 base_url)
llm = ChatOpenAI(
    model="deepseek-v4-pro",
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)


# 小助手:给一个"角色设定(system)"+"具体内容(user)",返回 LLM 的回答。
# 关键认知:同一个 llm,换不同的 system 提示词,就变成不同"角色"的 Agent。
def ask_llm(system: str, user: str) -> str:
    reply = llm.invoke([("system", system), ("human", user)])
    return reply.content


# State = "在图里流动的那张表"。
class State(TypedDict):
    question: str    # 用户的问题
    plan: str        # 规划者产出:分析角度
    analysis: str    # 执行者产出:逐角度分析
    critique: str    # 批判者产出:挑毛病
    verdict: str     # 批判者的结论:PASS(通过)/ REVISE(要改)
    attempts: int    # 执行者已经分析了几次(防死循环用)
    answer: str      # 汇总者产出:最终答案


# ---- 四个角色,每个是一个节点(工位) ----

def planner(state: State) -> State:
    system = "你是分析规划专家。把用户的问题拆成 3 个最值得深入的分析角度,每个角度一句话,用 1. 2. 3. 列出,只输出这三条。"
    return {"plan": ask_llm(system, state["question"])}


def worker(state: State) -> State:
    n = state.get("attempts", 0) + 1
    print(f"  [执行者] 第 {n} 次分析...")
    system = "你是分析专家。针对给定问题,按下面每个角度给出有深度、具体的分析。"
    user = f"问题:{state['question']}\n\n分析角度:\n{state['plan']}"
    # 如果是被打回重做,带上上一版的批判意见,针对性改进
    if state.get("critique"):
        user += f"\n\n上一版被批判者指出以下问题,请针对性改进:\n{state['critique']}"
    return {"analysis": ask_llm(system, user), "attempts": n}


def critic(state: State) -> State:
    system = (
        "你是严格的批判者。先在第一行只输出一个词:PASS(分析已足够好)或 REVISE(需要修改);"
        "从第二行起再写你的具体意见(薄弱点/遗漏/偏颇),不要重写分析。"
    )
    user = f"问题:{state['question']}\n\n待审分析:\n{state['analysis']}"
    text = ask_llm(system, user)
    first_line = text.split("\n", 1)[0].upper()
    verdict = "REVISE" if "REVISE" in first_line else "PASS"
    print(f"  [批判者] 结论:{verdict}")
    return {"critique": text, "verdict": verdict}


def synthesizer(state: State) -> State:
    system = "你是总编辑。综合下面的分析和批判意见,产出一份高质量、平衡、结构清晰的最终答案。"
    user = (
        f"问题:{state['question']}\n\n"
        f"分析:\n{state['analysis']}\n\n"
        f"批判意见:\n{state['critique']}"
    )
    return {"answer": ask_llm(system, user)}


# ---- 路由函数:批判者之后,决定"回炉重做"还是"定稿" ----
# 这是"条件边":根据 state 的内容,动态决定下一步去哪个节点。
def route_after_critic(state: State) -> str:
    # 要改 且 还没到重做上限(最多让执行者跑 3 次)→ 打回执行者
    if state["verdict"] == "REVISE" and state.get("attempts", 0) < 3:
        return "worker"
    # 否则(通过了 / 或已达上限)→ 去定稿
    return "synthesizer"


# ---- 接图:注意 critic 后面用的是"条件边" ----
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
    {"worker": "worker", "synthesizer": "synthesizer"},  # 路由函数返回值 → 去哪个节点
)
builder.add_edge("synthesizer", END)
graph = builder.compile()


if __name__ == "__main__":
    question = "学生时期的恋爱和工作时期的恋爱的优劣"
    print(f"【问题】{question}\n--- 智囊团开始工作 ---")
    result = graph.invoke({"question": question})

    print("\n【① 规划者拆的角度】\n", result["plan"])
    print("\n【② 执行者的分析(共", result["attempts"], "版)】\n", result["analysis"])
    print("\n【③ 批判者最终结论】", result["verdict"], "\n", result["critique"])
    print("\n【④ 汇总者的最终答案】\n", result["answer"])
