#! /usr/local/epd/bin/python
"""
Configure bss. Specify Atlas directory, BrainSuite installation directory
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
__copyright__ = "Copyright 2014, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "sjoshi@bmap.ucla.edu"


import argparse
import os
import sys
import traceback
import glob


def main():
    parser = argparse.ArgumentParser(description='Configure bss. Prompts for the BrainSuite installation directory, '
                                                 'and the atlas directory.\n')
    args = parser.parse_args()
    bss_config(args)


def bss_config(args):

    config_file = os.path.join(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), os.pardir), 'bss_config.ini')

    if os.path.exists(config_file):
        sys.stdout.write('A previous bss_config.ini exists at ' + config_file + '\n')
        sys.stdout.write('Quitting now.\n')
        return

    try:
        sys.stdout.write('This program will create a bss_config.ini in your bss installation directory.\n')
        sys.stdout.write('The configuration file will be stored as ' + config_file + '.\n')

        while True:
            atlasdir = raw_input('Specify the location of the BrainSuite atlas directory: ').rstrip()
            if os.path.exists(atlasdir):
                # Check if it's a valid atlas directory
                valid_files = glob.glob(os.path.join(atlasdir, 'mri.*.cortex.dfs'))
                if any("mri.left.mid" in s for s in valid_files) & \
                        any("mri.right.mid" in s for s in valid_files) & \
                        any("mri.left.pial" in s for s in valid_files) & \
                        any("mri.right.pial" in s for s in valid_files) & \
                        any("mri.left.inner" in s for s in valid_files) & \
                        any("mri.right.inner" in s for s in valid_files):
                    break
                else:
                    sys.stdout.write('Error: Atlas directory' +
                                     atlasdir + ' may be missing a few files. '
                                                'Please rectify and re-enter (Press Ctrl-C to exit).\n')
            else:
                sys.stdout.write('Error: Atlas ' +
                                 atlasdir + ' does not exist. Please re-enter (Press Ctrl-C to exit).\n')

        while True:
            brainsuite_dir = raw_input('Specify the location of the BrainSuite installation directory: ').rstrip()
            if os.path.exists(brainsuite_dir):
                break
            else:
                sys.stdout.write('Error: BrainSuite installation directory does not exist.'
                                 + 'Please rectify and re-enter (Press Ctrl-C to exit).\n')

        sys.stdout.write('Saving the configuration file at ' + config_file)
        fid = open(config_file, 'wt')

        fid.write('[bss]\n')
        fid.write('brainsuite_dir={0:s}\n'.format(brainsuite_dir))
        fid.write('atlas_dir={0:s}\n'.format(atlasdir))
        fid.close()
        sys.stdout.write('Done.\n')

    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except:
        print "Something went wrong. Please send this error message to the developers." \
              "\nUnexpected error:", sys.exc_info()[0]
        print traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
    main()
