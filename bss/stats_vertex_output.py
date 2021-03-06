#! /usr/local/epd/bin/python

"""Output specification and formatting for vertex wise statistical results"""

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
__copyright__ = "Copyright 2015, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center"\
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"

import numpy as np
import os
import dfsio
import sys
import colormaps


class StatsVtxOutput(object):

    def __init__(self, statsresult, dim=0):
        self.statsresult = statsresult
        pass

    def save(self, outdir, outprefix, atlas_filename):
        sys.stdout.write('Saving output files...\n')
        self.statsresult.adjust_for_multi_comparisons()

        s1 = dfsio.readdfs(atlas_filename)

        s1.attributes = self.statsresult.pvalues
        # print s1.attributes

        if len(s1.attributes) == s1.vertices.shape[0]:
            # Also write color to the field
            s1.vColor = colormaps.Colormap.get_rgb_color_array('pvalue', s1.attributes)
            dfsio.writedfs(os.path.join(outdir, outprefix + '_atlas_pvalues.dfs'), s1)
            if len(self.statsresult.pvalues_adjusted) > 0:
                s1.attributes = self.statsresult.pvalues_adjusted
                # Also write color to the field
                s1.vColor = colormaps.Colormap.get_rgb_color_array('pvalue', s1.attributes)
                dfsio.writedfs(os.path.join(outdir, outprefix + '_atlas_pvalues_adjusted.dfs'), s1)
        else:
            sys.stdout.write('Error: Dimension mismatch between the p-values and the number of vertices. '
                             'Quitting without saving.\n')

        if len(self.statsresult.corrvalues) > 0:
            s1.attributes = self.statsresult.corrvalues
            s1.vColor = colormaps.Colormap.get_rgb_color_array('corr', s1.attributes)
            dfsio.writedfs(os.path.join(outdir, outprefix + '_corr.dfs'), s1)
            self.statsresult.corrvalues[np.abs(self.statsresult.pvalues_adjusted) > 0.05] = 0
            s1.attributes = self.statsresult.corrvalues
            # Also write color to the field
            s1.vColor = colormaps.Colormap.get_rgb_color_array('corr', s1.attributes)
            dfsio.writedfs(os.path.join(outdir, outprefix + '_corr_adjusted.dfs'), s1)
        sys.stdout.write('Done.\n')
