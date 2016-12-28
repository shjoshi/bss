#! /usr/local/epd/bin/python

"""Model specification for statistical tests"""

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

import ConfigParser
import re
import sys
from stats_data import StatsData
import numpy as np
import os.path
import traceback
from labeldesc_io import LabelDesc


class ModelSpec(object):

    # TODO: Could move this into a config file in the future
    measure_dict = {'gmthickness': 'Mean_Thickness(mm)',
                    'gmvolume': 'GM_Volume(mm^3)',
                    'area': 'Cortical_Area_pial(mm^2)',
                    'swmFA': 'swmFA',
                    'swmMD': 'swmMD',
                    'swmRD': 'swmRD',
                    'swmAD': 'swmAD',
                    }

    def __init__(self, modelfile):
        self.subjectid = ''
        self.demographics = ''
        self.fileid = ''
        self.atlas = ''
        self.maskfile = None
        self.maskroiid = None

        self.modeltype = ''
        self.fullmodel = ''
        self.nullmodel = ''
        self.stat_test = ''

        self.roimeasure = ''
        self.roiid = ''
        self.variables = ''
        self.unique = ''
        self.factors = []
        self.analysis_type = ''
        self.valid_analysis_types = ['vbm', 'tbm', 'cbm', 'dbm', 'croi', 'droi']
        self.read_success = True
        self.read_modelfile(modelfile)

        if self.read_success == False:
            return

        self.parse_model()

    def read_modelfile(self, modelfile):
        if not os.path.isfile(modelfile):
            sys.stdout.write('Modelfile: ' + modelfile + ' does not exist.\n')
            self.read_success = False
            return

        config = ConfigParser.ConfigParser()
        config.read(modelfile)

        config.options(config.sections()[0])
        try:
            self.subjectid = config.get('subjectinfo', 'subjectid')
            self.demographics = config.get('subjectinfo', 'demographics')
            self.fileid = config.get('subjectinfo', 'fileid')
            self.atlas = config.get('subjectinfo', 'atlas')
        except ConfigParser.NoSectionError:
            sys.stdout.write('Error: ' + 'Missing subjectinfo section or some fields in the modelspec file ' + modelfile + '.\n')
            self.read_success = False
            return

        try:
            self.maskfile = config.get('subjectinfo', 'maskfile')
        except ConfigParser.NoSectionError:
            self.maskfile = None

        try:
            temp_mask_roiid = config.get('subjectinfo', 'maskroiid')
            roiid = [int(i) for i in str.split(temp_mask_roiid, ',')]
            self.maskroiid = roiid

        except ConfigParser.NoOptionError:
            self.maskroiid= None

        if not os.path.isfile(self.demographics):
            sys.stdout.write('Demographics file: ' + self.demographics + ' does not exist.\n')
            self.read_success = False
            return

        try:
            # Read ahead demographics.csv and check if the fileid column points to roiwisetxt files
            demographics_data = StatsData.read_demographics(self.demographics)
            if demographics_data is None:
                self.read_success = False
                return
            if 'roiwise' in demographics_data[self.fileid][0]:
                self.roimeasure = config.get('subjectinfo', 'roimeasure')
                temp_roiid = config.get('subjectinfo', 'roiid')
                roiid = [int(i) for i in str.split(temp_roiid, ',')]

                if self.roimeasure not in self.measure_dict:
                    sys.stdout.write('Error: Valid values for roimeasure are ' + ', '.join(self.measure_dict.keys()) + '.\n')
                    self.read_success = False
                    return
                if not LabelDesc.validate_roiid(roiid):
                    sys.stdout.write('Error: Incorrect label ids ' + temp_roiid + '. Valid values are given in ' + LabelDesc.label_desc_file + '.\n')
                    self.read_success = False
                    return
                else:
                    self.roiid = roiid
        except KeyError as keyerr:
            sys.stdout.write('Error: Demographics csv does not contain the field ' + self.fileid + '. \n')
            self.read_success = False
            return
        except ConfigParser.NoOptionError as noopterror:
            sys.stdout.write('Error: ' + noopterror.message + ' in ' + self.demographics + '.\n')
            sys.stdout.write('Required for ROI statistical analysis. \n')
            # print traceback.format_exception_only(type(noopterror), noopterror)
            self.read_success = False
            return

        if not os.path.isfile(self.atlas):
            sys.stdout.write('Atlas surface file: ' + self.atlas + ' does not exist.\n')
            self.read_success = False
            return

        try:
            self.analysis_type = config.get('analysis', 'type')
            if self.analysis_type not in self.valid_analysis_types:
                sys.stdout.write('Error: ' + ' Valid analysis types are vbm, tbm, cbm, dbm, croi, droi.\n')
                sys.stdout.write('Please check and correct the type= value in the [analysis] section in your ' + modelfile + '.\n')
                self.read_success = False
                return
        except ConfigParser.NoOptionError as noopterror:
            sys.stdout.write('Error: ' + 'Missing section [analysis] ' + ' in ' + modelfile + '.\n')
            sys.stdout.write('Error: ' + noopterror.message + ' in ' + self.demographics + '.\n')
            sys.stdout.write('Error: ' + ' Please specify the type of analysis using the type= option. Valid types'
                                         'are vbm, tbm, cbm, dbm, croi, droi.\n')
            self.read_success = False
        except ConfigParser.NoSectionError as nosecerror:
            sys.stdout.write('Error: ' + 'Missing section [analysis] ' + ' in ' + modelfile + '.\n')
            sys.stdout.write('To rectify this error, ' + 'please include [analysis] ' + ' in ' + modelfile + '.\n')
            sys.stdout.write('Then please specify the type of analysis using the type= option. Valid types '
                                         'are vbm, tbm, cbm, dbm, croi, droi.\n')
            self.read_success = False
            return

        self.read_success = False
        self.model_flag = False
        self.measure_flag = False
        self.hypothesis_flag = False
        # Check if all the sections [model], [measure], and [hypothesis] are present
        self.model_flag = 'model' in config.sections()
        self.measure_flag = 'measure' in config.sections()
        self.hypothesis_flag = 'hypothesis' in config.sections()
        if self.model_flag and self.measure_flag and self.hypothesis_flag:
            sys.stdout.write('The modelspec.ini can only contain one statistical design ([model] or [measure] or [hypothesis]).\n'
                             'Multiple designs are not currently supported, but this may change in the future.\n')
            self.read_success = False
            return

        try:
            self.modeltype = config.get('model', 'modeltype')
            self.fullmodel = config.get('model', 'fullmodel')
            self.nullmodel = config.get('model', 'nullmodel')
            self.stat_test = config.get('model', 'test')
            self.model_flag = True
            self.read_success = True
        except ConfigParser.NoSectionError:
            self.read_success = False

        try:
            self.coeff = config.get('measure', 'coeff')
            self.variable = config.get('measure', 'variable')
            self.stat_test = self.coeff
            self.measure_flag = True
            # Check if self.variable exists in the demographics file
            if self.variable not in demographics_data.columns:
                sys.stdout.write('The covariate named ' + self.variable + ' specified in the variable= section does '
                                                                          'not exist in the demographics file ' +
                                 self.demographics + '. Please check for typos/spelling etc...\n')
                self.read_success = False
                return
            self.read_success = True
        except ConfigParser.NoSectionError:
            self.read_success = False

        try:
            self.hypothesis_group = config.get('hypothesis', 'group')
            self.hypothesis_test = config.get('hypothesis', 'test')
            if self.hypothesis_test != "paired_ttest" and self.hypothesis_test != "unpaired_ttest":
                sys.stdout.write('Error: Incorrect value for test in {0:s}. '
                                 '\nValid options for a hypothesis test are paired_ttest or unpaired_ttest.\n'.format(modelfile))
                return
            self.hypothesis_pair_id = None
            if self.hypothesis_test == 'unpaired_ttest':
                # if test is unpaired and the option "pair=" is specified, then give a warning
                if config.has_option('hypothesis', 'pair'):
                    sys.stdout.write('Warning: An unpaired t-test is specified, however the option for pair= is also specified. '
                                     '\nWill ignore the paired column and run the independent samples t-test.\n')

            if self.hypothesis_test == 'paired_ttest':
                # if test is paired, the option "pair=" must be specified
                if config.has_option('hypothesis', 'pair'):
                    self.hypothesis_pair_id = config.get('hypothesis', 'pair')
                    if self.hypothesis_pair_id not in demographics_data.keys():
                        sys.stdout.write('The column for the pair field is missing from {0:s}\n'.format(self.demographics))
                        return
                else:
                    sys.stdout.write('For a paired t-test, please specify the paired column variable. '
                                     'It should exist in your demographics csv file.\n')
                    return

            if self.hypothesis_group not in demographics_data.keys():
                sys.stdout.write('The column for the group field is missing from {0:s}\n'.format(self.demographics))

            self.stat_test = self.hypothesis_test
            self.hypothesis_flag = True
            self.read_success = True
        except ConfigParser.NoSectionError:
            self.read_success = False

        if self.model_flag:
            self.read_success = True
            return

        if self.measure_flag:
            self.read_success = True
            return


        # factorstring = config.get('model', 'factors')
        # for i in re.split(' ', factorstring):
        #     self.factors.append(i.rstrip().lstrip())

    def parse_model(self):
        if self.model_flag:
            # Parse fullmodel and nullmodel
            set_full = set()
            set_null = set()
            for i in re.split('\+|', self.fullmodel):
                set_full.add(i.rstrip().lstrip())
            for i in re.split('\+', self.nullmodel):
                set_null.add(i.rstrip().lstrip())
            self.unique = list(set_full - set_null)[0]  # TODO check: only one element should be present
            demographic_data_temp = StatsData.read_demographics(self.demographics)
            if demographic_data_temp is None:
                self.read_success = False
                return

            # Check if the covariates specified in the full and null models exist in the demographics file
            for var in set_full:
                if var not in demographic_data_temp.columns:
                    sys.stdout.write('The covariate named ' + var + ' specified in the fullmodel= section does '
                                                                              'not exist in the demographics file ' +
                                     self.demographics + '. Please check for typos/spelling etc...\n')
                    self.read_success = False
                    return
            for var in set_null:
                if var not in demographic_data_temp.columns:
                    sys.stdout.write('The covariate named ' + var + ' specified in the nullmodel= section does '
                                                                              'not exist in the demographics file ' +
                                     self.demographics + '. Please check for typos/spelling etc...\n')
                    self.read_success = False
                    return

            # If the unique variable (the main effect in regression) is not numeric show an error and return
            if not np.isreal(demographic_data_temp[self.unique]).any():
                sys.stdout.write('The variable for main effect "' + self.unique + '" is not numeric. Please recode as numeric and rerun.\n\n\n')
                self.read_success = False
                return
        elif self.measure_flag:
            # self.variables = set_full | set_null
            return

    def nump_full_model(self):  # Number of parameters of full model
        return len(self.fullmodel.split('+'))

    def nump_null_model(self):  # Number of parameters of null model
        return len(self.nullmodel.split('+'))

    def validate_model(self):
        #TODO validate model
        pass


