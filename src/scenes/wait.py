import os
import pygame

from src.renderers.text_renderer import TextRenderer
from src.renderers.image_renderer import ImageRenderer

class WaitScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.title_font = pygame.font.SysFont("malgungothic", 40, bold=True)
        self.sub_font = pygame.font.SysFont("malgungothic", 24)
        self.small_font = pygame.font.SysFont("malgungothic", 18)

        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (240, 240, 240)
        self.COLOR_SUB = (180, 180, 180)

        self.room_name = ""
        self.room_id = ""
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        logo_path = os.path.join(
            project_root,
            "src",
            "assets",
            "image",
            "wait_player_background.png"
        )

        self.logo_image = None
        if os.path.exists(logo_path):
            self.logo_image = pygame.image.load(logo_path).convert_alpha()

    def set_room_info(self, room_id, room_name):
        self.room_id = str(room_id)
        self.room_name = room_name

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return {"action": "go_home"}

        return None

    def draw(self):
        if self.logo_image:
            ImageRenderer.draw_center(
                self.screen,
                self.logo_image,
                center=(self.width // 2, self.height // 2),
                size=(1300, 800)
            )

        TextRenderer.draw_center(
            self.screen,
            self.sub_font,
            "다른 플레이어의 접속을 기다리는 중입니다...",
            self.COLOR_SUB,
            (self.width // 2, 450)
        )