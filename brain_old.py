from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from personality import SYSTEM_PROMPT
import memory
import re

_client = Anthropic(api_key=ANTHROPIC_API_KEY)
_history = []
_facts = memory.load_facts()
_EMOTION_RE = re.compile(r"\[EMOTION:(\w+)\]\s*$")
_VALID_EMOTIONS = {"happy", "sad", "angry", "neutral", "relaxed"}
_last_emotion = "neutral"

MAX_TURNS = 25

RESPOND_TOOL = {
    "name": "repondre",
    "description": "Fournit la réponse orale de Mary ainsi que l'émotion qu'elle ressent actuellement.",
    "input_schema": {
        "type": "object",
        "properties": {
            "texte": {
                "type": "string",
                "description": "Ce que Mary dit à voix haute, selon les règles de style du system prompt.",
            },
            "emotion": {
                "type": "string",
                "enum": ["happy", "sad", "angry", "neutral", "relaxed"],
                "description": "L'émotion que Mary ressent à ce moment, selon sa propre réaction à la conversation -- jamais un miroir de l'émotion de l'utilisateur.",
            },
        },
        "required": ["texte", "emotion"],
    },
}

CHECK_IN_NOTE = (
        "[note: aucune parole détectée depuis un moment — réagis naturellement "
    "à ce silence, comme quelqu'un qui remarque que l'autre est là mais ne "
    "dit rien, sans jamais mentionner cette note]"
        )

VISION_NOTE_TEMPLATE = (
   "[note: la webcam vient de détecter un changement dans la scène{mood_clause} — "
   "regarde l'image et réagis naturellement si c'est pertinent (quelqu'un "
   "qui arrive, qui part, un objet qui bouge, etc.). Si rien d'intéressant "
   "ne justifie un commentaire, tu peux rester silencieuse en répondant "
   "juste par '...'. Ne mentionne jamais cette note ni le fait que tu "
   "'analyses une image']"
)

MOOD_CHANGE_NOTE_TEMPLATE = (
   "[note: la détection d'émotion locale remarque que {name} a l'air "
   "{mood} maintenant -- réagis naturellement à ce changement d'humeur si "
   "c'est pertinent, sans jamais mentionner cette note ni le mécanisme de "
   "détection d'émotion. Si ce n'est pas assez significatif pour réagir, "
   "tu peux rester silencieuse en répondant juste par '...']"
)

GREETING_NOTE_TEMPLATE = (
   "[note: la reconnaissance faciale vient d'identifier {name} qui arrive "
   "devant la caméra{mood_clause} -- accueille-la/le naturellement par son "
   "nom, en tenant compte de son état d'esprit si c'est pertinent, comme si "
   "tu venais de la/le voir entrer, sans jamais mentionner cette note ni le "
   "mécanisme de reconnaissance faciale ou d'émotion]"
)

def get_last_emotion() -> str:
    return _last_emotion

def greet(name: str, mood: str | None = None) -> str:
    """Elle salue une personne reconnue par la webcam."""
    mood_clause = f", elle a l'air {mood}" if mood else ""
    return ask(GREETING_NOTE_TEMPLATE.format(name=name, mood_clause=mood_clause))


def check_in() -> str:
    return ask(CHECK_IN_NOTE)

def react_to_vision(image_b64: str, mood: str | None = None) -> str:
    """Elle prend l'initiative après un changement détecté par la webcam."""
    mood_clause = f" (la personne a l'air {mood})" if mood else ""
    return ask(VISION_NOTE_TEMPLATE.format(mood_clause=mood_clause), image_b64=image_b64)

def react_to_mood(name: str | None, mood: str) -> str:
    """Elle réagit à un changement d'humeur détecté indépendamment du mouvement."""
    who = name if name else "quelqu'un"
    return ask(MOOD_CHANGE_NOTE_TEMPLATE.format(name=who, mood=mood))

def _system_prompt() -> str:
    memory_block = memory.format_memory_block(_facts)
    if memory_block:
        return memory_block.strip() + "\n\n" + SYSTEM_PROMPT
    return SYSTEM_PROMPT

def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    for block in content:
        if block.get("type") == "text":
            return block["text"]
    return ""

def ask(user_text: str, image_b64: str | None = None) -> str:
    if image_b64:
        content = [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
                    },
                {"type": "text", "text": user_text},
                ]

    _history.append({"role": "user", "content": content if image_b64 else user_text})

    response = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            system=_system_prompt(),
            messages=_history[-MAX_TURNS:],
            tools=[RESPOND_TOOL],
            tool_choice={"type": "tool", "name": "repondre"},
            )

    tool_use = next((b for b in response.content if b.type == "tool_use"), None)

    if tool_use is None:
        reply = "..."
        _last_emotion = "neutral"
    else:
        reply = tool_use.input.get("text", "...").strip()
        emotion = tool_use.input.get("emotion", "neutral")
        _last_emotion = emotion if emotion in _VALID_EMOTIONS else "neutral"

    """reply = "".join(block.text for block in response.content if block.type == "text").strip() 

    global _last_emotion
    match = _EMOTION_RE.search(reply)
    if match and match.group(1) in _VALID_EMOTIONS:
        _last_emotion = match.group(1)
        reply = _EMOTION_RE.sub("", reply).strip()

    else:
        print(f"[debug] AUCUN tag d'émotion valide trouvé, réponse brute : {reply!r}")
        _last_emotion = "neutral"
    """
    
    _history.append({"role": "assistant", "content": reply})
    return reply

def update_memory():
    """ À appeler en quittant : résume la conversation et met à jour la mémoire."""
    global _facts

    if len(_history) < 2:
        return

    existing = "\n".join(f"- {f}" for f in _facts) or "(aucun fait pour l'instant)"
    convo = "\n".join(f"{m['role']}: {_text_of(m['content'])}" for m in _history)

    extraction_prompt = (
        "Faits déjà connus sur l'utilisateur :\n"
        f"{existing}\n\n"
        "Conversation qui vient d'avoir lieu :\n"
        f"{convo}\n\n"
        "Mets à jour la liste des faits durables et utilises à retenir sur "
        "l'utilisateur (préférences, événements importants, contexte de vie, "
        "état émotionnel récurrent). Fusionne avec les faits existants, " 
        "enlève les doublons et l'bosolète, garde au maximum 25 faits." 
        "Réponds uniquement avec un fait par ligne, sans numéro, sans tiret." 
        )

    response = _client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": extraction_prompt}]
        )
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    new_facts = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]

    if new_facts:
        _facts = new_facts
        memory.save_facts(_facts)

def reset():
    _history.clear()                                            
