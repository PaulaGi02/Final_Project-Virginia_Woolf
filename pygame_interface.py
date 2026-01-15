import pygame
import sys
from pathlib import Path
import markovify
import spacy
from scr.processes import clean_text, expand_with_vectors
from scr.voice import analyze_voice, DEFAULT_BAN_LEMMAS, build_candidates, generate_biased

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Retro terminal colors - stark black and white with green accent
BG_COLOR = (0, 0, 0)  # Pure black
TEXT_COLOR = (255, 255, 255)  # Pure white
ACCENT_COLOR = (0, 255, 0)  # Classic terminal green
DIM_COLOR = (100, 100, 100)  # Grey for subtle elements
CURSOR_COLOR = (0, 255, 0)  # Blinking green cursor

CONTROL_BAR_HEIGHT = 70
CONTROL_BAR_Y = WINDOW_HEIGHT - CONTROL_BAR_HEIGHT - 10

CONTENT_BOTTOM_Y = CONTROL_BAR_Y - 20  # hard stop for text

PAGE_MAIN = "main"
PAGE_PROCESS = "process"

PROCESS_TEXT = """
PROCESS LOG :: HOW THE TEXT IS GENERATED
1) Corpus selection:
   - Clarissa corpus: extracted passages
   - Septimus corpus: extracted passages

2) Preprocessing:
   - Normalize whitespace and punctuation
   - Preserve sentence punctuation to keep Woolf-like rhythm

3) Voice analysis (spaCy):
   - Sentence length, POS proportions, frequent lemmas

4) Candidate lexicon:
   - Build frequent lemmas per character (stopwords removed)
   - Exclude character names and reporting verbs

5) Semantic expansion:
   - User prompt word expanded via spaCy vectors (cosine similarity)
   - Produces a semantic field (word + nearest neighbors)

6) Markov generation:
   - Generate many candidate sentences per character (Markov chain)
   - Score each by keyword hits from semantic field
   - Choose the best-scoring sentence

7) Output:
   - Chain 3 sentences for a longer “voice block”
""".strip()
# Monospace font for terminal aesthetic
try:
    # Try to use a monospace font
    TITLE_FONT = pygame.font.SysFont('courier', 48, bold=True)
    NAME_FONT = pygame.font.SysFont('courier', 32, bold=True)
    TEXT_FONT = pygame.font.SysFont('courier', 20)
    INPUT_FONT = pygame.font.SysFont('courier', 28)
    SMALL_FONT = pygame.font.SysFont('courier', 16)
except:
    # Fallback to default
    TITLE_FONT = pygame.font.Font(None, 48)
    NAME_FONT = pygame.font.Font(None, 32)
    TEXT_FONT = pygame.font.Font(None, 20)
    INPUT_FONT = pygame.font.Font(None, 28)
    SMALL_FONT = pygame.font.Font(None, 16)


class TextBlock:
    """Wraps text into multiple lines with typing animation"""
    def __init__(self, text, font, max_width, color):
        self.lines = []
        self.color = color
        self.full_text = text

        words = text.split()
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    self.lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            self.lines.append(' '.join(current_line))

    def render(self, surface, x, y, font, line_spacing=4):
        """Render the text block at position (x, y)"""
        current_y = y
        for line in self.lines:
            text_surf = font.render(line, True, self.color)
            surface.blit(text_surf, (x, current_y))
            current_y += font.get_height() + line_spacing
        return current_y


