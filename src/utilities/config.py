# src/config.py

# 기본값은 로컬로 잡아두고, HomeScene에서 입력받으면 이 값이 바뀝니다.
SERVER_ADDRESS = "localhost:8080"
BASE_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080/ws"

def update_server_address(new_address):
    global SERVER_ADDRESS, BASE_URL, WS_URL
    SERVER_ADDRESS = new_address.strip()
    
    # 동기화 로직은 뒤로 미루기로 했으니, 일단 단순 문자열 조립만 해둡니다.
    if "localhost" in SERVER_ADDRESS:
        BASE_URL = f"http://{SERVER_ADDRESS}"
        WS_URL = f"ws://{SERVER_ADDRESS}/ws"
    else:
        BASE_URL = f"https://{SERVER_ADDRESS}"
        WS_URL = f"wss://{SERVER_ADDRESS}/ws"
    
    print(f"⚙️ [Config Changed] 주소 변경 완료 -> BASE: {BASE_URL}")