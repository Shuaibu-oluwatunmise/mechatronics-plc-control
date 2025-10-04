# Gesture Control System - User Guide

## Quick Reference

### Starting the System

1. Start PLCSIM Advanced with instance "GestureControl"
2. Navigate to `MECHATRONICS\virtual\`
3. Double-click `launcher.bat`
4. Wait for "System ready" message
5. Position hand 15-25cm above Leap Motion controller

### Stopping the System

Press `Ctrl+C` in console window. The system shuts down gracefully. The bridge can remain running for your next session.

---

## Supported Gestures

| Gesture | Motion | PLC Bit | Typical Use |
|---------|--------|---------|-------------|
| Swipe Left | Fast leftward hand movement | gestures.%X0 | Navigate left/decrease |
| Swipe Right | Fast rightward hand movement | gestures.%X1 | Navigate right/increase |
| Swipe Up | Fast upward hand movement | gestures.%X2 | Confirm/activate |
| Swipe Down | Fast downward hand movement | gestures.%X3 | Cancel/deactivate |
| Circle | Circular motion (reserved) | gestures.%X4 | Future use |

### Gesture Tips

- **Speed threshold:** ~800mm/s (move quickly and deliberately)
- **Cooldown:** 500ms between repeated gestures
- **Hand position:** 15-25cm above controller, palm down
- **Environment:** Avoid bright overhead lights

---

## Console Output

### Python Console
[LEAP] Device found: S332A000585     ← Controller connected
[STATS] Frames: 120 | FPS: 62.1      ← Performance
[GESTURE] Detected: swipe_right      ← Gesture recognized
[PLC] ✓ Sent swipe_right             ← Sent to PLC

### Bridge Console
[RX] Client#1: WRITE M 0 1 1         ← Command received
[TX] Client#1: OK                    ← Success

Command format: `WRITE [Area] [Byte] [Bit] [Value]`

---

## TIA Portal Integration

### Basic Output Control

Ladder logic - Swipe right turns on Q0.0:
───┤ ├gestures.%X1├──────────( Q0.0 )───

### Counter Example

Count swipe right gestures:
───┤ ├gestures.%X1├──────[CTU]───
CV → MW10

### State Machine (SCL)
CASE current_state OF
0: // Idle state
IF gestures.%X1 THEN  // Swipe right to start
current_state := 1;
END_IF;
1: // Active state
    IF gestures.%X0 THEN  // Swipe left to stop
        current_state := 0;
    END_IF;
END_CASE;

### Safety Logic - Confirmation Required
// Require gesture twice within 3 seconds to confirm
IF gestures.%X1 AND NOT confirmed THEN
confirmed := TRUE;
confirm_timer(IN := TRUE, PT := T#3s);
END_IF;
IF confirm_timer.Q THEN
confirmed := FALSE;  // Timeout - reset
END_IF;
IF gestures.%X1 AND confirmed THEN
// Execute critical action only after confirmation
DO_CRITICAL_ACTION;
confirmed := FALSE;
END_IF;

---

## Customization

### Adjusting Gesture Sensitivity

Edit `gesture_detector.py`:
```python
# Line ~85: Speed threshold (lower = more sensitive)
if speed > 800:  # Default: 800mm/s
    ...

# Line ~50: Cooldown between same gestures
self.gesture_cooldown = 0.5  # Default: 500ms
Adding New Gestures
1. Update gesture_config.json:
json{
  "gesture_sets": {
    "primary": {
      "byte": 0,
      "gestures": {
        "swipe_left": 0,
        "swipe_right": 1,
        "swipe_up": 2,
        "swipe_down": 3,
        "circle": 4,
        "pinch": 5        ← New gesture
      }
    }
  }
}
2. Add detection logic in gesture_detector.py:
pythondef detect_gesture(self, hand) -> str:
    # Add your detection
    if hand.pinch_strength > 0.8:
        return "pinch"
    # ... existing code
