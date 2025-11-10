from __future__ import annotations

from numpy import (
    complexfloating,
    ndarray,
    pi
)

from ..Components.Component import Component
from ..Components import Clock

from .PhotonDetector import SinglePhotonDetector

#from collections import namedtuple

from .SimpleDevices import PhaseSample
from .SimpleDevices import BeamSplitter

from ..Constants import EMPTY_FIELD

from ..utils import display_class_instances_data

# TODO multiport
# Handling multiport SinglePhotonDetector

class AsymmetricMachZehnderInterferometer(Component):
    """
    AsymmetricMachZehnderInterferometer class
    """
    def __init__(self, clock:Clock, time_delay:float, 
                splitting_ratio_ti:float = 0.5, splitting_ratio_tf:float = 0.5,
                save_simulation: bool = False, name: str = "default_asymmetric_machzehnder_interferometer"):
        super().__init__(name)

        # Simulation parameters
        self._save_simulation = save_simulation

        # AMZI parameters
        self._time_delay = time_delay
        self._input_beam_splitter = BeamSplitter(splitting_ratio_ti, name="input_beam_splitter")
        self._output_beam_joiner = BeamSplitter(splitting_ratio_tf, name="output_beam_joiner")

        # Phase controls
        self._short_arm_phase_sample = PhaseSample(name="short_arm_phase_sample")
        self._long_arm_phase_sample = PhaseSample(name="long_arm_phase_sample")

        # Measure ports
        self._SPD0 = SinglePhotonDetector(save_simulation=self._save_simulation, name="SPD_0")
        self._SPD1 = SinglePhotonDetector(save_simulation=self._save_simulation, name="SPD_π")

        self._electric_field: complexfloating = EMPTY_FIELD
        """electric_field data for AsymmetricMachZehnderInterferometer"""

        self._electric_field_port2: complexfloating = EMPTY_FIELD
        """electric_field_port2 data for AsymmetricMachZehnderInterferometer"""

        # Delay buffer
        self._buffer_size: int = max(1, int(time_delay / clock.dt))
        self._field_buffer: list[complexfloating] = []

    def _handle_SPD_data(self):
        """AsymmetricMachZehnderInterferometer _handle_SPD_data method"""
        if(not self._save_simulation):
            print(f"{self.name} did not save simulation data")
            return True
        elif(self._SPD0._handle_get_data() or self._SPD1._handle_get_data()):
            print(f"{self.name} cannot get SPD data")
            return True
        return False

    def store_data(self):
        """AsymmetricMachZehnderInterferometer store_data method"""
        self._SPD0.store_data()
        self._SPD1.store_data()

    def reset_data(self):
        """AsymmetricMachZehnderInterferometer reset_data method"""
        #return super().reset_data()
        self._field_buffer.clear()

        self._SPD0.reset_data()
        self._SPD1.reset_data()

    def reset(self, save_simulation:bool = False):
        """AsymmetricMachZehnderInterferometer reset method"""
        #return super().reset(args)
        self._save_simulation = save_simulation
        self._SPD0.reset(save_simulation)
        self._SPD1.reset(save_simulation)

    def set(self, clock: Clock, time_delay: float, 
            splitting_ratio_ti: float = 0.5, splitting_ratio_tf: float = 0.5):
        """AsymmetricMachZehnderInterferometer set method"""
        #return super().set()

        # Beam splitters
        self._input_beam_splitter.set(splitting_ratio_ti)
        self._output_beam_joiner.set(splitting_ratio_tf)

        # Delay buffer
        self._buffer_size = max(1, int(time_delay / clock.dt))
        self._field_buffer.clear()

    def set_phases(self, short_arm_phase:  float|None = None, long_arm_phase:  float|None = None, 
                short_arm_phase_interval: float|None = None, long_arm_phase_interval: float|None = None):
        """AsymmetricMachZehnderInterferometer set phases method"""
        if(short_arm_phase):
            self._short_arm_phase_sample.set(short_arm_phase, 
                                        phase_interval= short_arm_phase_interval)
        if(long_arm_phase):
            self._long_arm_phase_sample.set(long_arm_phase, 
                                        phase_interval= long_arm_phase_interval)

    def simulate(self, electric_field: complexfloating):
        """AsymmetricMachZehnderInterferometer simulate method"""
        #return super().simulate(clock)

        # input field
        E_short, E_long = self._input_beam_splitter.simulate(electric_field)

        # long arm
        E_long = self._long_arm_phase_sample.simulate(E_long)

        # Handle buffer
        self._field_buffer.append(E_long)
        E_long = self._field_buffer.pop(0) if len(self._field_buffer) > self._buffer_size else EMPTY_FIELD

        # short arm
        E_short = self._short_arm_phase_sample.simulate(E_short)

        # Recombine
        self._electric_field, self._electric_field_port2 = self._output_beam_joiner.simulate(E_short, E_long)

        # Photon Detection
        self._SPD0.simulate(self._electric_field_port2)
        self._SPD1.simulate(self._electric_field)

    def input_port(self):
        """AsymmetricMachZehnderInterferometer input port method"""
        #return super().input_port()
        kwargs = {'electric_field':None}
        return kwargs
    
    def output_port(self, kwargs: dict = {}):
        """AsymmetricMachZehnderInterferometer output port method"""
        #return super().output_port(kwargs)
        kwargs['electric_field'] = self._electric_field
        kwargs['electric_field_port2'] = self._electric_field_port2
        return kwargs
    
    def display_SPD_data(self, time_data: ndarray, simulation_keys:tuple[str,...]|None=None):
        """AsymmetricMachZehnderInterferometer display_SPD_data method"""        
        
        # Handle cases
        if(self._handle_SPD_data()):
            return

        display_class_instances_data((self._SPD0, self._SPD1), time_data, simulation_keys)

    def get_SPD_data(self):
        """AsymmetricMachZehnderInterferometer get_SPD_data method"""

        # Handle cases
        if(self._handle_SPD_data()):
            return

        # Store SPD data
        _SPD_data = {'SPD0':self._SPD0.get_data(), 'SPD1':self._SPD1.get_data()}
        return _SPD_data