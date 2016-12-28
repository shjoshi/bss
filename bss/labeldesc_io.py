#! /usr/local/epd/bin/python

"""Data io for the label description file"""

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
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

from xml.dom import minidom
import os
from numpy import unique


class LabelDesc(object):
    this_dir, this_filename = os.path.split(__file__)
    # TODO: The name brainsuite_labeldescriptions_14May2014.xml is hardcoded. Could be loaded from a conf file in future
    label_desc_file = os.path.join(this_dir, "conf", "brainsuite_labeldescriptions_14May2014.xml")
    xmldoc = minidom.parse(label_desc_file)
    idlist = xmldoc.getElementsByTagName('label')
    labelids = [int(id.attributes['id'].value) for id in idlist]
    labelnames = [id.attributes['fullname'].value for id in idlist]
    roilabels = dict(zip(labelids, labelnames))

    @classmethod
    def read_labeldesc(cls):
        print open(cls.label_desc_file)

    @classmethod
    def validate_roiid(cls, roiid):
        for i in roiid:
            if i not in cls.labelids:
                return False
        return True

    @classmethod
    def validate_roiid_against_atlas_labels(cls, roiid, atlas_labels):
        # First validate roiids if they exist in label description file
        if LabelDesc.validate_roiid(roiid):
            # Then validate roiid against the atlas labels
            atlas_label_ids = unique(atlas_labels)
            for i in roiid:
                if i not in atlas_label_ids:
                    return False
        else:
            return False
        return True

    @classmethod
    def validate_roiid_only_against_atlas_labels(cls, roiid, atlas_labels):
        atlas_label_ids = unique(atlas_labels)
        for i in roiid:
            if i not in atlas_label_ids:
                return False
        return True
