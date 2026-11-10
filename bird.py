"""새 이미지의 프레임 좌표와 비행 동작."""

from pico2d import load_image, get_canvas_width
import game_framework

FRAME_COUNT = 14
FLAP_CYCLE_SECONDS = 0.6
FLAP_FRAMES_PER_SECOND = FRAME_COUNT / FLAP_CYCLE_SECONDS
SHEET_COLUMNS = 5
SHEET_ROWS = 3
PIXEL_PER_METER = 10.0 / 0.3
FLY_SPEED_KMPH = 18.0
FLY_SPEED_MPS = FLY_SPEED_KMPH * 1000.0 / 3600.0
FLY_SPEED_PPS = FLY_SPEED_MPS * PIXEL_PER_METER
FLOCK_SIZE = 10
MIN_FLIGHT_Y = 350
MAX_FLIGHT_Y = 500


def frame_rect(frame, image_width, image_height):
    """위에서부터 읽은 프레임을 pico2d의 아래쪽 원점으로 변환한다."""
    index = int(frame) % FRAME_COUNT
    column = index % SHEET_COLUMNS
    row = index // SHEET_COLUMNS
    # 원본 918 × 506px의 나머지 여백은 제외한다.
    width = image_width // SHEET_COLUMNS
    height = image_height // SHEET_ROWS
    return column * width, image_height - (row + 1) * height, width, height


class Bird:
    image = None
    width = 90

    def __init__(self, x, y, direction=1, frame=0):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = x, y
        self.direction = 1 if direction >= 0 else -1
        self.frame = float(frame) % FRAME_COUNT
        _, _, source_width, source_height = frame_rect(
            0, self.image.w, self.image.h)
        self.height = self.width * source_height / source_width

    def update(self):
        self.frame = (self.frame + FLAP_FRAMES_PER_SECOND *
                      game_framework.frame_time) % FRAME_COUNT
        left = self.width / 2
        span = get_canvas_width() - self.width
        if span <= 0:
            self.x = get_canvas_width() / 2
            return
        # 왕복 경로를 펼쳐 계산하면 큰 시간 간격에도 경계 안에 머문다.
        offset = self.x - left
        path = offset if self.direction > 0 else 2 * span - offset
        path = (path + FLY_SPEED_PPS * game_framework.frame_time) % (2 * span)
        self.x = left + (path if path < span else 2 * span - path)
        self.direction = 1 if path < span else -1

    def draw(self):
        self.image.clip_composite_draw(
            *frame_rect(self.frame, self.image.w, self.image.h),
            0, 'h' if self.direction < 0 else '',
            self.x, self.y, self.width, self.height)


def create_flock():
    """시작 위치, 방향, 날갯짓 위상을 분산한 새 10마리를 만든다."""
    available_width = max(0, get_canvas_width() - Bird.width)
    return [
        Bird(
            Bird.width / 2 + available_width * (index + 0.5) / FLOCK_SIZE,
            MIN_FLIGHT_Y + (MAX_FLIGHT_Y - MIN_FLIGHT_Y) * index / (FLOCK_SIZE - 1),
            direction=1 if index % 2 == 0 else -1,
            frame=FRAME_COUNT * index / FLOCK_SIZE,
        )
        for index in range(FLOCK_SIZE)
    ]
