#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
from six import iteritems
import networkx as nx
from msnpy.portals import load_trees
from dimspy.portals.hdf5_portal import save_peaklists_as_hdf5
from dimspy.models.peaklist import PeakList
from dimspy.process.peak_alignment import align_peaks
import itertools
import numpy as np
import ast
import re

peaklists = []
trees = load_trees("test-data/A06_annotated_trees_backup.json")
plsd = {}

# get peaklist for each header
for tree in trees:
    tv = tree.nodes.values()
    plsd[tree.graph['id']] = []
    for header, group in itertools.groupby(tv, key=lambda x: x['header']):
        # get mz, intensity, mass, molecular formula, adduct
        print(header)
        mz = []
        intensity = []
        mf_details = []
        mass = []
        mf = []
        adduct = []
        metad = {'tree_id'=tree.graph['id'], 'header'=header}
        for d in list(group):

            if d['precursor']:

                mf_details = d['mf'].values()[0]
                metad['precursor{}_mz'.format(d['mslevel'])] = d['mz']
                metad['precursor{}_mass'.format(d['mslevel'])] = mf_details['mass']
                metad['precursor{}_adduct'.format(d['mslevel'])] = mf_details['adduct']
                metad['precursor{}_mf'.format(d['mslevel'])] = mf_details['mf']
                continue
            elif d['mslevel'] == 1:
                continue

            mz.append(d['mz'])
            intensity.append(d['intensity'])
            mf_details = d['mf'].values()[0]
            mass.append(mf_details['mass'])
            mf.append(mf_details['mf'])
            adduct.append(mf_details['adduct'])

        if not mz:
            continue

        # create dimspy array object
        pl = PeakList(ID='{}: {}'.format(tree.graph['id'], header),
                      mz=mz,
                      intensity=intensity,
                      **metad)
        pl.add_attribute('mass', mass)
        pl.add_attribute('mf', mf)
        pl.add_attribute('adduct', adduct)

        plsd[tree.graph['id']].append(pl)


# Merge
plms = []
for (key, pls) in iteritems(plsd):
    merged_id = "<#>".join([pl.ID for pl in pls])
    pm = align_peaks(pls, ppm=2.0)
    plm = pm.to_peaklist(ID=merged_id)
    plms.append(plm)

save_peaklists_as_hdf5(plms, 'merged_pls.hdf5')

pls = [y for x in list(plsd.values()) for y in x]
save_peaklists_as_hdf5(pls, 'pls.hdf5')
