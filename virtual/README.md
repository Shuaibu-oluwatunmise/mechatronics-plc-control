The markdown is rendering incorrectly because the code blocks aren't closed properly. Here's the corrected version:
markdown# Gesture Control System for Industrial Automation

Control virtual and physical PLCs using Leap Motion hand gestures for touchless industrial automation.

## Quick Start

1. Start PLCSIM Advanced with instance "GestureControl"
2. Navigate to `MECHATRONICS\virtual\`
3. Double-click `launcher.bat`
4. Position hand 15-25cm above Leap Motion controller
5. Perform gestures (swipe left/right/up/down)

## Supported Gestures

| Gesture | Motion | PLC Bit | Use Case |
|---------|--------|---------|----------|
| Swipe Left | Fast leftward hand movement | gestures.0 | Navigate/decrease |
| Swipe Right | Fast rightward hand movement | gestures.1 | Navigate/increase |
| Swipe Up | Fast upward hand movement | gestures.2 | Confirm/activate |
| Swipe Down | Fast downward hand movement | gestures.3 | Cancel/deactivate |
| Circle | Circular motion (reserved) | gestures.4 | Future use |

## Documentation

- **[SETUP.md](SETUP.md)** - Complete installation and configuration guide
- **[USER_GUIDE.md](USER_GUIDE.md)** - Daily usage, troubleshooting, and integration examples

## System Architecture
┌─────────────────┐
│  Leap Motion    │  Hand tracking (110+ FPS)
│   Controller    │
└────────┬────────┘
│
v
┌─────────────────┐
│  Python         │  gesture_detector.py
│  Gesture        │  Filters & debounce
│  Detector       │
└────────┬────────┘
│ TCP/IP (localhost:5000)
v
┌─────────────────┐
│  C# Bridge      │  PLCSIMBridge.exe
│  (.NET 8.0)     │  Auto-discovers PLC tags
└────────┬────────┘
│ PLCSIM Advanced API
v
┌─────────────────┐
│  Virtual PLC    │  PLCSIM Advanced
│  (PLCSIM)       │  Instance: GestureControl
└────────┬────────┘
│
v
┌─────────────────┐
│  TIA Portal     │  Ladder logic / SCL code
│  Program        │  Responds to gesture bits
└─────────────────┘

## Requirements

### Software

- **PLCSIM Advanced V6.0** or higher
- **TIA Portal V19** or higher
- **Python 3.8+** with Leap Motion SDK
- **Visual Studio 2022** (for development only)
- **.NET 8.0 Runtime** (included)

### Hardware

- **Leap Motion Controller** (USB hand tracking device)
- **Windows 10/11** (64-bit)
- **Minimum 8GB RAM**

## Project Structure
MECHATRONICS/
├── tia_project/
│   └── PIONEER/
├── virtual/
│   ├── launcher.bat
│   ├── README.md
│   ├── SETUP.md
│   ├── release/
│   │   └── PLCSIMBridge.exe
│   ├── gesture_control/
│   │   ├── gesture_config.json
│   │   ├── gesture_detector.py
│   │   └── plc_virtual_communicator.py
│   ├── PLCSIMBridge/
│   │   └── Program.cs
│   └── Tests/
└── physical/

## Configuration

Gesture mappings in `gesture_control/gesture_config.json`:
```json
{
  "gesture_sets": {
    "primary": {
      "byte": 0,
      "gestures": {
        "swipe_left": 0,
        "swipe_right": 1,
        "swipe_up": 2,
        "swipe_down": 3,
        "circle": 4
      }
    }
  },
  "active_set": "primary"
}
Performance

Gesture Detection: 110-120 FPS
End-to-End Latency: <20ms
Bridge Communication: <5ms per operation
Resource Usage: ~150MB RAM, <10% CPU

Safety Notes
Designed for non-safety-critical applications. For production:

Implement timeout logic
Use physical E-stop buttons
Add confirmation gestures for critical operations
Test thoroughly before connecting to physical systems

Version History
v1.0 (Current) - Virtual PLC support

5 gesture types with configurable mapping
Auto-discovery C# bridge
Real-time hand tracking at 110+ FPS

Next Steps
Testing

Add PLC logic in TIA Portal
Test gesture sequences
Adjust sensitivity in gesture_detector.py

Production

Integrate with NX/robot control via OPC UA
Implement physical PLC support
Add data logging and diagnostics

Support
For issues:

Check SETUP.md troubleshooting section
Verify PLCSIM Advanced is running
Review console output from both Python and C# bridge
Ensure Leap Motion service is running

License
Educational/Research use - Siemens PLCSIM Advanced license required