import json
from pathlib import Path

MEMORY_PATH = Path(__file__).parent / "memory.json"
MAX_FACTS = 25

def load_facts() -> list[str]:
    if not MEMORY_PATH.exists():
        return []
    try:
        data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        return data.get("faits", [])
    except (json.JSONDecodeError, OSError):
        return []

def save_facts(facts: list[str]):
    facts = facts[:MAX_FACTS]
    MEMORY_PATH.write_text(
            json.dumps({"faits": facts}, ensure_ascii=False, indent=2), encoding="utf-8",
            )

def format_memory_block(facts: list[str]) -> str:
    if not facts:
        return ""
    bullets = "\n".join(f"- {f}" for f in facts)
    return (
            "IMPORTANT — Faits vrais et à jour sur lui, à utiliser activement "
        "pour répondre à ses questions. Si une question porte sur un de ces "
        "faits (son nom, son âge, sa ville, peu importe lequel), réponds-y "
        "correctement et directement — ne dis JAMAIS que tu ne sais pas "
        "alors que c'est écrit juste ici. Intègre-les naturellement dans la "
        f"conversation, sans les réciter comme une liste :\n{bullets}"
            )

