#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
from dimspy.portals import hdf5_portal
import numpy as np

msp_type = 'massbank'
polarity = 'positive'
# MSP format
msp_params = {}

if msp_type == 'massbank':
    msp_params['name'] = '^RECORD_TITLE:'
    msp_params['polarity'] = 'AC$MASS_SPECTROMETRY: ION_MODE'
    msp_params['precursor_mz'] = 'MS$FOCUSED_ION: PRECURSOR_M/Z '
    msp_params['precursor_type'] = 'MS\$FOCUSED_ION: PRECURSOR_TYPE'
    msp_params['num_peaks'] = 'PK$NUM_PEAK:'
    msp_params['cols'] = 'PK$PEAK: m/z int. rel.int.'

else:
    msp_params['name'] = 'NAME:'
    msp_params['polarity'] = 'POLARITY:'
    msp_params['precursor_mz'] = 'PRECURSOR_MZ:'
    msp_params['precursor_type'] = 'PRECURSOR_TYPE:'
    msp_params['num_peaks'] = 'Num Peaks:'
    msp_params['cols'] = ''


# read in peaklist
pls = hdf5_portal.load_peaklists_from_hdf5('test-data/A06_processed_peaklists.hdf5')


with open("test-data/test.msp", "w+") as f:
    # Loop through peaklist
    for pl in pls:
        dt = pl.dtable[pl.flags]
        if dt.shape[0] == 0:
            continue

        f.write('{} {}\n'.format(msp_params['name'], pl.ID))
        f.write('{} {}\n'.format(msp_params['polarity'], polarity))
        f.write('{} {}\n'.format(msp_params['precursor_type'], 'TODO'))
        f.write('{} {}\n'.format(msp_params['num_peaks'], dt.shape[0]))
        if msp_params['cols']:
            f.write('{}'.format(msp_params['cols']))

        mz = dt['mz']
        intensity = dt['intensity']
        ra = dt['intensity'] / np.max(dt['intensity']) * 100

        for i in range(0, len(mz)-1):
            mzi = mz[i]
            intensityi = intensity[i]
            rai = ra[i]
            if msp_type=='massbank':
                f.write('{}\t{}\t{}\n'.format(mzi, intensityi, rai))
            else:
                f.write('{}\t{}\n'.format(mzi, rai))
        f.write('\n')


# have option to filter on header text (e.g. MS2)

# Get precursors from header if not available anywhere else

# Make MSP


