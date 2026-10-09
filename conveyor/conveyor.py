"""Drive the OpenPLC ladder-logic conveyor over Modbus TCP.

coil 8  start_btn   (%QX1.0)  write   coil 12 motor      (%QX1.4)  read
coil 9  stop_btn    (%QX1.1)  write   coil 13 batch_done (%QX1.5)  read
coil 10 part_sensor (%QX1.2)  write   holding reg 1 part_count (%QW1)
coil 11 reset_btn   (%QX1.3)  write

Usage: python3 conveyor.py watch|start|stop|part|reset|sim
"""
import sys
import time

from pymodbus.client import ModbusTcpClient

HOST, PORT = "127.0.0.1", 502
START, STOP, SENSOR, RESET, MOTOR = 8, 9, 10, 11, 12
PULSE = 0.3  # seconds a "button" stays pressed; longer than a PLC scan


def pulse(client, coil):
    """Press and release, like a real momentary push button."""
    client.write_coil(coil, True)
    time.sleep(PULSE)
    client.write_coil(coil, False)


def status(client):
    coils = client.read_coils(MOTOR, count=2)
    regs = client.read_holding_registers(1, count=1)
    if coils.isError() or regs.isError():
        return None
    motor, done = coils.bits[:2]
    return motor, done, regs.registers[0]


def show(client):
    s = status(client)
    if s is None:
        print("Modbus error")
        return
    motor, done, count = s
    print(f"{time.strftime('%H:%M:%S')}  motor={'RUN ' if motor else 'stop'}  "
          f"boxes={count}  {'BATCH DONE' if done else ''}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "watch"
    client = ModbusTcpClient(HOST, port=PORT)
    if not client.connect():
        raise SystemExit(f"Could not connect to {HOST}:{PORT}. Is the PLC running with the Modbus server on?")
    try:
        if cmd == "watch":
            while True:
                show(client)
                time.sleep(1)
        elif cmd in ("start", "stop", "part", "reset"):
            pulse(client, {"start": START, "stop": STOP, "part": SENSOR, "reset": RESET}[cmd])
            time.sleep(0.2)
            show(client)
        elif cmd == "sim":
            pulse(client, START)
            while True:
                time.sleep(1.5)  # a box every couple of seconds
                s = status(client)
                if s is None or not s[0]:
                    break
                pulse(client, SENSOR)
                show(client)
            show(client)
            print("Belt stopped. Run 'reset' then 'sim' again for another batch.")
        else:
            raise SystemExit(__doc__)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()


if __name__ == "__main__":
    main()
