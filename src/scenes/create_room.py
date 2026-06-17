import pygame

class CreateRoomScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        self.title_font = pygame.font.SysFont("malgungothic", 40, bold=True)
        self.label_font = pygame.font.SysFont("malgungothic", 20)
        self.input_font = pygame.font.SysFont("malgungothic", 24)
        self.button_font = pygame.font.SysFont("malgungothic", 24)
        
        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (240, 240, 240)
        self.COLOR_BTN = (60, 64, 67)
        self.COLOR_HOVER = (95, 99, 104)
        self.COLOR_SUBMIT = (43, 108, 176)
        self.COLOR_SUBMIT_HOVER = (66, 153, 225)
        
        # 인풋 상자 및 버튼 영역 정의
        self.input_rect = pygame.Rect((self.width - 400) // 2, 350, 400, 50)
        self.input_text = ""
        self.is_active = False
        self.max_chars = 15
        
        btn_w, btn_h = 180, 55
        self.back_btn_rect = pygame.Rect((self.width // 2) - btn_w - 20, 500, btn_w, btn_h)
        self.submit_btn_rect = pygame.Rect((self.width // 2) + 20, 500, btn_w, btn_h)

    def handle_event(self, event):
        """방 만들기 화면의 마우스 및 키보드 입력을 처리합니다."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            if self.input_rect.collidepoint(mouse_pos):
                self.is_active = True
            else:
                self.is_active = False
                
            if self.back_btn_rect.collidepoint(mouse_pos):
                return {"action": "go_home"}
                
            if self.submit_btn_rect.collidepoint(mouse_pos):
                if self.input_text.strip() != "":
                    return {"action": "submit_create_room", "room_name": self.input_text.strip()}

        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.input_text.strip() != "":
                    return {"action": "submit_create_room", "room_name": self.input_text.strip()}
            else:
                if len(self.input_text) < self.max_chars and event.unicode.isprintable():
                    self.input_text += event.unicode
                    
        return None

    def draw(self):
        """방 만들기 화면 렌더링"""
        self.screen.fill(self.COLOR_BG)
        
        title_surf = self.title_font.render("새로운 방 만들기", True, self.COLOR_TEXT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, 160)))
        
        label_surf = self.label_font.render("방 제목 입력", True, (150, 150, 150))
        self.screen.blit(label_surf, (self.input_rect.x, self.input_rect.y - 30))
        
        border_color = (66, 153, 225) if self.is_active else (100, 100, 100)
        pygame.draw.rect(self.screen, (45, 49, 52), self.input_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, self.input_rect, width=2, border_radius=5)
        
        if self.input_text == "" and not self.is_active:
            text_surf = self.input_font.render("제목을 입력하세요...", True, (100, 100, 100))
        else:
            text_surf = self.input_font.render(self.input_text, True, self.COLOR_TEXT)
        self.screen.blit(text_surf, (self.input_rect.x + 15, self.input_rect.y + (self.input_rect.h - text_surf.get_height()) // 2))
        
        mouse_pos = pygame.mouse.get_pos()
        
        back_color = self.COLOR_HOVER if self.back_btn_rect.collidepoint(mouse_pos) else self.COLOR_BTN
        pygame.draw.rect(self.screen, back_color, self.back_btn_rect, border_radius=8)
        back_text = self.button_font.render("뒤로가기", True, self.COLOR_TEXT)
        self.screen.blit(back_text, back_text.get_rect(center=self.back_btn_rect.center))
        
        submit_color = self.COLOR_SUBMIT_HOVER if self.submit_btn_rect.collidepoint(mouse_pos) else self.COLOR_SUBMIT
        pygame.draw.rect(self.screen, submit_color, self.submit_btn_rect, border_radius=8)
        submit_text = self.button_font.render("방 만들기", True, self.COLOR_TEXT)
        self.screen.blit(submit_text, submit_text.get_rect(center=self.submit_btn_rect.center))