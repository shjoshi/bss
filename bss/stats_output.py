#! /usr/local/epd/bin/python

"""Output specification for statistical tests"""

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
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center"\
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import numpy as np
import os
import dfsio
import sys
from stats_mult_comp import Stats_Multi_Comparisons
import colormaps


class StatsOutput(object):

    def __init__(self, dim=0):
        self.pvalues = np.zeros(dim)
        self.pvalues_signed = np.zeros(dim)
        self.pvalues_adjusted = np.zeros(dim)
        self.tvalues = np.zeros(dim)
        self.corrvalues = []

    def adjust_for_multi_comparisons(self):
            self.pvalues_adjusted = Stats_Multi_Comparisons.adjust(self.pvalues)

    def save(self, outdir, outprefix, atlas_filename):
        sys.stdout.write('Saving output files...\n')
        self.adjust_for_multi_comparisons()

        s1 = dfsio.readdfs(atlas_filename)

        s1.attributes = self.pvalues
        # print s1.attributes

        if len(s1.attributes) == s1.vertices.shape[0]:
            # Also write color to the field
            s1.vColor = colormaps.Colormap.get_rgb_color_array('pvalue', s1.attributes)
            dfsio.writedfs(os.path.join(outdir, outprefix + '_atlas_pvalues.dfs'), s1)
            if len(self.pvalues_adjusted) > 0:
                s1.attributes = self.pvalues_adjusted
                # Also write color to the field
                s1.vColor = colormaps.Colormap.get_rgb_color_array('pvalue', s1.attributes)
                dfsio.writedfs(os.path.join(outdir, outprefix + '_atlas_pvalues_adjusted.dfs'), s1)
        else:
            sys.stdout.write('Error: Dimension mismatch between the p-values and the number of vertices. '
                             'Quitting without saving.\n')

        if len(self.corrvalues) > 0:
            s1.attributes = self.corrvalues
            s1.vColor = colormaps.Colormap.get_rgb_color_array('corr', s1.attributes)
            dfsio.writedfs(os.path.join(outdir, outprefix + '_corr.dfs'), s1)
            self.corrvalues[np.abs(self.pvalues_adjusted) > 0.05] = 0
            s1.attributes = self.corrvalues
            # Also write color to the field
            s1.vColor = colormaps.Colormap.get_rgb_color_array('corr', s1.attributes)
            dfsio.writedfs(os.path.join(outdir, outprefix + '_corr_adjusted.dfs'), s1)
        sys.stdout.write('Done.\n')
