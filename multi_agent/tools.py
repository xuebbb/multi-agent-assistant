"""工具层:给 Agent 接现实世界的能力(联网搜索)。"""
from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """用 DuckDuckGo 搜索,返回格式化后的纯文本结果。无结果时返回空字符串。"""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    if not results:
        return ""
    # 每条结果格式: [标题] 摘要 —— 拼成一大段给 LLM 当上下文
    return "\n".join(f"[{r['title']}] {r['body']}" for r in results)
