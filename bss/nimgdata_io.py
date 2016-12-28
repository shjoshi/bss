""" This module implements a container class for neuroimaging data IO including surfaces, curves, and images
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

import numpy as np
import struct
import os
import sys
import nibabel as nib
import dfsio
import dfcio
import nii_io
import pandas
from scipy.io import savemat, loadmat
import excepts
from os.path import splitext


class NimgDataio(object):

    def __init__(self):
        pass

    datatype = {'.dfs': 'surface',
                # '.dfc': 'curve,',
                # '.ucf': 'curve',
                '.nii.gz': 'nifti_image',
                }

    @staticmethod
    def findext(filename):

        if filename[-7:] == '.nii.gz':
            return '.nii.gz'
        if filename[-4:] == '.dfs':
            return '.dfs'
        # filenamewoext, filext = os.path.splitext(filename)
        # return filext

    @staticmethod
    def validatetype(filename):
        filext = NimgDataio.findext(filename)
        if filext not in NimgDataio.datatype.keys():
            raise TypeError('Error: Unsupported data type. Supported data types are: ' + ', '.join(NimgDataio.datatype.keys()))
        else:
            return NimgDataio.datatype[filext]

    @staticmethod
    def read(filename, maskimgfile=None, attributes_only=True):
        filetype = NimgDataio.validatetype(filename)
        if filetype == 'surface':
            if not attributes_only:
                return NimgDataio.read_surface(filename)
            else:
                return NimgDataio.read_surface_attributess(filename)

        if filetype == 'nifti_image':
            if attributes_only:
                return NimgDataio.read_nifi_image_as_array(filename, maskimgfile)
            else:
                return NimgDataio.read_nifi_image_obj(filename, maskimgfile)

    @staticmethod
    def read_surface(filename, mask_idx=None):
        filetype = NimgDataio.validatetype(filename)
        if filetype == 'surface':
            return dfsio.readdfs(filename)

    @staticmethod
    def read_surface_attributess(filename, mask_idx=None):
        filetype = NimgDataio.validatetype(filename)
        if filetype == 'surface':
            return dfsio.readdfsattributes(filename)

    @staticmethod
    def read_nifi_image_obj(filename, maskimgfile=None):
        nimgobj = nii_io.readnii(filename)
        return nimgobj

    @staticmethod
    def read_nifi_image_mask_idx(filename):
        nimgobj = nii_io.readnii(filename)
        nifti_img = nimgobj.get_data()
        nifti_img = np.reshape(nifti_img, (1, nifti_img.shape[0]*nifti_img.shape[1]*nifti_img.shape[2]))
        mask_idx = (nifti_img > 0).nonzero()[1]
        if len(mask_idx) == 0:
            raise excepts.FileZeroElementsReadError('Read zero elements from the mask file ' + filename +
                                              '. Any values that need to be masked must be > 0.')
        return mask_idx

    @staticmethod
    def read_nifi_image_as_array(filename, maskimgfile=None):
        nimgobj = nii_io.readnii(filename)
        nifti_img = nimgobj.get_data()
        nifti_img = np.reshape(nifti_img, (1, nifti_img.shape[0]*nifti_img.shape[1]*nifti_img.shape[2]))

        # mask_idx = np.ones((0, nifti_img.size))
        mask_idx = np.arange(0, nifti_img.size)
        if maskimgfile:
            mask_nimgobj = nii_io.readnii(maskimgfile)
            mask_nifti_img = mask_nimgobj.get_data()
            mask_nifti_img = np.reshape(mask_nifti_img, (1, mask_nifti_img.shape[0]*mask_nifti_img.shape[1]*mask_nifti_img.shape[2]))
            mask_idx = np.where(mask_nifti_img == 255)
        return nifti_img[0, mask_idx]

    @staticmethod
    def write_nifti_image(filename, nifti_img_data):
        new_image = nib.Nifti1Image(nifti_img_data, affine=np.eye(4))
        nib.save(new_image, filename)

    @staticmethod
    def write_nifti_image_from_array(filename, nifti_img_data_array, nifti_img_obj):
        nifti_img_obj_data = nifti_img_obj.get_data()
        nifti_img_data_array = np.reshape(nifti_img_data_array,
                                          (nifti_img_obj_data.shape[0], nifti_img_obj_data.shape[1], nifti_img_obj_data.shape[2]))
        new_image = nib.Nifti1Image(nifti_img_data_array, affine=nifti_img_obj.get_affine())
        nib.save(new_image, filename)

    @staticmethod
    def read_aggregated_attributes_from_filelist(filelist, attrib_siz):
        attribute_array = np.empty((len(filelist), attrib_siz), 'float')
        filelist = [i.rstrip().lstrip() for i in filelist]
        for i in range(0, len(filelist)):
            if not os.path.isfile(filelist[i].rstrip().lstrip()):
                raise IOError('File  ' + filelist[i] + ' does not exist.\n')
                # sys.stdout.write('File: ' + filelist[i] + ' does not exist.\n')
                # return []

            sys.stdout.write('Reading file ' + filelist[i] + '.\n')
            sys.stdout.flush()
            filext = NimgDataio.findext(filelist[0])
            # filenamewoext, ext = os.path.splitext(filelist[0])
            if filext not in NimgDataio.datatype.keys():
                raise TypeError('Error: Unsupported data type. Supported data types are: ' + ', '.join(NimgDataio.datatype.keys()))
            elif NimgDataio.datatype[filext] == 'surface':
                attributes = dfsio.readdfsattributes(filelist[i])
            elif NimgDataio.datatype[filext] == 'nifti_image':
                nimgobj = nii_io.readnii(filelist[i])
                nifti_img = nimgobj.get_data()
                attributes = np.reshape(nifti_img, (1, nifti_img.size))
            if attributes.size != attrib_siz:
                sys.stdout.write("Length of attributes in File " + filelist[i] + " and the atlas do not match. "
                                                                                  "Please check if the hemispheres match. Quitting.\n")
                attribute_array = []
                return attribute_array
            else:
                attribute_array[i, :] = attributes
        return attribute_array

    @staticmethod
    def read_aggregated_attributes(filename):
        data_list = pandas.read_table(filename, sep='\t')
        filelist = data_list['File']
        return NimgDataio.read_aggregated_attributes_from_filelist(filelist)

    @staticmethod
    def export_data_to_mat(filelist, outputfile):
        fid = open(filelist, 'rt')
        filenames = [filename.rstrip('\n') for filename in fid.readlines()]

        # Read the first file to get the size of the attributes
        temp_array = NimgDataio.read(filenames[0], attributes_only=True)
        attribute_array = NimgDataio.read_aggregated_attributes_from_filelist(filenames, temp_array.shape[0])
        savemat(outputfile, {'data_array': attribute_array})
        sys.stdout.write('Done.\n')

    @staticmethod
    def write_attribute_to_surface(insurface, attribute_file, outsurface):
        s1 = NimgDataio.read_surface(insurface)
        filext = splitext(attribute_file)[1]
        attributes = []
        if filext == '.txt':
            attributes = np.loadtxt(attribute_file)
        elif filext == '.mat':
            temp = loadmat(attribute_file)
            attributes = temp[temp.keys()[0]]  # Just read the first variable in the .mat file
        else:
            raise ValueError('Error: Invalid attribute file' + attribute_file +
                             '. Attribute file should have a .mat or a .txt format.\n')

        if s1.vertices.shape[0] != attributes.shape[1]:
            raise excepts.AttributeLengthError('Error: Attribute lengths of data in {0:s} and the surface {1:s} do not match.\n'.format(attribute_file, insurface))

        s1.attributes = attributes
        dfsio.writedfs(outsurface, s1)
