"""새 이미지의 프레임 좌표와 비행 동작."""

FRAME_COUNT = 14
SHEET_COLUMNS = 5
SHEET_ROWS = 3


def frame_rect(frame, image_width, image_height):
    """위에서부터 읽은 프레임을 pico2d의 아래쪽 원점으로 변환한다."""
    index = int(frame) % FRAME_COUNT
    column = index % SHEET_COLUMNS
    row = index // SHEET_COLUMNS
    # 원본 918 × 506px의 나머지 여백은 제외한다.
    width = image_width // SHEET_COLUMNS
    height = image_height // SHEET_ROWS
    return column * width, image_height - (row + 1) * height, width, height
