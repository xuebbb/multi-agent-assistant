"""State = 在图里流动的那张共享状态表。每个节点读它、往里写自己的产物。"""
from typing import TypedDict


class State(TypedDict):
    question: str    # 用户的问题(入口)
    plan: str        # 规划者产出:3 个分析角度
    analysis: str    # 执行者产出:逐角度分析
    critique: str    # 批判者产出:挑毛病
    verdict: str     # 批判者的结论:PASS(通过) / REVISE(要改)
    attempts: int    # 执行者已经分析了几次(防死循环的安全阀)
    answer: str      # 汇总者产出:最终答案
