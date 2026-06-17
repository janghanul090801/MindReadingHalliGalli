import pygame

class FindRoomScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        self.title_font = pygame.font.SysFont("malgungothic", 40, bold=True)
        self.item_font = pygame.font.SysFont("malgungothic", 22)
        self.btn_font = pygame.font.SysFont("malgungothic", 24)
        
        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (240, 240, 240)
        self.COLOR_BTN = (60, 64, 67)
        self.COLOR_HOVER = (95, 99, 104)
        
        # 뒤로가기 버튼 영역
        self.back_btn_rect = pygame.Rect(30, 30, 140, 50)
        
        # 방 리스트가 그려질 스크롤 뷰포트 영역 (중앙에 배치)
        self.scroll_rect = pygame.Rect(100, 150, 600, 550)
        self.scroll_y = 0  # 스크롤 이동 변수
        
        # 서버에서 받아올 방 리스트 저장 공간
        # 각 항목 서식: {"id": 1, "name": "방제목", "player_count": 1}
        self.rooms = []
        
        # 마우스 오버 처리를 위해 실시간 생성되는 방 버튼들의 위치 저장용 list
        self.room_buttons = []

    def update_room_list(self, rooms_data):
        """run.py의 서버 통신단으로부터 수신된 최신 방 목록을 업데이트합니다."""
        self.rooms = rooms_data

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # 1. 마우스 클릭 이벤트
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 뒤로가기 버튼 클릭 시
            if self.back_btn_rect.collidepoint(mouse_pos):
                return {"action": "go_home"}
                
            # 스크롤 뷰포트 안의 특정 방을 클릭했는지 검사
            if self.scroll_rect.collidepoint(mouse_pos):
                for btn in self.room_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        print(f"[FindRoom] 방 선택됨 -> ID: {btn['room_id']}")
                        return {"action": "submit_join_room", "room_id": btn["room_id"]}
                        
        # 2. 마우스 휠 스크롤 이벤트 (스크롤 박스 영역 내에서만 작동)
        if event.type == pygame.MOUSEBUTTONDOWN and self.scroll_rect.collidepoint(mouse_pos):
            if event.button == 4:  # 휠 업
                self.scroll_y = min(0, self.scroll_y + 30)
            elif event.button == 5:  # 휠 다운
                # 전체 리스트가 화면 높이보다 길 때만 아래로 스크롤 가능하게 제한 가능
                self.scroll_y -= 30
                
        return None

    def draw(self):
        self.screen.fill(self.COLOR_BG)
        
        # 1. 상단 UI (뒤로가기 & 타이틀)
        mouse_pos = pygame.mouse.get_pos()
        back_color = self.COLOR_HOVER if self.back_btn_rect.collidepoint(mouse_pos) else self.COLOR_BTN
        pygame.draw.rect(self.screen, back_color, self.back_btn_rect, border_radius=8)
        back_text = self.btn_font.render("뒤로가기", True, self.COLOR_TEXT)
        self.screen.blit(back_text, back_text.get_rect(center=self.back_btn_rect.center))
        
        title_surf = self.title_font.render("개설된 방 목록", True, self.COLOR_TEXT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, 60)))
        
        # 2. 방 리스트 구역 테두리 그리기
        pygame.draw.rect(self.screen, (45, 49, 52), self.scroll_rect, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), self.scroll_rect, width=2, border_radius=10)
        
        # 3. 스크롤 영역 클리핑 시스템 서피스 생성
        # 스크롤 뷰포트 내부 크기만큼의 임시 서피스를 만들어 그 위에 그린 뒤 blit 처리함
        list_surf = pygame.Surface((self.scroll_rect.width - 10, self.scroll_rect.height - 10), pygame.SRCALPHA)
        
        self.room_buttons = [] # 매 프레임 좌표 갱신을 위해 초기화
        
        item_h = 70
        gap = 15
        
        for i, room in enumerate(self.rooms):
            # 아이템이 배치될 Y 절대 좌표 (스크롤 오프셋 반영)
            item_y = i * (item_h + gap) + self.scroll_y
            
            # 클리핑 영역 밖을 벗어난 아이템은 연산 및 드로우 생략 (최적화)
            if item_y + item_h < 0 or item_y > self.scroll_rect.height:
                continue
                
            # 화면상의 실질적인 충돌 감지용 마우스 Rect 연산 (서피스 상대 좌표 -> 메인 창 절대 좌표)
            actual_rect = pygame.Rect(self.scroll_rect.x + 5, self.scroll_rect.y + 5 + item_y, self.scroll_rect.width - 10, item_h)
            self.room_buttons.append({"rect": actual_rect, "room_id": room["id"]})
            
            # 마우스 호버 시 강조 색상 변경
            is_hover = actual_rect.collidepoint(mouse_pos)
            bg_color = (80, 85, 90) if is_hover else (55, 59, 62)
            
            # 리스트 아이템 배경 사각형 그리기
            pygame.draw.rect(list_surf, bg_color, (5, item_y, self.scroll_rect.width - 20, item_h), border_radius=8)
            
            # 방 정보 텍스트 그리기
            info_text = f" [{room['id']}]  {room['name']}"
            count_text = f"{room['player_count']} / 2 "
            
            txt_surf = self.item_font.render(info_text, True, self.COLOR_TEXT)
            cnt_surf = self.item_font.render(count_text, True, (0, 255, 0) if room['player_count'] == 1 else (255, 0, 0))
            
            list_surf.blit(txt_surf, (20, item_y + (item_h - txt_surf.get_height()) // 2))
            list_surf.blit(cnt_surf, (self.scroll_rect.width - 100, item_y + (item_h - cnt_surf.get_height()) // 2))

        # 임시 서피스를 메인 윈도우 스크롤 존에 얹기
        self.screen.blit(list_surf, (self.scroll_rect.x + 5, self.scroll_rect.y + 5))