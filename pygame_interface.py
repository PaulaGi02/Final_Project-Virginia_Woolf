import pygame
import sys
import markovify
import spacy

from scr.processes import clean_text, expand_with_vectors
from scr.voice import analyze_voice, DEFAULT_BAN_LEMMAS, build_candidates, generate_biased
from scr.pro import PROCESS_SECTIONS  # <-- your structured process content

# Pygame init
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 255, 0)
DIM_COLOR = (100, 100, 100)
CURSOR_COLOR = (0, 255, 0)

CONTROL_BAR_HEIGHT = 70
CONTROL_BAR_Y = WINDOW_HEIGHT - CONTROL_BAR_HEIGHT - 10
CONTENT_BOTTOM_Y = CONTROL_BAR_Y - 20  # hard stop for content text

PAGE_MAIN = "main"
PAGE_PROCESS = "process"

# Fonts (monospace for terminal aesthetic)
try:
    TITLE_FONT = pygame.font.SysFont("courier", 48, bold=True)
    NAME_FONT = pygame.font.SysFont("courier", 32, bold=True)
    TEXT_FONT = pygame.font.SysFont("courier", 20)
    INPUT_FONT = pygame.font.SysFont("courier", 28)
    SMALL_FONT = pygame.font.SysFont("courier", 16)
except Exception:
    TITLE_FONT = pygame.font.Font(None, 48)
    NAME_FONT = pygame.font.Font(None, 32)
    TEXT_FONT = pygame.font.Font(None, 20)
    INPUT_FONT = pygame.font.Font(None, 28)
    SMALL_FONT = pygame.font.Font(None, 16)


# Helper: simple word-wrap block
class TextBlock:
    def __init__(self, text, font, max_width, color):
        self.lines = []
        self.color = color
        words = text.split()
        current = []
        for w in words:
            test = " ".join(current + [w])
            if font.size(test)[0] <= max_width:
                current.append(w)
            else:
                if current:
                    self.lines.append(" ".join(current))
                current = [w]
        if current:
            self.lines.append(" ".join(current))

    def render(self, surface, x, y, font, line_spacing=4, max_y=None):
        cur_y = y
        for line in self.lines:
            if max_y is not None and cur_y > max_y:
                break
            surf = font.render(line, True, self.color)
            surface.blit(surf, (x, cur_y))
            cur_y += font.get_height() + line_spacing
        return cur_y


