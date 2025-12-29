# 🎯 Gesture Control for Siemens PLCs

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![.NET 8.0](https://img.shields.io/badge/.NET-8.0-512BD4.svg)](https://dotnet.microsoft.com/)
[![TIA Portal](https://img.shields.io/badge/TIA_Portal-V16+-009999.svg)](https://www.siemens.com/tia-portal)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)

> **Touchless industrial automation using hand gestures to control Siemens S7 PLCs - both virtual (PLCSIM Advanced) and physical hardware**

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Performance Metrics](#performance-metrics)
- [Use Cases](#use-cases)
- [Documentation](#documentation)
- [Future Extensions](#future-extensions)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

---

## 🎯 Overview

This project implements a **touchless gesture control system** for industrial automation, enabling operators to control Siemens S7-1200/1500 PLCs through **hand gestures** captured by a Leap Motion controller. The system supports both **virtual PLCs** (PLCSIM Advanced) and **physical PLCs** over Ethernet.

### The Problem
Traditional industrial HMI requires physical contact with control panels, creating:
- Hygiene concerns in clean rooms and food processing
- Slower operator response times during emergencies
- Limited mobility in hazardous environments
- Inefficient workflows requiring proximity to control stations

### Our Solution
A modular, sensor-agnostic architecture that:
1. **Captures hand gestures** with Leap Motion (110+ FPS tracking)
2. **Filters and debounces** movements to prevent false triggers
3. **Communicates with PLCs** via C# bridge (virtual) or snap7 (physical)
4. **Updates PLC memory bits** in real-time (<20ms latency)
5. **Triggers ladder logic** programmed in TIA Portal

The architecture is **extensible** - replace gesture detection with computer vision for safety applications like PPE detection, proximity sensing, or quality inspection.

---

## ✨ Key Features

- 🎮 **5 Gesture Types** - Swipe left/right/up/down, circle (configurable via JSON)
- 🖥️ **Dual PLC Support** - Works with both PLCSIM Advanced and physical S7 PLCs
- 🔌 **Plug-and-Play** - Automated launcher script handles startup sequence
- ⚡ **Ultra-Low Latency** - <20ms gesture-to-PLC response time
- 🔒 **Safety Features** - Debouncing, cooldown periods, timeout logic
- 📊 **Auto-Discovery** - C# bridge automatically detects PLC tags
- 🔧 **Fully Documented** - Complete setup guides and user manuals
- 🌐 **Network-Ready** - Physical PLC control over Ethernet (snap7 protocol)

---

## 🏗️ System Architecture

### Virtual PLC (PLCSIM Advanced)
```
┌─────────────────┐       TCP/IP      ┌──────────────────┐    PLCSIM API    ┌─────────────────┐
│  Leap Motion    │ ══════════════════> │   C# Bridge      │ ═══════════════> │ PLCSIM Advanced │
│   Controller    │                    │  (.NET 8.0)      │                  │  (Virtual PLC)  │
│                 │                    │                  │                  │                 │
│ • Hand Tracking │                    │ • TCP Server     │                  │ • Instance:     │
│ • 110+ FPS      │                    │ • Tag Discovery  │                  │   GestureControl│
└─────────────────┘                    │ • Memory Access  │                  └─────────────────┘
         ↓                             └──────────────────┘                           ↓
    Python Script                       PLCSIMBridge.exe                       TIA Portal
  gesture_detector.py                    (localhost:5000)                    (%MB0 gestures)
```

### Physical PLC (S7-1200/1500)
```
┌─────────────────┐                    ┌──────────────────┐    Ethernet     ┌─────────────────┐
│  Leap Motion    │ ══ Direct Call ══> │  Python snap7    │ ═══════════════> │  Physical PLC   │
│   Controller    │                    │   Communicator   │   S7 Protocol   │  S7-1200/1500   │
│                 │                    │                  │                  │                 │
│ • Hand Tracking │                    │ • Direct Mem.    │                  │ • PUT/GET       │
│ • 110+ FPS      │                    │   Read/Write     │                  │   Enabled       │
└─────────────────┘                    │ • Network Comm.  │                  └─────────────────┘
         ↓                             └──────────────────┘                           ↓
    Python Script                      plc_communicator.py                  Industrial Equipment
  gesture_detector.py                  (via python-snap7)                   (Motors, Conveyors)
```

**Key Difference:**
- **Virtual:** Requires C# bridge to interface with PLCSIM Advanced API
- **Physical:** Direct Python-to-PLC communication over Ethernet (no bridge needed)

---

## 🛠️ Technologies Used

### Hardware
- **Leap Motion Controller (LM-010)** - Infrared hand tracking sensor
- **Siemens S7-1200/1500 PLC** - Industrial programmable logic controller
- **PLCSIM Advanced V6.0+** - Virtual PLC simulation environment

### Software Stack

#### Virtual PLC Side
![C#](https://img.shields.io/badge/C%23-10.0-239120?logo=csharp&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-8.0-512BD4?logo=dotnet&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8-3776AB?logo=python&logoColor=white)

- **C# Bridge:** .NET 8.0 console application
- **PLCSIM API:** Siemens.Simatic.Simulation.Runtime.Api.x64.dll
- **Python:** Leap Motion SDK, socket communication

#### Physical PLC Side
![Python](https://img.shields.io/badge/Python-3.8-3776AB?logo=python&logoColor=white)
![snap7](https://img.shields.io/badge/snap7-0.7-green?logo=python&logoColor=white)

- **python-snap7:** S7 protocol implementation
- **Leap Motion SDK:** Ultraleap Gemini API
- **NumPy:** Data processing

#### PLC Programming
![TIA Portal](https://img.shields.io/badge/TIA_Portal-V16+-009999)

- Ladder Logic (LAD)
- Structured Control Language (SCL)
- Function Block Diagram (FBD)

---

## 🚀 Quick Start

### Prerequisites

**Hardware:**
- Leap Motion Controller
- PC with Windows 10/11 (64-bit)
- (For physical PLC) Network connection to S7-1200/1500

**Software:**
- Python 3.8+
- TIA Portal V16+
- PLCSIM Advanced V6.0+ (for virtual setup)
- Visual Studio 2022 (only if modifying C# bridge)

### Installation

#### Virtual PLC Setup
```powershell
# Clone repository
git clone https://github.com/Shuaibu-oluwatunmise/mechatronics-plc-control.git
cd mechatronics-plc-control/virtual

# Create Python environment
python -m venv ..\..\..\leap_env
..\..\..\leap_env\Scripts\activate

# Install dependencies
pip install leap-sdk

# Start PLCSIM Advanced with instance name "GestureControl"
# Then run the launcher
launcher.bat
```

#### Physical PLC Setup
```powershell
# Navigate to physical folder
cd mechatronics-plc-control/physical/gesture_control

# Activate environment
..\..\..\..\leap_env\Scripts\activate

# Install snap7
pip install python-snap7 leap-sdk

# Configure PLC network settings in TIA Portal
# Enable PUT/GET communication
# Then run gesture detector
python gesture_detector.py
# Enter PLC IP when prompted (e.g., 192.168.0.1)
```

### Running the System

**Virtual PLC:**
1. Start PLCSIM Advanced (instance: "GestureControl")
2. Double-click `virtual/launcher.bat`
3. Perform gestures over Leap Motion

**Physical PLC:**
1. Connect to PLC network
2. Run `python gesture_detector.py`
3. Enter PLC IP address
4. Perform gestures

**See [Setup Guides](virtual/SETUP.md) for detailed instructions.**

---

## 📁 Project Structure
```
mechatronics-plc-control/
├── virtual/                         # Virtual PLC (PLCSIM) setup
│   ├── launcher.bat                # ⭐ One-click startup
│   ├── README.md                   # Virtual-specific docs
│   ├── SETUP.md                    # Installation guide
│   ├── USER_GUIDE.md               # Daily usage guide
│   │
│   ├── gesture_control/            # Python gesture detection
│   │   ├── gesture_detector.py    # Main detection script
│   │   ├── gesture_config.json    # Gesture → bit mapping
│   │   └── plc_virtual_communicator.py  # TCP client for bridge
│   │
│   ├── PLCSIMBridge/               # C# bridge source code
│   │   └── Program.cs             # PLCSIM API integration
│   │
│   ├── release/                    # Compiled bridge executable
│   │   └── PLCSIMBridge.exe       # Standalone .NET app
│   │
│   └── Tests/                      # Connection test scripts
│
├── physical/                       # Physical PLC setup
│   ├── README.md                  # Physical-specific docs
│   ├── SETUP.md                   # Network configuration guide
│   ├── USER_GUIDE.md              # Operations manual
│   │
│   └── gesture_control/           # Python scripts
│       ├── gesture_detector.py    # Main script (snap7 version)
│       ├── gesture_config.json    # Same as virtual
│       └── plc_communicator.py    # snap7 Ethernet communication
│
├── tia_project/                   # TIA Portal sample projects
│   └── PIONEER/                   # Example PLC program
│
└── README.md                      # This file
```

---

## 📊 Performance Metrics

| Metric | Virtual PLC | Physical PLC |
|--------|-------------|--------------|
| **Gesture Detection** | 110-120 FPS | 110-120 FPS |
| **Communication Latency** | <5ms | 10-50ms (network) |
| **Total Response Time** | <20ms | 30-70ms |
| **CPU Usage** | <10% | <10% |
| **RAM Usage** | ~150MB | ~150MB |
| **Concurrent Connections** | Multiple | 1 per PLC* |

*S7 protocol limitation: one PUT/GET connection at a time

---

## 🎯 Use Cases

### Current Implementation: Gesture Control
- Navigate HMI screens without touching panels
- Trigger machine start/stop sequences
- Adjust parameters via swipe gestures
- Emergency stop via downward swipe

### Extensible Architecture: Computer Vision
Replace `gesture_detector.py` with computer vision for:

**Safety Applications:**
- **PPE Detection:** Hard hat/gloves missing → deny machine access
- **Proximity Sensing:** Person enters danger zone → pause equipment
- **Posture Monitoring:** Unsafe posture detected → trigger alarm

**Quality Inspection:**
- **Defect Detection:** Vision spots flaw → divert to reject bin
- **Presence Verification:** Component missing → stop assembly line
- **Color/Size Matching:** Part dimensions verified → route to correct station

**Process Automation:**
- **Barcode/RFID Reading:** Product ID → configure machine parameters
- **Object Counting:** Vision tracks parts → update inventory in PLC
- **Level Monitoring:** Tank fill level → control valves

The `plc_communicator.py` module can be imported by any Python application needing PLC access.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Virtual README](virtual/README.md) | PLCSIM Advanced overview |
| [Virtual Setup Guide](virtual/SETUP.md) | Installation and configuration |
| [Virtual User Guide](virtual/USER_GUIDE.md) | Daily operations and troubleshooting |
| [Physical README](physical/README.md) | Physical PLC overview |
| [Physical Setup Guide](physical/SETUP.md) | Network setup and snap7 installation |
| [Physical User Guide](physical/USER_GUIDE.md) | Operations manual |

---

## 🔮 Future Extensions

### Planned Features
- [ ] Multi-hand support for dual-operator control
- [ ] Voice command integration
- [ ] Mobile app for remote gesture control
- [ ] Web-based configuration interface
- [ ] Data logging and analytics dashboard
- [ ] Support for additional PLC brands (Allen-Bradley, Mitsubishi)

### Research Directions
- [ ] Gesture vocabulary expansion (10+ gestures)
- [ ] Adaptive learning from operator corrections
- [ ] Integration with AR/VR for training simulations
- [ ] Edge computing deployment (Raspberry Pi)

---

## 🔒 Safety Notice

**This system is NOT safety-rated and must not be used as a primary safety mechanism.**

**For production deployment:**
- Always use physical E-stop buttons
- Implement PLC-side timeout logic (safe state if no gesture for X seconds)
- Require confirmation gestures for critical operations
- Test thoroughly in safe environment before connecting to machinery
- Follow all industrial safety protocols (ISO 13849, IEC 62061)
- Get supervisor/safety officer approval

**The system is designed for:**
- ✅ Monitoring and non-critical control
- ✅ HMI navigation and parameter adjustment
- ✅ Training and demonstration
- ❌ Emergency stop functions
- ❌ Safety-critical interlocks
- ❌ Standalone operation without backup systems

---

## 🤝 Contributing

Feedback and suggestions are welcome!

### If You're Interested:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request with detailed description

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note:** Siemens PLCSIM Advanced requires a separate license from Siemens.

---

## 🙏 Acknowledgments

- **Middlesex University London** - Academic support and lab facilities
- **Anthropic's Claude** - Development assistance, debugging, and architecture design
- **Ultraleap** - Leap Motion SDK and documentation
- **Siemens** - TIA Portal, PLCSIM Advanced, and technical resources
- **Open Source Community** - python-snap7, .NET ecosystem, and countless tutorials

---

## 👨‍💻 Author

**Raph (Oluwatunmise Shuaibu)** - BEng Mechatronics and Robotics Student  
Middlesex University London (Graduating July 2025)

- 🔗 GitHub: [@Shuaibu-oluwatunmise](https://github.com/Shuaibu-oluwatunmise)
- 📧 Email: shuaibuoluwatunmise@gmail.com
- 💼 LinkedIn: [Oluwatunmise Shuaibu](https://linkedin.com/in/oluwatunmise-shuaibu-881519257)

---

## 📸 Demo

> *Coming soon: Video demonstration of virtual and physical PLC control*

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ and lots of ☕ in London

</div>