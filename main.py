from pathlib import Path

with open ("data/clarissa.txt") as f:
    clarissa_txt = f.read()

with open ("data/septimus.txt") as f:
    septimus_txt = f.read()

print (len(septimus_txt), len(clarissa_txt))