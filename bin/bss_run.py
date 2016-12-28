#! /usr/local/epd/bin/python
"""
Execute statistical modules in the package bss
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
import time
import logging
import warnings
warnings.filterwarnings("ignore")  # Suppress rpy2 and R warnings about data.table etc... # TODO make this specific later
import os
import sys
import subprocess
import shutil
# from bss import rimport

# rimport.check_R_path()

try:
    from bss import excepts
    from bss.modelspec import ModelSpec
    from bss.stats_data import StatsData
    from bss.stats_engine import StatsEngine
    from bss.stats_vertex_output import StatsVtxOutput
    import traceback
    from bss.stats_nimg_output import StatsNimgOutput
except Exception as e:
    sys.stdout.write('\nError: ' + e.message + '\n')
    sys.stdout.write('\nSomething happened during imports. \nPerhaps R is not installed properly or R_HOME is not set'
                     'to the correct version. \nPlease send the whole message to the developers.\n')
    exit(0)
except:
    print "\nSomething went wrong. Please send this error message to the developers." \
          "\nUnexpected error:", sys.exc_info()[0]
    print traceback.print_exc(file=sys.stdout)


def main():
    parser = argparse.ArgumentParser(description='Perform statistical analysis on Brainsuite processed data.\n')
    parser.add_argument('modelspec', help='<txt file for model specification [ini]>')
    parser.add_argument('outdir', help='<output directory>')
    # parser.add_argument('-prefix', dest='outprefix', help='<output prefix>', required=False, default='left')
    parser.add_argument('-statsengine', dest='statsengine', help='<statistical engine [R/sm]>',
                        required=False, choices=['R', 'sm', 'np'], default='np')
    args = parser.parse_args()
    t = time.time()

    bss_run(args.modelspec, args.outdir, args.statsengine)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.\n")


def bss_run(modelspec, outdir, opt_statsengine):

    try:
        outprefix = ''
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        logging.basicConfig(filename=os.path.join(outdir, 'bss.log'), level=logging.DEBUG,
                            format='%(levelname)s:%(message)s', filemode='w')
        logging.info('Reading model file ' + modelspec)
        model = ModelSpec(modelspec)
        logging.info('Done.')
        if model.read_success == False:
            # sys.stdout.write('The modelspec file is incorrectly formatted. Perhaps it is missing some sections/fields.\n')
            return
        # Dump the modelspec file in the log file to track provenance
        fid = open(modelspec, 'rt')
        modeltxt = fid.readlines()
        fid.close()
        [logging.info(model_line.rstrip('\n')) for model_line in modeltxt ]

        logging.info('Reading demographics file ' + model.demographics + ' and creating a data frame...')
        statsdata = StatsData(model.demographics, model)
        if statsdata.data_read_flag:
            logging.info('Done.')
            # Save the phenotype array to a ascii file for debugging
            statsdata.write_subject_phenotype_array(os.path.join(outdir, 'phenotype_array.mat'))
            logging.info('Computing ' + model.modeltype + ' with ' + model.stat_test + '...')
            statsengine = StatsEngine(model, statsdata, engine=opt_statsengine)
            statsresult = statsengine.run()
            if model.measure_flag:
                outprefix = model.stat_test + '_' + model.variable + '_' + os.path.splitext(os.path.split(model.atlas)[1])[0]
            elif model.model_flag:
                outprefix = model.stat_test + '_' + model.unique  + '_' + os.path.splitext(os.path.split(model.atlas)[1])[0]
            elif model.hypothesis_flag:
                if model.hypothesis_test == 'paired_ttest':
                    outprefix = model.stat_test + '_' + model.hypothesis_pair_id + '_' + os.path.splitext(os.path.split(model.atlas)[1])[0]
                elif model.hypothesis_test == 'unpaired_ttest':
                    outprefix = model.stat_test + '_' + model.hypothesis_group + '_' + os.path.splitext(os.path.split(model.atlas)[1])[0]


            statsnimgout = StatsNimgOutput(outdir, outprefix, statsresult, statsdata.mask_idx)
            statsnimgout.save(model.atlas)
            # Copy the modelspec to the output directory
            try:
                shutil.copy(os.path.abspath(modelspec), outdir)
            except shutil.Error as err:  # This error is raised if both file names are the same. Do nothing.
                pass
            logging.info('Done.')
        else:
            sys.stdout.write('Problem in reading either the model or the data.\n'
                             'Please check if the modelspec file is correctly formatted and/or if the data is processed and all files exist.\n'
                             'Please also check if the individual cortical surfaces exist, and/or are registered to the same atlas.\n')
            sys.stdout.write('Exiting the statistical analysis.\n')
    except (IOError, excepts.ModelFailureError, excepts.FileZeroElementsReadError, excepts.DemographicsDataError) as ioerr:
        sys.stdout.write('\nError: ' + ioerr.message + '\n')
    except:
        print "\nSomething went wrong. Please send this error message to the developers." \
              "\nUnexpected error:", sys.exc_info()[0]
        print traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    main()
