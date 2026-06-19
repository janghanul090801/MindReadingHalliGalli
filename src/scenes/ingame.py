import math
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
        self.opp_name = "상대방"

        self.my_cards_count = 0
        self.opp_cards_count = 0

        self.my_top_card = None
        self.opp_top_card = None
        self.opp_next_card = None

        self.current_turn_id = None
        self.game_message = "게임 진행 중..."
        self.msg_timer = 0

        self.my_animating_card = None
        self.my_anim_start_pos = None
        self.my_anim_end_pos = None
        self.my_anim_progress = 0

        self.opp_animating_card = None
        self.opp_anim_start_pos = None
        self.opp_anim_end_pos = None
        self.opp_anim_progress = 0

        self.anim_duration = 18

        self.last_my_top_signature = None
        self.last_opp_top_signature = None

        card_w, card_h = 120, 180
        cx = self.width // 2
        cy = self.height // 2

        # 종 기준 좌우 배치
        self.opp_pile_rect = pygame.Rect(cx - 210, cy - 90, card_w, card_h)
        self.my_pile_rect = pygame.Rect(cx + 90, cy - 90, card_w, card_h)

        # 상대 다음 카드 미리보기
        self.opp_next_preview_rect = pygame.Rect(35, 55, card_w, card_h)

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

        my_sig = self.get_card_signature(my_top)
        opp_sig = self.get_card_signature(opp_top)

        if my_sig is not None and my_sig != self.last_my_top_signature:
            self.start_my_draw_animation(my_top)

        if opp_sig is not None and opp_sig != self.last_opp_top_signature:
            self.start_opp_draw_animation(opp_top)

        self.last_my_top_signature = my_sig
        self.last_opp_top_signature = opp_sig

    def get_card_signature(self, card):
        if card is None:
            return None
        return f"{card.getFruit()}-{card.getQuantity()}"

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

    def ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def get_hand_rects(self, count, center_x, center_y, radius, arc_degrees, direction="bottom"):
        if count <= 0:
            return []

        card_w, card_h = 120, 180

        if count == 1:
            angles = [0]
        else:
            max_arc = arc_degrees
            step = max_arc / (count - 1)
            start = -max_arc / 2
            angles = [start + step * i for i in range(count)]

        rects = []

        for angle_deg in angles:
            rad = math.radians(angle_deg)

            if direction == "bottom":
                x = center_x + radius * math.sin(rad)
                y = center_y - radius * math.cos(rad)
                card_angle = -angle_deg
            else:
                x = center_x + radius * math.sin(rad)
                y = center_y + radius * math.cos(rad)
                card_angle = angle_deg

            rect = pygame.Rect(0, 0, card_w, card_h)
            rect.center = (int(x), int(y))

            rects.append((rect, card_angle))

        return rects

    def get_my_hand_rects(self):
        return self.get_hand_rects(
            count=self.my_cards_count,
            center_x=self.width // 2 + 180,
            center_y=self.height + 120,
            radius=300,
            arc_degrees=min(95, max(20, self.my_cards_count * 7)),
            direction="bottom"
        )

    def get_opp_hand_rects(self):
        return self.get_hand_rects(
            count=self.opp_cards_count,
            center_x=self.width // 2 - 180,
            center_y=-120,
            radius=300,
            arc_degrees=min(95, max(20, self.opp_cards_count * 7)),
            direction="top"
        )

    def get_middle_hand_start_pos(self, rects, target_rect):
        if not rects:
            return target_rect.topleft

        middle_index = len(rects) // 2
        start_rect = rects[middle_index][0]

        return (
            start_rect.centerx - target_rect.width // 2,
            start_rect.centery - target_rect.height // 2
        )

    def start_my_draw_animation(self, card):
        self.my_animating_card = card
        self.my_anim_start_pos = self.get_middle_hand_start_pos(
            self.get_my_hand_rects(),
            self.my_pile_rect
        )
        self.my_anim_end_pos = self.my_pile_rect.topleft
        self.my_anim_progress = 0

    def start_opp_draw_animation(self, card):
        self.opp_animating_card = card
        self.opp_anim_start_pos = self.get_middle_hand_start_pos(
            self.get_opp_hand_rects(),
            self.opp_pile_rect
        )
        self.opp_anim_end_pos = self.opp_pile_rect.topleft
        self.opp_anim_progress = 0

    def update_animation(self):
        if self.my_animating_card is not None:
            self.my_anim_progress += 1
            if self.my_anim_progress >= self.anim_duration:
                self.my_animating_card = None

        if self.opp_animating_card is not None:
            self.opp_anim_progress += 1
            if self.opp_anim_progress >= self.anim_duration:
                self.opp_animating_card = None

    def draw_moving_card(self, card, start_pos, end_pos, progress):
        if card is None:
            return

        t = progress / self.anim_duration
        t = max(0, min(1, t))
        t = self.ease_out_cubic(t)

        sx, sy = start_pos
        ex, ey = end_pos

        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t

        rect = pygame.Rect(int(x), int(y), 120, 180)

        CardRenderer.draw(
            self.screen,
            rect,
            card,
            self.font_title,
            self.font_info
        )

    def draw_hand(self, rects, invert_angle=False):
        for rect, angle in rects:
            if invert_angle:
                angle = -angle

            CardRenderer.draw_back_rotated(
                self.screen,
                rect,
                angle=angle
            )

    def draw_my_area(self):
        self.draw_hand(self.get_my_hand_rects())

        if self.my_animating_card is None:
            CardRenderer.draw(
                self.screen,
                self.my_pile_rect,
                self.my_top_card,
                self.font_title,
                self.font_info
            )
        else:
            CardRenderer.draw(
                self.screen,
                self.my_pile_rect,
                None,
                self.font_title,
                self.font_info
            )

        my_color = self.COLOR_TURN if self.is_my_turn() else self.COLOR_TEXT

        TextRenderer.draw_center(
            self.screen,
            self.font_info,
            f"{self.my_name} (남은 카드: {self.my_cards_count}장)",
            my_color,
            (self.width // 2 + 180, self.height - 20)
        )

    def draw_opp_area(self):
        self.draw_hand(self.get_opp_hand_rects())

        if self.opp_animating_card is None:
            CardRenderer.draw(
                self.screen,
                self.opp_pile_rect,
                self.opp_top_card,
                self.font_title,
                self.font_info
            )
        else:
            CardRenderer.draw(
                self.screen,
                self.opp_pile_rect,
                None,
                self.font_title,
                self.font_info
            )

        opp_color = self.COLOR_TURN if self.is_opp_turn() else self.COLOR_TEXT

        TextRenderer.draw_center(
            self.screen,
            self.font_info,
            f"{self.opp_name} (남은 카드: {self.opp_cards_count}장)",
            opp_color,
            (self.width // 2 - 180, 245)
        )

    def draw_opp_next_preview(self):
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

    def draw_message_or_turn_guide(self):
        if self.game_message:
            TextRenderer.draw_center(
                self.screen,
                self.font_status,
                self.game_message,
                (255, 242, 0),
                (self.width // 2, self.height // 2 - 155)
            )
            return

        turn_text = "내 차례입니다! (스페이스바)" if self.is_my_turn() else "상대방의 차례를 기다리는 중..."

        TextRenderer.draw_center(
            self.screen,
            self.font_info,
            turn_text,
            (200, 200, 200),
            (self.width // 2, self.height // 2 - 145)
        )

    def draw(self):
        self.screen.fill(self.COLOR_BG)

        if self.msg_timer > 0:
            self.msg_timer -= 1
        elif "승리" not in self.game_message and "패배" not in self.game_message:
            self.game_message = ""

        self.draw_opp_area()
        self.draw_my_area()
        self.draw_opp_next_preview()

        self.draw_moving_card(
            self.opp_animating_card,
            self.opp_anim_start_pos,
            self.opp_anim_end_pos,
            self.opp_anim_progress
        )

        self.draw_moving_card(
            self.my_animating_card,
            self.my_anim_start_pos,
            self.my_anim_end_pos,
            self.my_anim_progress
        )

        self.update_animation()

        BellRenderer.draw(self.screen, self.bell, self.font_info)
        self.draw_message_or_turn_guide()