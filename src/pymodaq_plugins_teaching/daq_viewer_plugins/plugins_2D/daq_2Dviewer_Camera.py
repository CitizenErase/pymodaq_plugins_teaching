import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer


class DAQ_2DViewer_Camera(DAQ_Viewer_base):
    """ Instrument plugin class for a 2D viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    blam

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.

    """
    params = comon_parameters + [
        {'title': 'Position:', 'name': 'pos', 'type': 'float', 'value': 0},
        {'title': 'Amplitude:', 'name': 'amp', 'type': 'float', 'value': 0},
        {'title': 'Linewidth:', 'name': 'lw', 'type': 'float', 'value': 0},
        {'title': 'Noise:', 'name': 'noise', 'type': 'float', 'value': 0},
        {'title': 'Update settings:', 'name': 'update', 'value': False,
              'label': 'Update!'},
    ]

    def ini_attributes(self):
        self.controller: Spectrometer = None

        self.x_axis = None
        self.y_axis = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'pos':
           self.controller.data_wavelength = param.value()
        elif param.name() == 'amp':
            self.controller.amplitude = param.value()
        elif param.name() == 'lw':
            self.controller.width = param.value()
        elif param.name() == 'noise':
            self.controller.noise = param.value()
        elif param.name() == 'update':
            self.settings.child('pos').setValue(self.controller.data_wavelength)
            self.settings.child('amp').setValue(self.controller.amplitude)
            self.settings.child('lw').setValue(self.controller.width)
            self.settings.child('noise').setValue(self.controller.noise)
        else:
            pass

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        if self.is_master:
            self.controller = Spectrometer()
            initialized = self.controller.open_communication()
        else:
            self.controller = controller
            initialized = True

        self.settings.child('pos').setValue(self.controller.data_wavelength)
        self.settings.child('amp').setValue(self.controller.amplitude)
        self.settings.child('lw').setValue(self.controller.width)
        self.settings.child('noise').setValue(self.controller.noise)

        # get the x_axis
        data_x_axis = self.controller.get_wavelength_axis()
        self.x_axis = Axis(data=data_x_axis, label='Wavelength', units='nm', index=1)

        # get the y_axis
        data_y_axis = self.controller.get_image_axis()
        self.y_axis = Axis(data=data_y_axis, label='Position', units='', index=0)

        self.dte_signal_temp.emit(DataToExport('Camera',
                                               data=[DataFromPlugins(name='Image', data=[np.zeros((128, 256))],
                                                                     dim='Data2D', labels=['Data'],
                                                                     axes=[self.y_axis, self.x_axis]),]))

        info = "hello"
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close_communication()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """

        # get the x_axis
        data_x_axis = self.controller.get_wavelength_axis()
        self.x_axis = Axis(data=data_x_axis, label='Wavelength', units='nm', index=1)

        ##synchrone version (blocking function)
        data_tot = self.controller.grab_image()
        self.dte_signal.emit(DataToExport('Camera',
                                          data=[DataFromPlugins(name='Image', data=[data_tot],
                                                                dim='Data2D', labels=['Data'],
                                                                axes=[self.y_axis, self.x_axis] )]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.emit_status(ThreadCommand('Update_Status', ['ok']))
        return ''


if __name__ == '__main__':
    main(__file__)
