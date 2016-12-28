"""
Resample image values to shape (surface/curve)
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
__copyright__ = "Copyright 2016, Shantanu H. Joshi Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

import argparse
import traceback
import sys
from bss.math_ops import image_to_shape
import os
import time


def main():
    parser = argparse.ArgumentParser(description='Resample image values to shape (surface/curve) '
                                                 'and overwrites the attribute field in the shape file.\n'
                                                 'Assumes shape and image lie in the same coordinate space.\n')
    parser.add_argument('image', help='nifti image (nii.gz)')
    parser.add_argument('shape', help='shape (dfs)')
    parser.add_argument('-output', dest='output', help='output shape (if not provided, the attributes of input shape are overwritten)',
                        required=False)
    parser.add_argument('-resample', dest='resample', help='resampling method [nearest/mean/max]',
                        required=False, choices=['nearest', 'mean', 'max'], default='mean')

    args = parser.parse_args()

    t = time.time()
    bss_image_to_shape(args.image, args.shape, args.output, args.resample)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.\n")


def bss_image_to_shape(image, shape, output, resample):

    try:
        image_to_shape(image, shape, output, resample)
    except (IOError, TypeError, IndexError) as e:
        sys.stdout.write(e.args[0] + '\n')
    except:
        sys.stdout.write("Something went wrong. Please send this error message to the developers.")
        sys.stdout.write(traceback.print_exc(file=sys.stdout))

if __name__ == '__main__':
    main()
