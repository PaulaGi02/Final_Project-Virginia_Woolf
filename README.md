# The Room Between Us

A small interactive “voice simulation” tool for *Mrs. Dalloway* that compares Clarissa and Septimus through computational text generation.  
It trains separate Markov models on manually extracted passages (each character’s thoughts + spoken words), then steers generation using spaCy word vectors to build a “semantic field” from a user prompt. A retro Pygame terminal UI lets you enter a word and see both voices respond side-by-side.


## Repository structure
├── pygame_interface.py # Main app (Pygame UI + model loading + generation)
├── scr/
│ ├── processes.py # Text cleaning + cosine similarity + vector-based expansion
│ ├── voice.py # Voice stats + candidate pool + biased generation helpers
│ └── pro.py # PROCESS_SECTIONS content shown in the process page
└── data/
├── clarissa.txt # Extracted corpus: Clarissa (thoughts + speech)
└── septimus.txt # Extracted corpus: Septimus (thoughts + speech)



## Libraries / dependencies
- pygame
- spacy
- markovify
- numpy
- spaCy model: en_core_web_md 


## How to run

### 1) Create and activate a virtual environment (recommended)
**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)
```python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```pip install pygame spacy markovify numpy
python -m spacy download en_core_web_md
```
### 3) Start the interface
Run python pygame_interface.py (needs a moment to load)

Type a word → Enter to generate
ESC → exit (or go back from process page)
Click PROCESS / METHOD → open the process page
