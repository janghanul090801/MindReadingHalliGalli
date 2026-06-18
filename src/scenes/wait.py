import pygame

from src.renderers.text_renderer import TextRenderer


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

    def set_room_info(self, room_id, room_name):
        self.room_id = str(room_id)
        self.room_name = room_name

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return {"action": "go_home"}

        return None

    def draw(self):
        self.screen.fill(self.COLOR_BG)

        TextRenderer.draw_center(
            self.screen,
            self.title_font,
            f"[{self.room_id}번방] {self.room_name}",
            self.COLOR_TEXT,
            (self.width // 2, 250)
        )

        TextRenderer.draw_center(
            self.screen,
            self.sub_font,
            "다른 플레이어의 접속을 기다리는 중입니다...",
            self.COLOR_SUB,
            (self.width // 2, 450)
        )

        TextRenderer.draw_center(
            self.screen,
            self.small_font,
            "ESC를 누르면 홈으로 돌아갑니다",
            (120, 120, 120),
            (self.width // 2, 520)
        )