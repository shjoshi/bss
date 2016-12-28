#! /usr/local/epd/bin/python

"""
Create modelspec.ini file
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
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


import argparse
import sys, traceback
from bss.modelspec import ModelSpec
import os
import pandas
from bss.stats_data import StatsData


def main():
    parser = argparse.ArgumentParser(description='Create a modelspec.ini for BrainSuite statistical toolbox.\n')
    parser.add_argument('modelspec_file', help='<output file for model specification [ini]>')
    args = parser.parse_args()
    bss_create_modelspec(args.modelspec_file)


def bss_create_modelspec(modelspec_file):

    try:
        sys.stdout.write('This program will help you generate a modelspec.ini file\n')
        sys.stdout.write('It is recommended to have the demographics spreadsheet with the subjects and the covariates ready.\n')
        sys.stdout.write('Additionally, the spreadsheet should have a column called File that specifies the dfs files you want to analyze.\n')
        sys.stdout.write('I will ask you a series of questions to help create the modelspec.ini.\n')
        sys.stdout.write("Let's start with the subject information first....\n")
        sys.stdout.write("===================================================================\n")
        sys.stdout.write("========================Subject Information========================\n")
        sys.stdout.write("===================================================================\n")

        while True:
            atlas = raw_input('Specify the location of the BrainSuite atlas (Type in full path of the *.pial.cortex.dfs file in the atlas directory):').rstrip()
            if os.path.exists(atlas):
                break
            else:
                sys.stdout.write('Error: Atlas ' + atlas + ' does not exist. Please re-enter.\n')

        while True:
            demographics_csv = raw_input('Location of the demographics file (This will be a csv file):').rstrip()
            if os.path.exists(demographics_csv):
                break
            else:
                sys.stdout.write('Error: Demographics file ' + demographics_csv + ' does not exist. Please re-enter.\n')


        sys.stdout.write("Parsing the demographics file....")
        demographic_data = StatsData.read_demographics(demographics_csv)

        while True:
            subjid = raw_input('Specify the unique subject identifier column name in the demographics file (subject ID for e.g.):')
            if subjid in demographic_data.columns:
                break
            else:
                sys.stdout.write('The subject identifier column name does not exist in ' + demographics_csv + '. Please re-enter.\n')
        while True:
            file_id = raw_input('Specify the File identifier column name in the demographics file (column that contains file names to analyze):').rstrip()
            if file_id in demographic_data.columns:
                break
            else:
                sys.stdout.write('The File identifier column name does not exist in ' + demographics_csv + '. Please re-enter.\n')

        sys.stdout.write('Done.\n')
        sys.stdout.write("Let's specify the statistical model information....\n")
        sys.stdout.write("=================================================================\n")
        sys.stdout.write("========================Model Information========================\n")
        sys.stdout.write("=================================================================\n")

        while True:
            modeltype = raw_input('Specify the type of model or measure (lm/corr):').rstrip().lower()
            if modeltype == 'lm' or 'corr':
                break
            else:
                sys.stdout.write('Incorrect choice. Please re-enter.\n')

        if modeltype == 'lm':


            while True:
                main_effect = raw_input('Specify the variable name for the main effect you want to test:').rstrip()
                if main_effect in demographic_data.columns:
                    break
                else:
                    sys.stdout.write('The variable name for the main effect does not exist in ' + demographics_csv + '. Please re-enter.\n')

            while True:
                covariates_string = raw_input('Specify the covariates (comma separated) you want to control for:').rstrip()
                covariates_list = covariates_string.split(',')
                covariates_list = [i.rstrip().lstrip() for i in covariates_list]
                if set(covariates_list).issubset(set(demographic_data.columns)):
                    break
                else:
                 sys.stdout.write('The covariate variable name(s) does not exist in ' + demographics_csv + '. Please re-enter.\n')

            fullmodel = main_effect + ' + ' + ' + '.join(covariates_list)
            nullmodel = ' + '.join(covariates_list)
            test = 'anova'

            sys.stdout.write('Saving the modelspec file + ' + modelspec_file + '...')
            fid = open(modelspec_file, 'wt')
            fid.write('[subjectinfo]\n')
            fid.write('subjectid={0:s}\n'.format(subjid))
            fid.write('demographics={0:s}\n'.format(demographics_csv))
            fid.write('fileid={0:s}\n'.format(file_id))
            fid.write('atlas={0:s}\n'.format(atlas))

            fid.write('\n[model]\n')
            fid.write('modeltype={0:s}\n'.format(modeltype))
            fid.write('fullmodel={0:s}\n'.format(fullmodel))
            fid.write('nullmodel={0:s}\n'.format(nullmodel))
            fid.write('test={0:s}\n'.format('anova'))
            fid.close()
            sys.stdout.write('Done.\n')

        elif modeltype == 'corr':
            while True:
                variable = raw_input('Specify the variable (sex, age for e.g.) to correlate:').rstrip()
                if variable in demographic_data.columns:
                    break
                else:
                    sys.stdout.write('The variable name does not exist in ' + demographics_csv + '. Please re-enter.\n')


            sys.stdout.write('Saving the modelspec file + ' + modelspec_file + '...')
            fid = open(modelspec_file, 'wt')
            fid.write('[subjectinfo]\n')
            fid.write('subjectid={0:s}\n'.format(subjid))
            fid.write('demographics={0:s}\n'.format(demographics_csv))
            fid.write('fileid={0:s}\n'.format(file_id))
            fid.write('atlas={0:s}\n'.format(atlas))

            fid.write('\n[measure]\n')
            fid.write('coeff={0:s}\n'.format("corr"))
            fid.write('variable={0:s}\n'.format(variable))
            fid.close()
            sys.stdout.write('Done.\n')


    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except:
        print "Something went wrong. Please send this error message to the developers." \
              "\nUnexpected error:", sys.exc_info()[0]
        print traceback.print_exc(file=sys.stdout)


    sys.exit(0)


if __name__ == '__main__':
    main()
