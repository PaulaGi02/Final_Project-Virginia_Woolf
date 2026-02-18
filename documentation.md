

## data collction 7.1
Before starting to programm I needed to filter both Characters thoughts and spoken words. 
Firstly I wanted to focus on just the spoken words as those were the most important passages for 
analysing speaking patterns. However, I realised that especially Septimus spoken words were very scant. 
I decided to broaden my extracts to also the thoughts of both characters. Here, I noticed that 
the thoughts were mostly about other characters. For instance, Clarissa often thinks and talks about Peter.
However, how Peter is as a character was not my intention to display.
This was one of the most time-consuming parts, as I could not solely filter the parts by command + f and then
searching the name, as Virginia Woolf writes long passages where the name gets sometimes mentioned at the beginning
an other character jumps in and then e.g. Clarissa talks again but the word "she" now arcus.
Therefore, I had to skip through the whole book which was quite time consuming.
### 8.1
**processes.py Documentation**
The data collection phase concluded with the completion of extracting passages and savin them into separate text files 
(`clarissa.txt` and `septimus.txt`) to enable independent analysis of each character's narrative voice.

### 10.1
The development began with setting up a virtual environment to ensure a clean workspace where package installations wouldn't conflict with system-wide 
Python libraries or other projects. The first major task was implementing text preprocessing to prepare the raw extracted passages for analysis. The `clean_text` 
function was created in `processes.py` to handle various formatting inconsistencies present in the source text. This function imports Python's `re` module 
(the regular-expression library) to perform pattern-based text substitutions. The cleaning process proceeds in several steps: first normalizing newlines by 
converting Windows-style `\r\n` line endings to Unix-style `\n`, then normalizing curly quotes (both opening and closing variants of double and single quotes) 
to their straight ASCII equivalents to prevent encoding issues and ensure consistent string matching. Following quote normalization, the function collapses 
excessive whitespace by replacing sequences of spaces and tabs with single spaces using `re.sub(r"[ \t]+", " ", text)`, and reduces runs of three or more newlines 
to just two newlines with `re.sub(r"\n{3,}", "\n\n", text)` to maintain paragraph breaks while removing excessive vertical spacing. Finally, `text.strip()` removes 
any leading or trailing whitespace from the entire string before returning the cleaned result.

A simple `main.py` file was created to test the text loading pipeline, reading both character files and using `len()` to verify that importation worked correctly. 
Initial Markov chain experiments were conducted with `tries=10` and `state_size=1`, generating sample outputs like "That he is probably the roses absolutely lovely; 
first getting sent down from the Queen, thought Clarissa..." for Clarissa and "It spared him, the drowned sailor; the immortal ode; the heat wave of the sky, 
muttering..." for Septimus. Despite the gibberish-like quality typical of low state-size Markov chains, the generated text clearly exhibited distinguishable 
characteristics revealing which character was which, validating that the underlying text corpora captured distinct voices.

The `cosine` function was implemented to calculate cosine similarity between two vectors, a fundamental operation for comparing word embeddings. 
This function computes the dot product of vectors `a` and `b`, then divides by the product of their norms (`np.linalg.norm`), returning a float between -1 and 1 
where values closer to 1 indicate higher semantic similarity. A denominator check prevents division by zero if either vector has zero magnitude.

The `expand_with_vectors` function represents the semantic expansion mechanism that transforms a user's single input word into a field of related keywords. 
This function takes the input word, converts it to lowercase, and retrieves its word vector from spaCy's vocabulary using `nlp.vocab[w]`. It then iterates through 
a pre-built list of candidate lemmas, retrieving each candidate's vector and checking if it has a valid vector representation (some words may lack embeddings). 
For each valid candidate, it calculates cosine similarity between the base word's vector and the candidate's vector using the `cosine` function. Candidates exceeding 
the `min_sim` threshold (0.45 by default) are collected with their similarity scores into a list, which is then sorted in descending order by similarity. 
The function returns the original input word followed by the top `k` (default 8) most similar candidates, creating a semantic field that guides the Markov chain 
generation toward thematically relevant content. The parameters `k=8` and `min_sim=0.45` were chosen to balance between having enough semantic variety while 
maintaining meaningful relevance to the input word.

**voice.py Documentation**

SpaCy was integrated to enable deeper linguistic analysis of each character's voice beyond simple Markov chain generation. The `voice.py` 
module was created to encapsulate voice analysis and biased generation functionality. At the top of the file, `DEFAULT_BAN_LEMMAS` was defined as a set 
containing character names ("clarissa", "dalloway", "mrs", "septimus", "warren", "smith", "peter", "holmes") and high-frequency speech and thought reporting 
verbs ("say", "think", "tell", "ask") along with vague words like "thing" and "like". This exclusion list emerged from examining the initial SpaCy analysis 
results, which revealed that these words dominated the frequency rankings but reflected narration mechanics and extraction artifacts rather than meaningful 
lexical preferences. There was some uncertainty about whether manually excluding these terms constituted inappropriate subjective influence on the outcome, 
but the decision was made to proceed with filtering to produce more interpretable and contentful results that better represent each character's thematic vocabulary.

The `VoiceStats` dataclass was defined using Python's `@dataclass` decorator to create a clean container for voice analysis results, holding three attributes: 
`mean_sent_len` (float for average sentence length), `top_pos` (dict mapping POS tags to their proportions), and `top_lemmas` (list of most frequent 
lemmas with counts).

The `analyze_voice` function performs comprehensive statistical analysis of a character's text. It accepts the text string, the spaCy NLP model, a 
parameter for how many top lemmas to return (`top_n_lemmas=10`), and an optional `ban_lemmas` set that defaults to an empty set if not provided. 
The function first processes the entire text through spaCy to create a `doc` object, then calculates sentence length statistics by iterating through 
`doc.sents`, filtering out whitespace-only tokens, and building a list of sentence lengths measured in tokens. The mean sentence length is computed using 
`np.mean()` and stored as a float, to show if there is a difference between Septimus's and Clarissa's speaking style. Next, POS (part-of-speech) proportions 
are calculated by counting all alphabetic tokens' POS tags using a `Counter`, 
then filtering to keep only five categories of interest: NOUN, VERB, ADJ (adjective), ADV (adverb), and PRON (pronoun). Each category's proportion is 
calculated by dividing its count by the total number of tokens, creating `top_pos` as a dictionary of normalized proportions that reveal syntactic preferences. 
The function then builds a lemma frequency list for vocabulary analysis, iterating through all tokens and filtering to keep only alphabetic tokens that aren't 
stop words and have length greater than 2 characters. Each token's lemma is converted to lowercase, checked against `ban_lemmas`, and appended to the list if 
not banned. Finally, `Counter` tallies lemma frequencies and `.most_common(top_n_lemmas)` extracts the top entries, which are stored in the `VoiceStats` 
object along with the other calculated statistics.

