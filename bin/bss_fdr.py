#! /usr/local/epd/bin/python
"""
Adjust pvalues after multiple comparisons using FDR
"""

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
__copyright__ = "Copyright 2014, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "sjoshi@bmap.ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


import argparse
from bss.stats_mult_comp import Stats_Multi_Comparisons
from bss import dfsio
import os
import sys
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Adjust p-values by testing for multiple comparisons using fdr.\n')
    parser.add_argument('pvaluein', help='input surface/curve or text file')
    parser.add_argument('pvalueout', help='output surface/curve or text file')
    parser.add_argument('-method', dest='method', help='correction method - BH, BY, bonferroni, holm, hochbergh',
                        required=False, default='BH')
    args = parser.parse_args()
    shape_fdr(args.pvaluein, args.pvalueout, args.method)


def shape_fdr(shapein, shapeout, method):

    rootnamein, extin = os.path.splitext(shapein)
    rootnameout, extout = os.path.splitext(shapein)

    if extin != extout:
        sys.stdout.write('Error: Input and output extensions should be same.\n')
        return

    if extin == '.txt':
        pvalues = np.loadtxt(shapein)
        fdr_adjusted_pvalues = Stats_Multi_Comparisons.adjust(pvalues, method=method)
        np.savetxt(shapeout, fdr_adjusted_pvalues)
    elif extin == '.dfs':
        s1 = dfsio.readdfs(shapein)
        s1.attributes = Stats_Multi_Comparisons.adjust(s1.attributes, method=method)
        dfsio.writedfs(shapeout, s1)


if __name__ == '__main__':
    main()
