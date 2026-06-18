import os
import pygame

from src.renderers.ui_renderer import UIRenderer
from src.renderers.text_renderer import TextRenderer
from src.renderers.image_renderer import ImageRenderer

class FindRoomScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.title_font = pygame.font.SysFont("malgungothic", 40, bold=True)
        self.item_font = pygame.font.SysFont("malgungothic", 22)
        self.btn_font = pygame.font.SysFont("malgungothic", 24)
        self.empty_font = pygame.font.SysFont("malgungothic", 22)

        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (30, 32, 34)
        self.COLOR_BTN = (254, 220, 29)
        self.COLOR_HOVER = (255, 241, 118)
        self.COLOR_PANEL = (45, 49, 52)

        self.back_btn_rect = pygame.Rect(30, 30, 140, 50)
        self.scroll_rect = pygame.Rect(100, 150, 600, 550)

        self.scroll_y = 0
        self.rooms = []
        self.room_buttons = []

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        logo_path = os.path.join(
            project_root,
            "src",
            "assets",
            "image",
            "find_room_background.png"
        )

        self.logo_image = None
        if os.path.exists(logo_path):
            self.logo_image = pygame.image.load(logo_path).convert_alpha()

    def update_room_list(self, rooms_data):
        self.rooms = rooms_data or []
        self.scroll_y = 0

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn_rect.collidepoint(mouse_pos):
                return {"action": "go_home"}

            if self.scroll_rect.collidepoint(mouse_pos):
                for btn in self.room_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        return {
                            "action": "submit_join_room",
                            "room_id": btn["room_id"]
                        }

        if event.type == pygame.MOUSEWHEEL:
            if self.scroll_rect.collidepoint(mouse_pos):
                self.scroll_y += event.y * 35
                self.clamp_scroll()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return {"action": "go_home"}

        return None

    def clamp_scroll(self):
        item_h = 70
        gap = 15

        content_height = len(self.rooms) * (item_h + gap)
        viewport_height = self.scroll_rect.height - 10

        if content_height <= viewport_height:
            self.scroll_y = 0
            return

        min_scroll = -(content_height - viewport_height)
        self.scroll_y = max(min(self.scroll_y, 0), min_scroll)

    def draw_room_list(self):
        # --- 1. 스크롤 영역 크기 축소 및 중앙 배치 설정 ---
        # 1300x800 화면 기준으로 높이를 줄이고 정확히 정중앙에 배치합니다.
        screen_w, screen_h = self.screen.get_size()
        
        # 원하는 크기 설정 (높이를 기존보다 축소)
        new_width = 500
        new_height = 430  
        
        # 중앙 좌표 계산 후 self.scroll_rect 업데이트
        self.scroll_rect.width = new_width
        self.scroll_rect.height = new_height
        self.scroll_rect.x = (screen_w - new_width) // 2
        self.scroll_rect.y = (screen_h - new_height) // 2 + 100

        # --- 2. 색상 정의 (그림판 노란색 감성 테마) ---
        COLOR_YELLOW_BG = (255, 248, 220)      # 부드러운 연노랑 패널 배경
        COLOR_YELLOW_BORDER = (254, 220, 29)  # 쨍한 메인 노란색 테두리
        
        COLOR_BTN_NORMAL = (243, 183, 13)     # 궁예 옷 느낌의 개나리색 버튼
        COLOR_BTN_HOVER = (255, 214, 46)      # 마우스 올렸을 때 밝은 노란색
        
        COLOR_TEXT_DARK = (40, 40, 40)        # 밝은 배경 위에 쓸 어두운 글자색

        # 배경 패널 그리기
        pygame.draw.rect(self.screen, COLOR_YELLOW_BG, self.scroll_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_YELLOW_BORDER, self.scroll_rect, width=3, border_radius=10)

        # 방이 없을 때 예외 처리
        if not self.rooms:
            TextRenderer.draw_center(
                self.screen,
                self.empty_font,
                "현재 개설된 방이 없습니다",
                (120, 120, 120),
                self.scroll_rect.center
            )
            return

        # 서피스 생성
        list_surf = pygame.Surface(
            (self.scroll_rect.width - 10, self.scroll_rect.height - 10),
            pygame.SRCALPHA
        )

        self.room_buttons = []
        item_h = 60 # 리스트 높이도 살짝 콤팩트하게 조절
        gap = 12
        mouse_pos = pygame.mouse.get_pos()

        for i, room in enumerate(self.rooms):
            item_y = i * (item_h + gap) + self.scroll_y

            if item_y + item_h < 0 or item_y > self.scroll_rect.height:
                continue

            actual_rect = pygame.Rect(
                self.scroll_rect.x + 5,
                self.scroll_rect.y + 5 + item_y,
                self.scroll_rect.width - 10,
                item_h
            )

            self.room_buttons.append({
                "rect": actual_rect,
                "room_id": room.get("id")
            })

            # 호버 상태에 따른 노란색 변경 적용
            is_hover = actual_rect.collidepoint(mouse_pos)
            bg_color = COLOR_BTN_HOVER if is_hover else COLOR_BTN_NORMAL

            local_rect = pygame.Rect(5, item_y, self.scroll_rect.width - 20, item_h)
            pygame.draw.rect(list_surf, bg_color, local_rect, border_radius=8)
            # 버튼에도 테두리를 주어 그림판/카툰 느낌 강조
            pygame.draw.rect(list_surf, COLOR_YELLOW_BORDER, local_rect, width=2, border_radius=8)

            room_id = room.get("id", "?")
            room_name = room.get("name", "이름 없는 방")
            player_count = room.get("player_count", 0)

            info_text = f"[{room_id}]  {room_name}"
            count_text = f"{player_count} / 2"

            # 글자색을 어두운 톤(COLOR_TEXT_DARK)으로 적용하여 가독성 확보
            txt_surf = self.item_font.render(info_text, True, COLOR_TEXT_DARK)
            
            # 인원 수 컬러 (1명일 땐 대기 상태를 뜻하는 초록, 다 찼을 땐 빨강)
            cnt_color = (0, 150, 0) if player_count == 1 else (200, 30, 30)
            cnt_surf = self.item_font.render(count_text, True, cnt_color)

            list_surf.blit(txt_surf, (20, item_y + (item_h - txt_surf.get_height()) // 2))
            list_surf.blit(
                cnt_surf,
                (self.scroll_rect.width - 100, item_y + (item_h - cnt_surf.get_height()) // 2)
            )

        self.screen.blit(list_surf, (self.scroll_rect.x + 5, self.scroll_rect.y + 5))

    def draw(self):
        ImageRenderer.draw_center(
            self.screen,
            self.logo_image,
            center=(self.width // 2, self.height // 2),
            size=(1300, 800)
        )

        UIRenderer.draw_button(
            self.screen,
            self.back_btn_rect,
            "뒤로가기",
            self.btn_font,
            self.COLOR_BTN,
            self.COLOR_HOVER,
            self.COLOR_TEXT
        )

        self.draw_room_list()