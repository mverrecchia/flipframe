import time
from core.display import Display, FrameGenerator
from utils.constants import HardwareConstants as HC

import serial
import RPi.GPIO as GPIO
import busio
import board
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_vl6180x

i2c = busio.I2C(board.SCL, board.SDA)

class FlipDiscDisplay(Display):    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.frame_builder = FrameGenerator()
    
    def initialize(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HC.PIN_EN_485, GPIO.OUT)
        GPIO.output(HC.PIN_EN_485, GPIO.HIGH)
        
        self.serial_port = serial.Serial(
            port=HC.SERIAL_PORT_NAME,
            baudrate=HC.SERIAL_BAUDRATE,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        self.clear()
    
    def send_frame(self, frame_matrix):
        frames = self.frame_builder.construct_frame(frame_matrix)
        
        for frame in frames:
            frame_bytes = bytearray(frame)
            self.serial_port.write(frame_bytes)
            time.sleep(0.01)
    
    def cleanup(self):
        if self.serial_port is not None and self.serial_port.is_open:
            self.serial_port.close()
            GPIO.cleanup()

class ButtonManager:
    def __init__(self):
        self.callbacks = {
            'left': [],
            'right': [],
        }
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HC.PIN_BUTTON_YELLOW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(HC.PIN_BUTTON_RED, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.add_event_detect(HC.PIN_BUTTON_YELLOW, GPIO.BOTH, callback=self._left_button_callback, bouncetime=HC.BUTTON_DEBOUNCE_TIME)
        GPIO.add_event_detect(HC.PIN_BUTTON_RED, GPIO.BOTH, callback=self._right_button_callback, bouncetime=HC.BUTTON_DEBOUNCE_TIME)
    
    def register_callback(self, button, callback):
        if button in self.callbacks:
            self.callbacks[button].append(callback)

    # buttons are active low
    def _left_button_callback(self, channel):
        if not GPIO.input(HC.PIN_BUTTON_YELLOW):
            for callback in self.callbacks['left']:
                callback()
    
    def _right_button_callback(self, channel):
        if not GPIO.input(HC.PIN_BUTTON_RED): 
            for callback in self.callbacks['right']:
                callback()
    
    def cleanup(self):
        GPIO.remove_event_detect(HC.PIN_BUTTON_YELLOW)
        GPIO.remove_event_detect(HC.PIN_BUTTON_RED)


class Slider:    
    def __init__(self):
        self.value = 0
        try:
            ads = ADS.ADS1015(i2c)
            self.analog_in = AnalogIn(ads, HC.ADS_CHANNEL_SLIDER)
        except Exception as e:
            print(f"Error initializing slider: {e}")
    
    def get_value(self):
        try:
            raw_value = self.analog_in.value
            self.value = int(100 * ((raw_value - HC.ADS_SLIDER_PCT_0_RAW) / (HC.ADS_SLIDER_PCT_100_RAW - HC.ADS_SLIDER_PCT_0_RAW)))
            self.value = max(0, min(100, self.value))
        except Exception as e:
            print(f"Error reading slider: {e}")
        
        return self.value
    
class DistanceSensor:
    def __init__(self):
        self.value = 0
        self.sensor = None
        try:
            self.sensor = adafruit_vl6180x.VL6180X(i2c)
            self.sensor.range_rate_limit = 1
            try:
                self.value = self.sensor.range * 10  # mm (VL6180X returns in mm already, but keeping *10 for consistency)
            except Exception as e:
                print(f"Error getting initial reading: {e}")
            
        except Exception as e:
            print(f'Error initializing distance sensor: {e}')

    def get_value(self):
        try:
            if self.sensor is not None:
                self.value = self.sensor.range * 10  # mm
        except Exception as e:
            print(f"Error reading distance sensor: {e}")
            
        return self.value
        
    def cleanup(self):
        pass
