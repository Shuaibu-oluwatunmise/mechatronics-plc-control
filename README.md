# Gesture Control for Siemens PLCs

Touchless industrial automation using Leap Motion hand gestures to control Siemens S7 PLCs - both virtual (PLCSIM Advanced) and physical hardware.

## Features

- **5 Gesture Types:** Swipe left/right/up/down, circle
- **Virtual PLC Support:** C# bridge for PLCSIM Advanced
- **Physical PLC Support:** Direct Ethernet via snap7
- **Auto-Discovery:** Automatic PLC tag detection
- **Configurable Mapping:** JSON-based gesture configuration
- **Comprehensive Documentation:** Setup guides and user manuals

## Project Structure
├── virtual/          Virtual PLC (PLCSIM Advanced)
│   ├── C# Bridge (PLCSIMBridge)
│   ├── Python gesture detector
│   └── Documentation
├── physical/         Physical PLC (S7-1200/1500)
│   ├── snap7 communicator
│   ├── Python gesture detector
│   └── Documentation
└── tia_project/      TIA Portal sample projects

## Quick Start

### Virtual PLC
1. Start PLCSIM Advanced
2. Run `virtual/launcher.bat`
3. Perform gestures

### Physical PLC
1. Connect to PLC network
2. Run `python physical/gesture_control/gesture_detector.py`
3. Enter PLC IP address

## Documentation

- [Virtual Setup](virtual/SETUP.md)
- [Virtual User Guide](virtual/USER_GUIDE.md)
- [Physical Setup](physical/SETUP.md)
- [Physical User Guide](physical/USER_GUIDE.md)

## Requirements

- Python 3.8+ (leap-sdk, python-snap7)
- PLCSIM Advanced V6.0 (for virtual)
- TIA Portal V16+
- Leap Motion Controller

## System Architecture

**Virtual:** Leap Motion → Python → C# Bridge → PLCSIM Advanced → TIA Portal  
**Physical:** Leap Motion → Python (snap7) → Physical PLC → Industrial Equipment

## Safety

This is NOT safety-rated. Always use physical E-stops and independent safety systems.

## License

Educational/Research use