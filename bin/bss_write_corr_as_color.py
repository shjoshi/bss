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
from bss import colormaps as cm
import sys


def main():
    parser = argparse.ArgumentParser(description='Convert p-values to rgb color. Assumes p-values already exist as attributes in the dfs file.\n')
    parser.add_argument('dfs_surface_in', help='<input dfs surface>')
    parser.add_argument('dfs_surface_out', help='<output dfs surface>')

    args = parser.parse_args()
    bss_write_corr_as_color(args.dfs_surface_in, args.dfs_surface_out)


def bss_write_corr_as_color(surfin, surfout):

    s1 = dfsio.readdfs(surfin)

    if not hasattr(s1, 'attributes'):
        sys.stdout.write('Error: The surface ' + surfin + ' is missing p-value attributes.\n')
        sys.exit(0)

    s1.vColor, cex, cmap = cm.Colormap.correlation_to_rgb(s1.attributes)
    # cm.Colormap.exportParaviewCmap(cdict_orig, surfout + '.xml')
    dfsio.writedfs(surfout, s1)
    return

if __name__ == '__main__':
    main()
