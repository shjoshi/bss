#! /usr/local/env python

"""Result formatting and saving for ROI statistical tests"""

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
__copyright__ = "Copyright 2015, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center"\
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import sys
import os
from bss.labeldesc_io import LabelDesc


class StatsRoiResult(object):

    def __init__(self, dim=0):
        self.cmd_str_list = []
        self.cmd_result_str_list = []
        self.statsout_txt = []

    def save(self, filename, statsdata, modelspec_file):
        self.save_r_cmds(filename, statsdata, modelspec_file)

    def save_r_cmds(self, filename, statsdata, modelspec_file, pandoc_dir=''):
        outdir = os.path.dirname(filename)
        sys.stdout.write('Saving commands to ' + outdir + '/r_cmds.R' + '...')
        with open(outdir + '/r_cmds.R', 'wt') as fid:
            fid.write('# ROI analysis commands\n')
            fid.write("roidataframe = read.csv('{0:s}')\n".format(outdir+'/roidata.csv'))
            for num, roi_idx in enumerate(self.cmd_str_list):
                fid.write('# ROI: ' + str(statsdata.roiid[num]) + ' - ' + LabelDesc.roilabels[statsdata.roiid[num]] + '\n')
                for jj in self.cmd_str_list[num]:
                    fid.write(jj.text + '\n')
                fid.write('\n#--------------------------------------------------------------------------------\n')
        sys.stdout.write('Done.\n')

        sys.stdout.write('Saving results to ' + filename + '...')
        with open(filename, 'wt') as fid:
            fid.write('# ROI results\n')
            for num, roi_idx in enumerate(self.cmd_result_str_list):
                fid.write('# ROI: ' + str(statsdata.roiid[num]) + ' - ' + LabelDesc.roilabels[statsdata.roiid[num]] + '\n')
                for jj in self.cmd_result_str_list[num]:
                    fid.write(jj)
                fid.write('\n##__________________________________________________________\n')
        sys.stdout.write('Done.\n')

        sys.stdout.write('Generating R markdown and saving to ' + outdir + '/r_commands.Rmd' + '...')
        with open(outdir + '/r_commands.Rmd', 'wt') as fid:
            fid.write('### BrainSuite ROI statistical analysis report\n\n')
            fid.write('##### The model is specified in {0:s}\n\n'.format(modelspec_file))
            fid.write('This report includes the complete set of commands to reproduce your analysis.\n')

            fid.write("\n```{r librar_cmds, echo=FALSE}\n")
            fid.write("library('knitr')\n")
            fid.write("library('pander')\n")
            fid.write("library('rmarkdown')\n")
            fid.write("```\n")
            fid.write('\n##### Load csv file\n')
            fid.write("```{r load_data}\n")
            fid.write("roidataframe = read.csv('{0:s}')\n".format(outdir+'/roidata.csv'))
            fid.write("```\n")
            ctr = 1
            for num, roi_idx in enumerate(self.cmd_str_list):
                fid.write('\n#### ROI: ' + str(statsdata.roiid[num]) + ' - ' + LabelDesc.roilabels[statsdata.roiid[num]] + '\n')
                for jj in self.cmd_str_list[num]:
                    if jj.display:
                        fid.write("```{r}\n")
                        fid.write('{0:s}'.format(jj.text) + '\n')
                        fid.write("```\n")
                    else:
                        fid.write("```{r results='hide'}\n")
                        fid.write('{0:s}'.format(jj.text) + '\n')
                        fid.write("```\n")
                    if jj.pander:
                        fid.write("```{r echo=FALSE}\n")
                        fid.write('pander({0:s})'.format(jj.text) + '\n')
                        fid.write("```\n")
                    fid.write("\n#### {0:s}\n".format(jj.caption))
                fid.write('\n##__________________________________________________________\n')
        sys.stdout.write('Done.\n')

