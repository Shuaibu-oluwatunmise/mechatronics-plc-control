#!/usr/bin/env python3
"""
Leap Motion → Physical PLC Gesture Control
Detects hand gestures and sends them to a Siemens PLC via snap7.
"""

import leap
import time
from plc_communicator import PLCCommunicator


class GestureToPLC(leap.Listener):
    def __init__(self, plc_communicator):
        super().__init__()
        self.plc = plc_communicator

        # Frame and gesture timing
        self.frame_count = 0
        self.start_time = time.time()
        self.gesture_cooldown = 0.5  # seconds between same gesture triggers
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

        for hand in event.hands:
            gesture = self.detect_gesture(hand)
            if gesture != "none":
                self.handle_gesture(gesture)

        # Print stats every ~2 seconds
        if self.frame_count % 120 == 0:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            print(f"[STATS] Frames: {self.frame_count} | FPS: {fps:.1f} | Hands: {len(event.hands)}")

    def detect_gesture(self, hand) -> str:
        """Detect gestures from hand data."""
        try:
            # Get finger states
            if hasattr(hand, 'digits'):
                fingers_extended = [d.is_extended for d in hand.digits]
            elif hasattr(hand, 'fingers'):
                fingers_extended = [f.is_extended for f in hand.fingers]
            else:
                return "none"

            if len(fingers_extended) < 5:
                return "none"

            # Detect swipes via palm velocity
            palm_velocity = getattr(hand.palm, 'velocity', None)
            if palm_velocity:
                speed = (palm_velocity.x**2 + palm_velocity.y**2 + palm_velocity.z**2) ** 0.5
                if speed > 800:
                    # Horizontal swipe
                    if abs(palm_velocity.x) > abs(palm_velocity.y):
                        return "swipe_right" if palm_velocity.x > 0 else "swipe_left"
                    # Vertical swipe
                    else:
                        return "swipe_up" if palm_velocity.y > 0 else "swipe_down"

            return "none"

        except Exception as e:
            if self.frame_count % 120 == 0:
                print(f"[ERROR] Gesture detection: {e}")
            return "none"

    def handle_gesture(self, gesture: str):
        """Send gesture to PLC with cooldown."""
        now = time.time()
        gesture_map = {
            "swipe_left": "swipe_left",
            "swipe_right": "swipe_right",
            "swipe_up": "swipe_up",
            "swipe_down": "swipe_down",
        }
        plc_gesture = gesture_map.get(gesture)
        if plc_gesture is None:
            return

        # Enforce cooldown
        last_time = self.last_trigger_time.get(plc_gesture, 0)
        if now - last_time < self.gesture_cooldown:
            return

        print(f"[GESTURE] Detected: {gesture} → {plc_gesture}")
        success = self.plc.write_gesture(plc_gesture, True)
        if success:
            print(f"[PLC] ✓ Sent {plc_gesture}")
            time.sleep(0.1)
            self.plc.write_gesture(plc_gesture, False)
            self.last_trigger_time[plc_gesture] = now
        else:
            print(f"[PLC] ✗ Failed to send {plc_gesture}")


def main():
    print("=" * 60)
    print("  Leap Motion → Physical PLC Gesture Control")
    print("=" * 60)

    plc_ip = input("Enter PLC IP address [192.168.2.23]: ").strip() or "192.168.2.23"
    print("\n[INIT] Connecting to PLC...")
    plc = PLCCommunicator(ip=plc_ip, rack=0, slot=1)

    if not plc.connect():
        print("[ERROR] Could not connect to PLC.")
        print("Check IP, cable, RUN mode, and firewall.")
        return

    state = plc.get_connection_state()
    print(f"[PLC] State: {state}")
    if state not in ("RUN", "CONNECTED"):
        print(f"[WARNING] PLC is in {state} mode.")
        proceed = input("Continue anyway? [y/N]: ").strip().lower()
        if proceed != 'y':
            plc.disconnect()
            return

    print("\n[READY] PLC connection established.")
    print("[INIT] Starting Leap Motion tracking...")

    listener = GestureToPLC(plc)
    connection = leap.Connection()
    connection.add_listener(listener)

    print("\nSupported gestures:")
    print("  • Swipe left / right / up / down")
    print("\nPress Ctrl+C to exit.")
    print("-" * 60)

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping gesture detection...")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        connection.remove_listener(listener)
        plc.disconnect()
        print("[SHUTDOWN] Complete.")


if __name__ == "__main__":
    main()
