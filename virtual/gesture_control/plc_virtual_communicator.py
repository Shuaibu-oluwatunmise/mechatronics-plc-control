import socket
import json
import os

class PLCVirtualCommunicator:
    def __init__(self, ip='localhost', port=5000, config_file='gesture_config.json'):
        self.ip = ip
        self.port = port
        self.bridge_socket = None
        
        # Load configuration
        self.load_config(config_file)
        
    def load_config(self, config_file):
        """Load gesture mappings from JSON config file"""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Get active gesture set
        active_set = config.get('active_set', 'primary')
        gesture_set = config['gesture_sets'][active_set]
        
        # Build address mapping
        self.gesture_addresses = {}
        byte_offset = gesture_set['byte']
        
        for gesture_name, bit_offset in gesture_set['gestures'].items():
            self.gesture_addresses[gesture_name] = ('M', byte_offset, bit_offset)
        
        print(f"Loaded gesture set '{active_set}' from {config_file}")
        print(f"  Byte: MB{byte_offset}")
        print(f"  Gestures: {list(gesture_set['gestures'].keys())}")
    
    def connect(self):
        """Connect to C# bridge"""
        try:
            print(f"Connecting to C# bridge at {self.ip}:{self.port}...")
            self.bridge_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.bridge_socket.connect((self.ip, self.port))
            print("✓ Connected to bridge")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from bridge"""
        try:
            if self.bridge_socket:
                self.bridge_socket.close()
                print("Disconnected from bridge")
        except Exception as e:
            print(f"Disconnect error: {e}")
    
    def write_gesture(self, gesture_name, value):
        """Write a gesture state to PLC via bridge"""
        if gesture_name not in self.gesture_addresses:
            print(f"Unknown gesture: {gesture_name}")
            return False
        
        area, byte_offset, bit_offset = self.gesture_addresses[gesture_name]
        
        try:
            command = f"WRITE {area} {byte_offset} {bit_offset} {1 if value else 0}\n"
            self.bridge_socket.sendall(command.encode())
            response = self.bridge_socket.recv(1024).decode().strip()
            return response == "OK"
        except Exception as e:
            print(f"Write error: {e}")
            return False
    
    def read_gesture(self, gesture_name):
        """Read a gesture state from PLC via bridge"""
        if gesture_name not in self.gesture_addresses:
            print(f"Unknown gesture: {gesture_name}")
            return None
        
        area, byte_offset, bit_offset = self.gesture_addresses[gesture_name]
        
        try:
            command = f"READ {area} {byte_offset} {bit_offset}\n"
            self.bridge_socket.sendall(command.encode())
            response = self.bridge_socket.recv(1024).decode().strip()
            return response == "1"
        except Exception as e:
            print(f"Read error: {e}")
            return None

# Test the communicator
if __name__ == "__main__":
    plc = PLCVirtualCommunicator()
    
    if plc.connect():
        print("\nTesting write/read operations:")
        
        for gesture in ['swipe_left', 'swipe_right', 'swipe_up', 'swipe_down', 'circle']:
            print(f"\n{gesture}:")
            plc.write_gesture(gesture, True)
            result = plc.read_gesture(gesture)
            print(f"  Write ON, Read: {result}")
            plc.write_gesture(gesture, False)
            result = plc.read_gesture(gesture)
            print(f"  Write OFF, Read: {result}")
        
        plc.disconnect()