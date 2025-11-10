from numpy import (
    complexfloating,
    mod, exp, sqrt,
    pi
)

from ..Components.Component import Component

from ..Constants import EMPTY_FIELD

class PhaseSample(Component):
    """
    PhaseSample class
    """
    def __init__(self, phase_delay: float = 0.0, name: str = "default_phase_sample"):
        super().__init__(name)

        self._phase_interval = 2 * pi
        """phase interval for PhaseSample"""

        phase_delay = mod(phase_delay, self._phase_interval)
        self._phase_change = exp(1j * phase_delay)
        """phase change for PhaseSample"""

        self._electric_field: complexfloating = EMPTY_FIELD
        """electric_field data for PhaseSample"""

    def set(self, phase_delay: float, phase_interval: float|None= None):
        """PhaseSample set method"""
        #return super().set()
        if(phase_interval):
            self._phase_interval = phase_interval
        phase_delay = mod(phase_delay, self._phase_interval)
        self._phase_change = exp(1j * phase_delay)

    def simulate(self, electric_field: complexfloating):
        """PhaseSample simulate method"""
        #return super().simulate(args)

        # Add phase change
        self._electric_field = self._phase_change * electric_field
        return self._electric_field

    def input_port(self):
        """PhaseSample input port method"""
        #return super().input_port()
        kwargs = {'electric_field':None}
        return kwargs
    
    def output_port(self, kwargs: dict = {}):
        """PhaseSample output port method"""
        #return super().output_port(kwargs)
        kwargs['electric_field'] = self._electric_field
        return kwargs
    
class Mirror(PhaseSample):
    """
    Mirror class
    """
    def __init__(self, name: str = "default_mirror"):
        super().__init__(pi, name)

    def set(self):
        """Mirror set method"""
        #return super().set(phase_delay, phase_interval)
        print("Mirror phase is fixed at pi")

class BeamSplitter(Component):
    """
    BeamSplitter class
    """
    def __init__(self, splitting_ratio_t: float = 0.5, name: str = "default_beam_splitter"):
        super().__init__(name)

        # Field coefficients
        self._t = sqrt(splitting_ratio_t)
        self._r = exp(0.5j * pi) * sqrt(1 - splitting_ratio_t)

        # Field variables
        self._E_transmitted: complexfloating = EMPTY_FIELD
        self._E_reflected: complexfloating = EMPTY_FIELD

    def set(self, splitting_ratio_t: float):
        """BeamSplitter reset method"""
        #return super().set()
        self._t = sqrt(splitting_ratio_t)
        self._r = exp(0.5j * pi) * sqrt(1 - splitting_ratio_t)

    def simulate(self, electric_field: complexfloating, electric_field_port2: complexfloating = EMPTY_FIELD):
        """BeamSplitter simulate method"""
        #return super().simulate(args)
        self._E_transmitted = self._t * electric_field + self._r * electric_field_port2
        self._E_reflected = self._r * electric_field + self._t * electric_field_port2
        return self._E_transmitted, self._E_reflected

    def input_port(self):
        """BeamSplitter input port method"""
        #return super().input_port()
        
        # Default port2 electric field
        kwargs = {'electric_field':None, 'electric_field_port2':EMPTY_FIELD}
        return kwargs
    
    def output_port(self, kwargs: dict = {}):
        """BeamSplitter output port method"""
        #return super().output_port(kwargs)
        kwargs['electric_field'] = self._E_transmitted
        kwargs['electric_field_port2'] = self._E_reflected
        return kwargs