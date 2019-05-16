#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
from dimspy.portals import hdf5_portal
import numpy as np
import ast
import re
msp_type = 'massbank'
polarity = 'positive'
ms_level = 2
msnpy_annotations = False
# MSP format
msp_params = {}

if msp_type == 'massbank':
    msp_params['name'] = 'RECORD_TITLE:'
    msp_params['polarity'] = 'AC$MASS_SPECTROMETRY: ION_MODE'
    msp_params['precursor_mz'] = 'MS$FOCUSED_ION: PRECURSOR_M/Z '
    msp_params['precursor_type'] = 'MS$FOCUSED_ION: PRECURSOR_TYPE'
    msp_params['num_peaks'] = 'PK$NUM_PEAK:'
    msp_params['cols'] = 'PK$PEAK: m/z int. rel.int.'
    msp_params['ms_level'] = 'AC$MASS_SPECTROMETRY: MS_TYPE '
    msp_params['resolution'] = 'AC$MASS_SPECTROMETRY: RESOLUTION '
    msp_params['fragmentation_mode'] = 'AC$MASS_SPECTROMETRY: FRAGMENTATION_MODE'
    msp_params['collision_energy'] = 'AC$MASS_SPECTROMETRY: COLLISION_ENERGY'
else:
    msp_params['name'] = 'NAME:'
    msp_params['polarity'] = 'POLARITY:'
    msp_params['precursor_mz'] = 'PRECURSOR_MZ:'
    msp_params['precursor_type'] = 'PRECURSOR_TYPE:'
    msp_params['num_peaks'] = 'Num Peaks:'
    msp_params['cols'] = ''
    msp_params['ms_level'] = 'MS_LEVEL:'
    msp_params['resolution'] = 'RESOLUTION:'
    msp_params['fragmentation_mode'] = 'FRAGMENTATION_MODE:'
    msp_params['collision_energy'] = 'COLLISION_ENERGY:'


# read in peaklist
pls = hdf5_portal.load_peaklists_from_hdf5('test-data/A06_processed_peaklists.hdf5')

# first merge the ms2 and ms3 peaklists


with open("test-data/test.msp", "w+") as f:
    # Loop through peaklist
    for pl in pls:
        dt = pl.dtable[pl.flags]
        if dt.shape[0] == 0:
            continue

        if re.search('.*Full ms .*', pl.ID) and ms_level > 1:
            continue

        f.write('{} {}\n'.format(msp_params['name'], pl.ID))
        f.write('{} {}\n'.format(msp_params['polarity'], polarity))

        if msnpy_annotations:
            f.write('{} {}\n'.format(msp_params['precursor_type'], 'TODO'))
        else:
            mtch = re.search('.*Full ms(\d+).*', pl.ID)
            if mtch:
                f.write('{} {}\n'.format(msp_params['ms_level'], mtch.group(1)))

            mtch = re.search('.*Full ms\d+ (.*) \[.*', pl.ID)
            if mtch:
                dl = mtch.group(1).split(" ")
                # get the last detail
                detail = dl[-1]

                mtch = re.search('(\d+.\d+)@(\D+)(.*)', detail)

                if mtch:
                    f.write('{} {}\n'.format(msp_params['precursor_mz'], mtch.group(1)))
                    f.write('{} {}\n'.format(msp_params['fragmentation_mode'], mtch.group(2)))
                    f.write('{} {}\n'.format(msp_params['collision_energy'], mtch.group(3)))

        f.write('{} {}\n'.format(msp_params['num_peaks'], dt.shape[0]))
        if msp_params['cols']:
            f.write('{}\n'.format(msp_params['cols']))

        mz = dt['mz']
        intensity = dt['intensity']
        ra = dt['intensity'] / np.max(dt['intensity']) * 100

        for i in range(0, len(mz)-1):
            mzi = mz[i]
            intensityi = intensity[i]
            rai = ra[i]
            if msp_type == 'massbank':
                f.write('{}\t{}\t{}\n'.format(mzi, intensityi, rai))
            else:
                f.write('{}\t{}\n'.format(mzi, rai))
        f.write('\n')


# have option to filter on header text (e.g. MS2)

# Get precursors from header if not available anywhere else

# Make MSP


