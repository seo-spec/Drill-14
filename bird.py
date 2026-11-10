"""새 이미지의 프레임 좌표와 비행 동작."""

from pico2d import load_image

FRAME_COUNT = 14
SHEET_COLUMNS = 5
SHEET_ROWS = 3
PIXEL_PER_METER = 10.0 / 0.3
FLY_SPEED_KMPH = 18.0
FLY_SPEED_MPS = FLY_SPEED_KMPH * 1000.0 / 3600.0
FLY_SPEED_PPS = FLY_SPEED_MPS * PIXEL_PER_METER


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
        pass

    def draw(self):
        self.image.clip_draw(
            *frame_rect(self.frame, self.image.w, self.image.h),
            self.x, self.y, self.width, self.height)
