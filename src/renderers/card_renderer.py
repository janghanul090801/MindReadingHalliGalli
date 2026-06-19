import pygame
from src.renderers.image_renderer import ImageRenderer

class CardRenderer:
    COLOR_CARD_BACK = (180, 50, 50)
    COLOR_EMPTY_SLOT = (20, 80, 40)
    COLOR_PREVIEW = (230, 240, 255)

    @staticmethod
    def draw(screen, rect, card_obj, font_title, font_info, is_deck=False, is_preview=False, angle=0):
        if is_deck:
            pygame.draw.rect(screen, CardRenderer.COLOR_CARD_BACK, rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), rect, width=2, border_radius=10)
            return

        if card_obj is None:
            pygame.draw.rect(screen, CardRenderer.COLOR_EMPTY_SLOT, rect, width=2, border_radius=10)
            return

        bg_color = CardRenderer.COLOR_PREVIEW if is_preview else (255, 255, 255)
        pygame.draw.rect(screen, bg_color, rect, border_radius=10)

        if hasattr(card_obj, "image") and card_obj.image:
            alpha = 180 if is_preview else None
            ImageRenderer.draw(screen, card_obj.image, rect, alpha=alpha)
        else:
            fruit_text = font_info.render(str(card_obj.getFruit()), True, (0, 0, 0))
            qty_text = font_title.render(str(card_obj.getQuantity()), True, (255, 0, 0))

            screen.blit(fruit_text, fruit_text.get_rect(center=(rect.centerx, rect.centery - 20)))
            screen.blit(qty_text, qty_text.get_rect(center=(rect.centerx, rect.centery + 20)))

        border_color = (0, 150, 255) if is_preview else (0, 0, 0)
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=10)

    @staticmethod
    def draw_back_rotated(screen, rect, angle=0):
        card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        pygame.draw.rect(
            card_surf,
            CardRenderer.COLOR_CARD_BACK,
            card_surf.get_rect(),
            border_radius=10
        )

        pygame.draw.rect(
            card_surf,
            (255, 255, 255),
            card_surf.get_rect(),
            width=2,
            border_radius=10
        )

        rotated = pygame.transform.rotate(card_surf, angle)
        rotated_rect = rotated.get_rect(center=rect.center)

        screen.blit(rotated, rotated_rect.topleft)