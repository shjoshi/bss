#! /usr/local/epd/bin/python
"""
This script will prepare the data input for running ROI analysis
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
__copyright__ = "Copyright 2015, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"



import argparse
import time
from glob import glob
from argparse import RawTextHelpFormatter
from pandas import read_csv
import os
import sys
import traceback


def main():
    parser = argparse.ArgumentParser(description='This program will prepare input data --roiwise stats etc. for ROI based analysis.\n'
                                                 'It will also create a skeleton modelspec.ini file that the user can edit and customize.',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('master_subj_dir', help='top level directory containing individual svreg output subject directories')
    parser.add_argument('demographics_csv', help='A csv file containing subject ids as a column. \n'
                                                 'The column header should be subjID, and the column can exist anywhere in the csv.\n'
                                                 'The csv file can contain other demographic variables.\n'
                                                 'A new column File_roi will be added to this csv.')
    parser.add_argument('modelspec', help='<output modelspec ini file>')
    parser.add_argument('roimeasure', help='<ROI measure>', choices=['gmthickness', 'gmvolume', 'area', 'swmFA',
                                                                     'swmMD', 'swmRD', 'swmAD'])
    parser.add_argument('roiid', help='<ROI id>')
    args = parser.parse_args()
    t = time.time()

    bss_prepare_data_for_roi(args.master_subj_dir, args.demographics_csv, args.modelspec, args.roimeasure, args.roiid)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.\n")


def bss_prepare_data_for_roi(master_subj_dir, demographics_csv, modelspec, roimeasure, roiid):

    try:
        if not os.path.exists(master_subj_dir):
            raise IOError('Directory name ' + master_subj_dir + ' does not exist.')

        demographic_data = read_csv(demographics_csv, dtype={'subjID': object})
        if 'File_roi' in demographic_data:
            sys.stdout.write('The file ' + demographics_csv + ' already contains a ' + 'File_roi' + ' column.\n')
            sys.stdout.write('Please delete it to avoid confusion and rerun.\n')
            return

        try:
            roistats_filelist = [glob(master_subj_dir + '/' + subjID + '/*.roiwise.stats.txt')[0]
                                 for subjID in demographic_data['subjID'].astype('str')]
        except IndexError as err:
            sys.stdout.write('One or more subjects may be missing roiwise.stats.txt files. '
                             '\nPlease make sure that svreg was executed on all the subjects and '
                             '{subjid}.roiwise.stats.txt exist.\n')
            return

        demographic_data['File_roi'] = roistats_filelist
        demographic_data.to_csv(demographics_csv, index=False)

        # Create a skeleton modelspec file

        # Open the svreg.log file for the first subject to get the path to the atlas directory
        try:
            svreg_log_file = glob(master_subj_dir + '/' + demographic_data['subjID'].astype('str')[0] +'/*.svreg.log')[0]
        except IndexError as err:
            sys.stdout.write('The first subject is missing the svreg.log file.'
                             '\nPlease make sure that svreg was executed on all the subjects and '
                             '{subjid}.svreg.log exists.\n')
            return



        fid = open(svreg_log_file, 'rt')
        first = fid.readline()
        svreg_log_second_line = fid.readline()
        fid.close()
        atlas_dir = os.path.split(svreg_log_second_line.split(' ')[2])[0]
        atlas = atlas_dir + '/mri.bfc.nii.gz'

        sys.stdout.write('Saving the modelspec file ' + modelspec + '...')
        fid = open(modelspec, 'wt')
        fid.write('[subjectinfo]\n')
        fid.write('subjectid=subjID\n')
        fid.write('demographics={0:s}\n'.format(demographics_csv))
        fid.write('fileid=File_roi\n')
        fid.write('roimeasure={0:s}\n'.format(roimeasure))
        fid.write('roiid={0:s}\n'.format(roiid))
        fid.write('atlas={0:s}\n'.format(atlas))
        fid.write('maskfile=\n')


        fid.write('\n[analysis]\n')
        fid.write('type=croi\n')

        fid.write('\n[model]\n')
        fid.write('modeltype=glm\n')
        fid.write('fullmodel=\n')
        fid.write('nullmodel=\n')
        fid.write('test=anova\n')

        fid.write('\n[measure]\n')
        fid.write('coeff={0:s}\n'.format("corr"))
        fid.write('variable=\n')
        fid.close()
        sys.stdout.write('Done.\n')
        sys.stdout.write('You can now edit ' + modelspec + ' to specify the statistical model.\n' +
                         'The file should contain either the [model] or the [measure] section but not both.\n')
        sys.stdout.write('=================================================================================\n')
        sys.stdout.write('To run the statistical analysis, simply type \n' +
                         os.path.dirname(sys.executable) + '/bss_roi.py ' + modelspec + ' <output directory>\n'
                         )

    except IOError as e:
        sys.stdout.write('\nError: ' + e.message + '\n')
    except KeyError as e:
        sys.stdout.write('\nError: ' + e.message + ' does not exist in the csv file ' + demographics_csv + '.\n')
        sys.stdout.write('The csv file should contain a column named subjID that contains subject identifiers. '
                         '\nThe subject identifiers should be the same as subject directories.'
                         '\nThe csv file can contain other demographic variables.\n')
    except:
         print "Something went wrong. Please send this error message to the developers." \
               "\nUnexpected error:", sys.exc_info()[0]
         print traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    main()

