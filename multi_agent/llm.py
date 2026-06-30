"""LLM 客户端封装。连 DeepSeek(兼容 OpenAI 接口),提供 ask_llm 小助手。"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()  # 从 .env 读 key,不硬编码、不进 git

# 同一个 llm 实例,换不同 system prompt 就变成不同"角色"的 Agent
llm = ChatOpenAI(
    model="deepseek-v4-pro",
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)


def ask_llm(system: str, user: str) -> str:
    """给一个角色设定(system) + 具体内容(user),返回 LLM 的回答文本。"""
    reply = llm.invoke([("system", system), ("human", user)])
    return reply.content
