"""Press the pedestrian button on the OpenPLC traffic light (coil 3 = %QX0.3)."""
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("127.0.0.1", port=502)
if not client.connect():
    raise SystemExit("Could not connect. Is the PLC running with the Modbus server on?")
result = client.write_coil(3, True)
print("Modbus error:", result) if result.isError() else print("Button pressed")
client.close()
