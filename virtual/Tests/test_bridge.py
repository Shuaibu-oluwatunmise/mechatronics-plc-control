import socket
import time

def test_bridge():
    print("Testing C# Bridge Connection...")
    
    try:
        # Connect to the bridge
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5000))
        print("✓ Connected to bridge on port 5000\n")
        
        # Test Write command
        print("Testing WRITE M0.0 = 1")
        sock.sendall(b"WRITE M 0 0 1\n")
        response = sock.recv(1024).decode().strip()
        print(f"Response: {response}\n")
        
        time.sleep(0.5)
        
        # Test Read command
        print("Testing READ M0.0")
        sock.sendall(b"READ M 0 0\n")
        response = sock.recv(1024).decode().strip()
        print(f"Response: {response}\n")
        
        # Test Write OFF
        print("Testing WRITE M0.0 = 0")
        sock.sendall(b"WRITE M 0 0 0\n")
        response = sock.recv(1024).decode().strip()
        print(f"Response: {response}\n")
        
        # Test Read again
        print("Testing READ M0.0 again")
        sock.sendall(b"READ M 0 0\n")
        response = sock.recv(1024).decode().strip()
        print(f"Response: {response}\n")
        
        sock.close()
        print("✓ All tests completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bridge()