# The Room Between Us - Project Documentation

## Research Question & Methodology
The project “The Room Between Us” asks whether computational text generation—using spaCy 
analysis, Markov chains, and vector calculations—can capture the reader’s perception of Clarissa 
and Septimus in Mrs. Dalloway. The models are trained only on each character’s own thoughts and 
spoken words. This methodological choice introduces a central difficulty: both characters primarily 
think about others rather than themselves, which means their textual voice is often indirect. 
At the same time, readers form their perception of Clarissa and Septimus not only through their 
own words and thoughts, but also through how other characters think and speak about them. 
Excluding those external perspectives avoids contaminating the stylistic analysis, but it also 
raises the question of whether the generated outputs can truly reflect the full spectrum of how 
readers experience these characters.

## Data Collection Phase

### Initial Planning
**Date:** 7.1.2026 <br>
**To-do:** Determine which text passages to extract for analysis <br>
**Solution:** Initially focused on spoken words only, as these were most important for analyzing speaking patterns. 
However, I realized Septimus's and Clarissa's spoken words were very scant, so broadened extracts to include both thoughts and spoken words 
of both characters.  <br>
**Challenge encountered:** Characters' thoughts were mostly about other characters. For instance, Clarissa often thinks 
and talks about Peter, but the intention was not to display how Peter is as a character.

### Manual Text Extraction
**Date:** 7.1.2026<br>
**To-do:** Extract relevant passages from Mrs. Dalloway for both characters  <br>
**Solution:** Manually went through the entire book to extract passages, as I could not simply use Command+F to search for 
character names because Virginia Woolf writes long, intertwined passages. For instance, mostly the character's names get 
mentioned at the beginning, then another character's perspective jumps in, while the original character (e.g., Clarissa) 
continues speaking but is now referred to as "she".  <br>
**Challenge encountered:** This was way more time-consuming than expected.

### File Organization
**Date:** 7.1 + 8.1<br>
**To-do:** Store extracted passages in a text file, suitable for analysis. <br>
**Solution:** Saved extracts into separate text files: `clarissa.txt` and `septimus.txt` to enable independent 
analysis of each character's narrative voice.<br>
**Status:** Data collection phase concluded.


## Development Phase - Initial Setup (Section 10.1)

### Virtual Environment Setup
**Date:** 8.1.2026<br>
**To-do:** Create a clean development environment  <br>
**Solution:** Set up a virtual environment to ensure package installations wouldn't conflict with system-wide 
Python libraries or other projects.

### Text Preprocessing Implementation
**Date:** 8.1.2026<br>
**To-do:** Handle formatting inconsistencies in extracted text passages <br>
**Solution:** Created `clean_text` function in `processes.py` to perform several text normalization steps:
- Normalize newlines by converting Windows-style `\r\n` to Unix-style `\n`
- Normalize curly quotes (both opening and closing variants of double and single quotes) to straight ASCII equivalents to prevent encoding issues
- Collapse excessive whitespace by replacing sequences of spaces and tabs with single spaces using `re.sub(r"[ \t]+", " ", text)`
- Reduce runs of three or more newlines to just two newlines with `re.sub(r"\n{3,}", "\n\n", text)` to maintain paragraph breaks while removing excessive vertical spacing
- Remove leading and trailing whitespace with `text.strip()` <br>
**References:** Python's `re` module for regular expressions - https://docs.python.org/3/library/re.html

### Basic Testing Setup
**Date:** 8.1.2026<br>
**To-do:** Verify that text files can be loaded correctly  <br>
**Solution:** Created `main.py` file to load both character files and test with `len()` function to 
verify importation worked correctly.  <br>
**Result:** Successfully confirmed file loading pipeline works. Yayyy :) 

### Initial Markov Chain Experiments
**Date:** 9.1.2026<br>
**To-do:** Test basic text generation to see if character voices are distinguishable  <br>
**Solution:** Ran initial Markov chain experiments with `tries=10` and `state_size=1`.  
**Results:** <br>
- Clarissa sample: "That he is probably the roses absolutely lovely; first getting sent down from the Queen, thought Clarissa, too, gave her hands already, quite enough of her time she looked out again."
- Septimus sample: "It spared him, the drowned sailor; the immortal ode; the heat wave of the sky, muttering, clasping his rock, like a Skye terrier snuffed his brain made her hold his eyes as he could not cut down trees"  
**Observation:** Despite the gibberish-like quality typical of low state-size Markov chains, the generated text clearly 
exhibited distinguishable characteristics revealing which character was which, validating that the underlying text corpora captured distinct voices.<p>
**References:** Course material week 3


