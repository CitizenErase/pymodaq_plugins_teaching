
from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.utils import ThreadCommand  # object used to send info back to the main thread
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_Move_Monochromator(DAQ_Move_base):
    """ Instrument plugin class for an actuator.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

    bazinga

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    is_multiaxes = False
    _axis_names: Union[List[str], Dict[str, int]] = ['Axis1', 'Axis2']
    _controller_units: Union[str, List[str]] = 'nm'
    _epsilon: Union[float, List[float]] = 0.1
    data_actuator_type = DataActuatorType.DataActuator

    params = [{'title': 'Grating:', 'name': 'grating', 'type': 'list', 'limits': []},
              {'title': 'Tau:', 'name': 'tau', 'type': 'float', 'value': 0, 'limits': [0,1000]},
                ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: Spectrometer = None
        pass

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """

        pos = DataActuator(data=self.controller.get_wavelength(),  # when writing your own plugin replace this line
                           units=self.axis_unit)
        pos = self.get_position_with_scaling(pos)
        return pos

    def user_condition_to_reach_target(self) -> bool:
        """ Implement a condition for exiting the polling mechanism and specifying that the
        target value has been reached

       Returns
        -------
        bool: if True, PyMoDAQ considers the target value has been reached
        """
        # TODO either delete this method if the usual polling is fine with you, but if need you can
        #  add here some other condition to be fullfilled either a completely new one or
        #  using or/and operations between the epsilon_bool and some other custom booleans
        #  for a usage example see DAQ_Move_brushlessMotor from the Thorlabs plugin
        return True

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close_communication()

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """


        if param.name() == "grating":
           self.controller.grating = param.value()
        if param.name() == "tau":
            self.controller.tau = int(param.value())
        else:
            pass



    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        if self.is_master:
            self.controller = Spectrometer()
            initialized = self.controller.open_communication()  # todo

        else:
            self.controller = controller
            initialized = True


        self.settings.child('grating').setLimits(self.controller.gratings)
        self.settings.child('grating').setValue(self.controller.grating)
        self.settings.child('tau').setValue(self.controller.tau)

        info = "yayyyyyy"
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one

        self.controller.set_wavelength(value.value(self.axis_unit), set_type='abs')
        self.emit_status(ThreadCommand('Update_Status', ['yayyyyy encore']))

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)

        self.controller.set_wavelength(value.value(self.axis_unit), set_type='rel')
        self.emit_status(ThreadCommand('Update_Status', ['yayyyy c\'est trop bien']))

    def move_home(self):
        """Call the reference method of the controller"""

        self.controller.find_reference()
        self.emit_status(ThreadCommand('Update_Status', ['wowwwww']))

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""

        self.controller.stop()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Oh no I\'ve stopped!!']))


if __name__ == '__main__':
    main(__file__)
