#! /usr/local/epd/bin/python

"""Data specification for ROI statistical tests"""

"""Copyright (C) Shantanu H. Joshi, David Shattuck,
Brain Mapping Center, University of California Los Angeles

Bss is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

Bss is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA."""


__author__ = "Shantanu H. Joshi"
__copyright__ = "Copyright 2015, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import numpy as np
import roi_io
from stats_data import StatsData


class StatsROIData(object):

    def __init__(self, demographics_file, model):
        self.dataframe = None
        self.model = model
        self.demographics_data = StatsData.read_demographics(demographics_file)
        self.roiid = model.roiid
        self.roimeasure = model.roimeasure
        self.roidata = np.zeros((self.demographics_data.shape[0], len(self.roiid)))
        self.read_roi_data_for_all_subjects()

    def read_roi_data_for_all_subjects(self):
        for idx, filename in enumerate(self.demographics_data[self.model.fileid].values):
            self.roidata[idx, :] = roi_io.read_roistats_txt(filename, self.roiid, self.roimeasure)
