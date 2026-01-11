from pathlib import Path
from scr.processes import clean_text
import markovify
import spacy
from scr.voice import analyze_voice, DEFAULT_BAN_LEMMAS

nlp = spacy.load("en_core_web_md")

def load_text(path: str) -> str:
    return Path(path).read_text()

with open ("data/clarissa.txt") as f:
    clarissa_txt = f.read()

with open ("data/septimus.txt") as f:
    septimus_txt = f.read()

clarissa_text = clean_text(clarissa_txt)
septimus_text = clean_text(septimus_txt)

clarissa_model = markovify.Text(clarissa_text, state_size=2)
septimus_model = markovify.Text(septimus_text, state_size=2)

clarissa_stats = analyze_voice(clarissa_text, nlp, ban_lemmas=DEFAULT_BAN_LEMMAS)
septimus_stats  = analyze_voice(septimus_text, nlp, ban_lemmas=DEFAULT_BAN_LEMMAS)

print("\n--- Clarissa stats ---")
print("Mean sentence length:", round(clarissa_stats.mean_sent_len, 1))
print("POS proportions:", {k: round(v, 3) for k, v in clarissa_stats.top_pos.items()})
print("Top lemmas:", clarissa_stats.top_lemmas)

print("\n--- Septimus stats ---")
print("Mean sentence length:", round(septimus_stats.mean_sent_len, 1))
print("POS proportions:", {k: round(v, 3) for k, v in septimus_stats.top_pos.items()})
print("Top lemmas:", septimus_stats.top_lemmas)

print("Clarissa sample:", clarissa_model.make_sentence(tries=10))
print("Septimus sample:", septimus_model.make_sentence(tries=10))

print(len(clarissa_text), len(septimus_text))

while True:
    prompt = input("\nType a word (or quit): ").strip()
    if prompt.lower() in {"quit", "exit", "q"}:
        break

    print("\nCLARISSA:", clarissa_model.make_sentence(tries=50))
    print("SEPTIMUS:", septimus_model.make_sentence(tries=50))