The `build_candidates` function creates a frequency-ranked list of lemmas that serves as the candidate pool for semantic expansion. This precomputed shortlist 
exists because the downstream `expand_with_vectors` function needs to search through possible keywords, and operating over a finite, frequency-ranked list of 
contentful lemmas speeds similarity searches while ensuring candidates represent meaningful vocabulary rather than rare words. The function takes the same 
filtering approach as `analyze_voice`, processing the text through spaCy, extracting alphabetic non-stopword lemmas longer than 2 characters, excluding banned 
lemmas, and returning the top `top_n=400` most frequent ones. This larger candidate pool (400 vs 10) provides sufficient diversity for vector similarity matching.

The `keyword_hits` function implements a scoring mechanism to evaluate how well a sentence aligns with a target semantic field. Given a sentence string 
and a list of keywords, it converts the sentence to lowercase and counts how many keywords appear using word-boundary matching with regular expressions 
(`re.search(rf"\b{kw}\b", s)`). The `\b` boundary anchors ensure whole-word matches only, reducing false positives that would occur from substring matching 
(e.g., preventing "run" from matching inside "running" or "trunk").

The `generate_biased` function represents the core biased generation algorithm that produces Markov chain sentences guided by keyword relevance and length 
constraints. It accepts a Markov model, a list of keywords, the number of attempts `n=120`, and length boundaries `min_chars=80` and `max_chars=450`. 
The function initializes `best` and `best_score` to track the highest-scoring sentence found, then runs up to `n` iterations. In each iteration, it calls 
`model.make_sentence(tries=20)` to generate a candidate sentence, immediately continuing to the next iteration if generation fails. Length validation occurs next: 
if the sentence falls outside the specified character range, it's rejected and the loop continues. For sentences that pass length validation, `keyword_hits` 
calculates a relevance score based on how many keywords appear in the sentence. If this score exceeds the current `best_score`, both `best_score` and `best` are 
updated to remember this superior candidate. After all iterations complete, the function returns the best sentence found, or `"(no output)"` if no suitable sentence 
was generated.

The `generate_biased_multi` function extends single-sentence generation to produce multi-sentence outputs by calling `generate_biased` multiple times 
(controlled by `num_sentences=3`) and collecting the results. Each generated sentence is checked to ensure it's valid (not None and not the failure string 
`"(no output)"`), then appended to a list. The sentences are finally joined with spaces using `" ".join(sentences)`, returning the combined result or `"(no output)"`
if no valid sentences were generated.

A complication arose during the initial integration of vector-based semantic expansion with spaCy, where variable names and function calls became mixed up 
between `voice.py` and `processes.py`, causing the vector expansion functionality to fail. This was resolved by tracing which functions belonged in which 
module and ensuring proper imports: `processes.py` handles text cleaning and vector operations (`clean_text`, `cosine`, `expand_with_vectors`), while `voice.py` 
focuses on voice analysis and biased generation (`analyze_voice`, `build_candidates`, `keyword_hits`, `generate_biased`, `generate_biased_multi`). The separation 
clarified that `expand_with_vectors` needed access to the spaCy model's vocabulary and therefore belonged in `processes.py` alongside other preprocessing utilities, 
while the generation functions naturally grouped with voice analysis in `voice.py`.


- finishing collection passages about Septimus and clarissa, putting passanges in seperate files to be analysed later

