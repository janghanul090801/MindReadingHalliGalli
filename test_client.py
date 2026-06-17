import pygame
import websocket
import threading
import json
import sys

# Pygame 초기화
pygame.init()
screen = pygame.size = pygame.display.set_mode((400, 300))
pygame.display.set_caption("HalliGalli Test Client")
clock = pygame.time.Clock()

# 웹소켓 연결 설정 (player_id를 쿼리 스트링으로 전달)
# 테스트를 위해 실행할 때마다 다른 ID를 쓰거나 고정할 수 있습니다.
PLAYER_ID = 12345 
ws_url = f"ws://localhost:8080/ws?player_id={PLAYER_ID}"

latest_state = {}

def on_message(ws, message):
    global latest_state
    latest_state = json.loads(message)
    print("서버에서 받은 데이터:", latest_state)

def on_open(ws):
    print("서버 연결 성공!")
    # 연결되자마자 방 생성 요청 보내기 테스트
    create_room_packet = {"type": "create_room"}
    ws.send(json.dumps(create_room_packet))

# 웹소켓을 별도 스레드에서 실행 (Pygame 루프가 멈추지 않도록)
ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
ws_thread.start()

# Pygame 메인 루프
running = True
while running:
    screen.fill((40, 44, 52)) # 배경색 (어두운 회색)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 키보드 스페이스바를 누르면 카드 뽑기(draw) 요청 전송 테스트
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                draw_packet = {"type": "draw"}
                ws.send(json.dumps(draw_packet))
                print("서버로 draw 요청 전송")

    # 화면에 간단한 텍스트 띄우기
    font = pygame.font.SysFont(None, 24)
    text = font.render("Spacebar: Draw Card", True, (255, 255, 255))
    screen.blit(text, (20, 20))
    
    if latest_state:
        state_text = font.render(f"Type: {latest_state.get('type')}", True, (0, 255, 0))
        screen.blit(state_text, (20, 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()