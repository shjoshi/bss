#! /usr/local/epd/bin/python

"""Class for performing multiple testing (comparisons)"""

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
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

from sys import stdout
import numpy as np


class Stats_Multi_Comparisons():

    def __init__(self):
        pass

    @staticmethod
    def adjust(pvalues, method='BH'):
        direction = np.sign(pvalues)
        if method == 'BH':
            p_adjust = Stats_Multi_Comparisons.adjust_BH(np.abs(pvalues))
        else:
            raise ValueError('method has to be BH.')
        return p_adjust*direction

    @staticmethod
    def adjust_BH(pvalues):

        direction = np.sign(pvalues)
        m = len(pvalues)
        idx = np.argsort(np.abs(pvalues))
        pvalues_sorted = np.sort(np.abs(pvalues))

        qarray = pvalues_sorted * m / (np.arange(m) + 1)
        new_qarray = np.minimum.accumulate(qarray[::-1])[::-1]

        p_adjust = new_qarray[np.argsort(idx)]

        return p_adjust*direction

