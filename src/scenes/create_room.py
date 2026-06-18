import os
import pygame

from src.renderers.ui_renderer import UIRenderer
from src.renderers.text_renderer import TextRenderer
from src.renderers.image_renderer import ImageRenderer


class CreateRoomScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.title_font = pygame.font.SysFont("malgungothic", 40, bold=True)
        self.label_font = pygame.font.SysFont("malgungothic", 20)
        self.input_font = pygame.font.SysFont("malgungothic", 24)
        self.button_font = pygame.font.SysFont("malgungothic", 24)

        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (30, 32, 34)
        self.COLOR_BTN = (243, 183, 13)
        self.COLOR_HOVER = (255, 214, 46)
        self.COLOR_SUBMIT = (254, 220, 29)
        self.COLOR_SUBMIT_HOVER = (255, 241, 118)
        self.COLOR_INPUT_BG = (45, 49, 52)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        logo_path = os.path.join(
            project_root,
            "src",
            "assets",
            "image",
            "create_room_background.png"
        )

        self.logo_image = None
        if os.path.exists(logo_path):
            self.logo_image = pygame.image.load(logo_path).convert_alpha()

        
        self.offset_X = 400

        self.input_rect = pygame.Rect((self.width - 400) // 2 + self.offset_X, 350, 400, 50)
        self.input_text = ""
        self.is_active = False
        self.max_chars = 15

        btn_w, btn_h = 180, 55
        self.back_btn_rect = pygame.Rect((self.width // 2) - btn_w - 20 + self.offset_X, 500, btn_w, btn_h)
        self.submit_btn_rect = pygame.Rect((self.width // 2) + 20 + self.offset_X, 500, btn_w, btn_h)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.input_rect.collidepoint(event.pos)

            if self.back_btn_rect.collidepoint(event.pos):
                return {"action": "go_home"}

            if self.submit_btn_rect.collidepoint(event.pos):
                return self.submit()

        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]

            elif event.key == pygame.K_RETURN:
                return self.submit()

            elif event.unicode and event.unicode.isprintable():
                if len(self.input_text) < self.max_chars:
                    self.input_text += event.unicode

        return None

    def submit(self):
        room_name = self.input_text.strip()

        if not room_name:
            return None

        return {
            "action": "submit_create_room",
            "room_name": room_name
        }

    def draw(self):
        ImageRenderer.draw_center(
            self.screen,
            self.logo_image,
            center=(self.width // 2, self.height // 2),
            size=(1300, 800)
        )

        UIRenderer.draw_input_box(
            self.screen,
            self.input_rect,
            self.input_text,
            self.input_font,
            self.is_active,
            (255, 255, 255),
            self.COLOR_INPUT_BG,
            (66, 153, 225),
            (100, 100, 100),
            placeholder="제목을 입력하세요..."
        )

        UIRenderer.draw_button(
            self.screen,
            self.back_btn_rect,
            "뒤로가기",
            self.button_font,
            self.COLOR_BTN,
            self.COLOR_HOVER,
            self.COLOR_TEXT
        )

        UIRenderer.draw_button(
            self.screen,
            self.submit_btn_rect,
            "방 만들기",
            self.button_font,
            self.COLOR_SUBMIT,
            self.COLOR_SUBMIT_HOVER,
            self.COLOR_TEXT
        )