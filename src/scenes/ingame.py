import pygame
import sys
# from src.models.bell import Bell # 아까 만든 Bell 클래스 위치에 맞게 임포트
from src.components.bell import Bell
from src.components.card import Card

class InGameScene:
    def __init__(self, screen, on_ring_server_func):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # 1. 중앙 종(Bell) 배치 (원형 클릭 영역)
        bell_size = 90
        bell_rect = pygame.Rect((self.width - bell_size) // 2, (self.height - bell_size) // 2, bell_size, bell_size)
        self.bell = Bell(bell_rect, on_ring_callback=on_ring_server_func)
        
        # 2. 폰트 및 색상 설정
        self.font_title = pygame.font.SysFont("malgungothic", 24, bold=True)
        self.font_info = pygame.font.SysFont("malgungothic", 20)
        
        self.COLOR_BG = (34, 112, 63)     # 보드게임 매트 느낌의 초록색
        self.COLOR_CARD_BACK = (180, 50, 50) # 카드 뒷면 (붉은 덱)
        self.COLOR_TEXT = (255, 255, 255)
        
        # 3. 데이터 바인딩용 변수 (run.py에서 실시간 데이터 매핑 예정)
        self.my_name = "나"
        self.my_cards_count = 0
        self.my_top_card = None  # 내 오픈 더미의 가장 위 카드 객체
        
        self.opp_name = "상대방"
        self.opp_cards_count = 0
        self.opp_top_card = None # 상대 오픈 더미의 가장 위 카드 객체
        
        # 4. 카드 및 오픈 더미가 그려질 2D 좌표 구역 정의 (배치 설계도)
        card_w, card_h = 120, 180
        cx = self.width // 2
        
        # [내 구역 (하단)]
        self.my_deck_rect = pygame.Rect(cx - card_w - 30, self.height - card_h - 40, card_w, card_h)
        self.my_pile_rect = pygame.Rect(cx + 30, self.height - card_h - 40, card_w, card_h)
        
        # [상대 구역 (상단)]
        self.opp_pile_rect = pygame.Rect(cx - card_w - 30, 40, card_w, card_h)
        self.opp_deck_rect = pygame.Rect(cx + 30, 40, card_w, card_h)

    def update_data(self, my_count, my_top, opp_count, opp_top):
        """run.py에서 서버 데이터를 받아 매 프레임 동기화하는 함수"""
        self.my_cards_count = my_count
        self.my_top_card = my_top
        self.opp_cards_count = opp_count
        self.opp_top_card = opp_top

    def handle_event(self, event):
        # 마우스로 중앙 종 클릭 감지
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.bell.rect.collidepoint(event.pos):
                self.bell.ring()
                return None
                
        # 키보드 핫키 처리 (스페이스: 카드 뽑기 / 엔터: 종 치기)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return {"action": "submit_draw"}
            elif event.key == pygame.K_RETURN:
                self.bell.ring()
                return None
                
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.bell.is_pressed = False
            
        return None

    def draw_card_sprite(self, rect, card_obj, is_deck=False):
        """카드를 화면에 이쁘게 그려주는 헬퍼 함수 (이미지 렌더링 반영)"""
        if is_deck:
            # 뒤집혀 있는 플레이어 덱 (카드 뒷면)
            pygame.draw.rect(self.screen, self.COLOR_CARD_BACK, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2, border_radius=10)
            return

        if card_obj is None:
            # 바닥에 오픈된 카드가 없을 때 가이드 점선 처리
            pygame.draw.rect(self.screen, (20, 80, 40), rect, width=2, border_radius=10)
        else:
            # 카드가 오픈되었을 때 기본 흰 배경 먼저 깔기
            pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=10)
            
            # ★ 카드 내부 이미지가 성공적으로 로드되었다면 이미지 그리기
            if card_obj.image:
                # 크기를 카드 Rect(120x180)에 맞게 조절하여 blit
                scaled_image = pygame.transform.smoothscale(card_obj.image, (rect.width, rect.height))
                self.screen.blit(scaled_image, rect.topleft)
            else:
                # 이미지 로드 실패 시 대체용 텍스트 출력 (백업용)
                txt_fruit = self.font_info.render(f"{card_obj.getFruit()}", True, (0, 0, 0))
                txt_qty = self.font_title.render(f"{card_obj.getQuantity()}", True, (255, 0, 0))
                self.screen.blit(txt_fruit, txt_fruit.get_rect(center=(rect.centerx, rect.centery - 20)))
                self.screen.blit(txt_qty, txt_qty.get_rect(center=(rect.centerx, rect.centery + 20)))
                
            # 카드 테두리 마감
            pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=10)

    def draw(self):
        self.screen.fill(self.COLOR_BG)
        
        # 1. 상단 상대방 영역 그리기
        self.draw_card_sprite(self.opp_deck_rect, None, is_deck=True)
        self.draw_card_sprite(self.opp_pile_rect, self.opp_top_card)
        
        opp_info = self.font_info.render(f"{self.opp_name} (남은 카드: {self.opp_cards_count}장)", True, self.COLOR_TEXT)
        self.screen.blit(opp_info, (self.opp_deck_rect.x, self.opp_deck_rect.bottom + 10))
        
        # 2. 하단 내 영역 그리기
        self.draw_card_sprite(self.my_deck_rect, None, is_deck=True)
        self.draw_card_sprite(self.my_pile_rect, self.my_top_card)
        
        my_info = self.font_info.render(f"{self.my_name} (남은 카드: {self.my_cards_count}장)", True, self.COLOR_TEXT)
        self.screen.blit(my_info, (self.my_deck_rect.x, self.my_deck_rect.y - 35))

        # 3. 중앙 종(Bell) 그리기
        bell_color = (211, 84, 0) if self.bell.is_pressed else (241, 196, 15)
        pygame.draw.circle(self.screen, bell_color, self.bell.rect.center, self.bell.rect.width // 2)
        pygame.draw.circle(self.screen, (255, 255, 255), self.bell.rect.center, self.bell.rect.width // 2, width=3)
        
        txt_bell = self.font_info.render("🔔", True, (0, 0, 0))
        self.screen.blit(txt_bell, txt_bell.get_rect(center=self.bell.rect.center))