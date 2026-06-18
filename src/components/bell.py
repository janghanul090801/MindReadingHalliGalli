class Bell:
    def __init__(self, rect, on_ring_callback=None):
        self.rect = rect
        self.on_ring = on_ring_callback
        self.is_pressed = False

    def ring(self):
        self.is_pressed = True

        if self.on_ring:
            self.on_ring()