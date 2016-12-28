#! /usr/local/epd/bin/python

"""Data specification for statistical tests"""

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

import dfsio
from glob import glob
import struct
import array
import os
import numpy as np
import pandas
import sys
from labeldesc_io import LabelDesc

import scipy.io
# from stats_roidata import StatsROIData
from nimgdata_io import NimgDataio
import roi_io


class StatsData(object):

    def __init__(self, demographics_file, model, max_block_size=20000, roi=False):
        self.demographic_data = ''
        self.dataframe = None
        self.roi_dataframe = None
        self.roi_flag = roi
        self.phenotype_files = []
        self.phenotype_array = None
        self.pre_data_frame = {}
        self.surface_average = None
        self.phenotype_dataframe = None
        # self.attribue_matrix = None
        self.phenotype_array = []
        self.data_read_flag = False
        self.max_block_size = max_block_size
        self.attrib_siz = 0
        self.datatype = NimgDataio.datatype[NimgDataio.findext(model.atlas)]
        self.mask_idx = []

        self.demographic_data = self.read_demographics(demographics_file)
        if self.demographic_data is None:
            self.data_read_flag = False
            return
        # if not model.phenotype_attribute_matrix_file and not model.phenotype:
        #     sys.stdout.write('Error: Phenotype is not set. Data frame will not be created.')
        #     return

        # # Choose the phenotype_attribute_matrix binary data if phenotype is also set
        # if model.phenotype_attribute_matrix_file and model.phenotype:
        #     self.read_subject_phenotype_attribute_matrix(model)
        #     self.create_data_frame(model)
        #     return

        # if model.phenotype:
        #     self.read_subject_phenotype(model)

        if not os.path.isfile(model.atlas):
            sys.stdout.write('Atlas surface file: ' + model.atlas + ' does not exist.\n')
            self.data_read_flag = False
            return
        if self.datatype == 'nifti_image':
            self.atlas_data = NimgDataio.read(model.atlas, attributes_only=True)
        elif self.datatype == 'surface':
            self.atlas_data = NimgDataio.read(model.atlas, attributes_only=False)

        # If ROI masks are set, validate them if they belong to the correct atlas
        if model.maskroiid:
            if not LabelDesc.validate_roiid_only_against_atlas_labels(model.maskroiid, self.atlas_data.labels):
                sys.stdout.write('One or more ROI labels {0:s} are not valid or do not belong to the atlas.\n'
                                 'If the ROI is valid please check if it belongs to the correct hemisphere.\n'
                                 .format(', '.join(str(x) for x in model.maskroiid)))
                self.data_read_flag = False
                return

        if self.datatype == 'nifti_image':
            self.attrib_siz = self.atlas_data.size
            self.mask_idx = np.arange(0, self.attrib_siz)
        elif self.datatype == 'surface':
            self.attrib_siz = self.atlas_data.vertices.shape[0]
            self.mask_idx = np.arange(0, self.atlas_data.vertices.shape[0])
        self.read(model)

        # After the data is read and if the maskroiid is set, mask the surface attributes by the ROI labels
        if model.maskroiid:
            self.mask_idx = np.empty((0, ), dtype=np.uint16)
            for idx in model.maskroiid:
                self.mask_idx = np.append(self.mask_idx, (self.atlas_data.labels == idx).nonzero()[0])
            self.phenotype_array = self.phenotype_array[:, self.mask_idx]

        # After the data is read, check if mask file exists
        if model.maskfile:
            if not os.path.exists(model.maskfile):
                raise IOError('Mask file ' + model.maskfile + ' does not exist.')

            self.mask_idx = NimgDataio.read_nifi_image_mask_idx(model.maskfile)
            self.phenotype_array = self.phenotype_array[:, self.mask_idx]

        return

    @classmethod
    def read_demographics(cls, demographics_file):
        if not os.path.isfile(demographics_file):
            sys.stdout.write('Demographics file: ' + demographics_file + ' does not exist.\n')
            demographic_data = None
            return

        filename, ext = os.path.splitext(demographics_file)
        if ext == '.csv':
            demographic_data = pandas.read_csv(demographics_file, dtype={'subjID': object})
        elif ext == '.txt':
            demographic_data = pandas.read_table(demographics_file, dtype={'subjID': object})

        # Iterate over all columns, and check if any of the values
        # are NaN for missing data
        for columns in demographic_data.columns.values:
            if len(np.where(demographic_data[columns].isnull())[0]) > 0:
                sys.stdout.write('Error: Some data may be missing from the demographics file: ' + demographics_file + '. ' +
                                 '\nIf nothing seems wrong at the first glance and if its a csv file, please open it in a '
                                 '\nplain text editor and check if there are missing values, rows, or columns.' +
                                 '\nAlso make sure there are no extra comma\'s at the end.' +
                                 '. Will quit now.\n')
                demographic_data = None
                break
        return demographic_data

    def validate_data(self):
        #TODO routines for validating self.demographic_data
        pass

    def read(self, model):
        if not self.roi_flag:
            self.phenotype_array = NimgDataio.read_aggregated_attributes_from_filelist(self.demographic_data[model.fileid],
                                                                                       self.attrib_siz)
        else:
            self.roiid = model.roiid
            self.roimeasure = model.roimeasure
            self.phenotype_array = self.read_roi_data_for_all_subjects(model)
            self.create_roi_data_frame()


        if len(self.phenotype_array) == 0:
            self.data_read_flag = False
        else:
            self.data_read_flag = True
            # self.create_data_frame(model)

            self.blocks_idx = []
            # At this point the data is completely read, so create indices of blocks
            if self.phenotype_array.shape[1] > self.max_block_size:
                quotient, remainder = divmod(self.phenotype_array.shape[1], self.max_block_size)
                for i in np.arange(quotient)+1:
                    self.blocks_idx.append(((i-1)*self.max_block_size, (i-1)*self.max_block_size + self.max_block_size))
                if remainder != 0:
                    i = quotient + 1
                    self.blocks_idx.append(((i-1)*self.max_block_size, (i-1)*self.max_block_size + remainder))
            else:
                self.blocks_idx.append((0, self.phenotype_array.shape[1]))
            return

    def read_subject_file(self, model):
        for filename in self.demographic_data[model.fileid]:
            self.phenotype_files.append(filename)
        s1, s1_average, self.phenotype_array = self.read_aggregated_attributes_from_surfacefilelist(self.phenotype_files)
        return

    def read_subject_phenotype(self, model):
        for subjectid in self.demographic_data[model.subjectid]:
            self.phenotype_files.append(glob(os.path.join(model.subjdir, subjectid, '*' + model.phenotype + '*'))[0])

        s1, s1_average, self.phenotype_array = dfsio.read_aggregated_attributes_from_surfacefilelist(self.phenotype_files)
        self.surface_average = s1_average

    def read_subject_phenotype_attribute_matrix(self, model):
        fid = open(model.phenotype_attribute_matrix_file, 'rb')
        rows = np.fromfile(fid, dtype='uint32', count=1)
        cols = np.fromfile(fid, dtype='uint32', count=1)
        arrayfloat = array.array('f')
        arrayfloat.fromfile(fid, rows*cols)
        self.phenotype_array = np.frombuffer(arrayfloat, dtype=np.float32, offset=0).reshape(cols, rows, order='F')
        fid.close()

    def write_subject_phenotype_array(self, filename):
        # scipy.io.savemat(filename, {'data_array': self.phenotype_array})
        # TODO: Use hdf5py to write the array
        pass

    def create_roi_data_frame(self):
        self.roi_dataframe = self.demographic_data.copy()
        for idx, roi in enumerate(self.roiid):
            self.roi_dataframe['ROI_'+str(roi)] = self.phenotype_array[:, idx]

    def create_data_frame(self, model):
        for i in model.variables:
            self.pre_data_frame[i] = self.demographic_data[i]

            # if i in model.factors:
            #     self.pre_data_frame[i] = self.demographic_data[i]
            # else:
            #     # Use either one of Int, Str, or Float vectors
            #     if self.demographic_data[i][0].dtype.type in (np.int32, np.int64):
            #         self.pre_data_frame[i] = self.demographic_data[i]
            #     elif self.demographic_data[i][0].dtype.type in (np.float32, np.float64): #TODO check this
            #         self.pre_data_frame[i] = self.demographic_data[i]
        # Create the phenotype array data frame
        # Create the column names for vertices automatically
        colnames = []
        for i in xrange(self.phenotype_array.shape[1]):
            colnames.append('V'+str(i))

        temp_frame = pandas.DataFrame(self.phenotype_array)
        temp_frame.columns = colnames
        temp_frame[model.subjectid] = self.demographic_data[model.subjectid]

        tot_dataframe = pandas.merge(self.demographic_data, temp_frame)
        tot_dataframe = pandas.melt(tot_dataframe, id_vars=self.demographic_data.columns)
        self.phenotype_dataframe = tot_dataframe
        return

    def get_data_frame_block(self, model, block_num):
        for i in model.variables:
            if i in model.factors:
                self.pre_data_frame[i] = self.demographic_data[i]
            else:
                # Use either one of Int, Str, or Float vectors
                if self.demographic_data[i][0].dtype.type in (np.int32, np.int64):
                    self.pre_data_frame[i] = self.demographic_data[i]
                elif self.demographic_data[i][0].dtype.type in (np.float32, np.float64): #TODO check this
                    self.pre_data_frame[i] = self.demographic_data[i]
        # Create the phenotype array data frame
        # Create the column names for vertices automatically
        colnames = []

        for i in range(self.blocks_idx[block_num][0], self.blocks_idx[block_num][1]):
            colnames.append('V'+str(i))

        temp_frame = pandas.DataFrame(self.phenotype_array[:, range(self.blocks_idx[block_num][0], self.blocks_idx[block_num][1])])
        temp_frame.columns = colnames
        temp_frame[model.subjectid] = self.demographic_data[model.subjectid]

        tot_dataframe = pandas.merge(self.demographic_data, temp_frame)
        tot_dataframe = pandas.melt(tot_dataframe, id_vars=self.demographic_data.columns.values)
        return tot_dataframe

    @staticmethod
    def read_aggregated_attributes_from_surfacefilelist(surfacefilelist, attrib_siz):
        attribute_array = np.empty((len(surfacefilelist), attrib_siz), 'float')
        for i in range(0, len(surfacefilelist)):
            if not os.path.isfile(surfacefilelist[i]):
                sys.stdout.write('Surface file: ' + surfacefilelist[i] + ' does not exist.\n')
                return []

            attributes = dfsio.readdfsattributes(surfacefilelist[i])
            if len(attributes) != attrib_siz:
                sys.stdout.write("Length of attributes in Files " + surfacefilelist[i] + " and " + surfacefilelist[0]
                                 + " do not match. Quitting.\n")
                attribute_array = []
                return attribute_array
            else:
                attribute_array[i, :] = attributes
        return attribute_array

    @staticmethod
    def read_aggregated_attributes_from_surfaces(filename):
        data_list = pandas.read_table(filename, sep='\t')
        surfacefile_list = data_list['File']
        return StatsData.read_aggregated_attributes_from_surfacefilelist(surfacefile_list)

    def read_roi_data_for_all_subjects(self, model):
        roidata = np.zeros((self.demographic_data.shape[0], len(self.roiid)))
        for idx, filename in enumerate(self.demographic_data[model.fileid].values):
            roidata[idx, :] = roi_io.read_roistats_txt(filename, self.roiid, self.roimeasure)
            if np.isnan(roidata).any():
                raise ValueError('One or more ROIs ' + ', '.join([str(i) for i in self.roiid]) + ' in ' + filename +
                                 ' may be missing or contain Nans.\n')
        return roidata

    @staticmethod
    def read_nimgdata_attributes(filename):
        data_list = pandas.read_table(filename, sep='\t')
        surfacefile_list = data_list['File']
        return NimgDataio.read_aggregated_attributes_from_filelist(surfacefile_list)

    def write_phenotype_array_to_csv(self, filename):
        self.roi_dataframe.to_csv(filename, float_format='%10.6f', index=False)
        # with open(filename, 'wb') as fid:
        #     # Make a copy of the demographic_data temporarily
        #     demographic_data_copy = self.demographic_data.copy()
        #     for idx, roi in enumerate(self.roiid):
        #         demographic_data_copy['ROI_'+str(roi)] = self.phenotype_array[:, idx]
        #
        #     demographic_data_copy.to_csv(filename, float_format='%10.6f', index=False)
