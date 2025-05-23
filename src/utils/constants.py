class DisplayConstants:
    WIDTH=28
    HEIGHT=28
    
    PANEL_0_ID=1
    PANEL_1_ID=2
    PANEL_2_ID=4
    PANEL_3_ID=8

    FRAME_HEADER = 128
    FRAME_COMMAND = 131
    FRAME_TAIL = 143
    FRAME_COMMAND_START_INDEX = 3
    FRAME_COMMAND_END_INDEX = 31
    FRAME_LENGTH = 32

    DISPLAY_PANEL_WIDTH_COUNT = 4
    PANEL_ROW_WIDTH_COUNT = 1
    ROW_DISC_WIDTH_COUNT = 7
    DISPLAY_PANEL_HEIGHT_COUNT = 1
    PANEL_ROW_HEIGHT_COUNT = 28
    ROW_DISC_HEIGHT_COUNT = 1

    DISPLAY_DISC_WIDTH_COUNT = DISPLAY_PANEL_WIDTH_COUNT * PANEL_ROW_WIDTH_COUNT * ROW_DISC_WIDTH_COUNT
    DISPLAY_DISC_HEIGHT_COUNT = DISPLAY_PANEL_HEIGHT_COUNT * PANEL_ROW_HEIGHT_COUNT * ROW_DISC_HEIGHT_COUNT

class SimConstants:
    WINDOW_WIDTH_INIT = 900
    WINDOW_WIDTH_MIN = 600
    WINDOW_WIDTH_MAX = 1800
    WINDOW_HEIGHT_INIT = 600
    WINDOW_HEIGHT_MIN = 400
    WINDOW_HEIGHT_MAX = 1200

    WINDOW_ASPECT_RATIO = 1.5
    WINDOW_TO_DISC_RATIO = 60

    DISC_BORDER = 0.1 # 10% border around disc

    DISC_TOP = 1
    DISC_BOTTOM = 0
    SIM_FPS = 30

class HardwareConstants:
    # pinouts
    PIN_SDA = 2
    PIN_SCL = 3
    PIN_EN_485 = 4
    PIN_BUTTON_RED = 16
    PIN_BUTTON_YELLOW = 12

    BUTTON_DEBOUNCE_TIME=50

    # ADS 1015
    ADS_CHANNEL_SLIDER = 0
    ADS_SLIDER_PCT_100_RAW = 13500
    ADS_SLIDER_PCT_0_RAW = 26380

    # serial config
    SERIAL_BAUDRATE = 19200
    SERIAL_PORT_NAME="/dev/ttyAMA0"