from numpy import (
    complexfloating
)

from LaserPy_Quantum.Components.Component import Clock

from ..Components.Component import Component
from ..Components import Connection

from .ComponentDriver import CurrentDriver
from .Laser import Laser

from ..Constants import EMPTY_FIELD

from ..utils import (
    InjectionField,
    LaserRunnerComponents
)

class VariableOpticalAttenuator(Component):
    """
    VariableOpticalAttenuator class
    """
    def __init__(self, attenuation_dB: float= 0.0, name: str = "default_variable_optical_attenuator"):
        super().__init__(name)
        self._attenuation_dB = attenuation_dB
        self._output_field: complexfloating = EMPTY_FIELD

    def set(self, attenuation_dB: float):
        """VariableOpticalAttenuator set method"""
        #return super().set()
        self._attenuation_dB = attenuation_dB

    def siulate(self, electric_field: complexfloating):
        """VariableOpticalAttenuator simulate method"""
        #return super().simulate(args)
        # Calculate attenuation factor on electric field amplitude
        attenuation_factor = 10 ** (-self._attenuation_dB / 20)
        self._output_field = electric_field * attenuation_factor
        return self._output_field
    
    def input_port(self):
        """VariableOpticalAttenuator input port method"""
        #return super().input_port()
        kwargs = {'electric_field': None}
        return kwargs
    
    def output_port(self, kwargs: dict = {}):
        """VariableOpticalAttenuator output port method"""
        #return super().output_port(kwargs)
        kwargs['electric_field'] = self._output_field
        return kwargs
    
# class OpticalCirculator(Connection):
#     """
#     OpticalCirculator class
#     """

#     # Specific type override
#     _input_components: tuple[Laser,...]

#     def __init__(self, input_components: Laser | tuple[Laser, ...], injection_components: LaserRunnerComponents | tuple[CurrentDriver, Laser], output_components: Component|tuple[Component, ...], name: str = "default_optical_circulator"):
#         if(isinstance(input_components, Laser)):
#             input_components = (input_components,)
#         self._input_components = input_components
#         """Master Lasers for OpticalCirculator"""

#         if(isinstance(injection_components, tuple)):
#             injection_components = LaserRunnerComponents._make(injection_components)

#         self._injection_laser_driver = injection_components.current_driver
#         """Slave Laser's Driver for OpticalCirculator"""

#         self._injection_laser = injection_components.laser
#         self._injection_laser.set_slave_Laser(True)
#         """Slave locked Laser for OpticalCirculator"""
        
#         super().__init__(self._injection_laser, output_components, name)

#     def simulate(self, clock: Clock):
#         """OpticalCirculator simulate method"""
#         # Injection devices
#         injection_kwargs: list[InjectionField] = []
#         for laser in (self._input_components):
#             injection_kwargs.append(laser.output_port({'injection_field': None})['injection_field'])

#         # Multi Master locked Slave Laser simulation
#         self._injection_laser.simulate(clock, self._injection_laser_driver._data, tuple(injection_kwargs))
#         if(self._injection_laser._save_simulation):
#             self._injection_laser.store_data()

#         # Simulate devices dependent on Slave laser data
#         super().simulate(clock)