## Vector Similarity Implementation

### Cosine Similarity Function
**Date:** 9.1.2026<br>
**To-do:** Create a method to compare semantic similarity between word vectors in `processes.py`<br>
**Solution:** Implemented `cosine` function to calculate cosine similarity between two vectors. The function:<br>
- Computes the dot product of vectors `a` and `b`
- Divides by the product of their norms using `np.linalg.norm()`
- Returns a float between -1 and 1 where values closer to 1 indicate higher semantic similarity
- Includes a denominator check to prevent division by zero if either vector has zero magnitude  <br>
**References:** Course material week 5, https://numpy.org/doc/stable/reference/generated/numpy.dot.html, https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html

### Semantic Expansion Mechanism
**Date:** 10.1.2026<br>
**To-do:** Transform a single user input word into a field of related keywords  <br>
**Solution:** Implemented `expand_with_vectors` function that:
- Takes the input word and converts it to lowercase
- Retrieves its word vector from spaCy's vocabulary using `nlp.vocab[w]`
- Iterates through a pre-built list of candidate lemmas
- Retrieves each candidate's vector and checks if it has a valid vector representation
- For each valid candidate, calculates cosine similarity between the base word's vector and the candidate's vector
- Collects candidates exceeding the `min_sim` threshold (0.45 by default) with their similarity scores
- Sorts results in descending order by similarity
- Returns the original input word followed by the top `k` (default 8) most similar candidates  <br>
**Parameters chosen:** `k=8` and `min_sim=0.45` were chosen to balance between having enough semantic variety while 
maintaining meaningful relevance to the input word.  <br>
**Purpose:** Creates a semantic field that guides the Markov chain generation toward thematically relevant content.<br>
**References**: Course material week 5, https://spacy.io/api/vocab, https://docs.python.org/3/howto/sorting.html<br>

## Voice Analysis Module (voice.py)

### SpaCy Integration Setup
**Date:** 11.1.2026<br>
**To-do:** Enable deeper linguistic analysis of each character's voice beyond simple Markov chain generation <br>
**Solution:** Created `voice.py` module to encapsulate voice analysis and biased generation functionality.<br>
**References:** Course material week 4

### Banned Lemmas Definition
**Date:** 11.1.2026 <br>
**To-do:** Filter out words that reflect narration mechanics rather than meaningful lexical preferences  <br>
**Solution:** Defined `DEFAULT_BAN_LEMMAS` as a set containing:
- Character names: "clarissa", "dalloway", "mrs", "septimus", "warren", "smith", "peter", "holmes"
- High-frequency speech and thought reporting verbs: "say", "think", "tell", "ask"
- Vague words: "thing", "like"<br>
**Rationale:** Examining initial SpaCy analysis results revealed these words dominated frequency rankings but reflected 
narration mechanics rather than meaningful lexical preferences.  <br>
**Uncertainty:** I had some concern about whether manually excluding these terms constituted inappropriate subjective 
influence on the outcome, but I decided to proceed with filtering to produce more interpretable and contentful 
results that better represent each character's thematic vocabulary.<br>
**References:** Course material week 4

### VoiceStats Data Structure
**Date:** 11.1.2026<br>
**To-do:** Create a clean container for voice analysis results <br>
**Solution:** Defined `VoiceStats` dataclass using Python's `@dataclass` decorator with three attributes:
- `mean_sent_len` (float): average sentence length
- `top_pos` (dict): mapping POS tags to their proportions
- `top_lemmas` (list): most frequent lemmas with counts <br>
**Purpose:** Provides structured storage for statistical analysis results.<br>
**Reference:** Course material week 4/ Course material from Tech Basics 1<br>

