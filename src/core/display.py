import numpy as np
from abc import ABC, abstractmethod
from utils.constants import DisplayConstants as DC

class Display(ABC):
    def __init__(self, width=DC.DISPLAY_DISC_WIDTH_COUNT, height=DC.DISPLAY_DISC_HEIGHT_COUNT):
        self.width = width
        self.height = height
        self.frame_buffer = np.zeros((height, width), dtype=np.uint8)
        self.prev_frame_buffer = np.zeros((height, width), dtype=np.uint8)
    
    @abstractmethod
    def initialize(self):
        pass
    
    @abstractmethod
    def send_frame(self, frame_matrix):
        pass
    
    @abstractmethod
    def cleanup(self):
        pass
    
    def clear(self):
        self.frame_buffer = np.zeros((self.height, self.width), dtype=np.uint8)
        self.send_frame(self.frame_buffer)
    
    def set_pixel(self, x, y, value):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.frame_buffer[y, x] = value
    
    def update(self):
        if not np.array_equal(self.frame_buffer, self.prev_frame_buffer):
            self.send_frame(self.frame_buffer)
            self.prev_frame_buffer = self.frame_buffer.copy()


class FrameGenerator:
    @staticmethod
    def construct_frame(data):
        PANEL_IDS = np.array([DC.PANEL_0_ID, DC.PANEL_1_ID, DC.PANEL_2_ID, DC.PANEL_3_ID], dtype=np.uint8)
        assert(data.shape == (DC.DISPLAY_DISC_WIDTH_COUNT, DC.DISPLAY_DISC_HEIGHT_COUNT))
        display_frame = np.empty((0, DC.FRAME_LENGTH), dtype=np.uint8)
        
        for panel in range(0, DC.DISPLAY_PANEL_WIDTH_COUNT):
            panel_sub_frame = np.empty((0, DC.PANEL_ROW_HEIGHT_COUNT), dtype=np.uint8)
            panel_frame = np.empty((0, DC.FRAME_LENGTH), dtype=np.uint8)
            panel_frame = np.append(panel_frame, [DC.FRAME_HEADER, DC.FRAME_COMMAND, PANEL_IDS[panel], DC.FRAME_TAIL])
            panel_data = data[0:DC.PANEL_ROW_HEIGHT_COUNT, panel*DC.ROW_DISC_WIDTH_COUNT:(panel+1)*DC.ROW_DISC_WIDTH_COUNT]
            
            for column in range(0, DC.PANEL_ROW_HEIGHT_COUNT):
                column_data = panel_data[column, :]
                column_data_int = 0
                for disc in column_data:
                    column_data_int = (column_data_int << 1) | disc
                panel_sub_frame = np.append(panel_sub_frame, np.array(column_data_int))
            
            panel_frame = np.insert(panel_frame, slice(DC.FRAME_COMMAND_START_INDEX, DC.FRAME_COMMAND_END_INDEX), panel_sub_frame)
            panel_frame = panel_frame.astype(np.uint8)
            display_frame = np.concatenate((display_frame, [panel_frame]), axis=0)
        
        return display_frame


def create_display_adapter(use_simulator=False):
    if use_simulator:
        from core.simulator import FlipSimDisplay
        return FlipSimDisplay()
    else:
        from core.hardware import FlipDiscDisplay
        return FlipDiscDisplay()