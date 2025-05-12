import argparse
import time
import sys
import numpy as np
import traceback

from detection import camera as camera_module
from detection import gesture as gesture_module

from core.display import create_display_adapter
from core.page_manager import PageManager
from core.input_manager import InputManager, InputEvent
from core.mqtt_manager import MQTTManager

def parse_args():
    parser = argparse.ArgumentParser(description="FlipDisc Display Application")
    parser.add_argument("-s", "--sim", action="store_true", help="Use simulator")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--flip", action="store_true", help="Flip display output upside down")
    return parser.parse_args()


def setup_camera(use_simulator=False):
    camera_module = None
    camera_initialized = False
    
    try:
        camera_initialized = camera_module.init(use_simulator)
    except ImportError as e:
        print(f"Warning: Camera module not available: {e}")
    except Exception as e:
        print(f"Error initializing camera: {e}")
    
    return camera_module, camera_initialized


def setup_gesture_detection():
    gesture_module = None
    gesture_initialized = False
    
    try:
        gesture_initialized = gesture_module.init()
    except ImportError as e:
        print(f"Warning: Gesture module not available: {e}")
    except Exception as e:
        print(f"Error initializing gesture detection: {e}")
    
    return gesture_module, gesture_initialized


def register_pages(page_manager):
    import traceback
    try:
        import pages
        if hasattr(pages, 'PAGES'):            
            for page_id, page_info in pages.PAGES.items():
                if isinstance(page_info, tuple) and len(page_info) >= 2:
                    page_class, metadata = page_info
                    page_manager.register_page(page_id, page_class, metadata)
                else:
                    page_manager.register_page(page_id, page_info)
            
            return True
        else:
            print("No 'PAGES' dictionary found in pages module")
            return False
    except Exception as e:
        print(f"Error registering pages: {e}")
        traceback.print_exc()
        return False

def main():
    args = parse_args()

    display = create_display_adapter(use_simulator=args.sim)
    display.initialize()
    page_manager = PageManager(display)
    mqtt_manager = MQTTManager(page_manager)
    mqtt_manager.initialize()
    if not register_pages(page_manager):
        print("Error: No pages available")
        return 1
        
    input_manager = InputManager(use_simulator=args.sim)
    
    if display is None:
        print("Error: Could not create display adapter")
        return 1
    
    try:   
        def handle_secondary_button():
            if page_manager.current_page and hasattr(page_manager.current_page, 'handle_secondary_button'):
                page_manager.current_page.handle_secondary_button()
        
        def handle_slider_change():
            value = input_manager.slider_value
            page_manager.handle_slider_change(value)

        input_manager.register_callback(InputEvent.PRIMARY, page_manager.next_page)
        input_manager.register_callback(InputEvent.SECONDARY, handle_secondary_button)
        # input_manager.register_callback(InputEvent.VALUE_CHANGE, handle_slider_change)
        
        input_manager.initialize_hardware()
        
        if args.sim:
            input_manager.initialize_simulator(display)
        
        camera_module, camera_initialized = setup_camera(use_simulator=args.sim)
        gesture_module, gesture_initialized = setup_gesture_detection()
        
        # go to first page
        page_ids = page_manager.get_page_ids()
        if page_ids:
            page_manager.navigate_to(page_ids[0])
        else:
            print("Error: No pages registered")
            return 1
        
        running = True
        last_frame_time = time.time()
        
        try:
            while running:
                camera_frame = None
                face_landmarks = None
                gestures = None
                
                # Get metadata for current page, safely handling None case
                metadata = page_manager.get_page_metadata(page_manager.current_page_id)
                camera_features = metadata.get("camera_features") if metadata else None
                
                if camera_features is not None:
                    if camera_initialized:
                        try:
                            camera_frame = camera_module.get_frame(debug=args.debug)
                        except Exception as e:
                            print(f"Error getting camera frame: {e}")
                    
                    if "landmark_detection" in camera_features:
                        if camera_frame is not None and hasattr(camera_module, 'get_face_landmarks'):
                            try:
                                face_landmarks = camera_module.get_face_landmarks(camera_frame)
                            except Exception as e:
                                print(f"Error getting face landmarks: {e}")
                    
                    if "gesture_detection" in camera_features:
                        if camera_frame is not None and gesture_initialized:
                            try:
                                gestures = gesture_module.detect_gestures(camera_frame)
                                
                                # Process gestures for navigation
                                if gestures:
                                    input_manager.process_gestures(gestures)
                            except Exception as e:
                                print(f"Error detecting gestures: {e}")
                
                # update the page
                page_manager.update(camera_frame, face_landmarks, gestures)
                frame = page_manager.render()

                if args.flip:
                    frame = np.flip(np.flip(frame, 0), 1)  # Flip both horizontally and vertically
        
                if frame is not None:
                    display.send_frame(frame)
                
                # limit the frame rate to 30 FPS
                elapsed = time.time() - last_frame_time
                if elapsed < 1/30:
                    time.sleep(1/30 - elapsed)
                
                last_frame_time = time.time()
        
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            # Cleanup
            page_manager.cleanup()
            input_manager.cleanup()
            display.cleanup()
            
            if mqtt_manager is not None:
                mqtt_manager.cleanup()   

            if camera_initialized and hasattr(camera_module, 'cleanup'):
                camera_module.cleanup()
            
            if gesture_initialized and hasattr(gesture_module, 'cleanup'):
                gesture_module.cleanup()
    
    except Exception as e:
        # Add more detailed error information
        print(f"Error in main loop: {e}")
        print("Traceback:")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())