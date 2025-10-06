import snap7
from snap7.util import set_bool, get_bool
from snap7.types import Areas

client = snap7.client.Client()
client.connect("192.168.2.23", 0, 1)

if client.get_connected():
    print("✅ Connected to PLC")

    # --- Read current memory byte ---
    data = client.read_area(Areas.MK, 0, 0, 1)
    print("Before:", data, "M0.0 =", get_bool(data, 0, 0))

    # --- Toggle the M0.0 bit ---
    set_bool(data, 0, 0, not get_bool(data, 0, 0))
    client.write_area(Areas.MK, 0, 0, data)

    # --- Verify ---
    data2 = client.read_area(Areas.MK, 0, 0, 1)
    print("After:", data2, "M0.0 =", get_bool(data2, 0, 0))

    client.disconnect()
else:
    print("❌ Connection failed")
