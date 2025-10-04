# Physical PLC Setup Guide

Complete setup instructions for physical PLC gesture control system.

## Prerequisites

### Hardware
- Siemens S7-1200 or S7-1500 PLC
- Ethernet cable (CAT5e or better)
- Network switch or router (optional)
- Leap Motion Controller
- Windows PC with Ethernet port

### Software
- TIA Portal V16 or higher
- Python 3.8 or higher
- Leap Motion SDK

---

## Part 1: Network Setup

### Option A: Direct Connection (Simplest)

Connect PC directly to PLC Ethernet port.

**1. Configure PLC IP in TIA Portal:**
- IP: `192.168.0.1`
- Subnet: `255.255.255.0`
- Download to PLC

**2. Configure PC IP:**
Windows Settings → Network → Ethernet → Properties

IP: 192.168.0.100
Subnet: 255.255.255.0
Gateway: (leave blank)


**3. Test Connection:**
```powershell
ping 192.168.0.1
Option B: Shared Network (Production)
Both PC and PLC connected to same switch/router.
1. Note your network subnet (e.g., 192.168.8.x)
2. Assign PLC IP in same subnet:

Example: 192.168.8.50
Subnet: 255.255.255.0
Gateway: Your router IP (e.g., 192.168.8.1)

3. PC gets IP automatically (DHCP)
4. Test Connection:
powershellping 192.168.8.50

Part 2: PLC Configuration in TIA Portal
Enable PUT/GET Communication
Critical: snap7 requires this to be enabled

Open your TIA Portal project
Select PLC → Properties → Protection & Security
Navigate to "Connection mechanisms"
Check "Permit access with PUT/GET"
Download to PLC

Create Gesture Tag

Navigate to: PLC → Program blocks → Default tag table
Add tag:

Name: gestures
Address: %MB0
Data type: Byte
Comment: "Leap Motion gesture inputs"


Bit mapping:

gestures.%X0 = Swipe Left
gestures.%X1 = Swipe Right
gestures.%X2 = Swipe Up
gestures.%X3 = Swipe Down
gestures.%X4 = Circle


Download to PLC

Verify PLC is in RUN Mode

Switch PLC to RUN (key switch or TIA Portal)
LED should show solid green


Part 3: Python Environment Setup
Install Python Packages
powershell# Navigate to project folder
cd C:\Users\shuai\leap_motion_control\MECHATRONICS\physical\gesture_control

# Activate virtual environment
..\..\..\..\leap_env\Scripts\activate

# Install snap7
pip install python-snap7

# Install Leap SDK (if not already installed)
pip install leap-sdk

# Verify installation
python -c "import snap7; print('snap7 version:', snap7.__version__)"
Test PLC Connection
powershellpython plc_communicator.py
Expected output:
Enter PLC IP address [192.168.0.1]: 192.168.8.50
[CONFIG] Loaded gesture set 'primary'
[CONNECT] Connecting to PLC at 192.168.8.50...
[SUCCESS] Connected to PLC
[INFO] CPU: CPU 1215C DC/DC/DC
[TEST] Testing gesture write/read operations:
  Testing: swipe_left
    Write ON:  ✓
    Write OFF: ✓
If you see errors:

Unreachable peer → Check IP address and network connection
ISO connect error → Enable PUT/GET in TIA Portal
CPU in STOP mode → Put PLC in RUN mode


Part 4: Windows Firewall Configuration
snap7 may be blocked by Windows Firewall.
Allow Python through firewall:

Windows Security → Firewall & network protection
Allow an app through firewall
Click "Change settings"
Find "Python" or add it manually
Check both "Private" and "Public" boxes
OK


Part 5: First Run
Start Gesture Detection
powershellcd C:\Users\shuai\leap_motion_control\MECHATRONICS\physical\gesture_control
python gesture_detector.py
Workflow:

Script asks for PLC IP
Connects to PLC via Ethernet
Checks PLC is in RUN mode
Starts Leap Motion tracking
Detects gestures and sends to PLC

Console output:
Enter PLC IP address [192.168.0.1]: 192.168.8.50

[INIT] Connecting to physical PLC...
[SUCCESS] Connected to PLC
[INFO] CPU: CPU 1215C DC/DC/DC
[READY] PLC connection established

[INIT] Starting Leap Motion tracking...
[LEAP] Connected to Leap Motion service
[LEAP] Device found: S332A000585
[READY] Gesture detection active

Troubleshooting
Cannot Connect to PLC
Check network:
powershellping 192.168.8.50
Check TIA Portal:

Go online with PLC
Verify IP address matches
Check PUT/GET is enabled

Check Windows:

Firewall allows Python
Correct network adapter selected
PC has IP in same subnet

Connection Works But Cannot Read/Write
Most common: PUT/GET not enabled

TIA Portal → PLC Properties → Protection & Security
Enable "Permit access with PUT/GET"
Download to PLC

PLC in STOP mode:

Switch to RUN mode
Check for compile errors in TIA Portal

Slow Response Time
Network latency:

Use direct connection instead of switch
Check for network congestion
Verify quality Ethernet cable

PLC scan cycle:

Optimize PLC program
Reduce OB1 cycle time


Next Steps
After successful setup, see USER_GUIDE.md for:

Daily operations
TIA Portal integration examples
Performance tuning
Safety guidelines
Troubleshooting during operation