"""分层测试:验证代码没破(L0-L3 秒出零 token) + 可选全链路(L4 烧 token)。

用法:
    python test_setup.py           # 跑 L0-L3,秒出
    python test_setup.py --full    # 额外跑 L4 全链路(烧 token,慢)
"""
import sys
import time
import argparse

sys.stdout.reconfigure(encoding="utf-8")

def layer_0_imports():
    """L0:所有模块能加载,无语法错/拼写错/循环导入。"""
    import multi_agent
    import multi_agent.state
    import multi_agent.llm      # 创建客户端对象,但不发请求
    import multi_agent.config
    import multi_agent.agents
    import multi_agent.graph
    import multi_agent.cli
    import multi_agent.tools
    print("  L0 [导入]   OK 所有模块加载成功")

def layer_1_prompts():
    """L1:prompts.yaml 能解析,4 个角色提示词都在且非空。"""
    from multi_agent.config import load_prompts
    prompts = load_prompts()
    expected = {"planner", "worker", "critic", "synthesizer"}
    assert set(prompts.keys()) == expected, f"提示词 key 不对: {set(prompts.keys())}"
    for k in prompts:
        assert prompts[k].strip(), f"提示词 {k} 为空"
    print(f"  L1 [配置]   OK prompts.yaml 结构正确 ({len(prompts)} 个角色)")

def layer_2_tool():
    """L2:联网搜索能拿到结果(一次 HTTP,~2s,不调 LLM)。"""
    from multi_agent.tools import web_search
    r = web_search("AI Agent", max_results=1)
    assert isinstance(r, str) and len(r) > 0, "搜索无结果"
    print(f"  L2 [工具]   OK 搜索返回 {len(r)} 字符")

def layer_3_graph():
    """L3:图能编译 + 条件边路由逻辑对(纯函数,零开销)。"""
    from multi_agent.graph import build_graph, route_after_critic
    # 路由逻辑(纯 if/else)
    assert route_after_critic({"verdict": "REVISE", "attempts": 0}) == "worker", "REVISE 应回炉"
    assert route_after_critic({"verdict": "REVISE", "attempts": 2}) == "worker", "REVISE 应回炉"
    assert route_after_critic({"verdict": "REVISE", "attempts": 3}) == "synthesizer", "达上限应定稿"
    assert route_after_critic({"verdict": "PASS", "attempts": 1}) == "synthesizer", "PASS 应定稿"
    assert route_after_critic({"verdict": "PASS", "attempts": 0}) == "synthesizer", "PASS 应定稿"
    # 图能编译(检查节点/边接好,不执行任何节点)
    g = build_graph()
    print("  L3 [图结构] OK 图编译通过 + 路由逻辑正确")

def layer_4_full():
    """L4:端到端全链路(烧 token,慢)。只在 --full 时跑。"""
    from multi_agent.graph import build_graph
    print("  L4 [全链路] 开始...(烧 token,约 30s+)")
    result = build_graph().invoke({"question": "用一句话介绍 LangGraph"})
    assert result.get("plan"), "无 plan"
    assert result.get("analysis"), "无 analysis"
    assert result.get("answer"), "无 answer"
    assert result["attempts"] >= 1
    print(f"  L4 [全链路] OK 共 {result['attempts']} 版,产出完整")


def main():
    parser = argparse.ArgumentParser(description="分层测试")
    parser.add_argument("--full", action="store_true", help="额外跑 L4 全链路(烧 token)")
    args = parser.parse_args()

    print("===== 分层测试开始 =====\n")
    t0 = time.time()

    layer_0_imports()
    layer_1_prompts()
    layer_2_tool()
    layer_3_graph()

    if args.full:
        layer_4_full()
    else:
        print("  L4 [全链路] 跳过(加 --full 跑,烧 token)")

    elapsed = time.time() - t0
    print(f"\n===== 全部通过 ({elapsed:.1f}s) =====")


if __name__ == "__main__":
    main()
