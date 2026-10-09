# Conveyor in ladder logic (OpenPLC Editor v4)

A belt motor with Start/Stop buttons, a photo-eye that counts boxes, and an
automatic stop after 5 boxes. Python presses the buttons and fakes the boxes.

Addresses start at `%QX1.0` / `%QW1`, so they never clash with the traffic light.

## 1. New project

File > New Project, name it `conveyor`, language **LD** (ladder), then open the `main` POU.

## 2. Variables (Class = Local)

Fill in Name, Type, Location and Initial Value. The Modbus column is only a note
of which number Python uses; the editor has no such column, so skip it.

| Name         | Type | Location | Initial | Modbus          |
|--------------|------|----------|---------|-----------------|
| start_btn    | BOOL | %QX1.0   |         | coil 8 (write)  |
| stop_btn     | BOOL | %QX1.1   |         | coil 9 (write)  |
| part_sensor  | BOOL | %QX1.2   |         | coil 10 (write) |
| reset_btn    | BOOL | %QX1.3   |         | coil 11 (write) |
| motor        | BOOL | %QX1.4   |         | coil 12 (read)  |
| batch_done   | BOOL | %QX1.5   |         | coil 13 (read)  |
| part_count   | INT  | %QW1     | 0       | holding reg 1   |
| batch_size   | INT  |          | 5       |                 |
| box_counter  | CTU  |          |         |                 |

The "buttons" are `%QX` coils, not `%IX` inputs, because Modbus can only write coils.

## 3. Rung 1: start/stop with seal-in

```
 |   start_btn      stop_btn    batch_done        motor   |
 |----| |-----+------|/|----------|/|-------------( )-----|
 |            |                                           |
 |   motor    |                                           |
 |----| |-----+                                           |
```

- `| |` = normally open contact, `|/|` = normally closed (negated) contact, `( )` = coil.
- The `motor` contact in parallel is the **seal-in**: once running, it keeps itself on
  after you let go of Start. Stop or a full batch breaks the circuit.

## 4. Rung 2: count boxes

```
 |   motor    part_sensor     +-----------+                      |
 |----| |--------| |----------| CU      Q |------( batch_done )--|
 |                            |           |                      |
 |   reset_btn                |           |                      |
 |----| |---------------------| R      CV |--- part_count        |
 |                            |           |                      |
 |               batch_size --| PV        |                      |
 |                            +-----------+                      |
 |                             box_counter (CTU)                 |
```

- Add a **function block**, pick **CTU**, name the instance `box_counter`.
- CU counts once on each rising edge, only while the belt runs.
- Q turns on when the count reaches PV (5), which opens the `batch_done` contact in rung 1.
- `reset_btn` zeroes the count so the belt can start again.

## 5. Run it

Save, compile, then upload from the editor to your Docker runtime and start the PLC
(the same way you uploaded the traffic light). This replaces the traffic light program on the runtime (one program at a time);
re-upload `traffic-light` whenever you want it back.

## 6. Drive it from Python

```
python3 conveyor.py watch     # live status, Ctrl+C to quit
python3 conveyor.py start     # press Start
python3 conveyor.py part      # one box passes the sensor
python3 conveyor.py stop      # press Stop
python3 conveyor.py reset     # clear the count
python3 conveyor.py sim       # hands-free: start, send boxes until the batch stops
```

Expected: `start` turns the motor on, five `part`s stop it with BATCH DONE,
`start` does nothing until `reset`.

## Gotchas we hit

- Paste the ASCII diagrams nowhere: they become rung comments. Drag real contacts/coils onto the rung.
- `stop_btn` and `batch_done` must be **Negated** contacts, and Q needs a real `batch_done` coil.
- New project = redo **Device > Configuration** (127.0.0.1:8443) and enable **Modbus TCP** under Servers.
- "Unknown program type ... in program instance": in **Resource > Instances**, set the Program
  column to your POU name (and don't give the instance the same name as the program).
