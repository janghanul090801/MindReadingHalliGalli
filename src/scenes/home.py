import pygame
import sys

class HomeScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # 폰트 및 색상 설정
        self.title_font = pygame.font.SysFont("malgungothic", 50, bold=True)
        self.button_font = pygame.font.SysFont("malgungothic", 28)
        
        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (240, 240, 240)
        self.COLOR_BTN = (60, 64, 67)
        self.COLOR_HOVER = (95, 99, 104)

        # 버튼 레이아웃 [영역, 텍스트, 액션명]
        btn_w, btn_h = 280, 60
        start_x = (self.width - btn_w) // 2
        
        self.buttons = [
            {"rect": pygame.Rect(start_x, 320, btn_w, btn_h), "text": "방 만들기", "action": "create"},
            {"rect": pygame.Rect(start_x, 410, btn_w, btn_h), "text": "방 찾기", "action": "find"},
            {"rect": pygame.Rect(start_x, 500, btn_w, btn_h), "text": "나가기", "action": "quit"}
        ]

    def handle_event(self, event):
        """마우스 클릭 시 해당하는 액션 딕셔너리를 리턴합니다."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for btn in self.buttons:
                if btn["rect"].collidepoint(mouse_pos):
                    if btn["action"] == "quit":
                        pygame.quit()
                        sys.exit()
                    else:
                        return {"action": btn["action"]}
        return None

    def draw(self):
        """메인 홈 화면 렌더링"""
        self.screen.fill(self.COLOR_BG)
        
        title_text = self.title_font.render("마인드리딩 할리갈리", True, self.COLOR_TEXT)
        self.screen.blit(title_text, title_text.get_rect(center=(self.width // 2, 160)))
        
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            is_hover = btn["rect"].collidepoint(mouse_pos)
            btn_color = self.COLOR_HOVER if is_hover else self.COLOR_BTN
            
            pygame.draw.rect(self.screen, btn_color, btn["rect"], border_radius=10)
            
            text_surf = self.button_font.render(btn["text"], True, self.COLOR_TEXT)
            self.screen.blit(text_surf, text_surf.get_rect(center=btn["rect"].center))