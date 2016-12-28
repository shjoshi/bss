#! /usr/local/epd/bin/python

"""Perform a two-sample paired t-test between shapes"""

__author__ = "Shantanu H. Joshi"
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import sys
import numpy as np
import argparse
import time
from bss.stats_data import StatsData
from scipy.stats import ttest_rel


def main():
    parser = argparse.ArgumentParser(description='This program performs a paired t-test between shapes.\n '
                                                 'The number of subjects should be same, and the number of shape '
                                                 'vertices for each subject should be same.')
    parser.add_argument('-sample1', dest='sample1', help='<txt file for sample 1>', required=True)
    parser.add_argument('-sample2', dest='sample2', help='<txt file for sample 1>', required=True)
    parser.add_argument('-output_shape', dest='output_shape', help='<output file for shape>', required=True)
    parser.add_argument('-output_log', dest='output_log', help='<log file>', required=False)

    args = parser.parse_args()
    t = time.time()
    # do stuff
    paired_t_test(args.sample1, args.sample2, args.output_shape, args.output_log)
    elapsed = time.time() - t
    print elapsed


def paired_t_test(sample1, sample2, output_shape, output_log):

    s1, s1_average, attrib1_array = StatsData.read_aggregated_attributes_from_surfaces(sample1)
    s2, s2_average, attrib2_array = StatsData.read_aggregated_attributes_from_surfaces(sample2)

    if attrib1_array == [] or attrib1_array == []:
        sys.exit('Error in Reading one or more files...Now Exiting.\n')

    # If files are successfully read, then proceed with the t-test
    tstat_array, pvalue_array = ttest_rel(attrib1_array, attrib2_array)
    pvalue_array_with_sign = np.sign(tstat_array)*pvalue_array

    # StatsData.write_pvalues_to_surface(pvalue_array_with_sign, s1_average, output_shape)
    sys.stdout.write('Done.\n')
    return

if __name__ == '__main__':
    main()
