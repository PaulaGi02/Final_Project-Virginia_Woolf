from pathlib import Path
from scr.processes import clean_text
import markovify
import spacy
from scr.voice import analyze_voice, DEFAULT_BAN_LEMMAS
from scr.processes import expand_with_vectors
from scr.voice import generate_biased
from scr.voice import build_candidates

nlp = spacy.load("en_core_web_md")

def load_text(path: str) -> str:
    return Path(path).read_text()


clarissa_txt = open ("data/clarissa.txt").read()
septimus_txt = open("data/septimus.txt").read()

clarissa_text = clean_text(clarissa_txt)
septimus_text = clean_text(septimus_txt)

clarissa_model = markovify.Text(clarissa_text, state_size=2)
septimus_model = markovify.Text(septimus_text, state_size=2)

clarissa_stats = analyze_voice(clarissa_text, nlp, ban_lemmas=DEFAULT_BAN_LEMMAS)
septimus_stats  = analyze_voice(septimus_text, nlp, ban_lemmas=DEFAULT_BAN_LEMMAS)

clarissa_candidates = build_candidates(clarissa_text, nlp, ban_lemmas=DEFAULT_BAN_LEMMAS)
septimus_candidates = build_candidates(septimus_text, nlp, ban_lemmas=DEFAULT_BAN_LEMMAS)

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

    kw_c = expand_with_vectors(prompt, nlp, clarissa_candidates)
    kw_s = expand_with_vectors(prompt, nlp, septimus_candidates)

    print("\nClarissa keywords:", kw_c[:10])
    print("Septimus keywords:", kw_s[:10])

    print("\nCLARISSA:", generate_biased(clarissa_model, kw_c))
    print("SEPTIMUS:", generate_biased(septimus_model, kw_s))
