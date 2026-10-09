"""Read the OpenPLC traffic light over Modbus TCP.

coil 0..4        = red, yellow, green, ped_button, walk  (%QX0.0..%QX0.4)
holding reg 0    = state               (%QW0)
"""
import time

from pymodbus.client import ModbusTcpClient

HOST, PORT = "127.0.0.1", 502

client = ModbusTcpClient(HOST, port=PORT)
if not client.connect():
    raise SystemExit(f"Could not connect to {HOST}:{PORT}. Is the PLC running with the Modbus server on?")

try:
    while True:
        coils = client.read_coils(0, count=5)
        regs = client.read_holding_registers(0, count=1)
        if coils.isError() or regs.isError():
            print("Modbus error:", coils if coils.isError() else regs)
        else:
            red, yellow, green, button, walk = coils.bits[:5]
            lamp = "RED" if red else "YELLOW" if yellow else "GREEN" if green else "off"
            print(f"{time.strftime('%H:%M:%S')}  state={regs.registers[0]}  {lamp:6}  {'WALK' if walk else '':4}  {'(button pressed)' if button else ''}")
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    client.close()