### 10.1.
- virtual enviroment: set up a clean environment so installs don’t conflict.
- cleaning text from quotes and whitespaces, paragraphs etc. with the function clean_text in the file processes.py
- here used library re (https://docs.python.org/3/library/re.html) which brings in Python’s regular-expression module used for pattern-based text substitutions (whitespace collapsing, newline normalization).

- created main.py to load both text files and just test with a simple len() if importation worked then added
- Clarissa sample: That he is probably the roses absolutely lovely; first getting sent down from the Queen, thought Clarissa, too, gave her hands already, quite enough of her time she looked out again.
Septimus sample: It spared him, the drowned sailor; the immortal ode; the heat wave of the sky, muttering, clasping his rock, like a Skye terrier snuffed his brain made her hold his eyes as he could not cut down trees
- First try with markov chain and tries = 10 and state_size = 1
- even though it is gibberish clear which character is who


- adding Spacy for more analysing the voices of each Character
- adding in voice.py analyze_words
  - added sentence length calculation for statistics to compare voices
  - analyzing POS proportions keep defines a set of POS tags we care about (nouns, verbs, adjectives, adverbs, pronouns). top_pos calculates proportions for these POS categories by dividing their counts by total.
  - lemmas = []: Build a list of lemmas to represent frequent content words and summarize vocabulary characteristic of a voice
  
- looked at resluts of spacey analysis and realised that there were a lot of speech filling words like say or tell and Names like Clarissa or septimus. wanted to remove them because when character think about a user topic i do not want their name
- here i experimented a bid and tried to find the inbetween between deleting too much and leaving too many common words. 
- For interpretability, I exclude character names and high-frequency speech/thought reporting verbs (e.g., ‘say’, ‘think’) from the top lemma lists, because they reflect narration/extraction artifacts rather than lexical preferences, with DEFAULT_BAN_LEMMAS
- wondered if it is alright to do so as I subjectivly influence the outcome

### 12.1 
- next step expand the user’s word into similar words using vectors. 
- creating voice.py to analyse common patterns in the texts of each character 
  - build_candidates extracts the most frequent lemmas from a text, intended as candidate keywords for vector expansion or for seeding generation because downstream semantic expansion (expand_with_vectors) operates over a finite list of candidate lemmas; precomputing a frequency-ranked short-list speeds similarity searches and ensures candidates are contentful.
  - keywords_hits used to score candidate sentences for how well they align with a requested semantic field (keywords). Word-boundary matching reduces false positives.
  - generate_biased samples up to n (=120) sentences from a Markov model and pick the one that:
    - meets length constraints (min_chars <= len <= max_chars), and maximizes the number of keyword matches (keyword_hits).
    - 
- first complication, connecting vectors with Spacy. first kinda mixed up the variables between voice.py and processes.py therefore did not work.
## Python Interface
The development of the `WoolfInterface` began with the goal of creating a simple Python interface inspired by early computer terminals, 
fitting the historical context of Virginia Woolf's "Mrs Dalloway" published in 1925. Pygame was chosen as the framework due to prior familiarity 
with the library. Initial setup involved defining constants for window dimensions (1200x800 pixels) and frame rate (60 FPS), along with establishing 
a retro terminal color palette using black backgrounds and green accent colors to evoke the aesthetic of vintage computing interfaces. Font initialization 
utilized `pygame.font.SysFont()` to load the Courier monospace font family, creating distinct sizes for titles, names, body text, input, and small labels, 
with fallback to default fonts if Courier was unavailable on the system.

The `TextBlock` helper class was implemented early to handle multi-line text rendering, as Pygame does not provide automatic word wrapping functionality. 
This class takes text, font, maximum width, and color parameters during initialization, then splits the input into words and iteratively builds lines by 
testing whether adding each subsequent word would exceed the allocated width using `font.size()`. When a word would cause overflow, the current line is 
saved to `self.lines` and a new line begins with that word. The `render` method centralizes the rendering logic for wrapped text, iterating through `self.lines` 
and blitting each line sequentially while tracking vertical position, with support for viewport clipping via the optional `max_y` parameter that stops rendering 
when the vertical boundary is reached.

User input handling was established by initializing `self.input_text = ""` to store the word typed by the user. The `load_models` method was created to handle 
initialization of the NLP and text generation components, printing a startup message and loading spaCy's medium English model (`en_core_web_md`) into `self.nlp`. 
This model includes word vectors required by the `expand_with_vectors` function for semantic similarity calculations. Loading spaCy represents one of the heavier 
startup costs, which is why there can be a noticeable delay between launching the script and the interface appearing on screen. All functionality from the 
original `main.py` file was transferred into `load_models`, consolidating the codebase and eliminating the need for that separate file. This included reading 
the Clarissa and Septimus text files, cleaning them with `clean_text`, building Markov models with `markovify.Text`, analyzing voice statistics with 
`analyze_voice`, and building candidate word lists with `build_candidates`.

Layout positioning was defined to place Clarissa's panel on the left side and Septimus's panel on the right side of the main interface, creating a visual 
divide between the two characters' outputs. Event handling was implemented to make the interface more intuitive for users, defining responses to `pygame.KEYDOWN` 
events such as `K_ESCAPE` for exiting or returning to the main page, `K_RETURN` for triggering text generation from the input word, `K_BACKSPACE` for deleting 
characters, and alphanumeric keys for typing. The `update` method was implemented to manage cursor blinking in the input field, using `self.clock.get_time()` to 
advance `cursor_timer` by the elapsed milliseconds since the last frame. When this timer exceeds `cursor_blink_speed` (500ms), it toggles `cursor_visible` and 
resets the timer, creating a synchronized blinking caret effect that operates independently of the frame rate.
The script concludes with the standard Python main guard (`if __name__ == "__main__":`), which ensures that when the file is executed directly rather than 
imported as a module, it prints a startup message and creates a `WoolfInterface` instance before calling `run()` to start the application loop.

Over time, several UI enhancements were added to improve user experience. The default cursor was changed to an arrow (`pygame.SYSTEM_CURSOR_ARROW`), 
and a process page was introduced to display methodology and intermediate outputs from the Markov chain generation stages. The motivation behind the 
process page was to capture and visualize the development process, as observing these intermediate stages seemed valuable for understanding how the 
system works. During development, the same three words (time, flower, world) were consistently used to generate Markov chain outputs, ensuring 
comparability across iterations. To support page navigation, `PAGE_MAIN` and `PAGE_PROCESS` constants were defined, along with detailed button placement logic 
through several dedicated functions: `draw_button` renders button outlines and centered labels, `draw_process_page` ensures the process documentation renders 
properly with scrolling support, and `draw_control_bar` draws a solid rectangle over the bottom region that serves dual roles as both a visual container for 
buttons and a mask preventing underlying text content from showing through in that area. The cursor behavior was enhanced to change to a hand cursor 
(`pygame.SYSTEM_CURSOR_HAND`) when hovering over buttons, providing visual feedback for clickable elements.

Button click functionality was implemented in the event loop using `event.type == pygame.MOUSEBUTTONDOWN` checks, allowing users to open the process page and 
return to main by clicking the drawn button areas. However, a problem emerged where generated text would extend beneath and overlap the control bar containing 
the buttons, necessitating the creation of a boundary. The `CONTENT_BOTTOM_Y` constant was introduced to define a hard stop for content rendering, calculated 
as `CONTROL_BAR_Y - 20` to provide spacing between content and the control bar.

Three critical bugs surfaced during development that required correction. First, the Markov chain text generation was not respecting the specified character 
length constraints of 80-450 characters. The `generate_longer_text` method was calling `generate_biased` which had length checking for individual sentences, 
but the main method wasn't enforcing these limits when combining multiple sentences together. This was initially addressed by adding explicit `min_chars` and 
`max_chars` parameters to `generate_longer_text` and validating each generated sentence before accepting it. Second, the hand cursor hover effect wasn't working 
because `update_cursor()` was only being called inside the event loop rather than every frame. Moving this call to the main `run()` loop ensures the cursor updates 
continuously based on mouse position, checking whether the mouse is over a button and setting the appropriate cursor type. Third, button click detection was 
unreliable because `collidepoint()` was being passed a nested tuple `((x, y))` instead of a simple tuple `(x, y)`. This caused collision detection to only work in 
certain areas of the button. The fix was to store `pos = event.pos` and pass it directly to `collidepoint(pos)` since `event.pos` already returns the correct tuple 
format, and add `continue` statements after successful button clicks to prevent further event processing in that frame.

However, the length constraint problem persisted despite the initial fix. The code underwent additional refinement to address a remaining issue with text length 
validation. While the initial fix added length checking to individual sentences, the `generate_longer_text()` method was still concatenating multiple sentences 
without tracking the cumulative output length. This meant that even though each sentence individually stayed within the 80-450 character range, combining three 
sentences together regularly exceeded the 450 character maximum, as evidenced by Clarissa's output consistently surpassing this limit. The updated implementation 
introduced a `total_length` tracking variable that monitors the cumulative character count across all sentences, including the space characters used to join them. 
Before adding each new sentence to the output, the method now calculates `potential_total` by adding the candidate sentence's length to the existing total, plus one 
character for the joining space if sentences already exist. If this potential total would exceed `max_chars`, the sentence is rejected during generation or the loop 
breaks if a suitable sentence cannot be found. An additional safety mechanism was added at the end: if the final joined result still exceeds `max_chars` 
(which should theoretically never happen but serves as defensive programming), the text is truncated at the last complete word within the limit using 
`rsplit(' ', 1)[0]` and appended with "...". Finally, the method validates that the complete output meets the minimum length requirement 
of 80 characters before returning, otherwise returning "(no output)". This ensures that both characters' generated text strictly adheres to the specified 
80-450 character constraint for the total output, not just individual sentences.

On January 13th, a bug was discovered where `self.load_models()` had been placed at the wrong position in the initialization sequence, 
causing the interface to fail when users entered a word. This was corrected by ensuring `load_models()` was called at the end of `__init__` after all other state 
variables were initialized. The process page content was extracted into a separate file (`pro.py`) to make the interface code more structured and maintainable, 
with `PROCESS_SECTIONS` imported from this module. A scrollbar was added to the process page to handle content longer than the viewport, though initially the 
text collided with the scrollbar rendering. This was addressed by adjusting the viewport width calculation and adding proper clipping. A rim was added between 
the button area and text content to create visual separation. Questions arose about why the minimum and maximum character constraints were not working, which l
ed to the deeper investigation of the cumulative length tracking issue described above.

On January 15th, the comprehensive fix for all three bugs was finalized and verified. The `generate_longer_text` method now properly enforces both individual 
and cumulative length constraints through the `total_length` tracking mechanism. The `update_cursor()` method is called every frame in the main loop, ensuring 
responsive cursor changes. Button clicks are handled correctly with proper tuple passing to `collidepoint()` and `continue` statements preventing duplicate event 
processing. These corrections ensure the interface functions as intended, with reliable text generation within specified bounds, intuitive cursor feedback, and 
responsive button interactions.

### 13.1 
- wanting to create a python interface
- wanted to keep it simple and inspired to the early interfaces of computers, as the book is also older and published in 1925
- here i worked with pygame as i have already worked with the library and am also familiar. 
  - added constants (window height, width and fps)
  - added retro terminal colors (black and green)
  - adding fonts with sys.font (https://python-utilities.readthedocs.io/en/latest/sysfont.html)
  - then adding TextBlock helper class — wraps and renders multi-line text ensures text is split on word boundaries into lines that will not overflow the allocated width when drawn. This is required because pygame doesn't do automatic word wrap.
  - def render: centralizes rendering logic for wrapped text and supports viewport clipping via max_y.
  - adding input_text = "" for user to type in a word
  - def load model: prints a message and loads spaCy's medium English model (en_core_web_md) into self.nlp. This model includes word vectors required by expand_with_vectors. Loading spaCy is one of the heavier startup costs.
    - therefore it can take some time until the interface pops up
  - transfering into loead model, everything from main.py as i dont need that file anymore
  - defining where everything on the interface is placed (clarissa text right, septimus text left)
  - defining events such as KEYDOWN or K_ESCAPE for users to manage more intuitive
  - def update: update uses the clock's elapsed time since last tick to advance cursor_timer; when it exceeds blink interval, toggle cursor_visible and reset timer. This implements blinking caret synchronized with the frame clock. Using clock.get_time() ensures blink timing is independent of FPS.
- lastly __name__ == "__main__": Standard Python main guard: when the script is executed directly (not imported), print a startup message and create a WoolfInterface instance and call run() to start the application.

- over time updated small UI things such as making the courser an arrow, adding a process page and changing the arrow courser to a hand when hovering over a button
  - the thought behind the process page was mainly to capture the outputs of the markov chain inbetween the stages, as I thought it could be interesting to also see this development
  - I did also always use the same three words to generate the markov chain (time, flower, world), to make it comparable
  - for this i added PAGE_MAIN and PROCESS_PAGE and a lot of descriptions on how the buttons are supposed to be placed through the functions:
  - draw_button -> draws the button
  - draw_process_page -> makes sure the process page gets rendered properly
  - draw_control_bar: Purpose: draws a solid rectangle (the control bar) over the bottom region. This serves two roles: a visual container for buttons, and a visual mask so text/content drawn underneath doesn’t show through in that area.
  - adding event.type in event for loop to Implements clickable buttons: users can open the PROCESS page and return to MAIN by clicking those drawn button areas.

- only problem i encountered when adding the button that the text generated went over it -> needed to create some kind of boundary
- furthermore, the hand hover effect and the length boundery for the texts were not working this was due to The original code had three critical bugs that needed 
- correction. First, the Markov chain text generation was not respecting the specified character length constraints (80-450 characters). While the 
- `generate_longer_text()` method was validating individual sentences for length, it was then concatenating multiple sentences together without checking the total
- output length, resulting in text exceeding 450 characters. This was fixed by implementing cumulative length tracking across all sentences, where each new sentence
- is checked against the remaining available space before being added to the output. The method now maintains a `total_length` variable and only appends sentences 
- if they fit within the max_chars limit, with a safety check at the end to truncate any output that still exceeds the maximum and reject outputs below the minimum 
- threshold. Second, the hand cursor hover effect wasn't working because `update_cursor()` was only being called inside the event loop rather than every frame.
- Moving this call to the main `run()` loop ensures the cursor updates continuously based on mouse position. Third, the button click detection was unreliable 
- because `collidepoint()` was being passed a nested tuple `((x, y))` instead of a simple tuple `(x, y)`. This caused the collision detection to only work in 
- certain areas of the button. The fix was to pass `event.pos` directly to `collidepoint()` since it's already in the correct tuple format, and add `continue` 
- statements after successful button clicks to prevent further event processing in that frame.

- however the length problem accoured again and what finally worked was : The code underwent additional refinement to address a remaining issue with the text length validation. While the initial fix added length checking to individual sentences, the generate_longer_text() method was still concatenating multiple sentences without tracking the cumulative output length. This meant that even though each sentence individually stayed within the 80-450 character range, combining three sentences together regularly exceeded the 450 character maximum, as evidenced by Clarissa's output consistently surpassing this limit.
The updated implementation introduced a total_length tracking variable that monitors the cumulative character count across all sentences, including the space 
- characters used to join them. Before adding each new sentence to the output, the method now calculates potential_total by adding the candidate sentence's 
- length to the existing total, plus one character for the joining space if sentences already exist. If this potential total would exceed max_chars, the sentence is rejected during generation or the loop breaks if a suitable sentence cannot be found. An additional safety mechanism was added at the end: if the final joined result still exceeds max_chars (which should theoretically never happen but serves as defensive programming), the text is truncated at the last complete word within the limit and appended with "...". Finally, the method validates that the complete output meets the minimum length requirement of 80 characters before returning, otherwise returning "(no output)". This ensures that both characters' generated text strictly adheres to the specified 80-450 character constraint for the total output, not just individual sentences.
13. Jan
- fixing bug, because i placed self.load_models() at the wrong place, when entering a word it did not work
- adding process into a seperate file (pro.py) to make the interface code more structured
- adding a scrollbar but text now collides with scrollbar
- adding a rim from button to text
- min and max character does not work why?
def generate_with_length(model, min_chars=80, max_chars=450, tries=200):
    for _ in range(tries):
        sentence = model.make_sentence(tries=20)
        if not sentence:
            continue
        if min_chars <= len(sentence) <= max_chars:
            return sentence
    return None

15.jan The original code had three critical bugs that needed correction. First, the Markov chain text generation was not respecting the specified character length constraints (80-450 characters). The generate_longer_text() method was calling generate_biased() which had length checking, but then the main method wasn't enforcing these limits when combining multiple sentences. This was fixed by adding explicit min_chars and max_chars parameters to generate_longer_text() and validating each generated sentence before accepting it. Second, the hand cursor hover effect wasn't working because update_cursor() was only being called inside the event loop rather than every frame. Moving this call to the main run() loop ensures the cursor updates continuously based on mouse position. Third, the button click detection was unreliable because collidepoint() was being passed a nested tuple ((x, y)) instead of a simple tuple (x, y). This caused the collision detection to only work in certain areas of the button. The fix was to pass event.pos directly to collidepoint() since it's already in the correct tuple format, and add continue statements after successful button clicks to prevent further event processing in that frame.

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
---

## Data Collection Phase

### Initial Planning
**Date:** 7.1.2026
**To-do:** Determine which text passages to extract for analysis  
**Solution:** Initially focused on spoken words only, as these were most important for analyzing speaking patterns. 
However, realized Septimus's spoken words were very scant, so broadened extracts to include both thoughts and spoken words 
of both characters.  
**Challenge encountered:** Characters' thoughts were mostly about other characters. For instance, Clarissa often thinks 
and talks about Peter, but the intention was not to display how Peter is as a character.

### Manual Text Extraction
**Date:** 7.1.2026
**To-do:** Extract relevant passages from Mrs. Dalloway for both characters  
**Solution:** Manually went through the entire book to extract passages. Could not simply use Command+F to search for 
character names because Virginia Woolf writes long passages where the name gets mentioned at the beginning, then another 
character's perspective jumps in, then the original character (e.g., Clarissa) continues speaking but is now referred to as "she".  
**Challenge encountered:** This was more time-consuming than expected.

### File Organization
**Date:** 7.1 + 8.1
**To-do:** Store extracted passages in a text file, suitable for analysis.  
**Solution:** Saved extracts into separate text files: `clarissa.txt` and `septimus.txt` to enable independent 
analysis of each character's narrative voice.  
**Status:** Data collection phase concluded.

---

## Development Phase - Initial Setup (Section 10.1)

### Virtual Environment Setup
**Date:** 8.1.2026
**To-do:** Create a clean development environment  
**Solution:** Set up a virtual environment to ensure package installations wouldn't conflict with system-wide 
Python libraries or other projects.  
**Purpose:** Maintain isolated dependencies and prevent version conflicts.

### Text Preprocessing Implementation
**Date:** 8.1.2026
**To-do:** Handle formatting inconsistencies in extracted text passages  
**Solution:** Created `clean_text` function in `processes.py` to perform several text normalization steps:
- Normalize newlines by converting Windows-style `\r\n` to Unix-style `\n`
- Normalize curly quotes (both opening and closing variants of double and single quotes) to straight ASCII equivalents to prevent encoding issues
- Collapse excessive whitespace by replacing sequences of spaces and tabs with single spaces using `re.sub(r"[ \t]+", " ", text)`
- Reduce runs of three or more newlines to just two newlines with `re.sub(r"\n{3,}", "\n\n", text)` to maintain paragraph breaks while removing excessive vertical spacing
- Remove leading and trailing whitespace with `text.strip()`  
**References:** Python's `re` module for regular expressions - https://docs.python.org/3/library/re.html

### Basic Testing Setup
**Date:** 8.1.2026
**To-do:** Verify that text files can be loaded correctly  
**Solution:** Created `main.py` file to load both character files and test with `len()` function to 
verify importation worked correctly.  
**Result:** Successfully confirmed file loading pipeline works. Yeahhh. 

### Initial Markov Chain Experiments
**Date:** 9.1.2026
**To-do:** Test basic text generation to see if character voices are distinguishable  
**Solution:** Ran initial Markov chain experiments with `tries=10` and `state_size=1`.  
**Results:**
- Clarissa sample: "That he is probably the roses absolutely lovely; first getting sent down from the Queen, thought Clarissa, too, gave her hands already, quite enough of her time she looked out again."
- Septimus sample: "It spared him, the drowned sailor; the immortal ode; the heat wave of the sky, muttering, clasping his rock, like a Skye terrier snuffed his brain made her hold his eyes as he could not cut down trees"  
**Observation:** Despite the gibberish-like quality typical of low state-size Markov chains, the generated text clearly 
exhibited distinguishable characteristics revealing which character was which, validating that the underlying text corpora captured distinct voices.
**References:** Course material week ...

---

## Vector Similarity Implementation

### Cosine Similarity Function
**Date:** 9.1.2026
**To-do:** Create a method to compare semantic similarity between word vectors  
**Solution:** Implemented `cosine` function to calculate cosine similarity between two vectors. This function:
- Computes the dot product of vectors `a` and `b`
- Divides by the product of their norms using `np.linalg.norm()`
- Returns a float between -1 and 1 where values closer to 1 indicate higher semantic similarity
- Includes a denominator check to prevent division by zero if either vector has zero magnitude  
**References:** ...

### Semantic Expansion Mechanism
**Date:** 10.1.2026
**To-do:** Transform a single user input word into a field of related keywords  
**Solution:** Implemented `expand_with_vectors` function that:
- Takes the input word and converts it to lowercase
- Retrieves its word vector from spaCy's vocabulary using `nlp.vocab[w]`
- Iterates through a pre-built list of candidate lemmas
- Retrieves each candidate's vector and checks if it has a valid vector representation
- For each valid candidate, calculates cosine similarity between the base word's vector and the candidate's vector
- Collects candidates exceeding the `min_sim` threshold (0.45 by default) with their similarity scores
- Sorts results in descending order by similarity
- Returns the original input word followed by the top `k` (default 8) most similar candidates  
**Parameters chosen:** `k=8` and `min_sim=0.45` were chosen to balance between having enough semantic variety while 
maintaining meaningful relevance to the input word.  
**Purpose:** Creates a semantic field that guides the Markov chain generation toward thematically relevant content.
**References**: ...

---

## Voice Analysis Module (voice.py)

### SpaCy Integration Setup
**Date:** Mid-January  
**To-do:** Enable deeper linguistic analysis of each character's voice beyond simple Markov chain generation  
**Solution:** Created `voice.py` module to encapsulate voice analysis and biased generation functionality.

### Banned Lemmas Definition
**Date:** Mid-January  
**To-do:** Filter out words that reflect narration mechanics rather than meaningful lexical preferences  
**Solution:** Defined `DEFAULT_BAN_LEMMAS` as a set containing:
- Character names: "clarissa", "dalloway", "mrs", "septimus", "warren", "smith", "peter", "holmes"
- High-frequency speech and thought reporting verbs: "say", "think", "tell", "ask"
- Vague words: "thing", "like"  
**Rationale:** Examining initial SpaCy analysis results revealed these words dominated frequency rankings but reflected 
narration mechanics and extraction artifacts rather than meaningful lexical preferences.  
**Uncertainty:** Some concern about whether manually excluding these terms constituted inappropriate subjective 
influence on the outcome, but decision was made to proceed with filtering to produce more interpretable and contentful 
results that better represent each character's thematic vocabulary.

### VoiceStats Data Structure
**Date:** Mid-January  
**To-do:** Create a clean container for voice analysis results  
**Solution:** Defined `VoiceStats` dataclass using Python's `@dataclass` decorator with three attributes:
- `mean_sent_len` (float): average sentence length
- `top_pos` (dict): mapping POS tags to their proportions
- `top_lemmas` (list): most frequent lemmas with counts  
**Purpose:** Provides structured storage for statistical analysis results.
**Reference:**

### Sentence Length Analysis
**Date:** Mid-January  
**To-do:** Calculate average sentence length to compare speaking styles  
**Solution:** Implemented sentence length calculation in `analyze_voice` function:
- Processes entire text through spaCy to create a `doc` object
- Iterates through `doc.sents`
- Filters out whitespace-only tokens
- Builds list of sentence lengths measured in tokens
- Computes mean sentence length using `np.mean()` and stores as float  
**Purpose:** Show if there is a difference between Septimus's and Clarissa's speaking style.

### POS (Part-of-Speech) Proportion Analysis
**Date:** Mid-January  
**To-do:** Analyze syntactic preferences of each character  
**Solution:** Implemented POS proportion calculation:
- Counts all alphabetic tokens' POS tags using a `Counter`
- Filters to keep only five categories of interest: NOUN, VERB, ADJ (adjective), ADV (adverb), and PRON (pronoun)
- Calculates each category's proportion by dividing its count by total number of tokens
- Creates `top_pos` as a dictionary of normalized proportions  
**Purpose:** Reveal syntactic preferences between characters.

### Lemma Frequency Analysis
**Date:** Mid-January  
**To-do:** Build vocabulary analysis for each character  
**Solution:** Implemented lemma frequency list building in `analyze_voice`:
- Iterates through all tokens
- Filters to keep only alphabetic tokens that aren't stop words and have length greater than 2 characters
- Converts each token's lemma to lowercase
- Checks against `ban_lemmas` and appends if not banned
- Uses `Counter` to tally lemma frequencies
- Extracts top entries with `.most_common(top_n_lemmas)`
- Stores results in `VoiceStats` object  
**Default parameter:** `top_n_lemmas=10`

### Candidate Lemma Pool Creation
**Date:** Mid-January  
**To-do:** Create a frequency-ranked list of lemmas for semantic expansion  
**Solution:** Implemented `build_candidates` function that:
- Processes text through spaCy
- Extracts alphabetic non-stopword lemmas longer than 2 characters
- Excludes banned lemmas
- Returns the top `top_n=400` most frequent ones  
**Purpose:** Provides sufficient diversity for vector similarity matching while ensuring candidates represent meaningful vocabulary rather than rare words. This precomputed shortlist speeds similarity searches in downstream `expand_with_vectors` function.  
**Parameter choice:** 400 candidates vs 10 top lemmas provides larger pool for vector matching.

### Keyword Scoring Mechanism
**Date:** Mid-January  
**To-do:** Evaluate how well a sentence aligns with a target semantic field  
**Solution:** Implemented `keyword_hits` function that:
- Takes a sentence string and list of keywords
- Converts sentence to lowercase
- Counts how many keywords appear using word-boundary matching with regular expressions `re.search(rf"\b{kw}\b", s)`
- Uses `\b` boundary anchors to ensure whole-word matches only  
**Purpose:** Reduces false positives that would occur from substring matching (e.g., preventing "run" from matching inside "running" or "trunk").

### Biased Generation Algorithm - Single Sentence
**Date:** Mid-January  
**To-do:** Generate Markov chain sentences guided by keyword relevance and length constraints  
**Solution:** Implemented `generate_biased` function that:
- Accepts a Markov model, list of keywords, number of attempts `n=120`, and length boundaries `min_chars=80` and `max_chars=450`
- Initializes `best` and `best_score` to track highest-scoring sentence
- Runs up to `n` iterations, each calling `model.make_sentence(tries=20)`
- Validates length: rejects sentences outside specified character range
- For valid sentences, calculates relevance score using `keyword_hits`
- Updates `best_score` and `best` when superior candidate found
- Returns best sentence found, or `"(no output)"` if no suitable sentence generated  
**Purpose:** Core biased generation algorithm for single sentences.

### Biased Generation Algorithm - Multiple Sentences
**Date:** Mid-January  
**To-do:** Extend single-sentence generation to produce multi-sentence outputs  
**Solution:** Implemented `generate_biased_multi` function that:
- Calls `generate_biased` multiple times (controlled by `num_sentences=3`)
- Collects results
- Checks each generated sentence is valid (not None and not `"(no output)"`)
- Joins sentences with spaces using `" ".join(sentences)`
- Returns combined result or `"(no output)"` if no valid sentences generated  
**Purpose:** Produces coherent multi-sentence outputs.

### Module Organization Bug Fix
**Date:** Mid-January  
**To-do:** Resolve variable name and function call conflicts between modules  
**Problem:** Initial integration of vector-based semantic expansion with spaCy failed due to mixed up variable names and function calls between `voice.py` and `processes.py`.  
**Solution:** Clarified module separation:
- `processes.py` handles: text cleaning and vector operations (`clean_text`, `cosine`, `expand_with_vectors`)
- `voice.py` focuses on: voice analysis and biased generation (`analyze_voice`, `build_candidates`, `keyword_hits`, `generate_biased`, `generate_biased_multi`)
- Ensured proper imports between modules  
**Rationale:** `expand_with_vectors` needed access to the spaCy model's vocabulary and therefore belonged in `processes.py` alongside other preprocessing utilities, while generation functions naturally grouped with voice analysis in `voice.py`.

---

## Python Interface Development (Section 13.1)

### Initial Pygame Setup
**Date:** January 13  
**To-do:** Create a simple Python interface for user interaction  
**Design philosophy:** Inspired by early computer terminal interfaces, fitting the historical context of Virginia Woolf's "Mrs Dalloway" published in 1925.  
**Solution:** Chose Pygame as the framework due to prior familiarity with the library. Defined:
- Window dimensions: 1200x800 pixels
- Frame rate: 60 FPS
- Retro terminal color palette: black backgrounds and green accent colors to evoke vintage computing aesthetic  
**References:** pygame documentation, sys.font documentation - https://python-utilities.readthedocs.io/en/latest/sysfont.html

### Font Initialization
**Date:** January 13  
**To-do:** Set up typography for the interface  
**Solution:** Used `pygame.font.SysFont()` to load the Courier monospace font family, creating distinct sizes for:
- Titles
- Names
- Body text
- Input
- Small labels  
**Fallback:** Default fonts if Courier unavailable on system.

### Text Wrapping Implementation
**Date:** January 13  
**To-do:** Handle multi-line text rendering since Pygame doesn't provide automatic word wrapping  
**Solution:** Implemented `TextBlock` helper class that:
- Takes text, font, maximum width, and color parameters during initialization
- Splits input into words
- Iteratively builds lines by testing whether adding each subsequent word would exceed allocated width using `font.size()`
- When a word would cause overflow, saves current line to `self.lines` and starts new line with that word
- Provides `render` method that:
  - Iterates through `self.lines`
  - Blits each line sequentially while tracking vertical position
  - Supports viewport clipping via optional `max_y` parameter that stops rendering when vertical boundary reached  
**Purpose:** Ensures text splits on word boundaries into lines that won't overflow the allocated width when drawn.

### User Input Handling
**Date:** January 13  
**To-do:** Enable users to type words for text generation  
**Solution:** Initialized `self.input_text = ""` to store the word typed by the user.

### Model Loading Implementation
**Date:** January 13  
**To-do:** Initialize NLP and text generation components  
**Solution:** Created `load_models` method that:
- Prints startup message
- Loads spaCy's medium English model (`en_core_web_md`) into `self.nlp`
- Transfers all functionality from original `main.py` file:
  - Reading Clarissa and Septimus text files
  - Cleaning them with `clean_text`
  - Building Markov models with `markovify.Text`
  - Analyzing voice statistics with `analyze_voice`
  - Building candidate word lists with `build_candidates`  
**Note:** Loading spaCy represents one of the heavier startup costs, which is why there can be a noticeable delay between launching the script and the interface appearing on screen.  
**Result:** `main.py` file no longer needed; codebase consolidated.

### Interface Layout Design
**Date:** January 13  
**To-do:** Define visual positioning of character panels  
**Solution:** Placed Clarissa's panel on left side and Septimus's panel on right side of main interface, creating a visual divide between the two characters' outputs.

### Keyboard Event Handling
**Date:** January 13  
**To-do:** Make interface more intuitive for users  
**Solution:** Implemented responses to `pygame.KEYDOWN` events:
- `K_ESCAPE`: exiting or returning to main page
- `K_RETURN`: triggering text generation from input word
- `K_BACKSPACE`: deleting characters
- Alphanumeric keys: typing  
**Purpose:** Provide standard keyboard navigation.

### Cursor Blinking Animation
**Date:** January 13  
**To-do:** Create visual feedback for input field  
**Solution:** Implemented `update` method to manage cursor blinking:
- Uses `self.clock.get_time()` to advance `cursor_timer` by elapsed milliseconds since last frame
- When timer exceeds `cursor_blink_speed` (500ms), toggles `cursor_visible` and resets timer
- Creates synchronized blinking caret effect that operates independently of frame rate  
**Purpose:** Standard text input cursor behavior.

### Main Loop Structure
**Date:** January 13  
**To-do:** Set up application entry point  
**Solution:** Script concludes with standard Python main guard `if __name__ == "__main__":` which:
- Ensures when file is executed directly (not imported as module), it prints startup message
- Creates `WoolfInterface` instance
- Calls `run()` to start application loop

---

## UI Enhancements

### Cursor Appearance
**Date:** Mid-January  
**To-do:** Improve default cursor appearance  
**Solution:** Changed default cursor to arrow (`pygame.SYSTEM_CURSOR_ARROW`).

### Process Page Addition
**Date:** Mid-January  
**To-do:** Display methodology and intermediate outputs  
**Solution:** Introduced process page to display methodology and intermediate outputs from Markov chain generation stages.  
**Motivation:** Capturing and visualizing intermediate stages seemed valuable for understanding how the system works. Observing these development stages during testing revealed interesting patterns worth preserving.  
**Testing approach:** During development, consistently used the same three words (time, flower, world) to generate Markov chain outputs, ensuring comparability across iterations.

### Page Navigation System
**Date:** Mid-January  
**To-do:** Enable switching between main interface and process documentation  
**Solution:** Defined constants and functions:
- `PAGE_MAIN` and `PAGE_PROCESS` constants
- `draw_button`: renders button outlines and centered labels
- `draw_process_page`: ensures process documentation renders properly with scrolling support
- `draw_control_bar`: draws solid rectangle over bottom region serving dual roles:
  - Visual container for buttons
  - Mask preventing underlying text content from showing through in that area

### Interactive Cursor Feedback
**Date:** Mid-January  
**To-do:** Provide visual feedback for clickable elements  
**Solution:** Enhanced cursor behavior to change to hand cursor (`pygame.SYSTEM_CURSOR_HAND`) when hovering over buttons.

### Button Click Functionality
**Date:** Mid-January  
**To-do:** Implement clickable navigation  
**Solution:** Implemented in event loop using `event.type == pygame.MOUSEBUTTONDOWN` checks, allowing users to open process page and return to main by clicking drawn button areas.

### Content Boundary Problem
**Date:** Mid-January  
**To-do:** Prevent generated text from overlapping control bar buttons  
**Problem:** Generated text would extend beneath and overlap the control bar containing buttons.  
**Solution:** Created `CONTENT_BOTTOM_Y` constant defining a hard stop for content rendering, calculated as `CONTROL_BAR_Y - 20` to provide spacing between content and control bar.

---

## Critical Bug Fixes (January 15)

### Bug 1: Text Length Constraints Not Working
**Date:** January 15  
**To-do:** Enforce character length constraints of 80-450 characters  
**Problem:** Markov chain text generation was not respecting specified length constraints. While `generate_biased` had length checking for individual sentences, the main method wasn't enforcing limits when combining multiple sentences together. Clarissa's output consistently exceeded 450 characters.  
**Initial attempt:** Added explicit `min_chars` and `max_chars` parameters to `generate_longer_text` and validated each generated sentence before accepting it.  
**Why initial fix failed:** The method was concatenating multiple sentences without tracking cumulative output length. Each sentence individually stayed within 80-450 character range, but combining three sentences together regularly exceeded 450 character maximum.  
**Final solution:** Implemented comprehensive cumulative length tracking:
- Introduced `total_length` tracking variable monitoring cumulative character count across all sentences, including space characters used to join them
- Before adding each new sentence, calculates `potential_total` by adding candidate sentence's length to existing total, plus one character for joining space if sentences already exist
- If `potential_total` would exceed `max_chars`, sentence is rejected during generation or loop breaks if suitable sentence cannot be found
- Added safety mechanism at end: if final joined result still exceeds `max_chars`, text is truncated at last complete word within limit using `rsplit(' ', 1)[0]` and appended with "..."
- Validates complete output meets minimum length requirement of 80 characters before returning, otherwise returns "(no output)"  
**Result:** Both characters' generated text strictly adheres to specified 80-450 character constraint for total output, not just individual sentences.

### Bug 2: Hand Cursor Hover Effect Not Working
**Date:** January 15  
**To-do:** Make cursor change when hovering over buttons  
**Problem:** Hand cursor hover effect wasn't working because `update_cursor()` was only being called inside the event loop rather than every frame.  
**Solution:** Moved `update_cursor()` call to main `run()` loop, ensuring cursor updates continuously based on mouse position. Method checks whether mouse is over a button and sets appropriate cursor type.  
**Result:** Responsive cursor changes providing visual feedback.

### Bug 3: Button Click Detection Unreliable
**Date:** January 15  
**To-do:** Fix inconsistent button click behavior  
**Problem:** `collidepoint()` was being passed a nested tuple `((x, y))` instead of a simple tuple `(x, y)`. This caused collision detection to only work in certain areas of the button.  
**Solution:**
- Store `pos = event.pos`
- Pass it directly to `collidepoint(pos)` since `event.pos` already returns correct tuple format
- Add `continue` statements after successful button clicks to prevent further event processing in that frame  
**Result:** Reliable button interactions throughout the interface.

### Load Models Bug Fix
**Date:** January 13  
**To-do:** Fix interface failure when users entered a word  
**Problem:** `self.load_models()` had been placed at wrong position in initialization sequence.  
**Solution:** Ensured `load_models()` called at end of `__init__` after all other state variables were initialized.  
**Result:** Interface functions correctly when users input words.

---

## Code Organization Improvements

### Process Content Extraction
**Date:** January 13  
**To-do:** Make interface code more structured and maintainable  
**Solution:** Extracted process page content into separate file (`pro.py`), with `PROCESS_SECTIONS` imported from this module.  
**Result:** Cleaner, more modular codebase.

### Scrollbar Implementation
**Date:** January 13  
**To-do:** Handle content longer than viewport on process page  
**Solution:** Added scrollbar to process page.  
**Initial problem:** Text collided with scrollbar rendering.  
**Fix:** Adjusted viewport width calculation and added proper clipping.

### Visual Separation Enhancement
**Date:** January 13  
**To-do:** Create clear visual boundary between interactive and content areas  
**Solution:** Added rim between button area and text content to create visual separation.


- concept/ storyline/ artist
- scene break
- shot list
- visual deck/ mood and tone2
- scedule
