""" This module implements tests for mathematical operations on images, surfaces, and vector fields
    Also see http://brainsuite.bmap.ucla.edu for the software
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
__copyright__ = "Copyright 2015, Shantanu H. Joshi, Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"


from bss import math_ops
from bss import nii_io
from nibabel.spatialimages import SpatialImage

in_mapfile = '/Users/sjoshi/research/tools/stats/bss_data/tbm/1004.svreg.map.nii.gz'
out_jac_file = '/Users/sjoshi/research/tools/stats/bss_data/tbm/1004.svreg.map.Jac.nii.gz'


def main():
    test_math_ops_jacboian(in_mapfile, out_jac_file)


# Test for Jacobians
def test_math_ops_jacboian(mapfile, out_jacfile):
    nii = nii_io.readnii(mapfile)
    nii_data = nii.get_data()
    v1 = nii_data[:, :, :, 0]
    v2 = nii_data[:, :, :, 1]
    v3 = nii_data[:, :, :, 2]
    detJ, J = math_ops.jacobian(v1, v2, v3)

    detJimg = SpatialImage(detJ, nii.affine)
    nii_io.writenii(out_jacfile, detJimg)
    print 'Done'


if __name__ == '__main__':
    main()