import time

import nidaqmx
import numpy as np

from MMLToolbox.util.LogHandler import LogHandler


class NISystem:
    """Handles NI DAQ operations including analog output and measurement."""

    _VOLTAGE_MIN = -5.0
    _VOLTAGE_MAX = 5.0

    def __init__(self, log_handler: LogHandler, device_name: str = 'Dev1', ao_channel: str = 'ao0', sample_rate: int = 10000):
        self.device_name = device_name
        self.ao_channel = ao_channel
        self.sample_rate = sample_rate
        self._log_handler = log_handler
        self._log_handler.init_log("ni")

    ################################
    # Public Functions
    ################################

    def start(self, startup_duration: float = 1, max_voltage: float = 1, target_voltage: float = 1, freq: int = 2, waveform:str="sin"):
        """Start the analog output with a ramp or sinus signal."""
        with nidaqmx.Task() as startup_task:
            startup_task.ao_channels.add_ao_voltage_chan(
                f"{self.device_name}/{self.ao_channel}", min_val=self._VOLTAGE_MIN, max_val=self._VOLTAGE_MAX
            )
            startup_task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                samps_per_chan=int(self.sample_rate * startup_duration)
            )
            if waveform == "sin":
                startup_signal = self._generate_startup_signal_sin(
                  duration=startup_duration,
                  max_voltage=max_voltage,
                  target_voltage=target_voltage,
                  freq=freq)
            elif waveform == "ramp":
                startup_signal = self._generate_startup_signal_ramp(
                  duration=startup_duration,
                  max_voltage=max_voltage,
                  target_voltage=target_voltage,
                  freq=freq)
                
            startup_task.write(startup_signal, auto_start=True)
            startup_task.wait_until_done(timeout=startup_duration + 1)

    def measure(self) -> tuple[float, float]:
        """Measure voltage and current from NI device."""
        with nidaqmx.Task() as task:
            try:
                task.ai_channels.add_ai_voltage_chan(
                    f"{self.device_name}/ai0", min_val=self._VOLTAGE_MIN, max_val=self._VOLTAGE_MAX
                )
                task.ai_channels.add_ai_voltage_chan(
                    f"{self.device_name}/ai1", min_val=self._VOLTAGE_MIN, max_val=self._VOLTAGE_MAX
                )
                data = task.read(number_of_samples_per_channel=100)

                voltage = np.mean(data[0]) * 100  # Rohrer amplifier factor 100V/V
                std_voltage = np.std(data[0]) * 100
                current = np.mean(data[1]) * 10   # Rohrer amplifier factor 10A/V
                std_current = np.std(data[1]) * 10

                log_data = {
                    "voltage": voltage,
                    "current": current,
                    "std_voltage": std_voltage,
                    "std_current": std_current
                }
                self._log_handler.write_log("ni", log_data)

                return voltage, current

            except nidaqmx.errors.DaqError as e:
                print(f"DAQmx Error during measurement: {e}")
                return 0.0, 0.0

    def stop(self):
        """Stop analog output by writing zero voltage."""
        with nidaqmx.Task() as stop_task:
            stop_task.ao_channels.add_ao_voltage_chan(
                f"{self.device_name}/{self.ao_channel}", min_val=self._VOLTAGE_MIN, max_val=self._VOLTAGE_MAX
            )
            stop_task.write(0.0, auto_start=True)
            time.sleep(0.1)

    ################################
    # Private Functions
    ################################

    def _generate_startup_signal_sin(self, duration: float, max_voltage: float, target_voltage: float, freq: int) -> np.ndarray:
        """Generate a startup signal ramp."""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        signal = (
            max_voltage * 2 * np.sin(2 * np.pi * freq * t) * t[::-1] / np.max(t)
        ) + (target_voltage * t / np.max(t))
        return signal
    
    def _generate_startup_signal_ramp(self, duration: float, max_voltage: float, target_voltage: float, freq: int) -> np.ndarray:
        """Generate a startup signal ramp."""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        signal = target_voltage * t / np.max(t)
        return signal


################################
# Example Usage
################################

if __name__ == "__main__":
    log_handler = LogHandler()
    system = NISystem(log_handler=log_handler)

    system.start()
    print("Startup complete, holding last value. Press Ctrl+C to stop.")

    try:
        while True:
            voltage, current = system.measure()
            print(f"Voltage: {voltage:.2f} V, Current: {current:.2f} A")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")

    system.stop()
    voltage, current = system.measure()
    print(f"After Stop - Voltage: {voltage:.2f} V, Current: {current:.2f} A")
    print("Analog Output operation completed.")