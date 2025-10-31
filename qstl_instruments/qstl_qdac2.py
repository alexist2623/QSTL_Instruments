"""QSTL QDAC2 Driver"""
import numpy as np
import time

from qcodes_contrib_drivers.drivers.QDevil import QDAC2

class QSTL_QDac2(QDAC2.QDac2):
    def __init__(
            self,
            name: str,
            address: str,
            ramp_rate: float,
            i_threshold: float,
            v_limit: float,
            contacts: dict,
        ):
        super().__init__(
            name = name,
            address = address
        )
        self.contacts: dict = None
        self.ramp_rate = ramp_rate ## V/sec
        self.i_threshold = i_threshold ## current threshold in Amps
        self.v_limit = v_limit ## voltage limit for safety
        self.contacts = contacts

    def validate_voltages(self, values: float) -> None:
        """
        Validate whether voltage does not exceed maximum limit of voltage

        Parameters
            values : values to be tested
            limit : limit voltage
        Returns
            None
        """
        if any(abs(np.array(values)) > self.v_limit):
            raise Exception("voltage is above the limit")
    
    def get_initial_voltages(self) -> dict:
        """
        Return initial voltages from QDAC2

        Parameters
            contacts : Ports of QDAC2 to read
        Return
            dict : {
                    PortName : VoltageValue
                }
        """
        Conditions = {}
        for key in self.contacts.keys():
            Conditions[key]= self.channels[self.contacts[key]-1].dc_constant_V()
        return Conditions

    def ramp_channels(self, channels: list, value: list) -> float:
        """
        Ramp the voltages of QDAC2
        """
        if len(value)!=1:
            raise Exception("Value should be a single-numbered 1D list")
        self.validate_voltages(value)
        channel_nums = [
            self.contacts[channel] for channel in channels
        ] 
        previous_v = []
        for i in channel_nums:
            previous_v.append(self.channels[i-1].dc_constant_V()) ## numbering starts from zero
            self.channels[i-1].dc_constant_V(value[0])
        
        max_diff = max(abs(np.array(previous_v)-value[0])) ## maximum difference between start_v and end_V
        max_time_to_ramp = max_diff/self.ramp_rate ## in sec
        time.sleep(max_time_to_ramp)
        return max_time_to_ramp

    def ramp_all_channels_to_zero(self) -> None:
        """
        Ramp all output voltage of ports to zeros.
        """
        for i in range(24):
            self.channels[i].dc_constant_V(0)

    def set_slew_rate_all_channels(self, rate: float) -> None:
        """
        Set slew rate of all output ports of ports
        """
        for i in range(24):
            self.channels[i].dc_slew_rate_V_per_s(rate)
