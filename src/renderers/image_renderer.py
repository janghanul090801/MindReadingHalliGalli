import pygame


class ImageRenderer:
    _scaled_cache = {}

    @staticmethod
    def draw(screen, image, rect, alpha=None):
        if image is None:
            return

        cache_key = (id(image), rect.width, rect.height, alpha)

        if cache_key in ImageRenderer._scaled_cache:
            scaled_image = ImageRenderer._scaled_cache[cache_key]
        else:
            scaled_image = pygame.transform.smoothscale(image, (rect.width, rect.height))

            if alpha is not None:
                scaled_image = scaled_image.copy()
                scaled_image.set_alpha(alpha)

            ImageRenderer._scaled_cache[cache_key] = scaled_image

        screen.blit(scaled_image, rect.topleft)

    @staticmethod
    def draw_center(screen, image, center, size=None, alpha=None):
        if image is None:
            return

        if size:
            rect = pygame.Rect(0, 0, size[0], size[1])
        else:
            rect = image.get_rect()

        rect.center = center
        ImageRenderer.draw(screen, image, rect, alpha)

    @staticmethod
    def clear_cache():
        ImageRenderer._scaled_cache.clear()