import chrpy
import numpy as np
import time

from collections import namedtuple
from chrpy.chr_connection import connection_from_config, ConnectionConfig
from chrpy.chr_cmd_id import OutputDataMode
from MMLToolbox.util.LogHandler import LogHandler


SensParams = namedtuple("SensParams", ["max_distance", "max_std"])
SENS_PARAMS = {
    0: SensParams(300, 10),
    1: SensParams(3000, 10)
}


class OpticSystem:
    """Handles optical measurement system via Ethernet connection."""

    def __init__(self, log_handler: LogHandler, ip_address: str = '192.168.170.2', id_sens: int = 1, n_samples: int = 1000):
        """Initialize Optic System."""
        self.ip_address = ip_address
        self.n_samples = n_samples
        self.id_sens = id_sens
        self.conn = None

        params = SENS_PARAMS.get(id_sens, SensParams(None, None))
        self.max_distance = params.max_distance
        self.max_std = params.max_std

        self._log_handler = log_handler
        self._log_handler.init_log("optic")

        self._init()

    ################################
    # Public Functions
    ################################

    def measure(self) -> tuple[float, float]:
        """Perform a distance measurement and return mean and standard deviation."""
        data = self.conn.wait_get_auto_buffer_samples(
            sample_cnt=self.n_samples,
            timeout=5,
            flush_buffer=True
        )

        mean_distance = np.nanmean(data.samples[:, 1])
        std_distance = np.nanstd(data.samples[:, 1])
        peak_intensity = np.nanmean(data.samples[:,2])

        if mean_distance > self.max_distance: mean_distance = np.nan
        if std_distance > self.max_std: mean_distance = np.nan
        if peak_intensity <= 10: mean_distance = np.nan
        if data.error_code != 0: mean_distance = np.nan

        log_data = {"mean": mean_distance, "std": std_distance, "intensity": peak_intensity}
        self._log_handler.write_log("optic", log_data)

        return (mean_distance, std_distance)

    def close(self):
        """Close the connection to the sensor."""
        if self.conn:
            self.conn.close()

    ################################
    # Private Functions
    ################################

    def _init(self):
        """Initialize the sensor connection and configuration."""
        config = ConnectionConfig()
        config.address = self.ip_address

        conn = connection_from_config(config=config)
        conn.open()
        conn.set_output_data_format_mode(OutputDataMode.DOUBLE)
        conn.exec('SODX',83,256,257)
        conn.exec('SEN', self.id_sens)
        conn.exec('SHZ',1000)

        self.conn = conn


################################
# TODO: Implement dark-field correction
################################
