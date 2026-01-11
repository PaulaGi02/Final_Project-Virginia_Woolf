from pathlib import Path
from scr.processes import clean_text
import markovify
import spacy
from collections import Counter
import numpy as np

nlp = spacy.load("en_core_web_md")

def load_text(path: str) -> str:
    return Path(path).read_text()

with open ("data/clarissa.txt") as f:
    clarissa_txt = f.read()

with open ("data/septimus.txt") as f:
    septimus_txt = f.read()

clarissa_text = clean_text(clarissa_txt)
septimus_text = clean_text(septimus_txt)

clarissa_model = markovify.Text(clarissa_text, state_size=1)
septimus_model = markovify.Text(septimus_text, state_size=1)

print("Clarissa sample:", clarissa_model.make_sentence(tries=10))
print("Septimus sample:", septimus_model.make_sentence(tries=10))

print(len(clarissa_text), len(septimus_text))