import json
import time
import traceback
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
from threading import Timer

load_dotenv()

mqtt_broker_address = os.getenv("MQTT_BROKER_ADDRESS")
mqtt_broker_port = int(os.getenv("MQTT_BROKER_PORT"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")

# topics
MQTT_PATTERN_TOPIC = "flip/pattern"
MQTT_DRAW_TOPIC = "flip/draw"
MQTT_CAMERA_TOPIC = "flip/camera"
MQTT_STATUS_TOPIC = "flip/manager/status"
MQTT_LOCK_REQUEST_TOPIC = "flip/lock/request"
MQTT_LOCK_RESPONSE_TOPIC = "flip/lock/response"

# 5 minute lockout
LOCK_TIMEOUT_MS = 5 * 60 * 1000

class MQTTManager:
    def __init__(self, page_manager):
        self.page_manager = page_manager
        self.broker_address = mqtt_broker_address
        self.broker_port = mqtt_broker_port
        self.username = mqtt_username
        self.password = mqtt_password
        self.client = None
        self._status_task = None
        
        self.client_locked = False
        self.authorized_client_id = ""
        self.lock_timestamp = 0
        
    def initialize(self):
        if mqtt is None:
            print("MQTT client not available")
            return False
            
        client_id = f"flipframe_{int(time.time())}"
        self.client = mqtt.Client(client_id=client_id)
        
        self.client.username_pw_set(self.username, self.password)
        
        will_payload = json.dumps({
            "status": "offline",
            "timestamp": int(time.time())
        })
        self.client.will_set(
            topic=MQTT_STATUS_TOPIC,
            payload=will_payload,
            qos=1,
            retain=True
        )
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        try:
            self.client.connect(self.broker_address, self.broker_port, 60)
            self.client.loop_start()
            
            self._schedule_status_update()
            return True
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            traceback.print_exc()
            return False

    def _schedule_status_update(self):
        self._publish_status()
        # Schedule next update
        Timer(1.0, self._schedule_status_update).start()

    def _publish_status(self):
        try:
            status = {
                "status": "online",
                "timestamp": time.time(),
                "current_page": self.page_manager.current_page_id,
            }
            
            # add lock status information
            status["locked"] = self.client_locked
            if self.client_locked:
                status["lockedBy"] = self.authorized_client_id
                status["lockTimeRemaining"] = (LOCK_TIMEOUT_MS - (int(time.time() * 1000) - self.lock_timestamp)) // 1000
            
            self.client.publish(MQTT_STATUS_TOPIC, json.dumps(status))
        except Exception as e:
            print(f"Error publishing status: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            # Subscribe to topics
            client.subscribe(MQTT_PATTERN_TOPIC)
            client.subscribe(MQTT_DRAW_TOPIC)
            client.subscribe(MQTT_CAMERA_TOPIC)
            client.subscribe(MQTT_LOCK_REQUEST_TOPIC)
            print("Subscribed to flip/* topics")
        else:
            print(f"Failed to connect to MQTT broker with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        try:
            if topic == MQTT_LOCK_REQUEST_TOPIC:
                self._handle_lock_message(payload)
            elif topic == MQTT_PATTERN_TOPIC:
                self._handle_pattern_message(payload)
            elif topic == MQTT_DRAW_TOPIC:
                self._handle_draw_message(payload)
            elif topic == MQTT_CAMERA_TOPIC:
                self._handle_camera_message(payload)
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
            traceback.print_exc()
    
    def _handle_lock_message(self, payload):
        try:
            data = json.loads(payload)
            action = data.get('action')
            client_id = data.get('clientId')
            
            if not client_id:
                print("Missing client ID in lock request")
                self._publish_lock_response(client_id, False, "Missing client ID")
                return
                
            if action == "lock":
                success = self._request_client_lock(client_id)
                self._publish_lock_response(client_id, success)
            elif action == "unlock":
                if self.client_locked and self.authorized_client_id == client_id:
                    success = self._release_client_lock(client_id)
                    self._publish_lock_response(client_id, success)
                else:
                    self._publish_lock_response(client_id, False, "Not authorized to unlock")
            elif action == "heartbeat":
                # update timestamp if this client holds the lock
                if self.client_locked and self.authorized_client_id == client_id:
                    self.lock_timestamp = int(time.time() * 1000)
                    # Publish updated lock status with new timeout
                    self._publish_lock_response(client_id, True)
            else:
                print(f"Unknown lock action: {action}")
                self._publish_lock_response(client_id, False, f"Unknown action: {action}")
        except json.JSONDecodeError:
            print("Invalid JSON in lock request")
    
    def _handle_pattern_message(self, payload):
        data = json.loads(payload)
        
        # check for client ID and authorization
        client_id = data.get('clientId')
        if not self._is_client_authorized(client_id):
            print(f"Pattern command rejected: Unauthorized client {client_id}")
            return
        
        if 'id' in data and data['enable']:
            pattern_type = data['id']
            pattern_speed = data.get('speed', 2.0)  # Default to 2.0
                        
            # Navigate to pattern page
            if self.page_manager.current_page_id != "pattern":
                page_ids = self.page_manager.get_page_ids()
                if "pattern" in page_ids:
                    print(f"Switching to pattern page from {self.page_manager.current_page_id}")
                    self.page_manager.navigate_to("pattern")
                else:
                    print("Pattern page not available")
                    return
            
            if hasattr(self.page_manager.current_page, 'set_pattern_by_id'):
                self.page_manager.current_page.set_pattern_by_id(pattern_type)
                self.page_manager.enabled = True
                if hasattr(self.page_manager.current_page, 'set_speed'):
                    self.page_manager.current_page.set_speed(float(pattern_speed))
            else:
                print("Current page doesn't support pattern setting")
        else:
            if self.page_manager.current_page_id == "pattern":
                self.page_manager.enabled = False
    
    def _handle_draw_message(self, payload):
        data = json.loads(payload)
        
        client_id = data.get('clientId')
        del data['clientId']
        if not self._is_client_authorized(client_id):
            print(f"Draw command rejected: Unauthorized client {client_id}")
            return
            
        if self.page_manager.current_page_id != "sketchpad":
            page_ids = self.page_manager.get_page_ids()
            if "sketchpad" in page_ids:
                print(f"Switching to sketchpad page from {self.page_manager.current_page_id}")
                self.page_manager.navigate_to("sketchpad")
            else:
                print("Sketchpad page not available")
                return
        else:
            self.page_manager.current_page.set_drawing(data)

    def cleanup(self):
        if self._status_task:
            self._status_task.cancel()
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            
    # Client lock implementation methods
    def _request_client_lock(self, client_id):
        """Request a lock for the specified client"""
        # If already locked by this client, just refresh timestamp
        if self.client_locked and self.authorized_client_id == client_id:
            self.lock_timestamp = int(time.time() * 1000)
            return True
        
        # If not locked or lock timed out, grant the lock
        if not self.client_locked or (int(time.time() * 1000) - self.lock_timestamp > LOCK_TIMEOUT_MS):
            self.client_locked = True
            self.authorized_client_id = client_id
            self.lock_timestamp = int(time.time() * 1000)
            print(f"Device locked by client: {client_id}")
            return True
        
        # Otherwise, lock request denied
        return False
    
    def _release_client_lock(self, client_id):
        """Release a lock held by the specified client"""
        # Only the lock owner can release it
        if self.client_locked and self.authorized_client_id == client_id:
            self.client_locked = False
            self.authorized_client_id = ""
            print(f"Device unlocked by client: {client_id}")
            return True
        return False
    
    def _is_client_authorized(self, client_id):
        if not client_id:
            return False
        self._check_lock_timeout()
        
        if self.client_locked:
            return self.authorized_client_id == client_id
        else:
            return False
                
    def _check_lock_timeout(self):
        if self.client_locked and (int(time.time() * 1000) - self.lock_timestamp > LOCK_TIMEOUT_MS):
            print(f"Client lock timed out for: {self.authorized_client_id}")
            self.client_locked = False
            self.authorized_client_id = ""
            self._publish_lock_response(self.authorized_client_id, False, "Lock timed out")

    def _publish_lock_response(self, client_id, success, message=None):
        response = {
            "clientId": client_id,
            "success": success,
            "locked": self.client_locked
        }
        
        if message:
            response["message"] = message
            
        if self.client_locked:
            response["lockedBy"] = self.authorized_client_id
            response["timeRemaining"] = (LOCK_TIMEOUT_MS - (int(time.time() * 1000) - self.lock_timestamp)) // 1000
        
        self.client.publish(MQTT_LOCK_RESPONSE_TOPIC, json.dumps(response))
        print(f"Publishing lock response: {response}")