import pygame
import os


class Card:
    _image_cache = {}

    def __init__(self, fruit, quantity, image_path=""):
        self.fruit = str(fruit).lower()
        self.quantity = int(quantity)
        self.image = None

        file_name = f"{self.fruit}-{self.quantity}.png"

        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_file_dir))

        full_path = os.path.join(project_root, "src", "assets", "cards", file_name)
        full_path = os.path.normpath(full_path)

        if full_path in Card._image_cache:
            self.image = Card._image_cache[full_path]
            return

        if os.path.exists(full_path):
            try:
                self.image = pygame.image.load(full_path).convert_alpha()
                Card._image_cache[full_path] = self.image
            except Exception as e:
                print(f"❌ [Card Error] 이미지 로드 실패: {e}")
        else:
            print(f"❌ [Card Warning] 카드 이미지 없음: {full_path}")

    def getFruit(self):
        return self.fruit

    def getQuantity(self):
        return self.quantity