import pygame

from src.components.bell import Bell
from src.renderers.card_renderer import CardRenderer
from src.renderers.bell_renderer import BellRenderer
from src.renderers.text_renderer import TextRenderer


class InGameScene:
    def __init__(self, screen, on_ring_server_func=None):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.bell = Bell(
            pygame.Rect((self.width - 90) // 2, (self.height - 90) // 2, 90, 90),
            on_ring_callback=None
        )

        self.on_ring_server_func = on_ring_server_func

        self.font_title = pygame.font.SysFont("malgungothic", 24, bold=True)
        self.font_info = pygame.font.SysFont("malgungothic", 20)
        self.font_status = pygame.font.SysFont("malgungothic", 28, bold=True)
        self.font_next = pygame.font.SysFont("impact", 22, bold=True)

        self.COLOR_BG = (34, 112, 63)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_TURN = (251, 197, 49)

        self.my_player_id = None
        self.opp_player_id = None

        self.my_name = "나"
        self.my_cards_count = 0
        self.my_top_card = None

        self.opp_name = "상대방"
        self.opp_cards_count = 0
        self.opp_top_card = None
        self.opp_next_card = None

        self.current_turn_id = None
        self.game_message = "게임 진행 중..."
        self.msg_timer = 0

        card_w, card_h = 120, 180
        cx = self.width // 2

        self.my_deck_rect = pygame.Rect(cx - card_w - 30, self.height - card_h - 60, card_w, card_h)
        self.my_pile_rect = pygame.Rect(cx + 30, self.height - card_h - 60, card_w, card_h)

        self.opp_pile_rect = pygame.Rect(cx - card_w - 30, 60, card_w, card_h)
        self.opp_deck_rect = pygame.Rect(cx + 30, 60, card_w, card_h)

        self.opp_next_preview_rect = pygame.Rect(cx + card_w + 40, 60, card_w, card_h)

    def update_data(
        self,
        my_count,
        my_top,
        opp_count,
        opp_top,
        turn_id,
        opp_next=None,
        my_player_id=None,
        opp_player_id=None
    ):
        self.my_cards_count = my_count
        self.my_top_card = my_top
        self.opp_cards_count = opp_count
        self.opp_top_card = opp_top
        self.current_turn_id = turn_id
        self.opp_next_card = opp_next

        if my_player_id is not None:
            self.my_player_id = str(my_player_id)

        if opp_player_id is not None:
            self.opp_player_id = str(opp_player_id)

    def set_message(self, text):
        self.game_message = text
        self.msg_timer = 300

    def is_my_turn(self):
        return (
            self.current_turn_id is not None
            and self.my_player_id is not None
            and str(self.current_turn_id) == str(self.my_player_id)
        )

    def is_opp_turn(self):
        return (
            self.current_turn_id is not None
            and self.opp_player_id is not None
            and str(self.current_turn_id) == str(self.opp_player_id)
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.bell.rect.collidepoint(event.pos):
                self.bell.ring()
                return {"action": "submit_ring"}

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return {"action": "submit_draw"}

            if event.key == pygame.K_RETURN:
                self.bell.ring()
                return {"action": "submit_ring"}

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.bell.is_pressed = False

        return None

    def draw_message_or_turn_guide(self):
        if self.game_message:
            TextRenderer.draw_center(
                self.screen,
                self.font_status,
                self.game_message,
                (255, 242, 0),
                (self.width // 2, self.height // 2 - 100)
            )
            return

        if self.is_my_turn():
            turn_text = "내 차례입니다! (스페이스바)"
        else:
            turn_text = "상대방의 차례를 기다리는 중..."

        TextRenderer.draw_center(
            self.screen,
            self.font_info,
            turn_text,
            (200, 200, 200),
            (self.width // 2, self.height // 2 - 80)
        )

    def draw(self):
        self.screen.fill(self.COLOR_BG)

        if self.msg_timer > 0:
            self.msg_timer -= 1
        elif "승리" not in self.game_message and "패배" not in self.game_message:
            self.game_message = ""

        CardRenderer.draw(
            self.screen,
            self.opp_deck_rect,
            None,
            self.font_title,
            self.font_info,
            is_deck=True
        )

        CardRenderer.draw(
            self.screen,
            self.opp_pile_rect,
            self.opp_top_card,
            self.font_title,
            self.font_info
        )

        if self.opp_next_card:
            CardRenderer.draw(
                self.screen,
                self.opp_next_preview_rect,
                self.opp_next_card,
                self.font_title,
                self.font_info,
                is_preview=True
            )

            TextRenderer.draw_left(
                self.screen,
                self.font_next,
                "NEXT LOOK",
                (0, 200, 255),
                (self.opp_next_preview_rect.x + 10, self.opp_next_preview_rect.y - 30)
            )
        else:
            CardRenderer.draw(
                self.screen,
                self.opp_next_preview_rect,
                None,
                self.font_title,
                self.font_info
            )

        opp_color = self.COLOR_TURN if self.is_opp_turn() else self.COLOR_TEXT
        TextRenderer.draw_left(
            self.screen,
            self.font_info,
            f"{self.opp_name} (남은 카드: {self.opp_cards_count}장)",
            opp_color,
            (self.opp_deck_rect.x - 40, self.opp_deck_rect.bottom + 10)
        )

        CardRenderer.draw(
            self.screen,
            self.my_deck_rect,
            None,
            self.font_title,
            self.font_info,
            is_deck=True
        )

        CardRenderer.draw(
            self.screen,
            self.my_pile_rect,
            self.my_top_card,
            self.font_title,
            self.font_info
        )

        my_color = self.COLOR_TURN if self.is_my_turn() else self.COLOR_TEXT
        TextRenderer.draw_left(
            self.screen,
            self.font_info,
            f"{self.my_name} (남은 카드: {self.my_cards_count}장)",
            my_color,
            (self.my_deck_rect.x, self.my_deck_rect.y - 35)
        )

        BellRenderer.draw(self.screen, self.bell, self.font_info)

        self.draw_message_or_turn_guide()