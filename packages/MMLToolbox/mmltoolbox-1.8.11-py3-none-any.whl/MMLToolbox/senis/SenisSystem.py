import serial
import struct
import time
import numpy as np

from MMLToolbox.util.LogHandler import LogHandler


class SenisSystem:
    """Handles communication with the Teslameter sensor."""

    _SLEEP_TIME = 0.005

    def __init__(self, log_handler: LogHandler, com_port:str=None, baudrate: int = 115200, timeout: float = 0.5, calibrated: bool = True, full_scale_mT: float = 20, offset=[-0.01805576,0.04297808,-0.0321784]):
        """Initialize the Teslameter connection."""
        self._port = "COM2" if com_port is None else com_port
        self._baudrate = baudrate
        self._offset = offset
        self._timeout = timeout
        self._calibrated = calibrated
        self._full_scale_mT = full_scale_mT
        self._log_handler = log_handler
        self._log_handler.init_log("senis")
        self._init()

    ################################
    # Public Functions
    ################################
    def measure(self, counts:int=50) -> tuple[float, float, float]:
        B_arr = self._measure_stream(counts)
        Bx_arr,By_arr,Bz_arr = B_arr[:,0],B_arr[:,1],B_arr[:,2]
        
        Bx_mean,Bx_std = self._compute_mean_std(Bx_arr)
        By_mean,By_std = self._compute_mean_std(By_arr*-1)
        Bz_mean,Bz_std = self._compute_mean_std(Bz_arr*-1)

        data_log = {"Bx_mean": Bx_mean, "By_mean": By_mean, "Bz_mean": Bz_mean,
                    "Bx_std": Bx_std, "By_std": By_std, "Bz_std": Bz_std,
                    "len_list": np.mean([len(Bx_arr),len(By_arr),len(Bz_arr)])}
        self._log_handler.write_log("senis", data_log)

        return (Bx_mean-self._offset[0],By_mean-self._offset[1],Bz_mean-self._offset[2])

    def close(self) -> None:
        """Close the serial connection."""
        self.ser.write(b'S')  # Stop data transfer
        self.ser.close()

    ################################
    # Private Functions
    ################################

    def _init(self) -> None:
        """Initialize the serial communication and set sensor mode."""
        self.ser = serial.Serial(self._port, baudrate=self._baudrate, timeout=self._timeout)
        # Set mode
        mode_command = b'C' if self._calibrated else b'D'
        self.ser.write(mode_command)
        time.sleep(self._SLEEP_TIME)
        self.ser.write(b'A4\r')
        time.sleep(self._SLEEP_TIME)
        self.ser.flush()

    def _get_calibration_scale(self) -> int:
        """Get the scale factor based on full_scale_mT."""
        if self._full_scale_mT == 2000:
            return 10
        elif self._full_scale_mT == 200:
            return 100
        elif self._full_scale_mT == 20:
            return 1000
        else:
            raise ValueError("Unsupported full_scale_mT value for calibration mode.")
        
    def _convert_packet(self, packet):
        Bx_raw = struct.unpack('<h', packet[0:2])[0]
        By_raw = struct.unpack('<h', packet[2:4])[0]
        Bz_raw = struct.unpack('<h', packet[4:6])[0]

        if self._calibrated:
            if self._full_scale_mT == 2000:
                scale_factor = 10
            elif self._full_scale_mT == 200:
                scale_factor = 100
            elif self._full_scale_mT == 20:
                scale_factor = 1000
            else:
                raise ValueError("Unsupported full_scale_mT value for calibration mode.")

            Bx = (Bx_raw / scale_factor) 
            By = (By_raw / scale_factor) 
            Bz = (Bz_raw / scale_factor) 

        else:
            Bx = (Bx_raw * self._full_scale_mT / 32768)
            By = (By_raw * self._full_scale_mT / 32768)
            Bz = (Bz_raw * self._full_scale_mT / 32768)

        return Bx, By, Bz
    
    def _measure_stream(self,count:int):
        """
        Starts continuous reading mode and collects `count` measurements.

        Args:
            count (int): Number of measurements to collect.

        Returns:
            List of (Bx, By, Bz) tuples in Tesla.
        """
        self.ser.reset_input_buffer()
        time.sleep(self._SLEEP_TIME)
        self.ser.write(b'B')  # Start streaming
        time.sleep(self._SLEEP_TIME)
        self.ser.flush()
        time.sleep(self._SLEEP_TIME)

        results = []
        buffer = bytearray()

        while len(results) < count:
            buffer += self.ser.read(self.ser.in_waiting or 1)

            while len(buffer) >= 7:
                for i in range(len(buffer) - 6):
                    if buffer[i+6] == 13:
                        packet = buffer[i:i+7]
                        buffer = buffer[i+7:]  # Remove processed bytes
                        try:
                            results.append(self._convert_packet(packet))
                        except Exception as e:
                            print(f"Conversion error: {e}")
                        break
                else:
                    break

        self.ser.write(b'S')  # Stop streaming
        return np.array(results)
        
    def _measure_once(self) -> tuple[float, float, float]:
        """Measure the Bx, By, Bz components in Tesla."""
        self.ser.reset_input_buffer()
        time.sleep(self._SLEEP_TIME)
        self.ser.write(b'B')
        time.sleep(self._SLEEP_TIME)
        self.ser.flush()
        time.sleep(self._SLEEP_TIME)

        data = self.ser.read(20)
        if len(data) < 7:
            raise IOError(f"Not enough data received. Received: {data}")

        for i in range(len(data) - 6):
            if data[i + 6] == 13:
                packet = data[i:i + 7]
                break
        else:
            raise IOError(f"No valid packet found. Received: {data}")

        Bx_raw = struct.unpack('<h', packet[0:2])[0]
        By_raw = struct.unpack('<h', packet[2:4])[0]
        Bz_raw = struct.unpack('<h', packet[4:6])[0]

        if self._calibrated:
            scale_factor = self._get_calibration_scale()
            Bx = (Bx_raw / scale_factor) / 1000
            By = (By_raw / scale_factor) / 1000
            Bz = (Bz_raw / scale_factor) / 1000
        else:
            Bx = (Bx_raw * self._full_scale_mT / 32768) / 1000
            By = (By_raw * self._full_scale_mT / 32768) / 1000
            Bz = (Bz_raw * self._full_scale_mT / 32768) / 1000

        return Bx, By, Bz
    
    def _compute_mean_std(self,B_arr) -> tuple[float,float]:
        mean = np.nanmean(B_arr)
        std = np.nanstd(B_arr)
        return (mean,std)

################################
# Example Usage
################################

if __name__ == "__main__":
    log_handler = LogHandler()
    senis_teslameter = SenisSystem(port='COM3', log_handler=log_handler, calibrated=True, full_scale_mT=20)

    try:
        Bx, By, Bz = senis_teslameter.measure()
        print(f"Bx: {Bx:.6f} T, By: {By:.6f} T, Bz: {Bz:.6f} T")
    finally:
        senis_teslameter.close()
