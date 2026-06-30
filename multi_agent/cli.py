"""命令行入口(typer)。用法: python main.py "你的问题" """
import sys
sys.stdout.reconfigure(encoding="utf-8")   # Windows 控制台默认 GBK,强制 UTF-8 中文才不乱码
import typer
from multi_agent.graph import build_graph

app = typer.Typer(help="多 Agent 协作智囊团 —— 输入问题,四角色协作产出带自我改进的高质量答案。")


@app.command()
def run(question: str = typer.Argument(..., help="要分析的开放问题")):
    """运行智囊团分析一个问题。"""
    typer.echo(f"【问题】{question}\n--- 智囊团开始工作 ---")
    result = build_graph().invoke({"question": question})

    typer.echo("\n【① 规划者拆的角度】\n" + result["plan"])
    typer.echo(f"\n【② 执行者的分析(共 {result['attempts']} 版)】\n" + result["analysis"])
    typer.echo("\n【③ 批判者最终结论】" + result["verdict"] + "\n" + result["critique"])
    typer.echo("\n【④ 汇总者的最终答案】\n" + result["answer"])


if __name__ == "__main__":
    app()
