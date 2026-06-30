"""四个角色节点(工位)。每个是一个纯函数:读 State -> 往 State 里写自己的产物。"""
from multi_agent.config import load_prompts
from multi_agent.llm import ask_llm
from multi_agent.tools import web_search

# 启动时一次性加载提示词,节点函数直接读这个字典
PROMPTS = load_prompts()


def planner(state) -> dict:
    """规划者:把问题拆成 3 个分析角度。"""
    return {"plan": ask_llm(PROMPTS["planner"], state["question"])}


def worker(state) -> dict:
    """执行者:先联网搜索拿真实信息,再逐角度给出有深度的分析。

    被打回重做时会带上上一版的批判意见针对性改进。
    """
    n = state.get("attempts", 0) + 1
    print(f"  [执行者] 第 {n} 次分析...(先联网搜索)")
    # ── 第一步:联网搜索,拿真实信息当素材 ──
    evidence = web_search(state["question"], max_results=5)
    user = f"问题:{state['question']}\n\n分析角度:\n{state['plan']}"
    # 把搜索结果作为"参考资料"喂给 LLM,让它基于真实信息分析而非凭空编
    if evidence:
        user += f"\n\n以下是联网搜索到的参考资料(请基于这些真实信息分析):\n{evidence}"
    # 如果是回炉重做,带上上一版的批判意见
    if state.get("critique"):
        user += f"\n\n上一版被批判者指出以下问题,请针对性改进:\n{state['critique']}"
    return {"analysis": ask_llm(PROMPTS["worker"], user), "attempts": n}


def critic(state) -> dict:
    """批判者:挑薄弱点,判 PASS / REVISE。第一行必须是 PASS 或 REVISE。"""
    user = f"问题:{state['question']}\n\n待审分析:\n{state['analysis']}"
    text = ask_llm(PROMPTS["critic"], user)
    first_line = text.split("\n", 1)[0].upper()
    verdict = "REVISE" if "REVISE" in first_line else "PASS"
    print(f"  [批判者] 结论:{verdict}")
    return {"critique": text, "verdict": verdict}


def synthesizer(state) -> dict:
    """汇总者:综合分析 + 批判,产出最终定稿。"""
    user = (
        f"问题:{state['question']}\n\n"
        f"分析:\n{state['analysis']}\n\n"
        f"批判意见:\n{state['critique']}"
    )
    return {"answer": ask_llm(PROMPTS["synthesizer"], user)}
