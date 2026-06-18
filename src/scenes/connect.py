import pygame

from src.renderers.ui_renderer import UIRenderer
from src.renderers.text_renderer import TextRenderer
from src.utilities.clipboard import get_clipboard_text


class ConnectScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.font = pygame.font.SysFont("malgungothic", 24)
        self.title_font = pygame.font.SysFont("malgungothic", 34, bold=True)

        self.input_rect = pygame.Rect((self.width - 440) // 2, 350, 440, 45)
        self.btn_rect = pygame.Rect((self.width - 200) // 2, 450, 200, 50)

        self.address_text = "localhost:8080"
        self.is_active = True
        self.max_chars = 80

        self.COLOR_BG = (240, 240, 240)
        self.COLOR_TEXT = (50, 50, 50)
        self.COLOR_INPUT_BG = (255, 255, 255)
        self.COLOR_ACTIVE = (70, 150, 230)
        self.COLOR_INACTIVE = (180, 180, 180)
        self.COLOR_BTN = (50, 150, 50)
        self.COLOR_BTN_HOVER = (70, 180, 70)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.input_rect.collidepoint(event.pos)

            if self.btn_rect.collidepoint(event.pos):
                return self.submit()

        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META):
                self.address_text += get_clipboard_text()
                self.address_text = self.address_text[:self.max_chars]
                return None

            if event.key == pygame.K_BACKSPACE:
                self.address_text = self.address_text[:-1]

            elif event.key == pygame.K_RETURN:
                return self.submit()

            elif event.unicode and event.unicode.isprintable():
                if len(self.address_text) < self.max_chars:
                    self.address_text += event.unicode

        return None

    def submit(self):
        address = self.address_text.strip()

        if not address:
            address = "localhost:8080"

        return {
            "action": "submit_connect",
            "address": address
        }

    def draw(self):
        self.screen.fill(self.COLOR_BG)

        TextRenderer.draw_center(
            self.screen,
            self.title_font,
            "서버 접속",
            self.COLOR_TEXT,
            (self.width // 2, 250)
        )

        TextRenderer.draw_left(
            self.screen,
            self.font,
            "접속할 서버 주소(URL)를 입력하세요 (Ctrl+V 지원)",
            self.COLOR_TEXT,
            (self.input_rect.x, self.input_rect.y - 40)
        )

        UIRenderer.draw_input_box(
            self.screen,
            self.input_rect,
            self.address_text,
            self.font,
            self.is_active,
            (0, 0, 0),
            self.COLOR_INPUT_BG,
            self.COLOR_ACTIVE,
            self.COLOR_INACTIVE,
            placeholder="localhost:8080"
        )

        UIRenderer.draw_button(
            self.screen,
            self.btn_rect,
            "서버 접속",
            self.font,
            self.COLOR_BTN,
            self.COLOR_BTN_HOVER,
            (255, 255, 255)
        )