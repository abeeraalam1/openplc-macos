# Traffic light dashboard

A window that shows the OpenPLC traffic light live (red, yellow, green, walk/don't walk,
current state) and has a button that presses the pedestrian button. It talks to the PLC
over Modbus TCP at 127.0.0.1:502, using the same addresses as `traffic_light_button.st`:

| Modbus address     | PLC variable | Meaning                         |
|--------------------|--------------|---------------------------------|
| coil 0             | %QX0.0       | red                             |
| coil 1             | %QX0.1       | yellow                          |
| coil 2             | %QX0.2       | green                           |
| coil 3             | %QX0.3       | pedestrian button (dashboard writes) |
| coil 4             | %QX0.4       | walk                            |
| holding register 0 | %QW0         | state (0 red, 1 green, 2 yellow) |

## Run it (Mac, conda)

1. Start the traffic light program in OpenPLC with the Modbus server on, as before.
2. In Terminal:

   ```bash
   conda activate base          # or whichever env you used for read_lights.py
   pip install pymodbus         # skip if read_lights.py already works
   cd path/to/dashboard
   python dashboard.py
   ```

3. Click **Press pedestrian button** while the light is green: it turns yellow, then red with WALK.

tkinter comes with conda's Python, so nothing else needs installing. If the PLC isn't
running, the window says so in red and keeps retrying, so you can start the PLC afterwards.
Close the window to quit.
