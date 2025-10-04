#!/usr/bin/env python3
"""
Leap Motion → PLC Gesture Control
Detects hand gestures and sends them to PLCSIM Advanced via bridge
"""

import leap
import time
from typing import Dict, List
from plc_virtual_communicator import PLCVirtualCommunicator


class GestureToPLC(leap.Listener):
    def __init__(self, plc_communicator):
        super().__init__()
        self.plc = plc_communicator
        
        # Frame counting
        self.frame_count = 0
        self.start_time = time.time()
        
        # Gesture state tracking
        self.last_gesture = "none"
        self.gesture_cooldown = 0.5  # 500ms between same gesture triggers
        self.last_trigger_time = {}
        
        print("[LEAP] Gesture detector initialized")
        
    def on_connection_event(self, event):
        print("[LEAP] Connected to Leap Motion service")
        
    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()
        print(f"[LEAP] Device found: {info.serial}")
        
    def on_tracking_event(self, event):
        self.frame_count += 1
        
        # Process each hand
        for hand in event.hands:
            gesture = self.detect_gesture(hand)
            if gesture != "none":
                self.handle_gesture(gesture)
        
        # Stats every 2 seconds
        if self.frame_count % 120 == 0:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            print(f"[STATS] Frames: {self.frame_count} | FPS: {fps:.1f} | Hands: {len(event.hands)}")
    
    def detect_gesture(self, hand) -> str:
        """Detect gestures from hand data"""
        try:
            # Get finger extension states
            fingers_extended = []
            if hasattr(hand, 'digits'):
                fingers_extended = [digit.is_extended for digit in hand.digits]
            elif hasattr(hand, 'fingers'):
                fingers_extended = [finger.is_extended for finger in hand.fingers]
            else:
                return "none"
            
            if len(fingers_extended) < 5:
                return "none"
            
            # Count extended fingers
            extended_count = sum(fingers_extended)
            
            # Get palm direction for swipe detection
            palm_direction = hand.palm.direction
            palm_velocity = hand.palm.velocity if hasattr(hand.palm, 'velocity') else None
            
            # Swipe detection (based on palm velocity and direction)
            if palm_velocity:
                speed = (palm_velocity.x**2 + palm_velocity.y**2 + palm_velocity.z**2) ** 0.5
                
                if speed > 800:  # Fast movement threshold
                    # Horizontal swipes
                    if abs(palm_velocity.x) > abs(palm_velocity.y):
                        return "swipe_right" if palm_velocity.x > 0 else "swipe_left"
                    # Vertical swipes
                    else:
                        return "swipe_up" if palm_velocity.y > 0 else "swipe_down"
            
            # Circle gesture (fist with index finger extended, rotating)
            # This is simplified - you can enhance based on your needs
            if extended_count == 1 and fingers_extended[1]:  # Only index extended
                # Could add rotation detection here
                # For now, we'll use grab_strength as a proxy
                if hand.grab_strength < 0.3:  # Relatively open hand
                    return "circle"
            
            # Pointing (index finger only)
            if extended_count == 1 and fingers_extended[1]:
                return "pointing"
            
            # Peace sign (index and middle)
            if extended_count == 2 and fingers_extended[1] and fingers_extended[2]:
                return "peace"
            
            # Open palm (all fingers extended)
            if extended_count == 5:
                return "open_palm"
            
            return "none"
            
        except Exception as e:
            if self.frame_count % 120 == 0:  # Don't spam errors
                print(f"[ERROR] Gesture detection: {e}")
            return "none"
    
    def handle_gesture(self, gesture: str):
        """Send gesture to PLC with cooldown"""
        current_time = time.time()
        
        # Map detected gestures to PLC gestures
        gesture_map = {
            "swipe_left": "swipe_left",
            "swipe_right": "swipe_right",
            "swipe_up": "swipe_up",
            "swipe_down": "swipe_down",
            "pointing": "circle",  # Map pointing to circle for now
            "open_palm": None,     # Ignore
            "peace": None          # Ignore
        }
        
        plc_gesture = gesture_map.get(gesture)
        if plc_gesture is None:
            return
        
        # Check cooldown
        last_time = self.last_trigger_time.get(plc_gesture, 0)
        if current_time - last_time < self.gesture_cooldown:
            return  # Too soon
        
        # Trigger gesture
        print(f"[GESTURE] Detected: {gesture} → {plc_gesture}")
        success = self.plc.write_gesture(plc_gesture, True)
        
        if success:
            print(f"[PLC] ✓ Sent {plc_gesture}")
            time.sleep(0.1)  # Hold briefly
            self.plc.write_gesture(plc_gesture, False)
            self.last_trigger_time[plc_gesture] = current_time
        else:
            print(f"[PLC] ✗ Failed to send {plc_gesture}")


def main():
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 12 + "Leap Motion → PLC Gesture Control" + " " * 13 + "║")
    print("╚" + "═" * 58 + "╝\n")
    
    # Connect to PLC bridge
    print("[INIT] Connecting to PLC bridge...")
    plc = PLCVirtualCommunicator()
    if not plc.connect():
        print("[ERROR] Could not connect to PLC bridge")
        print("        Make sure PLCSIMBridge.exe is running")
        return
    
    print("[READY] PLC connection established\n")
    
    # Start Leap Motion tracking
    print("[INIT] Starting Leap Motion tracking...")
    listener = GestureToPLC(plc)
    connection = leap.Connection()
    connection.add_listener(listener)
    
    print("[READY] Gesture detection active")
    print("\nSupported gestures:")
    print("  • Swipe left/right/up/down (fast hand movement)")
    print("  • Point (index finger) → triggers 'circle' in PLC")
    print("\nPress Ctrl+C to exit\n")
    print("─" * 60 + "\n")
    
    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while True:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Stopping gesture detection...")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
    finally:
        connection.remove_listener(listener)
        plc.disconnect()
        print("[SHUTDOWN] Complete")


if __name__ == "__main__":
    main()