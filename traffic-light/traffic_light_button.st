(* Traffic light with a pedestrian button, for OpenPLC Editor v4.
   Add the two NEW variables to the table (Class = Local), then replace
   the whole code body with the one below.

   Name        Type  Location  Initial
   red         BOOL  %QX0.0
   yellow      BOOL  %QX0.1
   green       BOOL  %QX0.2
   ped_button  BOOL  %QX0.3              <- NEW: Python writes this (coil 3)
   walk        BOOL  %QX0.4              <- NEW: pedestrian "walk" light (coil 4)
   state       INT   %QW0      0
   step_timer  TON

   Behaviour: green now lasts 10 s, but pressing the button cuts it short
   and goes straight to yellow. Walk is on while the light is red. *)

(* ---- code body ---- *)
CASE state OF
  0: (* RED for 5 s, pedestrians walk *)
    red := TRUE;  yellow := FALSE; green := FALSE; walk := TRUE;
    ped_button := FALSE;  (* ignore presses while already walking *)
    step_timer(IN := TRUE, PT := T#5s);
    IF step_timer.Q THEN step_timer(IN := FALSE); state := 1; END_IF;

  1: (* GREEN for 10 s, or until the button is pressed *)
    red := FALSE; yellow := FALSE; green := TRUE;  walk := FALSE;
    step_timer(IN := TRUE, PT := T#10s);
    IF step_timer.Q OR ped_button THEN
      step_timer(IN := FALSE); ped_button := FALSE; state := 2;
    END_IF;

  2: (* YELLOW for 2 s *)
    red := FALSE; yellow := TRUE;  green := FALSE; walk := FALSE;
    step_timer(IN := TRUE, PT := T#2s);
    IF step_timer.Q THEN step_timer(IN := FALSE); state := 0; END_IF;

ELSE
  state := 0;
END_CASE;
