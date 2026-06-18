BASE_URL = "http://localhost:8080"
WS_URL = "ws://localhost:8080/ws"

def update_server_address(new_address):
    global SERVER_ADDRESS, BASE_URL, WS_URL
    SERVER_ADDRESS = new_address.strip()

    BASE_URL = f"https://{SERVER_ADDRESS}"
    WS_URL = f"wss://{SERVER_ADDRESS}/ws"