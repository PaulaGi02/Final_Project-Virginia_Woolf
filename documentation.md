
seeing if the markov chain can replicate how the reader feels about the character in the book. 
also interesting because also capturing her inner thoughts which mostly precive other characters and not her -> how does this influence the markov
also clarissa taking in what other people thought about her. but difficult because i do not wantthe tone of the thinker
## data collction 7.1
- first i wanted to do the character analysis on what the characters were actually saying. 
- noticed not enough material in the Roman so therefore i decided to broaden the data collection to also the behaviour patterns.
- i overflew the whole roman as i could not just filter via command f the names as woolf often uses he or she, which made the process more time consumin than initiated

### 8.1
- finishing collection passages about Septimus

### 10.1.
- virtual enviroment: set up a clean environment so installs don’t conflict.
- created main.py to load both text files and just test with a simple len() if importation worked 
- cleaning text from quotes and whitespaces etc.
- Clarissa sample: That he is probably the roses absolutely lovely; first getting sent down from the Queen, thought Clarissa, too, gave her hands already, quite enough of her time she looked out again.
Septimus sample: It spared him, the drowned sailor; the immortal ode; the heat wave of the sky, muttering, clasping his rock, like a Skye terrier snuffed his brain made her hold his eyes as he could not cut down trees
- First try with markov chain and tries = 10 and state_size = 1
- even though it is gibberigh clear which character is who
- adding Spacy for more analysing the oices of each Character
- creating voice.py to analysie common patterns in the texts of each character such as 
- looked at resluts of spaacey analysis and realised that there were a lot of speech fillinf words like say or tell and Names like Clarissa or septimus. wanted to remove them because when character think about a user topic i do  not want their name
- here i experimented a bid and tried to find the inbetween between deleting too much and leavong too many common wordss. 
- For interpretability, I exclude character names and high-frequency speech/thought reporting verbs (e.g., ‘say’, ‘think’) from the top lemma lists, because they reflect narration/extraction artifacts rather than lexical preferences.

--- Clarissa stats ---
Mean sentence length: 20.6
POS proportions: {'NOUN': 0.155, 'VERB': 0.155, 'ADJ': 0.064, 'ADV': 0.067, 'PRON': 0.158}
Top lemmas: [('like', 15), ('love', 15), ('feel', 14), ('go', 14), ('party', 14), ('come', 11), ('stand', 11), ('old', 11), ('look', 10), ('little', 10)]

--- Septimus stats ---
Mean sentence length: 19.6
POS proportions: {'NOUN': 0.18, 'VERB': 0.16, 'ADJ': 0.058, 'ADV': 0.062, 'PRON': 0.132}
Top lemmas: [('man', 16), ('look', 15), ('world', 12), ('like', 12), ('cry', 12), ('beauty', 10), ('dead', 9), ('lie', 9), ('hand', 8), ('kill', 7)]

trying to connect to user intut: Type a word (or quit): time

CLARISSA: She could see Peter out of Mulberry's with her little pink face pursed in enquiry.
SEPTIMUS: He knew the meaning of the world itself is without meaning.

Type a word (or quit): flower

CLARISSA: Clarissa had leant forward, taken his hand, patting his knee and, feeling as she turned and walked back towards Bond Street, annoyed, because it was possible to go out of their ordinary ways, partly the background, it was time to move, to go--but where?
SEPTIMUS: there he was; still sitting alone on the lower shelf, then, gradually at the mantelpiece, with the jar of roses.

Type a word (or quit): world

CLARISSA: The leaden circles dissolved in the triumph and the strange high singing of some aeroplane overhead was what she looked like, but felt herself a stake driven in at the other end of the moment.
SEPTIMUS: I leant over the edge of the world, he said.

Type a word (or quit): 

to do
- delete  most common filler words 