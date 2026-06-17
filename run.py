import pygame
import sys
import websocket
import threading
import json
import random
import queue
import os

# 클립보드 텍스트를 가져오기 위한 표준 라이브러리 임포트
from tkinter import Tk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scenes.home import HomeScene
from src.scenes.create_room import CreateRoomScene
from src.scenes.wait import WaitScene
from src.scenes.find_room import FindRoomScene
from src.scenes.ingame import InGameScene
from src.components.card import Card

# ==========================================
# 🔌 최초 구동 시 서버 URL을 입력받는 화면 (Ctrl+V 연동)
# ==========================================
class ConnectScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.input_rect = pygame.Rect(200, 350, 400, 45)
        self.btn_rect = pygame.Rect(300, 450, 200, 50)
        self.address_text = "localhost:8080"
        self.is_active = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.is_active = True
            else:
                self.is_active = False
            
            if self.btn_rect.collidepoint(event.pos):
                return {"action": "submit_connect", "address": self.address_text}

        if event.type == pygame.KEYDOWN and self.is_active:
            # 📌 [핵심 추가] Ctrl + V (또는 맥의 Cmd + V) 단축키 감지
            # event.mod & pygame.KMOD_CTRL -> 윈도우 Ctrl 눌림 여부
            # event.mod & pygame.KMOD_META -> 맥 Cmd 눌림 여부
            if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META):
                try:
                    # Tkinter를 이용해 클립보드 텍스트 가져오기
                    clipboard_text = Tk().clipboard_get()
                    # 제어 문자나 줄바꿈이 섞여 들어오는 것을 방지하기 위해 정돈
                    clipboard_text = clipboard_text.strip().replace("\n", "").replace("\r", "")
                    self.address_text += clipboard_text
                    print(f"📋 클립보드에서 복사됨: {clipboard_text}")
                except Exception as e:
                    print(f"⚠️ 클립보드가 비어있거나 가져올 수 없습니다: {e}")
                return None

            # 기존 키 입력 처리
            if event.key == pygame.K_BACKSPACE:
                self.address_text = self.address_text[:-1]
            elif event.key == pygame.K_RETURN:
                return {"action": "submit_connect", "address": self.address_text}
            else:
                # Ctrl이나 변환 단축키 조합을 누를 때 찌꺼기 문자가 유니코드로 들어오는 현상 방어
                if event.unicode and ord(event.unicode) >= 32:
                    self.address_text += event.unicode
        return None

    def update(self):
        pass

    def draw(self):
        self.screen.fill((240, 240, 240))
        label = self.font.render("접속할 서버 주소(URL)를 입력하세요 (Ctrl+V 지원)", True, (50, 50, 50))
        self.screen.blit(label, (self.input_rect.x, self.input_rect.y - 40))
        
        pygame.draw.rect(self.screen, (135, 206, 250) if self.is_active else (200, 200, 200), self.input_rect, 2, border_radius=5)
        txt = self.font.render(self.address_text, True, (0, 0, 0))
        self.screen.blit(txt, (self.input_rect.x + 10, self.input_rect.y + 8))
        
        pygame.draw.rect(self.screen, (50, 150, 50), self.btn_rect, border_radius=5)
        btn_txt = self.font.render("서버 접속", True, (255, 255, 255))
        self.screen.blit(btn_txt, (self.btn_rect.x + 55, self.btn_rect.y + 10))


# 글로벌 네트워크 설정 값
BASE_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080/ws"

ws = None
player_id = random.randint(10000, 99999)
scenes = {}
current_scene_key = "connect"

game_state_queue = queue.Queue()

def update_network_config(user_input_address):
    global BASE_URL, WS_URL
    user_input_address = user_input_address.strip()
    
    if "localhost" in user_input_address:
        BASE_URL = f"http://{user_input_address}"
        WS_URL = f"ws://{user_input_address}/ws?player_id={player_id}"
    else:
        BASE_URL = f"https://{user_input_address}"
        WS_URL = f"wss://{user_input_address}/ws?player_id={player_id}"
    print(f"⚙️ [Network Config Mapped] -> BASE: {BASE_URL} / WS: {WS_URL}")