### Sentence Length Analysis
**Date:** 11.1.2026<br>
**To-do:** Calculate average sentence length to compare speaking styles  <br>
**Solution:** Implemented sentence length calculation in `analyze_voice` function:
- Processes entire text through spaCy to create a `doc` object
- Iterates through `doc.sents`
- Filters out whitespace-only tokens
- Builds list of sentence lengths measured in tokens
- Computes mean sentence length using `np.mean()` and stores as float  <br>
**Purpose:** Show if there is a difference between Septimus's and Clarissa's speaking style.<br>
**References:** Course material week 4

### POS (Part-of-Speech) Proportion Analysis
**Date:** 12.1.2026<br>
**To-do:** Analyze syntactic preferences of each character  <br>
**Solution:** Implemented POS proportion calculation:
- Counts all alphabetic tokens' POS tags using a `Counter`
- Filters to keep only five categories of interest: NOUN, VERB, ADJ (adjective), ADV (adverb), and PRON (pronoun)
- Calculates each category's proportion by dividing its count by total number of tokens
- Creates `top_pos` as a dictionary of normalized proportions <br>
**Purpose:** Reveal syntactic preferences between characters.<br>
**References:** Course material week 4

### Lemma Frequency Analysis
**Date:** 12.1.2026<br>
**To-do:** Build vocabulary analysis for each character <br>
**Solution:** Implemented lemma frequency list building in `analyze_voice`:
- Iterates through all tokens
- Filters to keep only alphabetic tokens that aren't stop words and have length greater than 2 characters
- Converts each token's lemma to lowercase
- Checks against `ban_lemmas` and appends if not banned
- Uses `Counter` to tally lemma frequencies
- Extracts top entries with `.most_common(top_n_lemmas)`
- Stores results in `VoiceStats` object  <br>
**Default parameter:** `top_n_lemmas=10`<br>
**References:** Course material week 4

### Candidate Lemma Pool Creation
**Date:** 12.1.2026<br>
**To-do:** Create a frequency-ranked list of lemmas for semantic expansion <br>
**Solution:** Implemented `build_candidates` function that:
- Processes text through spaCy
- Extracts alphabetic non-stopword lemmas longer than 2 characters
- Excludes banned lemmas
- Returns the top `top_n=400` most frequent ones  <br>
**Purpose:** Provides sufficient diversity for vector similarity matching while ensuring candidates represent meaningful vocabulary rather than rare words. This precomputed shortlist speeds similarity searches in downstream `expand_with_vectors` function.  <br>
**Parameter choice:** 400 candidates vs 10 top lemmas provides larger pool for vector matching.<br>
**References:** Course material week 4

### Keyword Scoring Mechanism
**Date:** 12.2026<br>
**To-do:** Evaluate how well a sentence aligns with a target semantic field<br>
**Solution:** Implemented `keyword_hits` function that:
- Takes a sentence string and list of keywords
- Converts sentence to lowercase
- Counts how many keywords appear using word-boundary matching with regular expressions `re.search(rf"\b{kw}\b", s)`
- Uses `\b` boundary anchors to ensure whole-word matches only  <br>
**Purpose:** Reduces false positives that would occur from substring matching (e.g., preventing "run" from matching inside "running" or "trunk").<br>
**References:** https://docs.python.org/3/library/re.html

### Biased Generation Algorithm - Single Sentence
**Date:** 12.2026 <br>
**To-do:** Generate Markov chain sentences guided by keyword relevance and length constraints  <br>
**Solution:** Implemented `generate_biased` function that:
- Accepts a Markov model, list of keywords, number of attempts `n=120`, and length boundaries `min_chars=80` and `max_chars=450`
- Initializes `best` and `best_score` to track highest-scoring sentence
- Runs up to `n` iterations, each calling `model.make_sentence(tries=20)`
- Validates length: rejects sentences outside specified character range
- For valid sentences, calculates relevance score using `keyword_hits`
- Updates `best_score` and `best` when superior candidate found
- Returns best sentence found, or `"(no output)"` if no suitable sentence generated  <br>
**Purpose:** Core biased generation algorithm for single sentences.<br>
**References:** Course material week 3

### Biased Generation Algorithm - Multiple Sentences
**Date:** 12.1.2026 <br>
**To-do:** Extend single-sentence generation to produce multi-sentence outputs  <br>
**Solution:** Implemented `generate_biased_multi` function that:
- Calls `generate_biased` multiple times (controlled by `num_sentences=3`)
- Collects results
- Checks each generated sentence is valid (not None and not `"(no output)"`)
- Joins sentences with spaces using `" ".join(sentences)`
- Returns combined result or `"(no output)"` if no valid sentences generated  <br>
**Purpose:** Produces coherent multi-sentence outputs.

