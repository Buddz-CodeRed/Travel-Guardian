"""Check that the local AI model loads and can explain a scan finding.

Run with:  tg_env\\Scripts\\python.exe check_model.py
Uses a made-up example finding, so no network scan is needed.
Prints the explanation and how long it took.
"""

import time
from pathlib import Path

from llama_cpp import Llama

MODEL_PATH = Path(__file__).parent / "models" / "Llama-3.2-1B-Instruct-Q4_K_M.gguf"

# An example result in the same shape the risk rules will produce later.
EXAMPLE_FINDING = (
    "Network: CafeFreeWiFi, encryption: Open (none). Risk: HIGH. "
    "Your device has port 445 (Windows file sharing) open. Risk: HIGH."
)

# The model explains the risk rating; it does not decide it.
SYSTEM_PROMPT = (
    "You are Travel Guardian, a friendly assistant that helps a traveller "
    "understand the results of a security check on their own laptop and Wi-Fi. "
    "Explain the results in plain English in at most 4 short sentences, "
    "then list 2 simple actions they can take. "
    "Keep the risk levels exactly as given and do not add new findings."
)

start = time.perf_counter()
model = Llama(model_path=str(MODEL_PATH), n_ctx=2048, verbose=False)
load_seconds = time.perf_counter() - start

start = time.perf_counter()
reply = model.create_chat_completion(
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Please explain my check results:\n" + EXAMPLE_FINDING},
    ],
    max_tokens=200,
    temperature=0.2,  # low temperature keeps answers consistent
)
answer_seconds = time.perf_counter() - start

text = reply["choices"][0]["message"]["content"].strip()
tokens = reply["usage"]["completion_tokens"]

print(text)
print()
print(f"Model load: {load_seconds:.1f}s | Answer: {answer_seconds:.1f}s "
      f"| {tokens} tokens ({tokens / answer_seconds:.1f} tokens/s)")
