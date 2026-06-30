"""加载角色提示词配置(config/prompts.yaml)。改提示词 = 改人设,不动代码。"""
import yaml
from pathlib import Path

# 本文件在 multi_agent/ 里,提示词在根目录 config/ 里,所以往上一层
_PROMPTS_PATH = Path(__file__).resolve().parent.parent / "config" / "prompts.yaml"


def load_prompts() -> dict:
    with open(_PROMPTS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
