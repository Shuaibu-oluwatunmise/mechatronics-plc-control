import snap7
from snap7.util import *
from snap7.types import Areas
import time
import json
import os

class PLCCommunicator:
    def __init__(self, ip='192.168.2.23', rack=0, slot=1, config_file='gesture_config.json'):
        """
        Initialize physical PLC communicator using snap7
        
        Args:
            ip: PLC IP address
            rack: PLC rack number (usually 0)
            slot: PLC slot number (usually 1 for CPU)
            config_file: Path to gesture configuration JSON
        """
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.client = None
        
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
        self.byte_offset = gesture_set['byte']
        
        for gesture_name, bit_offset in gesture_set['gestures'].items():
            self.gesture_addresses[gesture_name] = ('M', self.byte_offset, bit_offset)
        
        print(f"[CONFIG] Loaded gesture set '{active_set}'")
        print(f"[CONFIG] Memory: %MB{self.byte_offset}")
        print(f"[CONFIG] Gestures: {list(gesture_set['gestures'].keys())}")
    
    def connect(self):
        """Connect to physical PLC via Ethernet"""
        try:
            print(f"[CONNECT] Connecting to PLC at {self.ip}...")
            self.client = snap7.client.Client()
            self.client.connect(self.ip, self.rack, self.slot)
            
            if self.client.get_connected():
                print(f"[SUCCESS] Connected to PLC at {self.ip}")
                return True
            else:
                print(f"[ERROR] Connection failed (not connected)")
                return False
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from PLC"""
        try:
            if self.client and self.client.get_connected():
                self.client.disconnect()
                print("[DISCONNECT] Disconnected from PLC")
        except Exception as e:
            print(f"[ERROR] Disconnect error: {e}")
    
    def write_gesture(self, gesture_name, value):
        """
        Write a gesture state to PLC memory
        
        Args:
            gesture_name: Name of gesture (e.g., 'swipe_left')
            value: Boolean value (True/False)
        """
        if gesture_name not in self.gesture_addresses:
            print(f"[ERROR] Unknown gesture: {gesture_name}")
            return False
        
        area, byte_offset, bit_offset = self.gesture_addresses[gesture_name]
        
        try:
            # Read current memory byte
            data = self.client.read_area(Areas.MK, 0, byte_offset, 1)
            current_value = data[0]
            
            # Modify the specific bit
            if value:
                new_value = current_value | (1 << bit_offset)
            else:
                new_value = current_value & ~(1 << bit_offset)
            
            # Write back to PLC
            data[0] = new_value
            self.client.write_area(Areas.MK, 0, byte_offset, data)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Write failed: {e}")
            return False
    
    def read_gesture(self, gesture_name):
        """
        Read a gesture state from PLC memory
        
        Args:
            gesture_name: Name of gesture
            
        Returns:
            Boolean value or None on error
        """
        if gesture_name not in self.gesture_addresses:
            print(f"[ERROR] Unknown gesture: {gesture_name}")
            return None
        
        area, byte_offset, bit_offset = self.gesture_addresses[gesture_name]
        
        try:
            data = self.client.read_area(Areas.MK, 0, byte_offset, 1)
            bit_value = bool(data[0] & (1 << bit_offset))
            return bit_value
            
        except Exception as e:
            print(f"[ERROR] Read failed: {e}")
            return None
    
    def read_all_gestures(self):
        """Read all gesture states at once"""
        try:
            data = self.client.read_area(Areas.MK, 0, self.byte_offset, 1)
            byte_value = data[0]
            
            states = {}
            for gesture_name, (_, _, bit_offset) in self.gesture_addresses.items():
                states[gesture_name] = bool(byte_value & (1 << bit_offset))
            
            return states
            
        except Exception as e:
            print(f"[ERROR] Read all failed: {e}")
            return None
    
    def get_connection_state(self):
        """Check if PLC is still connected"""
        try:
            return "CONNECTED" if self.client and self.client.get_connected() else "DISCONNECTED"
        except Exception:
            return "DISCONNECTED"


# Test the communicator
if __name__ == "__main__":
    print("=" * 60)
    print("  Physical PLC Communicator Test")
    print("=" * 60)
    
    # Configuration
    PLC_IP = input("Enter PLC IP address [192.168.2.23]: ").strip() or "192.168.2.23"
    
    plc = PLCCommunicator(ip=PLC_IP, rack=0, slot=1)
    
    if plc.connect():
        print("\n[TEST] Connection successful!")
        print(f"[TEST] PLC State: {plc.get_connection_state()}")
        
        # Test write/read for each gesture
        print("\n[TEST] Testing gesture write/read operations:")
        for gesture in plc.gesture_addresses.keys():
            print(f"\n  Testing: {gesture}")
            
            # Write ON
            success = plc.write_gesture(gesture, True)
            if success:
                time.sleep(0.1)
                value = plc.read_gesture(gesture)
                print(f"    Write ON:  {'✓' if value else '✗'}")
            
            # Write OFF
            success = plc.write_gesture(gesture, False)
            if success:
                time.sleep(0.1)
                value = plc.read_gesture(gesture)
                print(f"    Write OFF: {'✓' if not value else '✗'}")
        
        # Read all at once
        print("\n[TEST] Reading all gestures:")
        all_states = plc.read_all_gestures()
        if all_states:
            for gesture, state in all_states.items():
                print(f"    {gesture}: {state}")
        
        plc.disconnect()
        print("\n[TEST] All tests completed successfully!")
    else:
        print("\n[ERROR] Could not connect to PLC")
        print("Check:")
        print("  - PLC IP address is correct")
        print("  - PLC is powered on")
        print("  - Network cable connected")
        print("  - Firewall allows snap7 communication")
