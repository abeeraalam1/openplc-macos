# OpenPLC restart cheat sheet (Mac)

How to bring everything back after a reboot or a break.

## 1. Start Docker
Open **Docker Desktop** from Applications. Wait until the whale icon in the menu bar says Docker is running.

## 2. Start the runtime
Open a new Terminal window and run:
```
docker start openplc-runtime
docker ps
```
`docker ps` should list `openplc-runtime` with ports **8443** and **502**.

**If `docker` says "command not found":** the PATH line is missing from `~/.zshrc`. Add it once:
```
echo 'export PATH="$PATH:/Applications/Docker.app/Contents/Resources/bin"' >> ~/.zshrc
source ~/.zshrc
```

**If the container is gone** (e.g. you deleted it), recreate it. Your programs live in the `openplc-runtime-data` volume, so they survive this:
```
docker run -d --name openplc-runtime \
  -p 8443:8443 -p 502:502 \
  -v openplc-runtime-data:/var/run/runtime \
  ghcr.io/autonomy-logic/openplc-runtime:latest
```

## 3. Connect the editor and start the PLC
1. Open **OpenPLC Editor** and your **TrafficLight** project.
2. Make sure the simulator is stopped (the editor is locked while it runs).
3. In **Device › Configuration**, the target is the OpenPLC Runtime (v4) at `127.0.0.1`, port `8443`. Log in with the username and password you created the first time.
4. Upload the program if you changed it, then **start the PLC**.
5. The Modbus TCP server (port **502**, under **Servers**) must be enabled in the project, or Python can't connect.

## 4. Run the Python scripts
Scripts are in the `traffic-light` folder (`read_lights.py`, `press_button.py`). In Terminal, from the folder where you saved them:
```
pip install pymodbus        # only needed once
python read_lights.py       # prints the lights every second, Ctrl+C to stop
python press_button.py      # in a 2nd window, while GREEN: cuts green short
```

## Modbus map
| Modbus address | PLC variable | Meaning |
|---|---|---|
| coil 0 | `red` %QX0.0 | red light |
| coil 1 | `yellow` %QX0.1 | yellow light |
| coil 2 | `green` %QX0.2 | green light |
| coil 3 | `ped_button` %QX0.3 | pedestrian button (Python writes) |
| coil 4 | `walk` %QX0.4 | walk light |
| holding reg 0 | `state` %QW0 | 0 red, 1 green, 2 yellow |

## Quick fixes
- **Python: "Could not connect"** → PLC not started, or Modbus server not enabled on port 502.
- **Editor buttons greyed out** → stop the simulator first.
- **Done for the day** → `docker stop openplc-runtime`, then quit Docker Desktop.
