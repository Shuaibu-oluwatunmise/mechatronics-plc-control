# Physical PLC Gesture Control

Direct Ethernet communication with physical Siemens S7-1200/1500 PLCs using Python snap7 library.

## Overview

This system connects Leap Motion gesture detection directly to physical PLCs without requiring a C# bridge. Communication happens over TCP/IP using the snap7 library which implements Siemens S7 protocol.

## Quick Start

1. Connect PC to same network as PLC
2. Note PLC IP address (e.g., 192.168.0.1)
3. Ensure PLC is in RUN mode
4. Run: `python gesture_detector.py`
5. Enter PLC IP when prompted
6. Perform gestures over Leap Motion

## System Architecture
┌─────────────────┐
│  Leap Motion    │  Hand tracking
│   Controller    │
└────────┬────────┘
│
v
┌─────────────────┐
│  Python         │  gesture_detector.py
│  Gesture        │  Detection + snap7
│  Detector       │
└────────┬────────┘
│ S7 Protocol over TCP/IP
v
┌─────────────────┐
│  Physical PLC   │  S7-1200/1500
│  (Ethernet)     │  %MB0 = gestures
└────────┬────────┘
│
v
┌─────────────────┐
│  Industrial     │  Motors, conveyors,
│  Equipment      │  robots, indicators
└─────────────────┘

## Key Differences from Virtual Setup

| Aspect | Virtual (PLCSIM) | Physical PLC |
|--------|------------------|--------------|
| Communication | C# Bridge + API | snap7 over Ethernet |
| Connection | localhost:5000 | PLC IP address |
| Startup | PLCSIM + Bridge | Just Python script |
| Requirements | PLCSIM Advanced license | Network access to PLC |
| Latency | <5ms | 10-50ms (network dependent) |

## Requirements

### Hardware
- Physical Siemens S7-1200 or S7-1500 PLC
- Ethernet connection to PLC
- Leap Motion Controller

### Software
- Python 3.8+ with `python-snap7` and `leap-sdk`
- TIA Portal (for PLC programming)
- Network access to PLC

### Network
- PC and PLC on same subnet OR
- PC with direct Ethernet connection to PLC OR
- VPN access to industrial network

## Project Structure
physical/
├── README.md              # This file
├── SETUP.md              # Network setup, installation
├── USER_GUIDE.md         # Daily usage guide
└── gesture_control/
├── gesture_config.json
├── gesture_detector.py
└── plc_communicator.py

## Supported PLCs

Tested with:
- S7-1200 series (CPU 1211C, 1212C, 1214C, 1215C, 1217C)
- S7-1500 series (CPU 1511, 1513, 1515, 1516, 1518)

Should work with any S7 PLC that supports:
- PUT/GET communication (must be enabled in TIA Portal)
- Ethernet/PROFINET interface

## Safety Notice

**This is NOT a safety-rated system.** Physical PLCs control real machinery:

- Never use gestures for emergency stops
- Always have physical E-stop buttons
- Test thoroughly in safe environment first
- Implement PLC-side timeout logic
- Follow all industrial safety protocols
- Get supervisor approval before deployment

## Network Security

When deploying on industrial networks:
- Use VLANs to isolate gesture control traffic
- Implement MAC address filtering
- Use strong passwords on PLC
- Log all gesture commands
- Consider read-only mode for monitoring applications

## Future Expansion

This architecture supports more than gestures:

**Computer Vision:**
- Object detection (OpenCV, YOLO)
- Person detection for safety zones
- Quality inspection with image recognition
- PPE compliance checking

**Other Sensors:**
- Voice commands
- RFID/NFC readers
- IoT sensor data
- Mobile device input

The `plc_communicator.py` module can be imported by any Python application needing PLC access.

## Documentation

- **[SETUP.md](SETUP.md)** - Network configuration, snap7 installation, PLC setup
- **[USER_GUIDE.md](USER_GUIDE.md)** - Daily operations, troubleshooting

## Performance

- **Gesture Detection:** 110-120 FPS
- **Network Latency:** 10-50ms (depends on network)
- **Total Response:** 30-70ms (gesture to PLC)
- **Concurrent Connections:** 1 per PLC (S7 limitation)

## Version

v1.0 - Physical PLC support with snap7
- Direct Ethernet communication
- 5 configurable gesture types
- Auto-discovery of PLC CPU info
- Connection state monitoring

## Next Steps

- See [SETUP.md](SETUP.md) for detailed installation
- Configure PLC network settings in TIA Portal
- Test connection with `python plc_communicator.py`
- Deploy gesture detection with `python gesture_detector.py`