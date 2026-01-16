import re
import numpy as np

import re
import numpy as np

def clean_text(text: str) -> str:
    # normalize newlines
    text = text.replace("\r\n", "\n")
    # normalize curly quotes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")

    # collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def cosine(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0


def expand_with_vectors(word: str, nlp, candidates, k=8, min_sim=0.45):
    w = word.lower()
    lex = nlp.vocab[w]

    base = lex.vector
    scored = []

    for cand in candidates:
        lex2 = nlp.vocab[cand]
        if not lex2.has_vector or lex2.vector_norm == 0:
            continue

        sim = cosine(base, lex2.vector)
        if sim >= min_sim:
            scored.append((cand, sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [w] + [c for c, _ in scored[:k]]