# Main UI class
class WoolfInterface:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("THE ROOM BETWEEN US")
        self.clock = pygame.time.Clock()

        # Cursor state (system cursor)
        self.current_cursor = pygame.SYSTEM_CURSOR_ARROW

        # App state
        self.page = PAGE_MAIN
        self.show_intro = True
        self.loading = False

        # Input state
        self.input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # ms

        # Generation results
        self.current_word = None
        self.clarissa_keywords = []
        self.septimus_keywords = []
        self.clarissa_output = ""
        self.septimus_output = ""
        self.clarissa_stats = None
        self.septimus_stats = None

        # Buttons
        self.process_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 150, CONTROL_BAR_Y + 15, 300, 40
        )
        self.back_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 80, CONTROL_BAR_Y + 15, 160, 40
        )

        # Process page scrolling (rendered once to a tall surface)
        self.process_scroll = 0
        self.process_surface = None
        self.process_surface_height = 0

        # Load models ONCE
        self.load_models()

    # Model loading
    def load_models(self):
        print("Loading models...")
        self.nlp = spacy.load("en_core_web_md")

        clarissa_txt = open("data/clarissa.txt", encoding="utf-8").read()
        septimus_txt = open("data/septimus.txt", encoding="utf-8").read()

        self.clarissa_text = clean_text(clarissa_txt)
        self.septimus_text = clean_text(septimus_txt)

        self.clarissa_model = markovify.Text(self.clarissa_text, state_size=2)
        self.septimus_model = markovify.Text(self.septimus_text, state_size=2)

        self.clarissa_stats = analyze_voice(
            self.clarissa_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )
        self.septimus_stats = analyze_voice(
            self.septimus_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )

        self.clarissa_candidates = build_candidates(
            self.clarissa_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )
        self.septimus_candidates = build_candidates(
            self.septimus_text, self.nlp, ban_lemmas=DEFAULT_BAN_LEMMAS
        )

        print("Models loaded!")

    # Generation
    def generate_longer_text(self, model, keywords, num_sentences=3):
        sentences = []
        for _ in range(num_sentences):
            sent = generate_biased(model, keywords, n=140)
            if sent and sent != "(no output)":
                sentences.append(sent)
        return " ".join(sentences) if sentences else "(no output)"

    def generate_from_word(self, word):
        self.loading = True
        self.current_word = word
        self.show_intro = False

        self.clarissa_keywords = expand_with_vectors(
            word, self.nlp, self.clarissa_candidates
        )
        self.septimus_keywords = expand_with_vectors(
            word, self.nlp, self.septimus_candidates
        )

        self.clarissa_output = self.generate_longer_text(
            self.clarissa_model, self.clarissa_keywords, num_sentences=3
        )
        self.septimus_output = self.generate_longer_text(
            self.septimus_model, self.septimus_keywords, num_sentences=3
        )

        self.loading = False


    # Cursor hover behavior
    def update_cursor(self):
        mouse_pos = pygame.mouse.get_pos()
        new_cursor = pygame.SYSTEM_CURSOR_ARROW

        if self.page == PAGE_MAIN and self.process_button_rect.collidepoint(mouse_pos):
            new_cursor = pygame.SYSTEM_CURSOR_HAND
        if self.page == PAGE_PROCESS and self.back_button_rect.collidepoint(mouse_pos):
            new_cursor = pygame.SYSTEM_CURSOR_HAND

        if new_cursor != self.current_cursor:
            pygame.mouse.set_cursor(new_cursor)
            self.current_cursor = new_cursor

    # Process page rendering (scrollable surface)
    def build_process_surface(self):
        """
        Render PROCESS_SECTIONS into one tall surface (document).
        Then we blit a clipped window from it based on self.process_scroll.
        """
        max_width = WINDOW_WIDTH - 140
        lines = []

        for title, body in PROCESS_SECTIONS:
            lines.append(("H1", title))
            lines.append(("SP", ""))

            for item in body:
                if item.strip() == "":
                    lines.append(("SP", ""))
                else:
                    lines.append(("P", item))

            lines.append(("SP", ""))
            lines.append(("SP", ""))

        # Wrap paragraphs to max_width
        wrapped = []
        for kind, text in lines:
            if kind in ("H1", "SP"):
                wrapped.append((kind, text))
                continue

            # wrap "P"
            words = text.split()
            current = []
            for w in words:
                test = " ".join(current + [w])
                if TEXT_FONT.size(test)[0] <= max_width:
                    current.append(w)
                else:
                    if current:
                        wrapped.append(("P", " ".join(current)))
                    current = [w]
            if current:
                wrapped.append(("P", " ".join(current)))

        # height compute
        h = 0
        for kind, _ in wrapped:
            if kind == "H1":
                h += NAME_FONT.get_height() + 10
            elif kind == "P":
                h += TEXT_FONT.get_height() + 6
            else:  # SP
                h += 12
        h = max(h, 1)

        surf = pygame.Surface((max_width, h), pygame.SRCALPHA)

        y = 0
        for kind, text in wrapped:
            if kind == "H1":
                s = NAME_FONT.render(text, True, ACCENT_COLOR)
                surf.blit(s, (0, y))
                y += NAME_FONT.get_height() + 10
            elif kind == "P":
                s = TEXT_FONT.render(text, True, TEXT_COLOR)
                surf.blit(s, (0, y))
                y += TEXT_FONT.get_height() + 6
            else:
                y += 12

        self.process_surface = surf
        self.process_surface_height = h
        self.process_scroll = 0

    def scroll_process(self, delta):
        if self.process_surface is None:
            return
        viewport_y = 140
        viewport_h = CONTENT_BOTTOM_Y - viewport_y
        max_scroll = max(0, self.process_surface_height - viewport_h)
        self.process_scroll = max(0, min(self.process_scroll + delta, max_scroll))

    def draw_scrollbar(self, viewport_rect):
        if self.process_surface is None:
            return
        content_h = self.process_surface_height
        view_h = viewport_rect.height
        if content_h <= view_h:
            return

        bar_w = 10
        bar_x = viewport_rect.right - bar_w - 4
        bar_y = viewport_rect.y + 4
        bar_h = viewport_rect.height - 8

        # track
        pygame.draw.rect(self.screen, DIM_COLOR, (bar_x, bar_y, bar_w, bar_h), 1)

        # thumb
        thumb_h = max(30, int(bar_h * (view_h / content_h)))
        max_scroll = content_h - view_h
        ratio = self.process_scroll / max_scroll if max_scroll > 0 else 0.0
        thumb_y = bar_y + int((bar_h - thumb_h) * ratio)

        pygame.draw.rect(self.screen, ACCENT_COLOR, (bar_x + 1, thumb_y, bar_w - 2, thumb_h), 0)

    # Drawing: common UI elements
    def draw_scanlines(self):
        for y in range(0, WINDOW_HEIGHT, 4):
            pygame.draw.line(self.screen, (10, 10, 10), (0, y), (WINDOW_WIDTH, y), 1)

    def draw_border(self):
        border_w = 2
        pygame.draw.rect(
            self.screen, TEXT_COLOR,
            (10, 10, WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20),
            border_w
        )
        corner_size = 20
        corners = [
            (10, 10), (WINDOW_WIDTH - 30, 10),
            (10, WINDOW_HEIGHT - 30), (WINDOW_WIDTH - 30, WINDOW_HEIGHT - 30)
        ]
        for cx, cy in corners:
            pygame.draw.rect(self.screen, ACCENT_COLOR, (cx, cy, corner_size, corner_size), border_w)

    def draw_title(self):
        title = TITLE_FONT.render("THE ROOM BETWEEN US", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))

        subtitle = SMALL_FONT.render(
            "MRS DALLOWAY :: VOICE SIMULATION ENGINE :: 1925", True, ACCENT_COLOR
        )
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 85)))

        pygame.draw.line(self.screen, DIM_COLOR, (30, 110), (WINDOW_WIDTH - 30, 110), 1)

    def draw_control_bar(self):
        pygame.draw.rect(self.screen, BG_COLOR, (0, CONTROL_BAR_Y, WINDOW_WIDTH, CONTROL_BAR_HEIGHT))
        pygame.draw.line(self.screen, DIM_COLOR, (30, CONTROL_BAR_Y), (WINDOW_WIDTH - 30, CONTROL_BAR_Y), 1)

    def draw_button(self, rect, label, active=True):
        border_color = ACCENT_COLOR if active else DIM_COLOR
        pygame.draw.rect(self.screen, border_color, rect, 2)
        text_surf = SMALL_FONT.render(label, True, border_color)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def draw_input_area(self):
        y_pos = 130
        prompt = TEXT_FONT.render(">", True, ACCENT_COLOR)
        self.screen.blit(prompt, (40, y_pos))

        input_display = INPUT_FONT.render(self.input_text, True, TEXT_COLOR)
        self.screen.blit(input_display, (70, y_pos - 2))

        if self.cursor_visible:
            cursor_x = 70 + INPUT_FONT.size(self.input_text)[0]
            cursor = INPUT_FONT.render("_", True, CURSOR_COLOR)
            self.screen.blit(cursor, (cursor_x, y_pos - 2))

        if self.show_intro:
            instructions = [
                "ENTER A WORD TO EXPLORE THE SEMANTIC DIVIDE",
                "PRESS [RETURN] TO EXECUTE :: [ESC] TO EXIT"
            ]
            inst_y = y_pos + 50
            for inst in instructions:
                inst_surf = SMALL_FONT.render(inst, True, DIM_COLOR)
                self.screen.blit(inst_surf, inst_surf.get_rect(center=(WINDOW_WIDTH // 2, inst_y)))
                inst_y += 25

    def draw_divider(self):
        y_start = 200
        x_center = WINDOW_WIDTH // 2
        for y in range(y_start, CONTENT_BOTTOM_Y, 10):
            pygame.draw.line(self.screen, DIM_COLOR, (x_center, y), (x_center, y + 5), 1)

    def draw_voice_panel(self, x, y, name, keywords, output, stats):
        current_y = y
        max_y = CONTENT_BOTTOM_Y

        # header
        name_surf = NAME_FONT.render(f"[{name}]", True, ACCENT_COLOR)
        self.screen.blit(name_surf, (x, current_y))
        current_y += 40

        # stats
        if stats and current_y < max_y:
            stat_text = f"AVG SENTENCE LENGTH: {stats.mean_sent_len:.1f}"
            stat_surf = SMALL_FONT.render(stat_text, True, DIM_COLOR)
            self.screen.blit(stat_surf, (x, current_y))
            current_y += 25

        # keywords
        if keywords and self.current_word and current_y < max_y:
            kw_label = SMALL_FONT.render("SEMANTIC FIELD:", True, DIM_COLOR)
            self.screen.blit(kw_label, (x, current_y))
            current_y += 20

            kw_text = " ".join(keywords[:8])
            kw_block = TextBlock(kw_text, SMALL_FONT, 500, ACCENT_COLOR)
            current_y = kw_block.render(self.screen, x, current_y, SMALL_FONT, line_spacing=3, max_y=max_y)
            current_y += 25

        # output
        if output and output != "(no output)" and current_y < max_y:
            out_label = SMALL_FONT.render("OUTPUT:", True, DIM_COLOR)
            self.screen.blit(out_label, (x, current_y))
            current_y += 25

            text_block = TextBlock(output, TEXT_FONT, 500, TEXT_COLOR)
            text_block.render(self.screen, x, current_y, TEXT_FONT, line_spacing=6, max_y=max_y)


    # Page drawing
    def draw_process_page(self):
        self.draw_title()

        if self.process_surface is None:
            self.build_process_surface()

        viewport_x = 60
        viewport_y = 140
        viewport_w = WINDOW_WIDTH - 120
        viewport_h = CONTENT_BOTTOM_Y - viewport_y

        viewport = pygame.Rect(viewport_x, viewport_y, viewport_w, viewport_h)

        # clip to viewport
        self.screen.set_clip(viewport)
        self.screen.blit(self.process_surface, (viewport_x, viewport_y - self.process_scroll))
        self.screen.set_clip(None)

        pygame.draw.rect(self.screen, DIM_COLOR, viewport, 1)
        self.draw_scrollbar(viewport)

        # control bar + back button on top
        self.draw_control_bar()
        self.draw_button(self.back_button_rect, "BACK [ESC]")

    def draw_main_page(self):
        self.draw_title()
        self.draw_input_area()

        if not self.show_intro:
            self.draw_divider()
            self.draw_voice_panel(
                x=50, y=200, name="CLARISSA",
                keywords=self.clarissa_keywords,
                output=self.clarissa_output,
                stats=self.clarissa_stats
            )
            self.draw_voice_panel(
                x=WINDOW_WIDTH // 2 + 50, y=200, name="SEPTIMUS",
                keywords=self.septimus_keywords,
                output=self.septimus_output,
                stats=self.septimus_stats
            )

        if self.loading:
            loading_text = TEXT_FONT.render("PROCESSING...", True, ACCENT_COLOR)
            self.screen.blit(loading_text, loading_text.get_rect(center=(WINDOW_WIDTH // 2, CONTROL_BAR_Y - 18)))

        # control bar + process button on top
        self.draw_control_bar()
        self.draw_button(self.process_button_rect, "PROCESS / METHOD")

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_scanlines()
        self.draw_border()

        if self.page == PAGE_PROCESS:
            self.draw_process_page()
        else:
            self.draw_main_page()

        pygame.display.flip()

    # -----------------------------
    # Event handling
    # -----------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # mouse wheel scroll (process page)
            if event.type == pygame.MOUSEWHEEL:
                if self.page == PAGE_PROCESS:
                    self.scroll_process(-event.y * 40)

            # mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if self.page == PAGE_MAIN and self.process_button_rect.collidepoint((mx, my)):
                    self.page = PAGE_PROCESS
                    if self.process_surface is None:
                        self.build_process_surface()
                    self.process_scroll = 0
                    return True
                self.update_cursor()

                if self.page == PAGE_PROCESS and self.back_button_rect.collidepoint((mx, my)):
                    self.page = PAGE_MAIN
                    return True

            # keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.page == PAGE_PROCESS:
                        self.page = PAGE_MAIN
                        return True
                    return False

                # process page scroll keys
                if self.page == PAGE_PROCESS:
                    if event.key == pygame.K_DOWN:
                        self.scroll_process(40)
                    elif event.key == pygame.K_UP:
                        self.scroll_process(-40)
                    elif event.key == pygame.K_PAGEDOWN:
                        self.scroll_process(200)
                    elif event.key == pygame.K_PAGEUP:
                        self.scroll_process(-200)
                    continue  # don't type into input while on process page
                self.update_cursor()

                # main page typing
                if event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        try:
                            self.generate_from_word(self.input_text.strip())
                            self.input_text = ""
                        except Exception as e:
                            print("ERROR during generation:", repr(e))
                            self.loading = False

                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]

                else:
                    if event.unicode.isalpha() or event.unicode == " ":
                        self.input_text += event.unicode

        return True

    # Update loop
    def update(self):
        # blink cursor in input field
        self.cursor_timer += self.clock.get_time()
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def run(self):
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
    WoolfInterface().run()
