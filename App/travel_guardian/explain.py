"""Step 6: ask the local AI to explain the rule book's results simply.

If the AI model is missing or fails, a plain summary is built from the
rules instead, so the app always shows an explanation.

Try it:  python -m App.travel_guardian.explain
"""

import re
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "Llama-3.2-1B-Instruct-Q4_K_M.gguf"

# The AI's job is small on purpose: reword the rule book's facts so they sound
# natural. Testing showed that the more freedom the small model gets, the more
# it invents, so the prompt tells it to say only what the facts say.
SYSTEM_PROMPT = (
    "You are Travel Guardian, a friendly assistant. A traveller has already checked "
    "their own laptop and Wi-Fi, and gives you the facts that were found. Rewrite those "
    "facts as one short, natural paragraph, speaking to the traveller as 'you'. "
    "Start with the first fact straight away. "
    "Use at most 3 short sentences and everyday words. Do not use a list. "
    "Say only what the facts say. Do not add new facts, risks or advice."
)

# The opening sentence comes from the rules, not the AI, so the overall
# verdict is always right. The AI's paragraph follows it.
VERDICTS = {
    "Low": "Good news: this network and your laptop look safe.",
    "Medium": "This network is mostly fine, but there is something to be careful about.",
    "High": "Be careful on this network.",
}

_model = None # loaded once, the first time it's needed

def load_model():
    """ Load the AI model the first time, then reuse it. """
    global _model
    if _model is None:
        from llama_cpp import Llama
        _model = Llama(model_path=str(MODEL_PATH), n_ctx=2048, verbose=False)
    return _model

def unload_model():
    """ Close the AI model cleanly when the app shuts down. """
    global _model
    if _model is not None:
        _model.close()
        _model = None

def facts_for_ai(assessment):
    """ Pick the facts worth explaining and return them as a list of sentences.

    If anything is Medium or High, only those findings are used, so the
    explanation goes straight to what matters. Otherwise all (Low) findings
    are used. Technical names in brackets such as (SMB) are removed, and a
    sentence that is already in the list is not added twice.
    """
    worries = [f for f in assessment["findings"] if f["risk"] != "Low"]
    facts = []
    for finding in worries or assessment["findings"]:
        fact = re.sub(r" \([^)]*\)", "", finding["reason"])
        if fact not in facts:
            facts.append(fact)
    return facts

def fallback_summary(assessment):
    """A plain explanation built from the rules, used if the AI can't run."""
    verdict = VERDICTS[assessment["overall"]]
    if assessment["overall"] == "Low":
        return verdict
    return verdict + " " + " ".join(facts_for_ai(assessment))

def as_paragraph(text):
    """ Join the AI's reply into one flowing paragraph.

    The small model sometimes writes a list even when told not to. This removes
    list marks (-, * or a bullet) from the start of each line, skips
    introduction lines that end with a colon, and joins the rest with spaces.
    """
    sentences = []
    for line in text.splitlines():
        line = line.strip().lstrip("-*• ").strip()
        if line and not line.endswith(":"):
            sentences.append(line)
    paragraph = " ".join(sentences)

    # If the reply was cut off mid-sentence, keep only the finished sentences.
    if paragraph and paragraph[-1] not in ".!?":
        paragraph = paragraph[:paragraph.rfind(".") + 1]
    return paragraph

def explain(assessment):
    """ Return (explanation text, True if the AI wrote it). """
    try:
        model = load_model()
        facts = "\n".join("- " + fact for fact in facts_for_ai(assessment))
        reply = model.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "I checked my own laptop and Wi-Fi. These are the facts:\n" + facts
                                            + "\nRewrite these facts for me as one short paragraph."},
            ],
            max_tokens=110,
            temperature=0.2
        )
        paragraph = as_paragraph(reply["choices"][0]["message"]["content"])
        if not paragraph:
            return fallback_summary(assessment), False
        # Rule-written verdict first, then the AI's wording of the facts.
        return VERDICTS[assessment["overall"]] + " " + paragraph, True
    except Exception:
        return fallback_summary(assessment), False


if __name__ == "__main__":
    from App.travel_guardian.risk import assess

    example = assess(
        wifi={"authentication": "Open", "cipher": "None"},
        discovery={"other_devices": []},
        open_ports=[{"port": 445, "service": "microsoft-ds"}],
    )
    text, from_ai = explain(example)
    print(text)
    print(f"\n(Written by AI: {from_ai})")
