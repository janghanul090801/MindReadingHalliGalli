import pygame


class UIRenderer:
    @staticmethod
    def draw_button(screen, rect, text, font, normal_color, hover_color, text_color, border_radius=8):
        mouse_pos = pygame.mouse.get_pos()
        color = hover_color if rect.collidepoint(mouse_pos) else normal_color

        pygame.draw.rect(screen, color, rect, border_radius=border_radius)

        text_surf = font.render(text, True, text_color)
        screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    @staticmethod
    def draw_input_box(
        screen,
        rect,
        text,
        font,
        active,
        text_color,
        bg_color,
        border_active_color,
        border_inactive_color,
        placeholder="",
        placeholder_color=(120, 120, 120),
        border_radius=5
    ):
        pygame.draw.rect(screen, bg_color, rect, border_radius=border_radius)

        border_color = border_active_color if active else border_inactive_color
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=border_radius)

        render_text = text if text else placeholder
        render_color = text_color if text else placeholder_color

        text_surf = font.render(render_text, True, render_color)
        y = rect.y + (rect.height - text_surf.get_height()) // 2
        screen.blit(text_surf, (rect.x + 12, y))