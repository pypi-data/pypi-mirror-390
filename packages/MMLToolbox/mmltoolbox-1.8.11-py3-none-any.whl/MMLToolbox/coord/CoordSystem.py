import time
import gclib
import tkinter as tk
import numpy as np

from dataclasses import dataclass
from .WASDHandler import WASDHandler
from MMLToolbox.util.LogHandler import LogHandler


@dataclass
class PIDParams:
    Kp: float
    Kd: float
    Ki: float


PID_PARAMS_NORMAL = {
    "X": PIDParams(5, 15, 1),
    "Y": PIDParams(10, 20, 2),
    "Z": PIDParams(48, 106, 20)
}

PID_PARAMS_PRECISION = {
    "X": PIDParams(15, 15, 1),
    "Y": PIDParams(27, 15, 4),
    "Z": PIDParams(48, 106, 20)
}


class CoordSystem:
    """Handles communication with Feinmess/Galil devices via RS232."""

    def __init__(self, log_handler: LogHandler, com_port: str = None):
        com_port = 'COM3 --baud 19200' if com_port is None else com_port
        self._log_handler = log_handler
        self._log_handler.init_log("coord")

        self.galil_tool = gclib.py()
        self.galil_tool.GOpen(com_port)
        print(f"Connecting System: {self.galil_tool.GInfo()}")

        self._mum_to_counts = 10
        self._status_motor_break = False
        self._is_init_position = False

    ################################
    # Public Functions
    ################################

    def do_init_positioning(self, do_repositioning:bool=False):
        if not self._is_init_position or do_repositioning:
          blocking_time = 480
          start_time = time.time()
          self.galil_tool.GCommand("XQ#NEWINIT")
          while (time.time() - start_time) < blocking_time:
              time.sleep(10)
              if float(self.galil_tool.GCommand("MG _XQ")) < 0:
                  self._is_init_position = True
                  print("Initialization Coord-System done")
                  break
          
          if not self._is_init_position:
              print("Max initialization time exceeded.\nRepeat do_init_positioning")
          
    def send_command(self, command: str):
        """Send a specific command."""
        self.galil_tool.GCommand(command)

    def relative_pos(self, x=None, y=None, z=None):
        """Move an axis relative to its current position."""
        self._prepare_movement()

        active_axis = ''

        if isinstance(x, list):
            self._set_axis_relative('X', x)
            active_axis += 'X'
        if isinstance(y, list):
            self._set_axis_relative('Y', y)
            active_axis += 'Y'
        if isinstance(z, list):
            self._set_axis_relative('Z', z)
            self.galil_tool.GCommand('SB 1')
            self.galil_tool.GCommand('WT 500')
            active_axis += 'Z'

        print("Starting movement!")
        self.galil_tool.GCommand('BG ' + active_axis)
        self.galil_tool.GMotionComplete(active_axis)
        self.galil_tool.GCommand('CB 1')
        print("Movement complete!")

    def absolute_pos(self, x=None, y=None, z=None, precision_mode: bool = False):
        """Move an axis to an absolute position."""
        if not self._status_motor_break:
            self._motor_on_break_off()

        active_axis = ''
        self._set_pid_parameter(precision_mode)
        is_z_axis_set = False

        if isinstance(x, list):
            self._set_axis_absolute('X', x, precision_mode)
            self.galil_tool.GCommand('SHX')
            active_axis += 'X'
        if isinstance(y, list):
            self._set_axis_absolute('Y', y, precision_mode)
            self.galil_tool.GCommand('SHY')
            active_axis += 'Y'
        if isinstance(z, list):
            self._set_axis_absolute('Z', z, precision_mode)
            self.galil_tool.GCommand('SHZ')
            self.galil_tool.GCommand('SB 1')
            self.galil_tool.GCommand('WT 500')
            active_axis += 'Z'
            is_z_axis_set = True

        self.galil_tool.GCommand('BG' + active_axis)
        time.sleep(0.5)

        if precision_mode:
            self.galil_tool.GCommand(f"MC {active_axis}")
            pos_ok, speed_ok = self._do_precision_pos(active_axis)
            self._set_pid_parameter(False)
        else:
            self.galil_tool.GMotionComplete(active_axis)
            pos_ok, speed_ok = self._do_precision_pos(active_axis)

        if is_z_axis_set and not precision_mode:
            self.galil_tool.GCommand('CB 1')
            self.galil_tool.GCommand('MOZ')

        self._write_log(x, y, z, precision_mode, pos_ok, speed_ok)

    def get_pos(self) -> np.ndarray:
        """Return the current position of all axes in µm."""
        data = self.galil_tool.GCommand('TP').split(',')
        data = [self._counts2pos(d) * -1 for d in data]
        data[1] *= -1
        return np.array(data)

    def wasd_movement(self):
        """Open a GUI to move the system with WASD keys."""
        root = tk.Tk()
        WASDHandler(root, self).pack(fill="both", expand=True)
        root.mainloop()

    def close(self):
        """Close the connection properly."""
        self.galil_tool.GCommand('CB 1')
        self.galil_tool.GCommand('MO')
        self.galil_tool.GCommand('AB')
        self.galil_tool.GClose()
        print("Coord connection closed!")

    ################################
    # Private Functions
    ################################

    def _prepare_movement(self):
        self.galil_tool.GCommand('AB')
        self.galil_tool.GCommand('CB 1')
        self.galil_tool.GCommand('MO')
        self.galil_tool.GCommand('SH')
        self.galil_tool.GCommand('AC 150000')
        self.galil_tool.GCommand('DC 150000')

    def _set_axis_relative(self, axis: str, params: list):
        self.galil_tool.GCommand(f'SP{axis} = {self._pos2counts(params[1])}')
        self.galil_tool.GCommand(f'PR{axis} = {"-" if axis != "Y" else ""}{self._pos2counts(params[0])}')

    def _set_axis_absolute(self, axis: str, params: list, precision_mode: bool):
        speed = 1000 if precision_mode else params[1]
        self.galil_tool.GCommand(f'SP{axis} = {self._pos2counts(speed)}')
        self.galil_tool.GCommand(f'PA{axis} = {"-" if axis != "Y" else ""}{self._pos2counts(params[0])}')

    def _motor_on_break_off(self):
        self.galil_tool.GCommand('SH')
        self.galil_tool.GCommand('SB 1')
        self.galil_tool.GCommand('AC 150000')
        self.galil_tool.GCommand('DC 150000')
        self._status_motor_break = True

    def _pos2counts(self, pos):
        return int(pos * self._mum_to_counts)

    def _counts2pos(self, counts):
        return int(counts) / self._mum_to_counts

    def _write_log(self, x, y, z, mode, pos_ok, speed_ok):
        real_pos_str = self.galil_tool.GCommand("TP")
        real_pos = list(map(self._counts2pos, real_pos_str.strip().split(',')))

        data = {
            "x_actual": real_pos[0], "y_actual": real_pos[1], "z_actual": real_pos[2],
            "x_target": self._get_pos_from_input(x),
            "y_target": self._get_pos_from_input(y),
            "z_target": self._get_pos_from_input(z),
            "mode": mode,
            "pos_ok": pos_ok,
            "speed_ok": speed_ok
        }

        self._log_handler.write_log("coord", data)

    def _get_pos_from_input(self, pos):
        return self._counts2pos(self._pos2counts(pos[0])) if isinstance(pos, list) else None

    def _set_pid_parameter(self, precision_mode: bool):
        params = PID_PARAMS_PRECISION if precision_mode else PID_PARAMS_NORMAL
        self.galil_tool.GCommand(f"KP {params['X'].Kp},{params['Y'].Kp},{params['Z'].Kp}")
        self.galil_tool.GCommand(f"KD {params['X'].Kd},{params['Y'].Kd},{params['Z'].Kd}")
        self.galil_tool.GCommand(f"KI {params['X'].Ki},{params['Y'].Ki},{params['Z'].Ki}")

    def _do_precision_pos(self, active_axis: str):
        sleep_time = 0.05
        blocking_time = 5
        is_blocking_time_reached = True
        start_time = time.time()

        while (time.time() - start_time) < blocking_time:
            all_pos_ok, all_speed_ok = self._is_pos_speed_ok(active_axis)
            if all_pos_ok and all_speed_ok:
                self.galil_tool.GCommand(f"AB")
                if "Z" in active_axis: self.galil_tool.GCommand('CB 1')
                self.galil_tool.GCommand("MO")
                is_blocking_time_reached = False
                break
            time.sleep(sleep_time)

        if is_blocking_time_reached:
            self.galil_tool.GCommand(f"AB")
            if "Z" in active_axis: self.galil_tool.GCommand('CB 1')
            self.galil_tool.GCommand("MO")
        all_pos_ok, all_speed_ok = self._is_pos_speed_ok(active_axis)
        return all_pos_ok, all_speed_ok
    
    def _is_pos_speed_ok(self, active_axis:str):
        pos_threshold = self._pos2counts(0.5)
        speed_threshold = self._pos2counts(1)

        pos_err = list(map(lambda x: abs(float(x)), self.galil_tool.GCommand(f"TE {active_axis}").strip().split(',')))
        speed = list(map(lambda x: abs(float(x)), self.galil_tool.GCommand(f"TV {active_axis}").strip().split(',')))
        all_pos_ok = all(err < pos_threshold for err in pos_err)
        all_speed_ok = all(s < speed_threshold for s in speed)

        return all_pos_ok, all_speed_ok
