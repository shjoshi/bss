#! /usr/local/epd/bin/python
"""
Execute statistical modules for ROI analysis in the package bss
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
__copyright__ = "Copyright 2015, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


import argparse
import time
import logging
import warnings
warnings.filterwarnings("ignore")  # Suppress rpy2 and R warnings about data.table etc... # TODO make this specific later
import sys
from shutil import copy, Error
import traceback
import pandas

try:
    from bss.modelspec import ModelSpec
    from bss.stats_data import StatsData
    from bss.stats_engine import StatsEngine
except Exception as e:
    sys.stdout.write('\nError: ' + e.message + '\n')
    sys.stdout.write('\nSomething happened during imports. \nPerhaps R is not installed properly or R_HOME is not set'
                     'to the correct version. \nPlease send the whole message to the developers.\n')
    exit(0)
except:
    print "\nSomething went wrong. Please send this error message to the developers." \
          "\nUnexpected error:", sys.exc_info()[0]
    print traceback.print_exc(file=sys.stdout)

from bss.stats_roi_result import StatsRoiResult
import os

import traceback


def main():
    parser = argparse.ArgumentParser(description='Perform statistical analysis on ROIs from Brainsuite processed data.\n')
    parser.add_argument('modelspec', help='<txt file for model specification [ini]>')
    parser.add_argument('outdir', help='<output directory>')
    args = parser.parse_args()
    args.statsengine = 'sm'
    t = time.time()

    bss_roi(args.modelspec, args.outdir, args.statsengine)
    elapsed = time.time() - t
    os.sys.stdout.write("Elapsed time " + str(elapsed) + " sec.")


def bss_roi(modelspec, outdir, opt_statsengine):

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
            sys.stdout.write('The modelspec file is incorrectly formatted. Perhaps it is missing some sections/fields.\n')
            return

        logging.info('Reading demographics file ' + model.demographics + ' and creating a data frame...')
        statsdata = StatsData(model.demographics, model, roi=True)
        if statsdata.data_read_flag:
            logging.info('Done.')
            # Save the roidata array to a mat file for debugging/external use
            statsdata.write_phenotype_array_to_csv(os.path.join(outdir, 'roidata.csv'))
            # Reload the roidata.csv file
            statsdata.demographic_data = pandas.read_csv(os.path.join(outdir, 'roidata.csv'), dtype={'subjID': object})
            logging.info('Computing ' + model.modeltype + ' with ' + model.stat_test + '...')
            statsengine = StatsEngine(model, statsdata, engine=opt_statsengine, roi=True)
            statsroiresult = statsengine.run()
            statsroiresult.save(outdir + '/results.txt', statsdata, modelspec)
            # Copy the modelspec to the output directory
            try:
                copy(os.path.abspath(modelspec), outdir)
            except Error as err:  # This error is raised if both file names are the same. Do nothing.
                pass
            logging.info('Done.')
    except ValueError as valerr:
        sys.stdout.write('Error: ' + valerr.message + '\n')
    except IOError as ioerr:
        sys.stdout.write('Error: ' + ioerr.message + '\n')

    except Exception as e:
        print "Something went wrong. Please send this error message to the developers." \
              "\nUnexpected error:", sys.exc_info()[0]
        print traceback.format_exception_only(type(e), e)
        print traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    main()