def on_message(ws, message):
    global current_scene_key
    data = json.loads(message)
    print(f"[서버 수신]: {data}")
    
    msg_type = data.get("type")
    
    if msg_type == "room_created":
        room_id = data.get("room_id")
        room_name = scenes["create_room"].input_text.strip()
        scenes["wait"].set_room_info(room_id, room_name)
        current_scene_key = "wait"
        
    elif msg_type == "room_list":
        if current_scene_key in ["ingame", "wait"]:
            return
        rooms_data = data.get("rooms", [])
        scenes["find_room"].update_room_list(rooms_data)
        
    elif msg_type == "game_state":
        print("[Network] game_state 패킷 수신 -> 메인 스레드 큐로 이관")
        game_state_queue.put(data)

def on_open(ws):
    print(f"서버 연결 성공! (Player ID: {player_id})")

def connect_websocket():
    global ws, WS_URL
    print(f"🔗 웹소켓 스레드 기동 중... 목적지: {WS_URL}")
    ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_open=on_open)
    ws.run_forever()
    
def send_ring_packet():
    global ws
    packet = {"type": "ring"}
    if ws and ws.sock and ws.sock.connected:
        ws.send(json.dumps(packet))
        print("[Network] 서버로 종 치기(ring) 패킷 전송 완료!")

def main():
    global current_scene_key, scenes
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Mind Reading Halli Galli")
    clock = pygame.time.Clock()
    
    update_network_config("localhost:8080")
    
    scenes = {
        "connect": ConnectScene(screen),
        "home": HomeScene(screen),
        "create_room": CreateRoomScene(screen),
        "wait": WaitScene(screen),
        "find_room": FindRoomScene(screen),
        "ingame": InGameScene(screen, on_ring_server_func=send_ring_packet)
    }
    
    running = True
    while running:
        try:
            while not game_state_queue.empty():
                data = game_state_queue.get_nowait()
                print("[System] 서버로부터 게임 상태 수신 -> 데이터를 동기화합니다.")
                
                queues = data.get("card_queues", {})
                stacks = data.get("card_stacks", {})
                my_id_str = str(player_id)
                
                opp_id_str = None
                for k in queues.keys():
                    if str(k) != my_id_str:
                        opp_id_str = str(k)
                        break
                
                my_count = queues.get(my_id_str, 0)
                opp_count = queues.get(opp_id_str, 0) if opp_id_str else 0
                
                my_top_card = None
                my_stack = stacks.get(my_id_str, [])
                if my_stack:
                    srv_card = my_stack[-1]
                    if "fruit" in srv_card:
                        my_top_card = Card(srv_card["fruit"], int(srv_card["number"]), "")
                        
                opp_top_card = None
                if opp_id_str:
                    opp_stack = stacks.get(opp_id_str, [])
                    if opp_stack:
                        srv_card = opp_stack[-1]
                        if srv_card.get("is_visible", True) and "fruit" in srv_card:
                            opp_top_card = Card(srv_card["fruit"], int(srv_card["number"]), "")
                
                scenes["ingame"].update_data(my_count, my_top_card, opp_count, opp_top_card)
                scenes["ingame"].my_name = f"플레이어 ({my_id_str})"
                if opp_id_str:
                    scenes["ingame"].opp_name = f"상대방 ({opp_id_str})"
                    
                current_scene_key = "ingame"
                print(f"[System] 인게임 화면 동기화 완료 (현재 턴: {data.get('turn')})")
        except queue.Empty:
            pass

        current_scene = scenes[current_scene_key]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            result = current_scene.handle_event(event)
            
            if result:
                action = result.get("action")
                
                if action == "submit_connect":
                    user_addr = result.get("address", "localhost:8080")
                    update_network_config(user_addr)
                    
                    ws_thread = threading.Thread(target=connect_websocket, daemon=True)
                    ws_thread.start()
                    
                    current_scene_key = "home"
                
                elif action == "create":
                    current_scene_key = "create_room"
                elif action == "find":
                    current_scene_key = "find_room"
                elif action == "go_home":
                    current_scene_key = "home"
                    
                elif action == "submit_create_room":
                    room_name = result.get("room_name")
                    packet = {"type": "create_room", "room_name": room_name}
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps(packet))
                        
                elif action == "submit_join_room":
                    if current_scene_key == "ingame":
                        continue
                    room_id = result.get("room_id")
                    packet = {"type": "join_room", "room_id": int(room_id)}
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps(packet))
                        
                elif action == "submit_draw":
                    packet = {"type": "draw"}
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps(packet))
                        
                elif action == "submit_ring":
                    packet = {"type": "ring"}
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps(packet))
        
        current_scene.draw()
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()