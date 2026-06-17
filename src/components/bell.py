class Bell:
    def __init__(self, rect, on_ring_callback=None):
        self.rect = rect  # Pygame 화면에서 종이 위치할 Rect 영역 (마우스 클릭 감지용)
        self.on_ring = on_ring_callback  # 종을 울렸을 때 실행할 네트워크 전송 함수
        self.is_pressed = False  # 종 애니메이션 효과용 상태 변수

    def ring(self):
        """종을 울립니다. 연결된 콜백 함수가 있다면 실행합니다."""
        print("[Bell] 땡! 종이 울렸습니다.")
        self.is_pressed = True # 클릭 시 순간적으로 찌그러지는 효과 등 연출용
        
        if self.on_ring:
            self.on_ring()  # main.py에서 넘겨받은 서버 전송 함수 실행

    def update(self):
        """매 프레임 상태를 업데이트 (눌렸다가 자연스럽게 복구되는 연출)"""
        if self.is_pressed:
            # 나중에 애니메이션 프레임을 나누거나 타이머를 둬서 해제 가능
            # 여기서는 우선 단순하게 유지합니다.
            pass