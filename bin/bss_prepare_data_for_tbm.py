#! /usr/local/epd/bin/python
"""
This script will create the jacobians, smooth them and save them in the svreg subject directory
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
from argparse import RawTextHelpFormatter
import time
from glob import glob
import bss_ops
from pandas import read_csv, DataFrame, merge, concat
import os
import sys
import traceback


def main():
    parser = argparse.ArgumentParser(description='This program will prepare input data -- jacobians, determinants etc. for tbm.\n'
                                                 'It will also create a skeleton modelspec.ini file that the user can edit and customize.',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('master_subj_dir', help='top level directory containing individual svreg output subject directories')
    parser.add_argument('demographics_csv', help='A csv file containing subject ids as a column. \n'
                                                 'The column header should be subjID, and the column can exist anywhere in the csv.\n'
                                                 'The csv file can contain other demographic variables.\n'
                                                 'A new column File_tbm will be added to this csv.')
    parser.add_argument('modelspec', help='output modelspec ini file')
    parser.add_argument('-sigma', dest='sigma', help='smoothing gaussian kernel sigma for the jacobian determinants in mm. \n'
                                                     'If not specified, no smoothing performed', default=0, type=float)
    args = parser.parse_args()
    t = time.time()

    bss_prepare_data_for_tbm(args.master_subj_dir, args.demographics_csv, args.modelspec, args.sigma)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.\n")


def bss_prepare_data_for_tbm(master_subj_dir, demographics_csv, modelspec, sigma):

    try:

        if not os.path.exists(master_subj_dir):
            raise IOError('Directory name ' + master_subj_dir + ' does not exist.')

        demographic_data = read_csv(demographics_csv, dtype={'subjID': object})
        if 'File_tbm' in demographic_data:
            sys.stdout.write('The file ' + demographics_csv + ' already contains a "File_tbm" column.\n')
            sys.stdout.write('Please delete it to avoid confusion and rerun.\n')
            return

        # Check if jacobian determinants exist in the subject directories...
        # Note: if jacobian determinants exist, they will always be in the atlas space.
        # Create a list of *.jacdet*.nii.gz files
        calc_jaobian = False
        if sigma == 0:
            try:
                out_inv_Jacdet_filelist = [glob(master_subj_dir + '/' + subjID + '/*.jacdet.nii.gz')[0] for subjID in demographic_data['subjID'].astype('str')]
            except IndexError as err:
                sys.stdout.write('One or more subjects may be missing jacobian determinants. \nWill recalculate jacobian determinants for all subjects.\n')
                calc_jaobian = True
        else:
            try:
                out_inv_Jacdet_filelist = [glob(master_subj_dir + '/' + subjID + '/*.jacdet.smooth' + str(sigma) + 'mm.nii.gz')[0] for subjID in demographic_data['subjID'].astype('str')]
            except IndexError as err:
                sys.stdout.write('One or more subjects may be missing jacobian determinants at the smoothing level ' + str(sigma) + ' mm.'
                                 '\nWill recalculate jacobian determinants for all subjects.\n')
                calc_jaobian = True

        if calc_jaobian:

            # Create a list of *.svreg.inv.map.nii.gz files
            try:
                inv_map_filelist = [glob(master_subj_dir + '/' + subjID + '/*.svreg.inv.map.nii.gz')[0] for subjID in demographic_data['subjID'].astype('str')]
            except IndexError as err:
                sys.stdout.write('One or more subjects may be missing *.svreg.inv.map.nii.gz files. These are required for computing the jacobians.\n'
                                 'Please ensure that svreg was executed on the subjects and *.svreg.inv.map.nii.gz exists in each subject directory.\n')
                return


            # Calculate Jacobians and smooth them
            out_inv_Jacdet_filelist = [os.path.splitext(os.path.splitext(fname)[0])[0]+'.jacdet.smooth' + str(sigma) + 'mm.nii.gz'
                                       for fname in inv_map_filelist]

            class opsargs:
                filein = ''
                fileout = ''
                sigma = 0

            for idx, outfile in enumerate(out_inv_Jacdet_filelist):
                opsargs.filein = inv_map_filelist[idx]
                opsargs.fileout = outfile
                opsargs.sigma = sigma
                bss_ops.jacdet(opsargs)
                sys.stdout.write('Saved smoothed Jacobian determinant in ' + outfile + '\n')

        demographic_data['File_tbm'] = out_inv_Jacdet_filelist
        demographic_data.to_csv(demographics_csv, index=False)
        sys.stdout.write("Added a column 'File_tbm' to " + demographics_csv + '.\n')
        # Create a skeleton modelspec file

        # Open the svreg.log file for the first subject to get the path to the atlas directory

        svreg_log_file = glob(master_subj_dir + '/' + demographic_data['subjID'].astype('str')[0] +'/*.svreg.log')[0]
        fid = open(svreg_log_file, 'rt')
        first = fid.readline()
        svreg_log_second_line = fid.readline()
        fid.close()
        atlas_dir = os.path.split(svreg_log_second_line.split(' ')[2])[0]
        atlas = atlas_dir + '/mri.bfc.nii.gz'
        maskfile = atlas_dir + '/mri.cerebrum.mask.nii.gz'

        sys.stdout.write('Saving the modelspec file ' + modelspec + '...')
        fid = open(modelspec, 'wt')
        fid.write('[subjectinfo]\n')
        fid.write('subjectid=subjID\n')
        fid.write('demographics={0:s}\n'.format(demographics_csv))
        fid.write('fileid=File_tbm\n')
        fid.write('atlas={0:s}\n'.format(atlas))
        fid.write('maskfile={0:s}\n'.format(maskfile))


        fid.write('\n[analysis]\n')
        fid.write('type=tbm\n')

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
                         os.path.dirname(sys.executable) + '/bss_run.py ' + modelspec + ' <output directory>\n'
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
