import pygame


class BellRenderer:
    @staticmethod
    def draw(screen, bell, font):
        bell_color = (211, 84, 0) if bell.is_pressed else (241, 196, 15)

        pygame.draw.circle(
            screen,
            bell_color,
            bell.rect.center,
            bell.rect.width // 2
        )

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            bell.rect.center,
            bell.rect.width // 2,
            width=3
        )

        text = font.render("🔔", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=bell.rect.center))