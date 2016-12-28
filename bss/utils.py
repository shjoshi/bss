#! /usr/local/epd/bin/python

"""General utilities"""

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
__email__ = "s.joshi@g.ucla.edu"

import os


class FileTypes(object):

    types = \
        {'cortical_thickness_left': 'atlas_pvcthickness.left.mid.cortex.svreg.dfs',
         'cortical_thickness_right': 'atlas_pvcthickness.right.mid.cortex.svreg.dfs',
         'tbm': '.svreg.map.nii.gz',
         'roi': '.roiwise.stats.txt',
         'cerebrum_mask': '.cerebrum.mask.nii.gz',
         }


class FileLists(object):

    @staticmethod
    def construct(subjdir, subjid, hemi, type):
        if len(subjid) > 0:
            filelist = []
            for subj in subjid:
                if type == 'cortical_thickness_left' or type == 'cortical_thickness_right':
                    filesuffix = FileTypes.types[type]
                else:
                    filesuffix = '{0:s}{2:s}'.format(subj, FileTypes.types[type])
                filelist.append(os.path.join(subjdir, filesuffix, '{0:s}{1:s}'.format(subjid, FileTypes.types[type])))
            return filelist
        else:
            if type == 'cortical_thickness_left' or type == 'cortical_thickness_right':
                filesuffix = FileTypes.types[type]
            else:
                filesuffix = '{0:s}{2:s}'.format(subjid, FileTypes.types[type])
            return os.path.join(subjdir, filesuffix, '{0:s}{1:s}'.format(subjid, FileTypes.types[type]))
