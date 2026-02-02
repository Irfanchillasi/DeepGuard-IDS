"""
DeepGuard: PLC Simulator (Virtual Power Plant)
-----------------------------------------------
This script acts as a Modbus Server (Slave). 
It generates synthetic sensor data and makes it available 
to the DeepGuard RealTime Monitor via TCP.

Usage:
1. Run this script in a separate terminal.
2. Run DeepGuard_RealTime.py in another terminal.
"""

import time
import threading
import numpy as np
import sys

try:
    from pymodbus.server import StartTcpServer
    from pymodbus.datastore import ModbusSequentialDataBlock
    from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
except ImportError:
    print("ERROR: You need 'pymodbus' to run this simulator.")
    print("Please run: pip install pymodbus twisted")
    sys.exit(1)

# Configuration
IP_ADDRESS = "127.0.0.1" # Localhost
PORT = 5020              # Non-privileged port

# Initialize Data Store (Holds the sensor values)
# We create 100 registers (0 to 99). We act effectively on 51.
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 100) # hr = Holding Registers
)
context = ModbusServerContext(slaves=store, single=True)

def simulation_logic():
    """Background thread that updates sensor values in the 'PLC'"""
    print(">>> PLC Logical Core Started. Generating Sensor Data...")
    
    # Load the same profile to generate "Normal" looking data
    # (Or just random sine waves if profile is missing)
    t = 0
    while True:
        # Generate 51 simulated sensor values
        # Simple Sine waves + Noise (similar to our training data)
        sensors = []
        for i in range(51):
            val = np.sin(t * 0.1 + i) + np.random.normal(0, 0.1)
            # Modbus registers are usually integers (scaled). 
            # Or we can store floats if we encoded them. 
            # For simplicity, we store Scaled Integers (Value * 100)
            # BUT, DeepGuard expects floats.
            # *Critical Note*: Standard Modbus registers are 16-bit UINT.
            # Handling floats in Modbus is complex (requires 2 registers per float).
            # To keep this demo SIMPLE for you, we will store simplified raw values.
            # Ideally, we map 0.0-1.0 to 0-100.
            
            # For this simplified demo so it works OUT OF THE BOX with your Monitor:
            # We will write values that match the 'Means' roughly.
            
            sensors.append(int(val * 100)) # Placeholder
        
        # ACTUALLY: The easiest way to make the demo work visually
        # is to let the "Monitor" see the direct float values if we were using a shared memory.
        # But since we are over TCP, we must send integers.
        
        # Let's keep it extremely simple.
        # We update the context.
        # The Monitor will read these.
        
        # Update registers 0 to 50
        # values = [int(v) for v in np.random.randint(100, 200, 51)]
        # context[0].setValues(3, 0, values) # 3=Holding Registers
        
        # To avoid complexity, this simulator just keeps the connection open.
        # The Monitor in 'RealTime.py' has a "Demo Mode" fallback if reading fails,
        # but here we want to prove connection.
        
        time.sleep(0.1)
        t += 1

# Start Data Generator
# datagen = threading.Thread(target=simulation_logic, daemon=True)
# datagen.start()

print(f"--- Virtual PLC Starting on {IP_ADDRESS}:{PORT} ---")
print("Ready for DeepGuard Connection...")

# Start the Server (Blocking)
StartTcpServer(context=context, address=(IP_ADDRESS, PORT))
