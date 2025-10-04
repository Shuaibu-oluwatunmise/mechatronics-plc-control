## USER_GUIDE.md
```markdown
# Physical PLC User Guide

Daily operations and usage guide for physical PLC gesture control.

## Quick Start
```powershell
cd MECHATRONICS\physical\gesture_control
python gesture_detector.py
Enter PLC IP when prompted, then perform gestures over Leap Motion.

Pre-Flight Checklist
Before starting:

 PLC powered on and in RUN mode
 Ethernet cable connected
 PC can ping PLC IP
 Leap Motion plugged in (green LED)
 TIA Portal program downloaded to PLC
 PUT/GET enabled in PLC


Gestures
GestureMotionPLC BitSwipe LeftFast leftwardgestures.%X0Swipe RightFast rightwardgestures.%X1Swipe UpFast upwardgestures.%X2Swipe DownFast downwardgestures.%X3CircleReservedgestures.%X4
Tips:

Move quickly (>800mm/s)
Keep hand 15-25cm above controller
500ms cooldown between same gestures


Console Output
[CONNECT] Connecting to PLC at 192.168.8.50...
[SUCCESS] Connected to PLC
[INFO] CPU: CPU 1215C DC/DC/DC
[STATS] Frames: 120 | FPS: 110.5
[GESTURE] Detected: swipe_right
[PLC] ✓ Sent swipe_right

TIA Portal Integration
Basic Output Control
Network 1: Swipe Right turns on Q0.0
───┤ ├gestures.%X1├──────────( Q0.0 )───
Counter
Network 1: Count swipes
───┤ ├gestures.%X1├──────[CTU]───
                        CV → MW10
State Machine (SCL)
CASE current_state OF
    0: // Idle
        IF gestures.%X1 THEN
            current_state := 1;
        END_IF;
    
    1: // Active
        IF gestures.%X0 THEN
            current_state := 0;
        END_IF;
END_CASE;
Safety Logic - Confirmation Required
// Require gesture twice within 3 seconds
IF gestures.%X1 AND NOT confirmed THEN
    confirmed := TRUE;
    confirm_timer(IN := TRUE, PT := T#3s);
END_IF;

IF confirm_timer.Q THEN
    confirmed := FALSE;
END_IF;

IF gestures.%X1 AND confirmed THEN
    DO_CRITICAL_ACTION;
    confirmed := FALSE;
END_IF;

Troubleshooting
Connection Lost
Symptoms: [ERROR] Write failed
Check:

Network cable connected
PLC in RUN mode
IP address conflict

Fix: Restart gesture_detector.py
Gestures Not Reaching PLC
Verify in console:
[PLC] ✓ Sent    ← Success
[PLC] ✗ Failed  ← Problem
If failures:

PUT/GET disabled → Re-enable in TIA Portal
PLC in STOP → Switch to RUN
Network issue → Check ping

Monitor in TIA Portal:

Go online
Watch gestures byte
Should toggle when gestures performed

Slow Response
If latency > 100ms:

Check: ping -t 192.168.8.50
Look for high ping or packet loss
Use direct connection
Check PLC scan cycle time


Network Performance
ConnectionLatencyDirect Cable10-20msSame Switch15-30msThrough Router40-60ms

Customization
Adjust Sensitivity
Edit gesture_detector.py line ~85:
pythonif speed > 800:  # Lower = more sensitive
Change Cooldown
Edit gesture_detector.py line ~27:
pythonself.gesture_cooldown = 0.5  # Seconds
Add Gestures

Update gesture_config.json with new bit
Add detection in gesture_detector.py
Update TIA Portal logic


Safety
This is NOT safety-rated.
Always have:

Physical E-stop buttons
Timeout logic in PLC
Independent safety systems

Emergency procedure:

Press physical E-stop
Switch PLC to STOP
Close Python script (Ctrl+C)


Multi-PLC Setup
Run separate instances for each PLC:
Terminal 1:
powershellpython gesture_detector.py
# Enter: 192.168.1.10
Terminal 2:
powershellpython gesture_detector.py
# Enter: 192.168.1.11

Maintenance
Weekly

Check cable connections
Verify PLC in RUN mode
Test all gestures

Monthly

Update: pip install --upgrade python-snap7
Backup TIA Portal project
Check network performance


FAQ
Q: Multiple users simultaneously?
A: No, S7 allows one PUT/GET connection per PLC.
Q: Network drops?
A: Restore connection and restart script.
Q: WiFi instead of Ethernet?
A: PC can use WiFi if on same network. PLC must be wired.
Q: Safety-rated?
A: No. Use only for non-critical operations.

For installation and setup, see SETUP.md