# Introduction + Research Question
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
