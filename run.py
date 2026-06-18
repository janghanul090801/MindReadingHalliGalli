import pygame
import sys
import websocket
import threading
import json
import random
import queue
import os


from src.scenes.connect import ConnectScene
from src.scenes.home import HomeScene
from src.scenes.create_room import CreateRoomScene
from src.scenes.wait import WaitScene
from src.scenes.find_room import FindRoomScene
from src.scenes.ingame import InGameScene
from src.components.card import Card
from src.core.game_state_parser import GameStateAdapter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    global current_scene_key, scenes, ws

    pygame.init()
    screen = pygame.display.set_mode((1300, 800))
    pygame.display.set_caption("Mind Reading Halli Galli")
    clock = pygame.time.Clock()

    scenes = {
        "connect": ConnectScene(screen),
        "home": HomeScene(screen),
        "create_room": CreateRoomScene(screen),
        "wait": WaitScene(screen),
        "find_room": FindRoomScene(screen),
        "ingame": InGameScene(screen, on_ring_server_func=send_ring_packet)
    }

    game_over_triggered = False
    game_over_timer = 0

    running = True

    while running:
        try:
            while not game_state_queue.empty():
                data = game_state_queue.get_nowait()
                msg_type = data.get("type")

                if msg_type == "ring_success":
                    p_id = data.get("player_id")
                    winner = "나" if p_id == player_id else "상대방"
                    scenes["ingame"].set_message(f"🔔 {winner} 종 치기 성공! 바닥 카드 회수")
                    continue

                elif msg_type == "ring_fail":
                    p_id = data.get("player_id")
                    loser = "나" if p_id == player_id else "상대방"
                    scenes["ingame"].set_message(f"❌ {loser} 잘못 쳤음! 패널티 1장 기부")
                    continue

                state = GameStateAdapter.parse_game_state(data, player_id)

                scenes["ingame"].update_data(
                    state["my_count"],
                    state["my_top_card"],
                    state["opp_count"],
                    state["opp_top_card"],
                    state["turn_id"],
                    opp_next=state["opp_next_card"],
                    my_player_id=state["my_id"],
                    opp_player_id=state["opp_id"]
                )

                scenes["ingame"].my_name = f"나 ({state['my_id']})"

                if state["opp_id"]:
                    scenes["ingame"].opp_name = f"상대방 ({state['opp_id']})"

                if state["opp_id"] and not game_over_triggered:
                    if state["my_count"] == 0:
                        scenes["ingame"].set_message("패배! 😭 (5초 후 메인화면으로 이동)")
                        game_over_triggered = True
                        game_over_timer = 300

                    elif state["opp_count"] == 0:
                        scenes["ingame"].set_message("승리! 🎉 (5초 후 메인화면으로 이동)")
                        game_over_triggered = True
                        game_over_timer = 300

                current_scene_key = "ingame"

        except queue.Empty:
            pass

        if game_over_triggered:
            game_over_timer -= 1

            if game_over_timer <= 0:
                if ws:
                    ws.close()

                game_over_triggered = False
                game_over_timer = 0
                current_scene_key = "connect"

        current_scene = scenes[current_scene_key]

        for event in pygame.event.get():
            if game_over_triggered and current_scene_key == "ingame":
                continue

            result = current_scene.handle_event(event)

            if result:
                action = result.get("action")

                if action == "submit_connect":
                    update_network_config(result.get("address", "localhost:8080"))
                    threading.Thread(target=connect_websocket, daemon=True).start()
                    current_scene_key = "home"

                elif action == "create":
                    current_scene_key = "create_room"

                elif action == "find":
                    current_scene_key = "find_room"

                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps({"type": "get_rooms"}))
                        print("📡 [System] 방 찾기 화면 진입: 서버에 방 목록 갱신 요청")

                elif action == "go_home":
                    current_scene_key = "home"

                elif action == "submit_create_room":
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps({
                            "type": "create_room",
                            "room_name": result.get("room_name")
                        }))

                elif action == "submit_join_room":
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps({
                            "type": "join_room",
                            "room_id": int(result.get("room_id"))
                        }))

                elif action == "submit_draw":
                    if ws and ws.sock and ws.sock.connected:
                        ws.send(json.dumps({"type": "draw"}))

                elif action == "submit_ring":
                    send_ring_packet()

                elif action == "quit":
                    running = False

        current_scene.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()