### Module Organization Bug Fix
**Date:** 12.1.2026<p>
**To-do:** Resolve variable name and function call conflicts between modules  <br>
**Problem:** Initial integration of vector-based semantic expansion with spaCy failed due to mixed up variable names and function calls between `voice.py` and `processes.py`. <br>
**Solution:** Clarified module separation:
- `processes.py` handles: text cleaning and vector operations (`clean_text`, `cosine`, `expand_with_vectors`)
- `voice.py` focuses on: voice analysis and biased generation (`analyze_voice`, `build_candidates`, `keyword_hits`, `generate_biased`, `generate_biased_multi`)
- Ensured proper imports between modules  <br>
**Rationale:** `expand_with_vectors` needed access to the spaCy model's vocabulary and therefore belonged in `processes.py` alongside other 
preprocessing utilities, while generation functions naturally grouped with voice analysis in `voice.py`.


## Python Interface Development (Section 13.1)

### Initial Pygame Setup
**Date:** 13.1.2026<br>
**To-do:** Create a simple Python interface for user interaction  <br>
**Design philosophy:** Inspired by early computer terminal interfaces, fitting the historical context of Virginia Woolf's "Mrs Dalloway" published in 1925.  <br>
**Solution:** Chose Pygame as the framework due to prior familiarity with the library. Defined:
- Window dimensions: 1200x800 pixels
- Frame rate: 60 FPS
- Retro terminal color palette: black backgrounds and green accent colors to evoke vintage computing aesthetic  <br>
**References:** https://python-utilities.readthedocs.io/en/latest/sysfont.html

### Font Initialization
**Date:** 13.1.2026<br>
**To-do:** Set up typography for the interface  <br>
**Solution:** Used `pygame.font.SysFont()` to load the Courier monospace font family, creating distinct sizes for:
- Titles
- Names
- Body text
- Input
- Small labels  <br>
**Fallback:** Default fonts if Courier unavailable on system.

### Text Wrapping Implementation
**Date:** 13.1.2026<br>
**To-do:** Handle multi-line text rendering since Pygame doesn't provide automatic word wrapping  <br>
**Solution:** Implemented `TextBlock` helper class that:
- Takes text, font, maximum width, and color parameters during initialization
- Splits input into words
- Iteratively builds lines by testing whether adding each subsequent word would exceed allocated width using `font.size()`
- When a word would cause overflow, saves current line to `self.lines` and starts new line with that word
- Provides `render` method that:
  - Iterates through `self.lines`
  - Blits each line sequentially while tracking vertical position
  - Supports viewport clipping via optional `max_y` parameter that stops rendering when vertical boundary reached  <br>
**Purpose:** Ensures text splits on word boundaries into lines that won't overflow the allocated width when drawn.<br>
**References:** https://www.pygame.org/docs/ref/font.html, https://stackoverflow.com/questions/49432109/how-to-wrap-text-in-pygame-using-pygame-font-font

### User Input Handling
**Date:** 13.1.2026<br>
**To-do:** Enable users to type words for text generation  <br>
**Solution:** Initialized `self.input_text = ""` to store the word typed by the user.

### Model Loading Implementation
**Date:** 14.1.2026<br>
**To-do:** Initialize NLP and text generation components  <br>
**Solution:** Created `load_models` method that:
- Prints startup message
- Loads spaCy's medium English model (`en_core_web_md`) into `self.nlp`
- Transfers all functionality from original `main.py` file:
  - Reading Clarissa and Septimus text files
  - Cleaning them with `clean_text`
  - Building Markov models with `markovify.Text`
  - Analyzing voice statistics with `analyze_voice`
  - Building candidate word lists with `build_candidates` <br>
**Note:** Loading spaCy represents one of the heavier startup costs, which is why there can be a noticeable delay between launching the script and the interface appearing on screen.  <br>
**Result:** `main.py` file no longer needed; codebase consolidated.<br>
**References:** Course material week 3/4

