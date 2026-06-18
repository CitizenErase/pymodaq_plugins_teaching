import laserbeamsize as lbs

from pymodaq.extensions.data_mixer.model import DataMixerModel, np  # np will be used in method eval of the formula
from pymodaq_data.data import DataToExport, DataCalculated


class DataMixerBeamProfilerModel(DataMixerModel):
    params = [
        {'title': 'Show D:', 'name': 'show_d', 'type': 'bool', 'value': True, 'default': False},
        {'title': 'Show xy:', 'name': 'show_xy', 'type': 'bool', 'value': True, 'default': False},
        {'title': 'Show phi:', 'name': 'show_phi', 'type': 'bool', 'value': True, 'default': False},
    ]
    
    def process_dte(self, dte: DataToExport):
        dte_processed = DataToExport('computed')
        dwa = dte[0]
        x, y, d_major, d_minor, phi = lbs.beam_size(dwa.data[0])

        if self.settings['show_xy']:
            dte_processed.append(
                DataCalculated('BeamSizexy',
                               data=[np.array([x]), np.array([y])],
                               dim='Data0D', units='px', labels=['X', 'Y']))
        if self.settings['show_d']:
            dte_processed.append(
                DataCalculated('BeamSizeD',
                               data=[np.array([d_major]), np.array([d_minor])],
                               dim='Data0D', units='px', labels=['Dmaj', 'Dmin']))
        if self.settings['show_phi']:
            dte_processed.append(
                DataCalculated('BeamSizePhi',
                               data=[np.array([phi])],
                               dim='Data0D', units='°', labels=['Phi']))

        return dte_processed
