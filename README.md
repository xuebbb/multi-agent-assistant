# 多 Agent 协作智囊团(Multi-Agent Think Tank)

用 **LangGraph** 编排的多智能体系统:针对一个开放问题,由四个角色 Agent 协作产出一份高质量答案,并带「批判 → 回炉重做」的自我改进循环。

## 它怎么工作

```
              ┌─ 规划者:把问题拆成 3 个分析角度
你的问题 ──→  ├─ 执行者:逐角度给出深度分析  ←─────┐
              ├─ 批判者:挑薄弱点,判 PASS / REVISE ─┤ REVISE 就带着意见回炉重做
              └─ 汇总者:综合分析+批判,定稿       └─(最多重做 2 次,防死循环)
```

四个角色本质是**同一个大模型戴不同「角色提示词(system prompt)」**;它们沿着一张**共享状态表(State)**接力,产物逐步累积。批判者之后用 **条件边(conditional edge)** 动态决定「回炉重做」还是「定稿」。

## 核心特性

- **多角色协作**:规划 / 执行 / 批判 / 汇总四个 Agent 分工。
- **自我改进循环**:批判者不满意 → 把分析打回执行者,带着意见重做。
- **安全阀**:重做有次数上限(最多 3 次分析),避免无限循环烧 token。
- **密钥安全**:API key 只放本地 `.env`,通过 `.gitignore` 确保不进版本库。

## 技术栈

- [LangGraph](https://github.com/langchain-ai/langgraph) —— Agent 流程编排(状态 / 节点 / 条件边)
- DeepSeek API（兼容 OpenAI 接口）

## 如何运行

```bash
# 1) 装依赖
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt   # Windows
# (macOS/Linux: source .venv/bin/activate && pip install -r requirements.txt)

# 2) 配置密钥:复制 .env.example 为 .env,填入自己的 key
#    DEEPSEEK_API_KEY=sk-xxxx

# 3) 跑
python main.py
```

## 设计笔记 / 学到了什么

- **「多 Agent」的本质**不是多个模型,而是**角色分工 + 通过共享状态通信 + 调度**——这与多智能体系统(角色分工、协同、防跑偏)的思想一致。
- **条件边**是「单向流水线」升级为「会自我改进的系统」的关键。
- **任何带循环的 Agent 都必须有次数上限**,否则会死循环。

---

*个人学习项目。后续可扩展:给执行者接入联网搜索工具、把角色提示词做成配置、加 Web 界面。*