class WoolfInterface:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("THE ROOM BETWEEN US")
        self.clock = pygame.time.Clock()
        self.current_cursor = pygame.SYSTEM_CURSOR_ARROW

        # State
        self.input_text = ""
        self.loading = False

        # Cursor blink
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # ms

        # Results
        self.current_word = None
        self.clarissa_keywords = []
        self.septimus_keywords = []
        self.clarissa_output = ""
        self.septimus_output = ""
        self.clarissa_stats = None
        self.septimus_stats = None

        # Show initial instructions
        self.show_intro = True

        # Page state
        self.page = PAGE_MAIN

        # Buttons (rectangles)
        self.process_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 150,
            CONTROL_BAR_Y + 15,
            300,
            40
        )

        self.back_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 80,
            CONTROL_BAR_Y + 15,
            160,
            40
        )
        # Load models ONCE at startup
        self.load_models()

    def update_cursor(self):
        mouse_pos = pygame.mouse.get_pos()
        new_cursor = pygame.SYSTEM_CURSOR_ARROW

        if self.page == PAGE_MAIN:
            if self.process_button_rect.collidepoint(mouse_pos):
                new_cursor = pygame.SYSTEM_CURSOR_HAND

        elif self.page == PAGE_PROCESS:
            if self.back_button_rect.collidepoint(mouse_pos):
                new_cursor = pygame.SYSTEM_CURSOR_HAND

        if new_cursor != self.current_cursor:
            pygame.mouse.set_cursor(new_cursor)
            self.current_cursor = new_cursor

    def draw_control_bar(self):
        # Solid black bar to block text behind it
        pygame.draw.rect(
            self.screen,
            BG_COLOR,
            (0, CONTROL_BAR_Y, WINDOW_WIDTH, CONTROL_BAR_HEIGHT)
        )

        # Top border line
        pygame.draw.line(
            self.screen,
            DIM_COLOR,
            (30, CONTROL_BAR_Y),
            (WINDOW_WIDTH - 30, CONTROL_BAR_Y),
            1
        )


    def draw_button(self, rect, label, active=True):
    # Border + text, terminal style
        border_color = ACCENT_COLOR if active else DIM_COLOR
        pygame.draw.rect(self.screen, border_color, rect, 2)

        text_surf = SMALL_FONT.render(label, True, border_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_process_page(self):
        # Background already filled in draw()
        self.draw_title()

        # Header
        header = NAME_FONT.render("[PROCESS]", True, ACCENT_COLOR)
        self.screen.blit(header, (50, 130))

        # Body text (wrapped)
        block = TextBlock(PROCESS_TEXT, TEXT_FONT, WINDOW_WIDTH - 100, TEXT_COLOR)
        block.render(self.screen, 50, 190, TEXT_FONT, line_spacing=6)

        # Back button
        self.draw_button(self.back_button_rect, "BACK [ESC]")

    def load_models(self):
        """Load text and build models"""
        print("Loading models...")

        # Load spaCy
        self.nlp = spacy.load("en_core_web_md")

        # Load texts
        clarissa_txt = open("data/clarissa.txt").read()
        septimus_txt = open("data/septimus.txt").read()

        self.clarissa_text = clean_text(clarissa_txt)
        self.septimus_text = clean_text(septimus_txt)

        # Build Markov models
        self.clarissa_model = markovify.Text(self.clarissa_text, state_size=2)
        self.septimus_model = markovify.Text(self.septimus_text, state_size=2)

        # Analyze voices
        self.clarissa_stats = analyze_voice(
            self.clarissa_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )
        self.septimus_stats = analyze_voice(
            self.septimus_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )

        # Build candidates for keyword expansion
        self.clarissa_candidates = build_candidates(
            self.clarissa_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )
        self.septimus_candidates = build_candidates(
            self.septimus_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )

        print("Models loaded!")

    def generate_longer_text(self, model, keywords, num_sentences=3):
        """Generate multiple sentences chained together"""
        sentences = []
        for _ in range(num_sentences):
            sent = generate_biased(model, keywords, n=140)
            if sent and sent != "(no output)":
                sentences.append(sent)

        return " ".join(sentences) if sentences else "(no output)"

    def generate_from_word(self, word):
        """Generate text from both voices based on input word"""
        self.loading = True
        self.current_word = word
        self.show_intro = False

        # Expand keywords
        self.clarissa_keywords = expand_with_vectors(
            word, self.nlp, self.clarissa_candidates
        )
        self.septimus_keywords = expand_with_vectors(
            word, self.nlp, self.septimus_candidates
        )

        # Generate text (3 sentences each for longer output)
        self.clarissa_output = self.generate_longer_text(
            self.clarissa_model, self.clarissa_keywords, num_sentences=3
        )
        self.septimus_output = self.generate_longer_text(
            self.septimus_model, self.septimus_keywords, num_sentences=3
        )

        self.loading = False

    def draw_scanlines(self):
        """Draw subtle scanlines for CRT effect"""
        for y in range(0, WINDOW_HEIGHT, 4):
            pygame.draw.line(self.screen, (10, 10, 10), (0, y), (WINDOW_WIDTH, y), 1)

    def draw_border(self):
        """Draw retro border"""
        border_width = 2
        # Outer border
        pygame.draw.rect(self.screen, TEXT_COLOR,
                        (10, 10, WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20), border_width)
        # Corner accents
        corner_size = 20
        corners = [
            (10, 10), (WINDOW_WIDTH - 30, 10),
            (10, WINDOW_HEIGHT - 30), (WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30)
        ]
        for cx, cy in corners:
            pygame.draw.rect(self.screen, ACCENT_COLOR, (cx, cy, corner_size, corner_size), border_width)

    def draw_title(self):
        """Draw title in retro style"""
        title = TITLE_FONT.render("THE ROOM BETWEEN US", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = SMALL_FONT.render("MRS DALLOWAY :: VOICE SIMULATION ENGINE :: 1925", True, ACCENT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 85))
        self.screen.blit(subtitle, subtitle_rect)

        # Separator line
        pygame.draw.line(self.screen, DIM_COLOR, (30, 110), (WINDOW_WIDTH - 30, 110), 1)

    def draw_input_area(self):
        """Draw input area with blinking cursor"""
        y_pos = 130

        # Prompt
        prompt = TEXT_FONT.render(">", True, ACCENT_COLOR)
        self.screen.blit(prompt, (40, y_pos))

        # Input text
        input_display = INPUT_FONT.render(self.input_text, True, TEXT_COLOR)
        self.screen.blit(input_display, (70, y_pos - 2))

        # Blinking cursor
        if self.cursor_visible:
            cursor_x = 70 + INPUT_FONT.size(self.input_text)[0]
            cursor = INPUT_FONT.render("_", True, CURSOR_COLOR)
            self.screen.blit(cursor, (cursor_x, y_pos - 2))

        # Instructions
        if self.show_intro:
            instructions = [
                "ENTER A WORD TO EXPLORE THE SEMANTIC DIVIDE",
                "PRESS [RETURN] TO EXECUTE :: [ESC] TO EXIT"
            ]
            inst_y = y_pos + 50
            for inst in instructions:
                inst_surf = SMALL_FONT.render(inst, True, DIM_COLOR)
                inst_rect = inst_surf.get_rect(center=(WINDOW_WIDTH // 2, inst_y))
                self.screen.blit(inst_surf, inst_rect)
                inst_y += 25

    def draw_divider(self):
        """Draw vertical divider"""
        y_start = 200
        x_center = WINDOW_WIDTH // 2

        # Dashed line
        for y in range(y_start, WINDOW_HEIGHT - 30, 10):
            pygame.draw.line(self.screen, DIM_COLOR,
                           (x_center, y), (x_center, y + 5), 1)

    def draw_voice_panel(self, x, y, name, keywords, output, stats):
        """Draw one character's panel"""
        current_y = y

        # Name header with ASCII art style
        name_surf = NAME_FONT.render(f"[{name}]", True, ACCENT_COLOR)
        self.screen.blit(name_surf, (x, current_y))
        current_y += 40

        # Stats
        if stats:
            stat_text = f"AVG SENTENCE LENGTH: {stats.mean_sent_len:.1f}"
            stat_surf = SMALL_FONT.render(stat_text, True, DIM_COLOR)
            self.screen.blit(stat_surf, (x, current_y))
            current_y += 25

        # Keywords
        if keywords and self.current_word:
            kw_label = SMALL_FONT.render("SEMANTIC FIELD:", True, DIM_COLOR)
            self.screen.blit(kw_label, (x, current_y))
            current_y += 20

            kw_text = " ".join([f"{w}" for w in keywords[:8]])
            kw_block = TextBlock(kw_text, SMALL_FONT, 500, ACCENT_COLOR)
            current_y = kw_block.render(self.screen, x, current_y, SMALL_FONT, line_spacing=3)
            current_y += 25

        # Output
        if output and output != "(no output)":
            # Output label
            output_label = SMALL_FONT.render("OUTPUT:", True, DIM_COLOR)
            self.screen.blit(output_label, (x, current_y))
            current_y += 25

            # Text output
            text_block = TextBlock(output, TEXT_FONT, 500, TEXT_COLOR)
            text_block.render(self.screen, x, current_y, TEXT_FONT, line_spacing=6)

    def draw(self):
        """Main draw function"""
        # Background
        self.screen.fill(BG_COLOR)

        # Retro effects
        self.draw_scanlines()
        self.draw_border()

        # Page routing
        if self.page == PAGE_PROCESS:
            self.draw_process_page()
            pygame.display.flip()
            return

        # MAIN page content
        self.draw_title()
        self.draw_input_area()

        # Process button (only on main page)
        self.draw_button(self.process_button_rect, "PROCESS / METHOD")


        # Content
        self.draw_title()
        self.draw_input_area()

        # Only show results after first generation
        if not self.show_intro:
            self.draw_divider()

            # Left panel - Clarissa
            self.draw_voice_panel(
                x=50,
                y=200,
                name="CLARISSA",
                keywords=self.clarissa_keywords,
                output=self.clarissa_output,
                stats=self.clarissa_stats
            )

            # Right panel - Septimus
            self.draw_voice_panel(
                x=WINDOW_WIDTH // 2 + 50,
                y=200,
                name="SEPTIMUS",
                keywords=self.septimus_keywords,
                output=self.septimus_output,
                stats=self.septimus_stats
            )

        # Loading indicator
        if self.loading:
            loading_y = WINDOW_HEIGHT - 40
            loading_text = TEXT_FONT.render("PROCESSING...", True, ACCENT_COLOR)
            loading_rect = loading_text.get_rect(center=(WINDOW_WIDTH // 2, loading_y))
            self.screen.blit(loading_text, loading_rect)

        pygame.display.flip()

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if self.page == PAGE_MAIN:
                    if self.process_button_rect.collidepoint(mx, my):
                        self.page = PAGE_PROCESS
                        return True

                elif self.page == PAGE_PROCESS:
                    if self.back_button_rect.collidepoint(mx, my):
                        self.page = PAGE_MAIN
                        return True


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.page == PAGE_PROCESS:
                        self.page = PAGE_MAIN
                        return True
                    return False


                elif event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        print(f"Generating for word: {self.input_text}")  # Debug
                        self.generate_from_word(self.input_text.strip())
                        self.input_text = ""  # Clear input after generating

                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]

                else:
                    # Add character if it's a letter or space
                    if event.unicode.isalpha() or event.unicode == ' ':
                        self.input_text += event.unicode
                        print(f"Input text: {self.input_text}")  # Debug

        return True

    def update(self):
        """Update game state"""
        # Cursor blink
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update_cursor()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    print("Starting The Room Between Us...")
    interface = WoolfInterface()
    interface.run()