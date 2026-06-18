class TextRenderer:
    @staticmethod
    def draw_center(screen, font, text, color, center):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=center)
        screen.blit(surface, rect)

    @staticmethod
    def draw_left(screen, font, text, color, pos):
        surface = font.render(text, True, color)
        screen.blit(surface, pos)