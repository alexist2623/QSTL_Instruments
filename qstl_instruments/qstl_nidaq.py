"""QSTL NIDaq Driver"""
import numpy as np
from functools import wraps
from typing import Optional

import nidaqmx
from nidaqmx.constants import AcquisitionType as AcqType
from nidaqmx.constants import TerminalConfiguration as TermConfig

class QSTL_NIDaq:
    def __init__(self, max_sampling_rate: float, gain: Optional[float]):
        self.max_sampling_rate = max_sampling_rate
        self.gain = gain

    @staticmethod
    def open_nidaqmx_task(f):
        """Decorator to manage opening and closing a NI-DAQmx Task."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            with nidaqmx.Task('ai_task') as ai_task:
                # Inject the task into the wrapped function’s kwargs
                return f(*args, ai_task=ai_task, **kwargs)
        return wrapper

    @open_nidaqmx_task
    def read_untriggered_voltage(
            self,
            ch_id: int,
            num_samples: int,
            v_min: float = -10,
            v_max: float = +10,
            timeout_sec: float = 4,
            ai_task: nidaqmx.Task = None,
        ) -> np.array:
        ai_task.ai_channels.add_ai_voltage_chan(ch_id, terminal_config=TermConfig.DIFF, min_val= v_min, max_val= v_max)
        ai_task.timing.cfg_samp_clk_timing(rate=self.max_sampling_rate, sample_mode=AcqType.FINITE, samps_per_chan=int(num_samples))
        ai_task.start()

        result = ai_task.read(number_of_samples_per_channel=num_samples, timeout=timeout_sec)

        ai_task.stop()
        return np.array(result)

    @open_nidaqmx_task
    def read_untriggered_multi_channels(
            self,
            ch_ids,
            num_samples_per_channel,
            v_min = -10,
            v_max = +10,
            timeout_sec = 5,
            ai_task: nidaqmx.Task = None,
        ) -> np.array:
        sampling_rate_per_channel = np.floor(self.max_sampling_rate/len(ch_ids))
        for ch_id in ch_ids:
            ai_task.ai_channels.add_ai_voltage_chan(ch_id, terminal_config=TermConfig.DIFF, min_val= v_min, max_val= v_max)
        ai_task.timing.cfg_samp_clk_timing(rate=sampling_rate_per_channel, sample_mode=AcqType.FINITE, samps_per_chan=int(num_samples_per_channel))
    
        ai_task.start()
        result = ai_task.read(number_of_samples_per_channel=num_samples_per_channel, timeout=timeout_sec)
        ai_task.stop()
        
        return np.array(result)
    
    @open_nidaqmx_task
    def read_triggered_voltage(
            self,
            sweep,
            ch_id,
            num_samples,
            v_min = -10,
            v_max = +10,
            timeout_sec = 5,
            ai_task: nidaqmx.Task = None,
        ) -> np.array:
        ai_task.ai_channels.add_ai_voltage_chan(ch_id, terminal_config=TermConfig.DIFF, min_val= v_min, max_val= v_max)
        ai_task.timing.cfg_samp_clk_timing(rate=self.max_sampling_rate, sample_mode=AcqType.FINITE, samps_per_chan=int(num_samples))
        ai_task.triggers.start_trigger.cfg_dig_edge_start_trig('pfi0')
        ai_task.start()
        sweep.start()  ## start the qdac2 sweep, which will generate the trigger for data acquisition
        result = ai_task.read(number_of_samples_per_channel=num_samples, timeout=timeout_sec)
        ai_task.stop()

        return np.array(result)

    @open_nidaqmx_task
    def read_triggered_multi_channels(
            self,
            sweep,
            ch_ids,
            num_samples_per_channel,
            v_min = -10,
            v_max = +10,
            timeout_sec = 5,
            ai_task: nidaqmx.Task = None,
        ) -> np.array:
        sampling_rate_per_channel = np.floor(self.max_sampling_rate/len(ch_ids))
        for ch_id in ch_ids:
            ai_task.ai_channels.add_ai_voltage_chan(ch_id, terminal_config=TermConfig.DIFF, min_val= v_min, max_val= v_max)
        ai_task.timing.cfg_samp_clk_timing(rate=sampling_rate_per_channel, sample_mode=AcqType.FINITE, samps_per_chan=int(num_samples_per_channel))
        ai_task.triggers.start_trigger.cfg_dig_edge_start_trig('pfi0')
        ai_task.start()

        sweep.start()  ## start the qdac2 sweep, which will generate the trigger for data acquisition
        result = ai_task.read(number_of_samples_per_channel=num_samples_per_channel, timeout=timeout_sec)

        ai_task.stop()
        return np.array(result)


    def convert_volts_to_amps(self, x: list[float]) -> list[float]:
        if self.gain is None:
            raise ValueError("Gain of preamp is not defined")
        return x/self.gain


    def reshape_array(self, x: list[float], num_bins: int) -> np.array:
        bin_length = int(len(x)/num_bins)
        y = np.empty(shape=num_bins, dtype=float)
        for i in range(num_bins):
            y[i] = np.mean(x[(i*bin_length):((i+1)*bin_length)])
        return y
