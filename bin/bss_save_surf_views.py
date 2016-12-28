#! /usr/local/epd/bin/python
"""
This script will save renderings of surfaces with colormaps
"""

"""Copyright (C) Shantanu H. Joshi
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
__copyright__ = "Copyright 2016, Shantanu H. Joshi Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

from bss import dfsio
import sys
import numpy as np
import os
from bss import colormaps as cm
try:
    from mayavi import mlab
except (ImportError, RuntimeError) as e:
    raise SystemExit('\nImportError: mayavi not installed. Skipping surface plotting.\n')

# import imcrop
import argparse
from copy import deepcopy
from bss import mpl_import
mpl_import.init()
from matplotlib import colors as mpl_colors


def main():
    parser = argparse.ArgumentParser(description='Plot surface views with a colormap overlay.')
    parser.add_argument('surfin', help='input surface')
    parser.add_argument('-hemi', dest='hemi', help='hemisphere [lh,rh]')
    parser.add_argument('-pngoutdir', dest='pngoutdir', help='Output directory for png files')
    parser.add_argument('-cmapout', help='output colormap', required=False, action='store_true')
    parser.add_argument('-colorbar', help='save colorbar', required=False, action='store_true')

    args = parser.parse_args()
    plot_surf_views(args.surfin, args.hemi, args.pngoutdir, args.cmapout, args.colorbar)


def plot_surf_views(surfin, hemi, pngoutdir, cmapout, colorbarflag):

    s1 = dfsio.readdfs(surfin)
    pex = np.max(np.abs(s1.attributes))
    cdict = cm.Colormap.create_bidirectional_logpvalues_cmap_dict(pex)

    cdict_orig = deepcopy(cdict)
    # Scale the attribute values in cdict from 0 to 1
    for i in range(0, len(cdict['red'])):
        cdict['red'][i] = ((cdict['red'][i][0] + pex)/(2*pex), cdict['red'][i][1], cdict['red'][i][2])
    for i in range(0, len(cdict['green'])):
        cdict['green'][i] = ((cdict['green'][i][0] + pex)/(2*pex), cdict['green'][i][1], cdict['green'][i][2])
    for i in range(0, len(cdict['blue'])):
        cdict['blue'][i] = ((cdict['blue'][i][0] + pex)/(2*pex), cdict['blue'][i][1], cdict['blue'][i][2])

    my_cmap = mpl_colors.LinearSegmentedColormap('my_bi_cmap', cdict, 256)
    my_cmap._init()

    # my_cmap, cdict_orig = cm.create_bidirectional_log_colormap(pminneg,pmaxneg,pminpos,pmaxpos,pIDneg,pIDpos)

    head,tail = os.path.split(surfin)
    cmap_png_filename = pngoutdir + '/' + os.path.splitext(tail)[0] +'_colormap' + '.png.eps'
    try:
        os.mkdir(pngoutdir)
    except OSError:
        pass

    if cmapout is not None:
        cmapfilename = os.path.join(pngoutdir, 'colormap')
        cm.Colormap.exportParaviewCmap(cdict_orig, cmapfilename + '.xml')
        # cm.Colormap.exportMayavi2LUT(-1*pex, 1*pex, cmapfilename)

    if colorbarflag:
        cm.Colormap.show_and_save_colorbar(s1.attributes, my_cmap, cdict_orig, cmap_png_filename)

    mlab.figure(size=(1200, 800),bgcolor=(1,1,1))
    tmesh = mlab.triangular_mesh(s1.vertices[:, 0], s1.vertices[:, 1], s1.vertices[:, 2], s1.faces, colormap='hot',
                                 scalars=s1.attributes, vmin=cdict_orig['red'][0][0], vmax=cdict_orig['red'][-1][0])

    lut = tmesh.module_manager.scalar_lut_manager.lut.table.to_array()
    tmesh.module_manager.scalar_lut_manager.lut.table = ((my_cmap._lut[0:256, :]*255).astype('uint32'))

#    if colorbaronlyflag:
#        mlab.colorbar(orientation='vertical',nb_labels=14,nb_colors=256)
#        pngfilename = pngoutdir + '/' + os.path.splitext(tail)[0] +'_colobar' +'.png'
#        mlab.savefig(pngfilename)
#        img = imcrop.autoCrop(pngfilename)
#        img = imcrop.imTrans(img)
#        img.save(pngfilename,'PNG')
#        return


    if hemi == 'lh':
        vs = np.array([[170, 65], [0, 90], [90, 100], [-90, 85], [-90, 180], [-90, 0]])
        rollvar = [75, -75, None, None, 0, 0]
    else:
        vs = np.array([[10, 75], [180, 90], [90, 100], [-90, 85], [-90, 180], [-90, 0]])
        rollvar = [-75, 75, None, None, 0, 0]

    for i in np.arange(0, len(vs)):
        mlab.view(vs[i][0], vs[i][1], roll=rollvar[i])
        pngfilename = pngoutdir + '/' + os.path.splitext(tail)[0] +'_view' + str(i+1)+'.png'
        mlab.savefig(pngfilename)
#         img = imcrop.autoCrop(pngfilename)
#         img = imcrop.imTrans(img)
#         img.save(pngfilename,'PNG')
        sys.stdout.write(str(i) + ' ')
        sys.stdout.flush()

if __name__ == "__main__":
    main()
