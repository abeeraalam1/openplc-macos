"""Live dashboard for the OpenPLC traffic light (traffic_light_button.st).

Polls the PLC over Modbus TCP and draws the lights; the button presses the
pedestrian button. Needs only pymodbus (tkinter ships with Python).

coil 0..4        = red, yellow, green, ped_button, walk  (%QX0.0..%QX0.4)
holding reg 0    = state  (0 red, 1 green, 2 yellow)    (%QW0)
"""
import logging
import tkinter as tk

from pymodbus.client import ModbusTcpClient

HOST, PORT = "127.0.0.1", 502
POLL_MS = 250

logging.getLogger("pymodbus").setLevel(logging.CRITICAL)  # we show errors in the window instead

OFF = "#2b2b2b"
COLORS = {"red": "#ff3b30", "yellow": "#ffcc00", "green": "#34c759", "walk": "#ffffff"}
STATE_NAMES = {0: "RED (walk)", 1: "GREEN", 2: "YELLOW"}


class Dashboard:
    def __init__(self, root):
        self.root = root
        self.client = ModbusTcpClient(HOST, port=PORT)
        root.title("OpenPLC traffic light")
        root.configure(bg="#111")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=260, height=420, bg="#111", highlightthickness=0)
        self.canvas.pack(padx=20, pady=(20, 10))
        # Traffic light housing and three lamps
        self.canvas.create_rectangle(20, 10, 130, 330, fill="#1c1c1e", outline="#444", width=2)
        self.lamps = {
            name: self.canvas.create_oval(35, y, 115, y + 80, fill=OFF, outline="#000", width=2)
            for name, y in (("red", 25), ("yellow", 130), ("green", 235))
        }
        # Pedestrian signal
        self.canvas.create_rectangle(155, 120, 245, 230, fill="#1c1c1e", outline="#444", width=2)
        self.walk_text = self.canvas.create_text(200, 175, text="DON'T\nWALK", fill="#ff9500",
                                                 font=("Helvetica", 16, "bold"), justify="center")
        self.state_text = self.canvas.create_text(130, 370, text="", fill="#ddd", font=("Helvetica", 15))
        self.button_text = self.canvas.create_text(130, 400, text="", fill="#8e8e93", font=("Helvetica", 12))

        self.button = tk.Button(root, text="Press pedestrian button", command=self.press,
                                font=("Helvetica", 14), padx=10, pady=6)
        self.button.pack(pady=(0, 10))
        self.status = tk.Label(root, text="Connecting…", fg="#8e8e93", bg="#111", font=("Helvetica", 11), wraplength=260)
        self.status.pack(pady=(0, 15))

        root.protocol("WM_DELETE_WINDOW", self.close)
        self.poll()

    def ensure_connected(self):
        if self.client.connected:
            return True
        return self.client.connect()

    def poll(self):
        try:
            if not self.ensure_connected():
                self.show_offline(f"Can't reach the PLC at {HOST}:{PORT}. Is it running with Modbus on?")
            else:
                coils = self.client.read_coils(0, count=5)
                regs = self.client.read_holding_registers(0, count=1)
                if coils.isError() or regs.isError():
                    self.show_offline(f"Modbus error: {coils if coils.isError() else regs}")
                else:
                    self.show(coils.bits[:5], regs.registers[0])
        except Exception as exc:  # connection dropped mid-read; retry next tick
            self.client.close()
            self.show_offline(f"Connection lost: {exc}")
        self.root.after(POLL_MS, self.poll)

    def show(self, bits, state):
        red, yellow, green, button, walk = bits
        for name, on in (("red", red), ("yellow", yellow), ("green", green)):
            self.canvas.itemconfigure(self.lamps[name], fill=COLORS[name] if on else OFF)
        if walk:
            self.canvas.itemconfigure(self.walk_text, text="WALK", fill=COLORS["walk"])
        else:
            self.canvas.itemconfigure(self.walk_text, text="DON'T\nWALK", fill="#ff9500")
        self.canvas.itemconfigure(self.state_text, text=f"State {state}: {STATE_NAMES.get(state, '?')}")
        self.canvas.itemconfigure(self.button_text, text="Button pressed, waiting…" if button else "")
        if not (red or yellow or green):
            # Modbus answers but nothing is lit: the PLC program isn't running
            self.status.configure(text=f"Connected to {HOST}:{PORT}, but all lights are off. "
                                       "Is the PLC program running?", fg="#ff9f0a")
        else:
            self.status.configure(text=f"Connected to {HOST}:{PORT}", fg="#34c759")
        self.button.configure(state="normal")

    def show_offline(self, message):
        for lamp in self.lamps.values():
            self.canvas.itemconfigure(lamp, fill=OFF)
        self.canvas.itemconfigure(self.walk_text, text="—", fill="#8e8e93")
        self.canvas.itemconfigure(self.state_text, text="")
        self.canvas.itemconfigure(self.button_text, text="")
        self.status.configure(text=message, fg="#ff453a")
        self.button.configure(state="disabled")

    def press(self):
        try:
            result = self.client.write_coil(3, True)
            if result.isError():
                self.status.configure(text=f"Button write failed: {result}", fg="#ff453a")
        except Exception as exc:
            self.status.configure(text=f"Button write failed: {exc}", fg="#ff453a")

    def close(self):
        self.client.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()
