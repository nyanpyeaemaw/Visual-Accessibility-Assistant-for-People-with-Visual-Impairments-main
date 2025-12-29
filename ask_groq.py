
# ask_groq.py — qualitative, directional guidance
import os, json
from groq import Groq

client = Groq(api_key="YOUR_GROQ_KEY")
MODEL = "llama-3.1-8b-instant"

HAZARD_CLASSES = {"car", "truck", "bus"}

def humor_allowed(scene):
    # Qualitative: treat vehicles 'near' or stairs 'near' or red light as hazard
    for o in scene.get("objects", []):
        lab = (o.get("label") or "").lower()
        prox = (o.get("proximity") or "").lower()
        if lab in HAZARD_CLASSES and prox in {"near", "medium"}:
            return False
        if lab == "stairs" and prox in {"near", "medium"}:
            return False
        if lab == "traffic_light" and (o.get("state") == "red"):
            return False
    return True

def build_messages(scene, question, kb):
    tone = "friendly, concise; tiny gentle joke allowed" if humor_allowed(scene) else "calm, safety-first; no humor"
    
    system = (
        "You are a smart mobility assistant for a blind user. "
        "Speak in 1–2 short friendly sentences for text to speech. "
        "Never invent objects not in the Scene. "
        "BUT if the user asks a general 'what if' or advice question, "
        "you may answer using the Knowledge rules, even if the object is not in the Scene. "
        "Answer only the question that is asked."
        "Use near/medium/far only; no meters. "
        "Prefer simple guidance like 'go straight', 'turn slightly left/right'. "
        "If vehicles, stairs, or a red light are near/medium, warn first. "
        "If 'blocking_ahead' is non-empty, do NOT say 'go straight' and give the user direction. "
        "Instead, mention the obstacle and give a brief detour"
        "If 'path_clear_ahead' is true and the user asks about moving forward, "
        "say it's safe to proceed straight with normal caution."
        "You should know that if camera detects lots of chairs and people, it is likely in a classroom."
        "Just 'tables or desks' not 'dining tables' "
        f" Tone: {tone}."
    )

    user = (
        "Scene:\n" + json.dumps(scene, ensure_ascii=False) +
        "\n\nKnowledge:\n" + json.dumps(kb, ensure_ascii=False) +
        "\n\nUser question:\n" + question +
        "\n\nReturn only the spoken answer text."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]

def ask(scene, question, kb):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=build_messages(scene, question, kb),
        temperature=0.2,
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()
