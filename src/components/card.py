import pygame
import os

class Card:
    def __init__(self, fruit, quantity, image_path=""):
        self.fruit = fruit.lower()
        self.quantity = int(quantity)
        self.image = None
        
        name_mapping = {
            "strawberry": "apple",
            "plum": "grape"
        }
        file_fruit = name_mapping.get(self.fruit, self.fruit)
        file_name = f"{file_fruit}-{self.quantity}.png"
        
        # 현재 파일 위치를 기준으로 프로젝트 루트 구하기
        current_file_dir = os.path.dirname(os.path.abspath(__file__)) # src/components
        project_root = os.path.dirname(os.path.dirname(current_file_dir)) # MindReadingHalliGalli
        
        # ★ 핵심 수정: 속성 창 위치에 맞춰서 "src" 경로를 중간에 삽입합니다!
        full_path = os.path.join(project_root, "src", "assets", "cards", file_name)
        full_path = os.path.normpath(full_path)
        
        if os.path.exists(full_path):
            try:
                self.image = pygame.image.load(full_path)
            except Exception as e:
                print(f"❌ [Card Error] 파일은 있는데 파이게임 로드 실패: {e}")
        else:
            print(f"❌ [Card Warning] 내 눈엔 안 보여!: {full_path}")

    def getFruit(self): return self.fruit
    def getQuantity(self): return self.quantity