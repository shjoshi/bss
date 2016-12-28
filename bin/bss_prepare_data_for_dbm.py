#! /usr/local/epd/bin/python
"""
This script will create modelspec file, smooth diffusion maps and save them in the svreg subject directory
"""

"""Copyright (C) Yeun Kim
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


__author__ = "Yeun Kim"
__copyright__ = "Copyright 2016, Yeun Kim, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "ykim10@g.ucla.edu"



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
    parser = argparse.ArgumentParser(description='This program will prepare input data -- fa, md, etc. for dbm.\n'
                                                 'It will also create a skeleton modelspec.ini file that the user can edit and customize.',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('master_subj_dir', help='top level directory containing individual svreg and bdp output subject directories')
    parser.add_argument('demographics_csv', help='A csv file containing subject ids as a column. \n'
                                                 'The column header should be subjID, and the column can exist anywhere in the csv.\n'
                                                 'The csv file can contain other demographic variables.\n'
                                                 'A new column File_dbm will be added to this csv.')
    parser.add_argument('modelspec', help='output modelspec ini file')
    parser.add_argument('-sigma', dest='sigma', help='smoothing gaussian kernel sigma for the diffusion maps in mm. \n'
                                                     'If not specified, no smoothing performed', default=0, type=float)
    parser.add_argument('-measure', dest='measure', help='Type of diffusion measure (i.e. fa)', required=True, choices=['fa', 'md', 'rd'])
    # temporary until multishell bdp is released
    parser.add_argument('-bval', dest='bval', help='B-value')
    args = parser.parse_args()
    t = time.time()

    bss_prepare_data_for_dbm(args.master_subj_dir, args.demographics_csv, args.modelspec, args.sigma, args.measure, args.bval)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.\n")


def bss_prepare_data_for_dbm(master_subj_dir, demographics_csv, modelspec, sigma, measure, bval):

    try:

        if not os.path.exists(master_subj_dir):
            raise IOError('Directory name ' + master_subj_dir + ' does not exist.')

        demographic_data = read_csv(demographics_csv, dtype={'subjID': object})
        if 'File_dbm_{0:s}'.format(measure) in demographic_data:
            sys.stdout.write('The file ' + demographics_csv + ' already contains a "File_dbm_{0:s}"'.format(measure) + ' column.\n')
            sys.stdout.write('Please delete it to avoid confusion and rerun.\n')
            return

        # Check if diffusion maps exist in the subject directories...
        # Note: the maps should already be in atlas space
        # Create a list of *bval.measuret*.nii.gz files
        if sigma == 0:
            try:
                out_diffusion_filelist = [glob(master_subj_dir + '/' + subjID + '/*{0:s}.{1:s}.atlas.nii.gz'.format(bval,measure))[0] for subjID in demographic_data['subjID'].astype('str')]
            except IndexError as err:
                sys.stdout.write('One or more subjects may be missing diffusion maps.\n')
                return
        else:
            try:
                out_diffusion_filelist = [glob(master_subj_dir + '/' + subjID + '/*{0:s}.{1:s}.atlas.'.format(bval,measure) + str(sigma) + 'mm.nii.gz')[0] for subjID in demographic_data['subjID'].astype('str')]
            except IndexError as err:
                sys.stdout.write('One or more subjects may be missing diffusion maps at the smoothing level ' + str(sigma) + ' mm.'
                                 '\nWill recalculate maps for all subjects.\n')

                # smooth diffusion maps
                to_be_smoothed_filelist = [glob(master_subj_dir + '/' + subjID + '/*{0:s}.{1:s}.atlas.nii.gz'.format(bval,measure))[0] for subjID in demographic_data['subjID'].astype('str')]
                out_diffusion_filelist = [os.path.splitext(os.path.splitext(fname)[0])[0]+'.smooth' + str(sigma) + 'mm.nii.gz'
                                           for fname in to_be_smoothed_filelist]

                class opsargs:
                    filein = ''
                    fileout = ''
                    sigma = 0

                for idx, outfile in enumerate(out_diffusion_filelist):
                    opsargs.filein = to_be_smoothed_filelist[idx]
                    opsargs.fileout = outfile
                    opsargs.sigma = sigma
                    bss_ops.smooth(opsargs)
                    sys.stdout.write('Saved smoothed diffusion map in ' + outfile + '\n')


        demographic_data['File_dbm_{0:s}'.format(measure)] = out_diffusion_filelist
        demographic_data.to_csv(demographics_csv, index=False)
        sys.stdout.write("Added a column 'File_dbm_{0:s}'".format(measure) + " to " + demographics_csv + '.\n')
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
        fid.write('fileid=File_dbm_{0:s}\n'.format(measure))
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
