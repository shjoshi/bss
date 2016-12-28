#! /usr/local/epd/bin/python
"""
This script will append SWM FA, MD, RD, and AD measures to subject wise roi stat txt file
This assumes that the SWM (Superficial White Matter) features (see O. Philips et al.) to be computed and
residing in the individual subject directories
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
__copyright__ = "Copyright 2016, Shantanu H. Joshi Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

import argparse
import time
from glob import glob
from argparse import RawTextHelpFormatter
from pandas import read_csv, read_table, DataFrame
import os
import sys
import traceback
from bss.dfsio import readdfs, readdfsattributes
from bss import roi_io
import numpy as np
from bss import excepts


# TODO: Could move this into a config file in the future
swm_measure_dict = {'swmFA': '*FA.dfs',
                    'swmMD': '*MD.dfs',
                    'swmRD': '*radial.dfs',
                    'swmAD': '*axial.dfs',
                    }


def main():
    parser = argparse.ArgumentParser(description='This script will append SWM FA, MD, RD, and AD measures to subject wise roi stat txt file. '
                                                 'This assumes that the SWM (Superficial White Matter) features (see O. Philips et al.) to be computed and '
                                                 'residing in the individual subject directories', formatter_class=RawTextHelpFormatter)
    parser.add_argument('master_subj_dir', help='top level directory containing individual svreg output subject directories')
    parser.add_argument('demographics_csv', help='A csv file containing subject ids as a column. \n'
                                                 'The column header should be subjID, and the column can exist anywhere in the csv.\n'
                                                 'The csv file can contain other demographic variables.\n')
    args = parser.parse_args()
    t = time.time()

    bss_append_swm_to_roistat(args.master_subj_dir, args.demographics_csv)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.\n")


def bss_append_swm_to_roistat(master_subj_dir, demographics_csv):
    # TODO: The code for checking roiwisestats.txt could be a part of a bigger class that checks for valid inputs
    try:
        if not os.path.exists(master_subj_dir):
            raise IOError('Directory name ' + master_subj_dir + ' does not exist.')

        demographic_data = read_csv(demographics_csv, dtype={'subjID': object})

        try:
            roistats_filelist = [glob(master_subj_dir + '/' + subjID + '/*.roiwise.stats.txt')[0]
                                 for subjID in demographic_data['subjID'].astype('str')]
        except IndexError as err:
            sys.stdout.write('Subject {0:s} may be missing roiwise.stats.txt files. '
                             '\nPlease make sure that svreg was executed on all the subjects and '
                             '{0:s}*.roiwise.stats.txt exist.\n'.format(subjID))
            return
    except IOError as e:
        sys.stdout.write('\nError: ' + e.message + '\n')
    except KeyError as e:
        sys.stdout.write('\nError: ' + e.message + ' does not exist in the csv file ' + demographics_csv + '.\n')
        sys.stdout.write('The csv file should contain a column named subjID that contains subject identifiers. '
                         '\nThe subject identifiers should be the same as subject directories.'
                         '\nThe csv file can contain other demographic variables.\n')
    try:

        # TODO: The name swm_roi_ids.txt is hardcoded. Could be loaded from a conf file in future
        dirname = os.path.dirname(sys.modules['bss'].__file__)
        temp_roi_ids = read_csv(os.path.join(dirname, 'conf/swm_colin_roi_id.csv'))
        swm_roi_ids = temp_roi_ids['left'].tolist() + temp_roi_ids['right'].tolist()

        # For each subject in the master_subj_dir, calculate mean ROI for all swm measures in swm_measure_dict
        for subjID in demographic_data['subjID']:
            sys.stdout.write('Processing Subject {0:s}...'.format(subjID))
            # Read atlas for left hemisphere
            s1_atlas_left = readdfs(os.path.join(master_subj_dir, subjID, '{0:s}_atlas.left.mid.cortex.svreg.dfs'.format(subjID)))
            s1_atlas_right = readdfs(os.path.join(master_subj_dir, subjID, '{0:s}_atlas.right.mid.cortex.svreg.dfs'.format(subjID)))
            # Read roiwise.stats.txt file
            roiwise_stats_filename = os.path.join(master_subj_dir, subjID, '{0:s}.roiwise.stats.txt'.format(subjID))
            roiwise_stats_df = read_table(roiwise_stats_filename, index_col='ROI_ID')
            # If roiwise_stats_df contains FA, MD, RD, AD columns, skip the subject
            if bool(set(swm_measure_dict.keys()) & set(roiwise_stats_df.columns)):
                sys.stdout.write('SWM measures already exist. Will delete and recreate...')
                # Delete the columns from dataframe
                for measure in swm_measure_dict.keys():
                    if measure in roiwise_stats_df.columns:
                        roiwise_stats_df = roiwise_stats_df.drop(measure, axis=1)

            s1_left_right_atlas_labels_combined = np.concatenate((s1_atlas_left.labels, s1_atlas_right.labels))
            temp = DataFrame(data=np.zeros((len(roiwise_stats_df), 4)), index=roiwise_stats_df.index.values, columns=swm_measure_dict.keys())
            for measure in swm_measure_dict.keys():
                sys.stdout.write(measure + '...')
                swm_measure_files = glob(master_subj_dir + '/' + subjID + '/{0}'.format(swm_measure_dict[measure]))
                # There should be only two swm_measure files, one for left, the other for right
                # If more than 2 files exist print an error:
                if len(swm_measure_files) > 2:
                    raise excepts.ExtraFilesError('SWM measure {0:s} has {1:d} files. Please delete extra files.\n'.format(measure, len(swm_measure_files)))

                s1_measure_attributes = np.concatenate((readdfsattributes(swm_measure_files[0]), readdfsattributes(swm_measure_files[1])))

                roi_mean = []
                for roi_label in swm_roi_ids:
                    idx = np.where(s1_left_right_atlas_labels_combined == int(roi_label))
                    if idx[0].any():
                        temp.ix[int(roi_label), measure] = np.mean(s1_measure_attributes[idx[0]])  # TODO Print error message if the number of labels, vertices don't reconcile

            roiwise_stats_df = roiwise_stats_df.join(temp)
            roiwise_stats_df.to_csv(roiwise_stats_filename, sep='\t')
            sys.stdout.write('Writing to {0:s}'.format(roiwise_stats_filename))
            sys.stdout.write('. Done.\n')
    except (IOError, excepts.ExtraFilesError, excepts.ModelFailureError, excepts.FileZeroElementsReadError, excepts.DemographicsDataError) as err:
        sys.stdout.write('\nError: ' + err.message + '\n')
    except excepts.ExtraFilesError as err:
        print err.message
    except:
         print "Something went wrong. Please send this error message to the developers." \
               "\nUnexpected error:", sys.exc_info()[0]
         print traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    main()