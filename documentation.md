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
Firstly I wanted to focus on just the spoken words as those were the most important passagenses for 
analysing speaking patterns. However, I realised that especially Septimus spoken words were very scant. 
I decided to broaden my extracts to also the thoughts of both characters. Here, I noticed that 
the thoughts were mostly about other characters. For instance, Clarissa often thinks and talks about Peter.
However how Peter is as a character was not my intention to display.
This was one of the most time consuming parts, as I could not solely filter the parts by command + f and then
searching the name, as Virginia Woolf writes long passanges where the name gets sometimes mentioned at the beginning
an other character jumps in and then e.g. Clarissa talks again but the word "she" now accours.
Therefore, I had to skip through the whole book which was quite time consuming.
### 8.1
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
  - added sentence length calulation for statistics to compare voices
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
- only problem i encountered when adding the button that the text generated went over it -> needed to create some kind of boundary
- 
- Bug: Individual sentences were validated for length, but concatenating multiple sentences exceeded the 450 character limit.
- Fix:Track total length across all sentences and stop adding when limit would be exceeded.
- 13. Jan
- fixing bug, because i placed self.load_models() at the wrong place, when entering a word it did not work
- adding different courser when courser hovers over a button, because page loads kinda long and can be confusing for user when takes too long
- adding process into a seperate file (pro.py) to make the interface code more structured
- adding a scrollbar but text now collides with scrollbar
- adding a rim from button to text
- min and max character does not work why?

15.jan The original code had three critical bugs that needed correction. First, the Markov chain text generation was not respecting the specified character length constraints (80-450 characters). The generate_longer_text() method was calling generate_biased() which had length checking, but then the main method wasn't enforcing these limits when combining multiple sentences. This was fixed by adding explicit min_chars and max_chars parameters to generate_longer_text() and validating each generated sentence before accepting it. Second, the hand cursor hover effect wasn't working because update_cursor() was only being called inside the event loop rather than every frame. Moving this call to the main run() loop ensures the cursor updates continuously based on mouse position. Third, the button click detection was unreliable because collidepoint() was being passed a nested tuple ((x, y)) instead of a simple tuple (x, y). This caused the collision detection to only work in certain areas of the button. The fix was to pass event.pos directly to collidepoint() since it's already in the correct tuple format, and add continue statements after successful button clicks to prevent further event processing in that frame.
