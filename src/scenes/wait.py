import pygame

class WaitScene:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        self.title_font = pygame.font.SysFont("malgungothic", 40, bold=True)
        self.sub_font = pygame.font.SysFont("malgungothic", 24)
        
        self.COLOR_BG = (30, 32, 34)
        self.COLOR_TEXT = (240, 240, 240)
        
        self.room_name = ""
        self.room_id = ""

    def set_room_info(self, room_id, room_name):
        """방 생성 완료 후 서버에서 받은 정보를 씬에 세팅합니다."""
        self.room_id = str(room_id)
        self.room_name = room_name

    def handle_event(self, event):
        # 대기방에서는 일단 호스트가 스스로 나가는 처리가 없다면 이벤트는 패스합니다.
        # 나중에 "방 깨기" 버튼을 추가하고 싶다면 여기에 추가하면 됩니다.
        return None

    def draw(self):
        self.screen.fill(self.COLOR_BG)
        
        # 방 정보 표시
        title_surf = self.title_font.render(f"[{self.room_id}번방] {self.room_name}", True, self.COLOR_TEXT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, 250)))
        
        # 대기 안내 애니메이션용 효과 (단순 텍스트)
        msg_surf = self.sub_font.render("다른 플레이어의 접속을 기다리는 중입니다...", True, (180, 180, 180))
        self.screen.blit(msg_surf, msg_surf.get_rect(center=(self.width // 2, 450)))