### Interface Layout Design
**Date:** 14.1.2026<br>
**To-do:** Define visual positioning of character panels  <br>
**Solution:** Placed Clarissa's panel on left side and Septimus's panel on right side of main interface, creating a visual divide between the two characters' outputs.

### Keyboard Event Handling
**Date:** 15.1.2026<br>
**To-do:** Make interface more intuitive for users  <br>
**Solution:** Implemented responses to `pygame.KEYDOWN` events:
- `K_ESCAPE`: exiting or returning to main page
- `K_RETURN`: triggering text generation from input word
- `K_BACKSPACE`: deleting characters
- Alphanumeric keys: typing  <br>
**Purpose:** Provide standard keyboard navigation.<br>
**References:** https://www.pygame.org/docs/ref/key.html

### Cursor Blinking Animation
**Date:** 15.1.2026<br>
**To-do:** Create visual feedback for input field  <br>
**Solution:** Implemented `update` method to manage cursor blinking:
- Uses `self.clock.get_time()` to advance `cursor_timer` by elapsed milliseconds since last frame
- When timer exceeds `cursor_blink_speed` (500ms), toggles `cursor_visible` and resets timer
- Creates synchronized blinking caret effect that operates independently of frame rate  
**Purpose:** Standard text input cursor behavior.<br>
**References:** https://www.pygame.org/docs/ref/time.html#pygame.time.Clock.get_time

### Main Loop Structure
**Date:** 15.1.2026<br>
**To-do:** Set up application entry point  <br>
**Solution:** Script concludes with standard Python main guard `if __name__ == "__main__":` which:
- Ensures when file is executed directly (not imported as module), it prints startup message
- Creates `WoolfInterface` instance
- Calls `run()` to start application loop


## UI Enhancements

### Cursor Appearance
**Date:** 17.1.2026<br>
**To-do:** Improve default cursor appearance <br>
**Solution:** Changed default cursor to arrow (`pygame.SYSTEM_CURSOR_ARROW`).

### Process Page Addition
**Date:** 17.1.2026  <br>
**To-do:** Display methodology and intermediate outputs  <br>
**Solution:** Introduced process page to display methodology and intermediate outputs from Markov chain generation stages.  <br>
**Motivation:** Capturing and visualizing intermediate stages seemed valuable for understanding how the system works. 
Observing these development stages during testing revealed interesting patterns worth preserving.  <br>
**Testing approach:** During development, consistently used the same three words (time, flower, world) to generate Markov chain outputs, ensuring comparability across iterations.

### Page Navigation System
**Date:** 17.1.2026 <br>
**To-do:** Enable switching between main interface and process documentation <br>
**Solution:** Defined constants and functions:
- `PAGE_MAIN` and `PAGE_PROCESS` constants
- `draw_button`: renders button outlines and centered labels
- `draw_process_page`: ensures process documentation renders properly with scrolling support
- `draw_control_bar`: draws solid rectangle over bottom region serving dual roles:
  - Visual container for buttons
  - Mask preventing underlying text content from showing through in that area

### Interactive Cursor Feedback
**Date:** 23.1.2026<br>
**To-do:** Provide visual feedback for clickable elements  <br>
**Solution:** Enhanced cursor behavior to change to hand cursor (`pygame.SYSTEM_CURSOR_HAND`) when hovering over buttons.

### Button Click Functionality
**Date:** 23.1.2026<br>
**To-do:** Implement clickable navigation  <br>
**Solution:** Implemented in event loop using `event.type == pygame.MOUSEBUTTONDOWN` checks, allowing users to open process page and return to main by clicking drawn button areas.

### Content Boundary Problem
**Date:** 23.1.2026 <br>
**To-do:** Prevent generated text from overlapping control bar buttons <br>
**Problem:** Generated text would extend beneath and overlap the control bar containing buttons. <br>
**Solution:** Created `CONTENT_BOTTOM_Y` constant defining a hard stop for content rendering, calculated as 
`CONTROL_BAR_Y - 20` to provide spacing between content and control bar.<br>
**Reference:** Here I tried to find a solution online however I didn't find anything. therefore, I pasted my code into Github Copilot and asked
to explain the problem and how to fix it.

## Critical Bug Fixes 

