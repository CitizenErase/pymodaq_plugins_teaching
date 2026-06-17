import laserbeamsize as lbs
import numpy as np

from pymodaq.control_modules.viewer_utility_classes import comon_parameters, main
from pymodaq_data.data import DataToExport, Axis
from pymodaq.utils.data import DataFromPlugins


from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera

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

    def grab_data(self, Naverage=1, **kwargs):
        data = self.average_data(Naverage)

        #calculation
        data_raw = data.data[0].data[0]
        x, y, d_major, d_minor, phi = lbs.beam_size(data_raw)

        #emission
        self.dte_signal.emit(DataToExport(name='BeamProfiler',
                                          data=[DataFromPlugins(name='Image', data=[data_raw],
                                                                dim='Data2D', labels=['Data']),
                                                DataFromPlugins(name='BeamSize', data=[np.array([d_major]), np.array([d_minor])],
                                                                dim='Data0D', labels=['Dx', 'Dy'])
                                                ]))


if __name__ == '__main__':
    main(__file__)
