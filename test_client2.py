import pygame
import websocket
import threading
import json
import sys

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("HalliGalli Test Client - Player 2")
clock = pygame.time.Clock()

# ★ 1. 첫 번째 유저와 반드시 다른 ID로 설정해야 합니다!
PLAYER_ID = 67890 
ws_url = f"ws://localhost:8080/ws?player_id={PLAYER_ID}"

latest_state = {}

def on_message(ws, message):
    global latest_state
    latest_state = json.loads(message)
    print("Player 2 수신 데이터:", latest_state)

def on_open(ws):
    print("서버 연결 성공! 방 입장을 시도합니다.")
    # ★ 2. 첫 번째 클라이언트가 만든 방 번호(1번)로 입장 요청을 보냅니다.
    join_room_packet = {
        "type": "join_room",
        "room_id": 1
    }
    ws.send(json.dumps(join_room_packet))

ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
ws_thread.start()

running = True
while running:
    screen.fill((40, 44, 52))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 스페이스바 누르면 카드 뽑기 요청
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                draw_packet = {"type": "draw"}
                ws.send(json.dumps(draw_packet))
                print("Player 2: draw 요청 전송")

    font = pygame.font.SysFont(None, 24)
    text = font.render("Spacebar: Draw Card (Player 2)", True, (255, 255, 255))
    screen.blit(text, (20, 20))
    
    if latest_state:
        state_text = font.render(f"Type: {latest_state.get('type')}", True, (0, 255, 0))
        screen.blit(state_text, (20, 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()