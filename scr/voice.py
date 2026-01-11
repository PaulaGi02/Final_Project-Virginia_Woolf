from dataclasses import dataclass
from collections import Counter
import numpy as np


DEFAULT_BAN_LEMMAS = {
    "clarissa", "dalloway", "mrs", "septimus", "warren", "smith", "peter", "holmes",
    "say", "think", "tell", "ask", "thing",
}

@dataclass
class VoiceStats:
    mean_sent_len: float
    top_pos: dict
    top_lemmas: list

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

    # POS proportions (simple “fingerprint”)
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
