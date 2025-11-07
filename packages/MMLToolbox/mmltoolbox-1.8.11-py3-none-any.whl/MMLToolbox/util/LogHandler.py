import os
import time
import json
import numpy as np

from enum import Enum


class NumpySafeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


class LogType(Enum):
    COORD = "coord"
    NI = "ni"
    SENIS = "senis"
    OPTIC = "optic"


class LogHandler:
    def __init__(self):
        self._timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        self._filenames = {
            LogType.COORD: f"coord_{self._timestamp}.json",
            LogType.NI: f"ni_{self._timestamp}.json",
            LogType.SENIS: f"senis_{self._timestamp}.json",
            LogType.OPTIC: f"optic_{self._timestamp}.json"
        }
        self._log_folder = "log"
        self._init_log_folder()

    ################################
    # Public Functions
    ################################

    def init_log(self, name):
        """Initialize (create) a new log file for the given name."""
        log_type = self._get_log_type(name)
        filename = self._filenames[log_type]
        self._handle_log(filename)

    def write_log(self, name, data):
        """Write data to the corresponding log file based on the name."""
        log_type = self._get_log_type(name)
        write_methods = {
            LogType.COORD: self._write_log_coord,
            LogType.NI: self._write_log_ni,
            LogType.SENIS: self._write_log_senis,
            LogType.OPTIC: self._write_log_optic
        }
        write_methods[log_type](data)

    ################################
    # Private Functions
    ################################

    def _init_log_folder(self):
        os.makedirs(self._log_folder, exist_ok=True)

    def _handle_log(self, filename):
        log_path = os.path.join(self._log_folder, filename)
        with open(log_path, 'w') as log_file:
            pass

    def _current_timestamp(self):
        return time.strftime("%Y-%m-%d_%H-%M-%S")

    def _get_log_path(self, log_type: LogType):
        return os.path.join(self._log_folder, self._filenames[log_type])
    
    def _get_log_type(self, name):
        try:
            return LogType(name)
        except ValueError:
            allowed = [lt.value for lt in LogType]
            raise ValueError(f"Invalid name '{name}'. Allowed names are: {allowed}")
    
    @staticmethod
    def _format_value(value):
        if isinstance(value, float):
            return f"{value:.5e}"
        return value

    def _write_log_coord(self, data):
        log_path = self._get_log_path(LogType.COORD)
        log_line = {
            "timestamp": self._current_timestamp(),
            "X in µm": {"actual": self._format_value(data["x_actual"] * -1), "target": self._format_value(data["x_target"])},
            "Y in µm": {"actual": self._format_value(data["y_actual"]), "target": self._format_value(data["y_target"])},
            "Z in µm": {"actual": self._format_value(data["z_actual"] * -1), "target": self._format_value(data["z_target"])},
            "PrecisionMode": data["mode"],
            "AllPosOK": data["pos_ok"],
            "AllSpeedOK": data["speed_ok"]
        }
        with open(log_path, "a") as file:
            file.write(json.dumps(log_line, ensure_ascii=False, cls=NumpySafeEncoder) + "\n")

    def _write_log_ni(self, data):
        log_path = self._get_log_path(LogType.NI)
        log_line = {
            "timestamp": self._current_timestamp(),
            "U in V": {"mean": self._format_value(data["voltage"]), "std": self._format_value(data["std_voltage"])},
            "I in A": {"mean": self._format_value(data["current"]), "std": self._format_value(data["std_current"])}
        }
        with open(log_path, "a") as file:
            file.write(json.dumps(log_line, cls=NumpySafeEncoder) + "\n")

    def _write_log_senis(self, data):
        log_path = self._get_log_path(LogType.SENIS)
        log_line = {
            "timestamp": self._current_timestamp(),
            "Bx in mT": {"mean": self._format_value(data["Bx_mean"]), "std": self._format_value(data["Bx_std"])},
            "By in mT": {"mean": self._format_value(data["By_mean"]), "std": self._format_value(data["By_std"])},
            "Bz in mT": {"mean": self._format_value(data["Bz_mean"]), "std": self._format_value(data["Bz_std"])},
            "counts": data["len_list"]
        }
        with open(log_path, "a") as file:
            file.write(json.dumps(log_line, cls=NumpySafeEncoder) + "\n")

    def _write_log_optic(self, data):
        log_path = self._get_log_path(LogType.OPTIC)
        log_line = {
            "timestamp": self._current_timestamp(),
            "distance in µm": {"mean": self._format_value(data["mean"]), "std": self._format_value(data["std"]), "intensity": self._format_value(data["intensity"])}
        }
        with open(log_path, "a") as file:
            file.write(json.dumps(log_line, ensure_ascii=False, cls=NumpySafeEncoder) + "\n")

    
