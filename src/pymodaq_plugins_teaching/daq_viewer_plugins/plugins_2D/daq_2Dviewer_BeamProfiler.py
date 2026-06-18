import laserbeamsize as lbs
import numpy as np

from pymodaq.control_modules.viewer_utility_classes import main
from pymodaq_data.data import DataToExport
from pymodaq.utils.data import DataFromPlugins, DataCalculated


from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera
from pyqtgraph.parametertree import Parameter


class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):
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

    params = DAQ_2DViewer_BSCamera().params + [
        {'title': 'Show D:', 'name': 'show_d', 'type': 'bool', 'value': True, 'default': False},
        {'title': 'Show xy:', 'name': 'show_xy', 'type': 'bool', 'value': True, 'default': False},
        {'title': 'Show phi:', 'name': 'show_phi', 'type': 'bool', 'value': True, 'default': False},
    ]

    def ini_attributes(self):
        super().ini_attributes()
        self.show_d = True
        self.show_xy = True
        self.show_phi = True

    def commit_settings(self, param: Parameter):
        super().commit_settings(param)
        if param.name() == 'show_d':
            self.show_d = self.settings.child('show_d').value()
        elif param.name() == 'show_xy':
            self.show_xy = self.settings.child('show_xy').value()
        elif param.name() == 'show_phi':
            self.show_phi = self.settings.child('show_phi').value()


    def grab_data(self, Naverage=1, **kwargs):
        data = self.average_data(Naverage)

        #calculation
        data_raw = data.data[0].data[0]
        x, y, d_major, d_minor, phi = lbs.beam_size(data_raw)

        #emission
        dte = DataToExport(name='BeamProfiler',
                           data=[DataFromPlugins(name='Image', data=[data_raw],
                                                 dim='Data2D', labels=['Data'])])
        if self.show_d:
            dte.append(DataCalculated(name='BeamSizeD',
                                      data=[np.array([d_major]), np.array([d_minor])],
                                      dim='Data0D', units='px', labels=['Dx', 'Dy'], ))
        if self.show_xy:
            dte.append(DataCalculated(name='BeamSizeXY',
                                      data=[np.array([x]), np.array([y])],
                                      dim='Data0D', units='px', labels=['x', 'y']))
        if self.show_phi:
            dte.append(DataCalculated(name='BeamSizePhi',
                                      data=[np.array([phi])],
                                      dim='Data0D', units='°', labels=['phi']))
        self.dte_signal.emit(dte)




if __name__ == '__main__':
    main(__file__)
