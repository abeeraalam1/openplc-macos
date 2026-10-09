(* Traffic light in Structured Text for OpenPLC Editor v4.
   In the editor, add these variables in the POU's variable table
   (Class = Local), then paste the code body below into the ST editor.

   Name    Type  Location  Initial
   red     BOOL  %QX0.0
   yellow  BOOL  %QX0.1
   green   BOOL  %QX0.2
   state   INT   %QW0      0
   step_timer  TON

   Modbus mapping (once the Modbus server is enabled):
     coil 0 = red, coil 1 = yellow, coil 2 = green, holding register 0 = state *)

(* ---- code body ---- *)
CASE state OF
  0: (* RED for 5 s *)
    red := TRUE;  yellow := FALSE; green := FALSE;
    step_timer(IN := TRUE, PT := T#5s);
    IF step_timer.Q THEN step_timer(IN := FALSE); state := 1; END_IF;

  1: (* GREEN for 4 s *)
    red := FALSE; yellow := FALSE; green := TRUE;
    step_timer(IN := TRUE, PT := T#4s);
    IF step_timer.Q THEN step_timer(IN := FALSE); state := 2; END_IF;

  2: (* YELLOW for 2 s *)
    red := FALSE; yellow := TRUE;  green := FALSE;
    step_timer(IN := TRUE, PT := T#2s);
    IF step_timer.Q THEN step_timer(IN := FALSE); state := 0; END_IF;

ELSE
  state := 0;
END_CASE;
