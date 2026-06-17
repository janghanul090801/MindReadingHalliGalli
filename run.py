# run.py 맨 상단 임포트 구역 수정
import pygame
import sys
import websocket
import threading
import json
import random
import queue
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scenes.home import HomeScene
from src.scenes.create_room import CreateRoomScene
from src.scenes.wait import WaitScene
from src.scenes.find_room import FindRoomScene
from src.scenes.ingame import InGameScene

# ★ 여기 경로를 src.components.card로 변경합니다!
from src.components.card import Card

ws = None
player_id = random.randint(10000, 99999)

scenes = {}
current_scene_key = "home"

# ★ 웹소켓 스레드와 파이게임 메인 스레드를 연결해 줄 안전한 큐 생성
game_state_queue = queue.Queue()

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
        # 인게임 상태일 때는 룸 리스트 때문에 화면이 튕기지 않도록 방어
        if current_scene_key in ["ingame", "wait"]:
            return
        rooms_data = data.get("rooms", [])
        scenes["find_room"].update_room_list(rooms_data)
        
    # ★ 핵심: game_state 패킷은 직접 처리하지 않고 메인 큐에 집어넣어 충돌을 방지합니다.
    elif msg_type == "game_state":
        print("[Network] game_state 패킷 수신 -> 메인 스레드 큐로 이관")
        game_state_queue.put(data)

def on_open(ws):
    print(f"서버 연결 성공! (Player ID: {player_id})")

def connect_websocket():
    global ws
    ws_url = f"ws://localhost:8080/ws?player_id={player_id}"
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
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
    
    ws_thread = threading.Thread(target=connect_websocket, daemon=True)
    ws_thread.start()
    
    scenes = {
        "home": HomeScene(screen),
        "create_room": CreateRoomScene(screen),
        "wait": WaitScene(screen),
        "find_room": FindRoomScene(screen),
        "ingame": InGameScene(screen, on_ring_server_func=send_ring_packet)
    }
    
    running = True
    while running:
        # ★ [추가] 파이게임 메인 스레드 안에서 안전하게 큐의 데이터를 꺼내 실시간 동기화 및 화면 전환 처리
        try:
            while not game_state_queue.empty():
                data = game_state_queue.get_nowait()
                print("[System] 서버로부터 게임 상태 수신 -> 데이터를 동기화합니다.")
                
                # 1. 서버 패킷에서 내 데이터와 상대방 데이터 추출
                queues = data.get("card_queues", {})
                stacks = data.get("card_stacks", {})
                
                # 내 ID 기반 데이터 파싱 (안전하게 문자열 변환 비교)
                my_id_str = str(player_id)
                
                # 상대방 ID 찾기 (딕셔너리 키 중 내 ID가 아닌 것)
                opp_id_str = None
                for k in queues.keys():
                    if str(k) != my_id_str:
                        opp_id_str = str(k)
                        break
                
                # 2. 덱에 남은 카드 개수 파싱 (없으면 0)
                my_count = queues.get(my_id_str, 0)
                opp_count = queues.get(opp_id_str, 0) if opp_id_str else 0
                
                # 3. 오픈된 카드 파일(Stack)의 맨 위 카드 파싱
                from src.components.card import Card
                
                my_top_card = None
                my_stack = stacks.get(my_id_str, [])
                if my_stack:
                    srv_card = my_stack[-1] # 맨 마지막 원소
                    if "fruit" in srv_card:
                        my_top_card = Card(srv_card["fruit"], int(srv_card["number"]), "")
                        
                opp_top_card = None
                if opp_id_str:
                    opp_stack = stacks.get(opp_id_str, [])
                    if opp_stack:
                        srv_card = opp_stack[-1] # 맨 마지막 원소
                        # 상대 카드가 보이고 fruit 정보가 있을 때만 내용 파싱
                        if srv_card.get("is_visible", True) and "fruit" in srv_card:
                            opp_top_card = Card(srv_card["fruit"], int(srv_card["number"]), "")
                
                # 4. 인게임 씬의 변수 갱신 및 화면 전환
                scenes["ingame"].update_data(my_count, my_top_card, opp_count, opp_top_card)
                
                # 이름도 ID로 이쁘게 세팅
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
                
                if action == "create":
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
                    # 이미 인게임 상태라면 추가 클릭 방지
                    if current_scene_key == "ingame":
                        continue
                    room_id = result.get("room_id")
                    packet = {"type": "join_room", "room_id": int(room_id)}
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps(packet))
                        
                # ★ 인게임에서 발생한 카드 뽑기(draw) 서버 전송
                elif action == "submit_draw":
                    packet = {"type": "draw"}
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps(packet))
                        
                # ★ 인게임에서 발생한 벨 치기(ring) 서버 전송
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