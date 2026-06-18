import os
import pygame

from src.renderers.image_renderer import ImageRenderer

class HomeScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.button_font = pygame.font.SysFont("malgungothic", 28)

        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (30, 32, 34)
        self.COLOR_BTN = (254, 220, 29)
        self.COLOR_HOVER = (255, 241, 118)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        logo_path = os.path.join(
            project_root,
            "src",
            "assets",
            "image",
            "home_background.png"
        )

        self.logo_image = None
        if os.path.exists(logo_path):
            self.logo_image = pygame.image.load(logo_path).convert_alpha()

        btn_w, btn_h = 280, 60
        start_x = (self.width - btn_w) // 2 + 450

        self.buttons = [
            {"rect": pygame.Rect(start_x, 320, btn_w, btn_h), "text": "방 만들기", "action": "create"},
            {"rect": pygame.Rect(start_x, 410, btn_w, btn_h), "text": "방 찾기", "action": "find"},
            {"rect": pygame.Rect(start_x, 500, btn_w, btn_h), "text": "나가기", "action": "quit"}
        ]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    return {"action": btn["action"]}

        return None

    def draw(self):
        from src.renderers.ui_renderer import UIRenderer
        from src.renderers.text_renderer import TextRenderer

        self.screen.fill(self.COLOR_BG)

        if self.logo_image:
            ImageRenderer.draw_center(
                self.screen,
                self.logo_image,
                center=(self.width // 2, self.height // 2),
                size=(1300, 800)
            )

        for btn in self.buttons:
            UIRenderer.draw_button(
                self.screen,
                btn["rect"],
                btn["text"],
                self.button_font,
                self.COLOR_BTN,
                self.COLOR_HOVER,
                self.COLOR_TEXT,
                border_radius=10
            )