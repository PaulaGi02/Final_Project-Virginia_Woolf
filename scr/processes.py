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

# Compute the cosine similarity between two numeric vectors a and b.
def cosine(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0

# Expand a single seed word into a short semantic field using spaCy vectors
def expand_with_vectors(word: str, nlp, candidates, k=8, min_sim=0.45):
    w = word.lower()
    # Look up the spaCy lexeme for the seed word (this gives vector, vector_norm, etc.)
    lex = nlp.vocab[w]

    base = lex.vector
    scored = []

    for cand in candidates:
        lex2 = nlp.vocab[cand]

        # Skip candidates with no vector information
        if not lex2.has_vector or lex2.vector_norm == 0:
            continue

        # Compute cosine similarity between seed vector and candidate vector
        sim = cosine(base, lex2.vector)

        # Keep candidate if it meets the minimum similarity threshold
        if sim >= min_sim:
            scored.append((cand, sim))

    # Sort candidates by similarity (highest first) and return top-k
    scored.sort(key=lambda x: x[1], reverse=True)
    return [w] + [c for c, _ in scored[:k]]