### Bug 1: Text Length Constraints Not Working
**Date:** 15.1 - 23.1.2026<br>
**To-do:** Enforce character length constraints of 80-450 characters  <br>
**Problem:** Markov chain text generation was not respecting specified length constraints. While `generate_biased` had length checking for individual sentences, the main method wasn't enforcing limits when combining multiple sentences together. Clarissa's output consistently exceeded 450 characters. <br>
**Initial attempt:** Added explicit `min_chars` and `max_chars` parameters to `generate_longer_text` and validated each generated sentence before accepting it. <br>
**Why initial fix failed:** The method was concatenating multiple sentences without tracking cumulative output length. Each sentence individually stayed within 80-450 character range, but combining three sentences together regularly exceeded 450 character maximum.<br>
**Final solution:** Implemented comprehensive cumulative length tracking:
- Introduced `total_length` tracking variable monitoring cumulative character count across all sentences, including space characters used to join them
- Before adding each new sentence, calculates `potential_total` by adding candidate sentence's length to existing total, plus one character for joining space if sentences already exist
- If `potential_total` would exceed `max_chars`, sentence is rejected during generation or loop breaks if suitable sentence cannot be found
- Added safety mechanism at end: if final joined result still exceeds `max_chars`, text is truncated at last complete word within limit using `rsplit(' ', 1)[0]` and appended with "..."
- Validates complete output meets minimum length requirement of 80 characters before returning, otherwise returns "(no output)"  <br>
**Result:** Both characters' generated text strictly adheres to specified 80-450 character constraint for total output, not just individual sentences.

### Bug 2: Hand Cursor Hover Effect Not Working
**Date:** 15.1.2026<br>
**To-do:** Make cursor change when hovering over buttons  <br>
**Problem:** Hand cursor hover effect wasn't working because `update_cursor()` was only being called inside the event loop rather than every frame.  <br>
**Solution:** Moved `update_cursor()` call to main `run()` loop, ensuring cursor updates continuously based on mouse position. Method checks whether mouse is over a button and sets appropriate cursor type.  <br>
**Result:** Responsive cursor changes providing visual feedback.

### Bug 3: Button Click Detection Unreliable
**Date:** 17.1.2026<br>
**To-do:** Fix inconsistent button click behavior  <br>
**Problem:** `collidepoint()` was being passed a nested tuple `((x, y))` instead of a simple tuple `(x, y)`. This caused collision detection to only work in certain areas of the button.  <br>
**Solution:**
- Store `pos = event.pos`
- Pass it directly to `collidepoint(pos)` since `event.pos` already returns correct tuple format
- Add `continue` statements after successful button clicks to prevent further event processing in that frame  <br>
**Result:** Reliable button interactions throughout the interface.

### Load Models Bug Fix
**Date:** 13.1.2026<br>
**To-do:** Fix interface failure when users entered a word  <br>
**Problem:** `self.load_models()` had been placed at wrong position in initialization sequence. <br>
**Solution:** Ensured `load_models()` called at end of `__init__` after all other state variables were initialized.<br>
**Result:** Interface functions correctly when users input words.

## Code Organization/ UI Improvements

### Process Content Extraction
**To-do:** Make interface code more structured and maintainable <br>
**Solution:** Extracted process page content into separate file (`pro.py`), with `PROCESS_SECTIONS` imported from this module.  <br>
**Result:** Cleaner, more modular codebase.

### Scrollbar Implementation
**To-do:** Handle content longer than viewport on process page  <br>
**Solution:** Added scrollbar to process page.  <br>
**Initial problem:** Text collided with scrollbar rendering.  <br>
**Fix:** Adjusted viewport width calculation and added proper clipping.<br>
**Reference:** https://pygame-menu.readthedocs.io/en/3.0.3/_source/widgets_scrollbar.html

### Visual Separation Enhancement
**To-do:** Create clear visual boundary between interactive and content areas  
**Solution:** Added rim between button area and text content to create visual separation.

### AI Usage
AI was used for:
- recommendations on how to structure the code more cleanly
- bug fixes when I could not find anything on the internet/ forums, e.g. asked for help with my boundary problem.
- to check the documentation for grammar and clearness

### Next possible steps
The next step would be to build a Chatbot that tries to make sense out of the created gibberish and formulates logical sentences.
Furthermore, the Chatbot tries to interpret "the room between" the two voices: What makes them different or maybe even similar.
