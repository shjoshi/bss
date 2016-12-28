#! /usr/local/epd/bin/python

"""
Convert p-values to rgb color
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
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


import argparse
from bss import dfsio
import sys
import numpy as np
from bss import colormaps as cm
from bss.math_ops import log10_transform
from bss.nimgdata_io import NimgDataio


def main():
    parser = argparse.ArgumentParser(description='Convert log p-values to rgb color. Assumes p-values already exist as attributes in the dfs file.\n')
    parser.add_argument('nimg_datain', help='<input dfs surface/nifti image>')
    parser.add_argument('nimg_dataout', help='<output dfs surface/nifti image>')

    args = parser.parse_args()
    bss_write_pvalue_as_log_color(args.nimg_datain, args.nimg_dataout)


def bss_write_pvalue_as_log_color(nimg_datain, nimg_dataout):

    nimg_data_type = NimgDataio.validatetype(nimg_datain)

    if nimg_data_type == 'surface':
        s1 = dfsio.readdfs(nimg_datain)
        if not hasattr(s1, 'attributes'):
            sys.stdout.write('Error: The surface ' + nimg_datain + ' is missing p-value attributes.\n')
            return
        if s1.attributes is None:
            sys.stdout.write('Error: The surface ' + nimg_datain + ' is missing p-value attributes.\n')
            return
        log_pvalues = s1.attributes
        s1.vColor, pex, cmap = cm.Colormap.log_pvalues_to_rgb(log_pvalues)
        dfsio.writedfs(nimg_dataout, s1)
    elif nimg_data_type == 'nifti_image':
        sys.stdout.write('Not implemented.\n')
        log_pvalues = NimgDataio.read(nimg_datain, attributes_only=True)
        cdict_pvalues, pex, cmap = cm.Colormap.log_pvalues_to_rgb(log_pvalues)
        LUT = cmap._lut[0:256, 0:3]
        fid = open(nimg_dataout, 'wt')
        for i in range(0, len(LUT)):
            fid.write("{0:f} {1:f} {2:f}\n".format(float(LUT[i, 0]), float(LUT[i, 1]), float(LUT[i, 2])))
        fid.close()
    else:
        raise TypeError(
            'Error: Unsupported data type. Supported data types are: ' + ', '.join(NimgDataio.datatype.keys()) + '.\n')
    sys.stdout.write('Done.\n')

if __name__ == '__main__':
    main()
