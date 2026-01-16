from dataclasses import dataclass
from collections import Counter
import numpy as np
import re

DEFAULT_BAN_LEMMAS = {
    "clarissa", "dalloway", "mrs", "septimus", "warren", "smith", "peter", "holmes",
    "say", "think", "tell", "ask", "thing", "like"
}


@dataclass
class VoiceStats:
    mean_sent_len: float
    top_pos: dict
    top_lemmas: list

def generate_with_length(model, min_chars=80, max_chars=450, tries=200):
    for _ in range(tries):
        sentence = model.make_sentence(tries=20)
        if not sentence:
            continue
        if min_chars <= len(sentence) <= max_chars:
            return sentence
    return None


def analyze_voice(text: str, nlp, top_n_lemmas: int = 10, ban_lemmas=None):
    if ban_lemmas is None:
        ban_lemmas = set()

    doc = nlp(text)

    # sentence length
    sent_lens = []
    for s in doc.sents:
        toks = [t for t in s if not t.is_space]
        if toks:
            sent_lens.append(len(toks))
    mean_sent_len = float(np.mean(sent_lens)) if sent_lens else 0.0

    # POS proportions
    pos_counts = Counter(t.pos_ for t in doc if t.is_alpha)
    total = sum(pos_counts.values()) or 1
    keep = ["NOUN", "VERB", "ADJ", "ADV", "PRON"]
    top_pos = {k: pos_counts[k] / total for k in keep}

    # frequent lemmas (for character signature + later keyword candidates)
    lemmas = []
    for t in doc:
        if not (t.is_alpha and not t.is_stop and len(t) > 2):
            continue
        lem = t.lemma_.lower()
        if lem in ban_lemmas:
            continue
        lemmas.append(lem)

    top_lemmas = Counter(lemmas).most_common(top_n_lemmas)

    return VoiceStats(
        mean_sent_len=mean_sent_len,
        top_pos=top_pos,
        top_lemmas=top_lemmas,
    )


def build_candidates(text: str, nlp, top_n: int = 400, ban_lemmas=None):
    if ban_lemmas is None:
        ban_lemmas = set()

    doc = nlp(text)
    lemmas = []
    for t in doc:
        if not (t.is_alpha and not t.is_stop and len(t) > 2):
            continue
        lem = t.lemma_.lower()
        if lem in ban_lemmas:
            continue
        lemmas.append(lem)

    return [w for w, _ in Counter(lemmas).most_common(top_n)]


def keyword_hits(sentence: str, keywords):
    """Count how many keywords appear in the sentence"""
    s = sentence.lower()
    return sum(1 for kw in keywords if re.search(rf"\b{kw}\b", s))


def generate_biased(model, keywords, n=120, min_chars=80, max_chars=450):
    """Generate a single sentence biased toward keywords and within a target length."""
    best = None
    best_score = -1

    for _ in range(n):
        sent = model.make_sentence(tries=20)
        if not sent:
            continue
        if not (min_chars <= len(sent) <= max_chars):
            continue

        score = keyword_hits(sent, keywords)
        if score > best_score:
            best_score = score
            best = sent

    return best or "(no output)"


def generate_biased_multi(model, keywords, num_sentences=3, n=120):
    sentences = []

    for _ in range(num_sentences):
        sent = generate_biased(model, keywords, n=n)
        if sent and sent != "(no output)":
            sentences.append(sent)

    return " ".join(sentences) if sentences else "(no output)"