3. Update TIA Portal logic to respond to gestures.%X5
Multiple Gesture Sets
Switch between different gesture modes:
json{
  "gesture_sets": {
    "primary": { "byte": 0, "gestures": {...} },
    "advanced": { "byte": 1, "gestures": {"rotate_cw": 0, "rotate_ccw": 1} }
  },
  "active_set": "advanced"    ← Change this to switch modes
}

Testing
Test Individual Gestures
Run the test script to verify each gesture works:
bashcd gesture_control
python plc_virtual_communicator.py
This automatically cycles through all gestures.
Monitor in TIA Portal

Go online with PLCSIM
Open watch table with gestures byte
Perform gestures
Observe bits toggle ON then OFF


Performance

Tracking Rate: 110-120 FPS
Latency: <20ms end-to-end
Resource Usage: ~150MB RAM, <10% CPU


Troubleshooting
No Gestures Detected
Check:

Leap Motion LED is green
Hand is 15-25cm above controller
Moving fast enough (~800mm/s)
No other applications using Leap Motion

Fix:
bash# Restart Leap Motion service
services.msc → Find "Leap Service" → Restart
Gestures Not Reaching PLC
Check:

Bridge console shows [RX] messages
Python shows [PLC] ✓ Sent messages
TIA Portal is online with PLCSIM

Fix:

Restart bridge: Close console, run launcher.bat again
Re-download TIA Portal program to PLCSIM

Too Many False Positives
Increase cooldown period:
pythonself.gesture_cooldown = 1.0  # 1 second instead of 0.5
Or increase speed threshold:
pythonif speed > 1200:  # Require faster movements

Safety Guidelines
This system is NOT safety-rated. For production use:

Always use physical E-stop buttons
Implement PLC timeout logic (safe state if no gesture for X seconds)
Require confirmation gestures for critical operations
Test thoroughly before connecting to machinery
Never rely solely on gestures for emergency stops


Advanced Features
Multi-Hand Detection
The system tracks both hands. Differentiate in gesture_detector.py:
pythondef on_tracking_event(self, event):
    for hand in event.hands:
        hand_type = "left" if str(hand.type) == "HandType.Left" else "right"
        # Use hand_type to trigger different actions
Gesture Sequences
Detect gesture combinations in PLC logic:
// Example: Swipe up then swipe right within 2 seconds
IF gestures.%X2 AND NOT sequence_started THEN
    sequence_started := TRUE;
    sequence_timer(IN := TRUE, PT := T#2s);
END_IF;

IF sequence_timer.Q THEN
    sequence_started := FALSE;
END_IF;

IF gestures.%X1 AND sequence_started THEN
    // Execute sequence action
    SEQUENCE_COMPLETE := TRUE;
    sequence_started := FALSE;
END_IF;

FAQ
Q: How many gestures can I have?
A: 8 bits per byte (0-7). Add more bytes for additional gestures.
Q: Can I use this with a physical PLC?
A: Yes, see MECHATRONICS/physical/ for snap7-based implementation.
Q: How do I change the instance name?
A: Run from command line: PLCSIMBridge.exe YourInstanceName
Q: Why do gestures sometimes not register?
A: Most common: moving too slowly. Swipe quickly (>800mm/s).
Q: Can I use this for safety applications?
A: No. This is not safety-rated. Use only for non-critical operations.

Performance Tuning
Reduce console output for better performance:
python# gesture_detector.py
# Change stats frequency
if self.frame_count % 300 == 0:  # Every 5 seconds instead of 2
    print(f"[STATS] ...")

## Quick Command Reference
```bash
# Start system
cd MECHATRONICS\virtual
launcher.bat

# Test gestures
cd gesture_control
python plc_virtual_communicator.py

# Run bridge manually (PowerShell)
cd release
.\PLCSIMBridge.exe GestureControl

# Run bridge manually (CMD)
cd release
PLCSIMBridge.exe GestureControl

# Check Leap Motion service
services.msc

For detailed setup instructions, see SETUP.md