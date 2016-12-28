#! /usr/local/epd/bin/python

"""Class that encapsulates the underlying statistical engine that will execute statistical tests"""

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
__copyright__ = "Copyright 2013, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center"\
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import sys
import cbm_stats
import tbm_stats
import roi_stats


class StatsEngine(object):

    def __init__(self, model, stats_data, engine='sm', roi=False):
        self.engine = engine
        self.model = model
        self.stats_data = stats_data
        self.commands_statmodels = None
        self.commands_r = None
        self.commands = {}
        self.roicommands = {}
        self.define_stats_commands()
        self.define_roi_stats_commands()
        self.roi = roi

    def define_stats_commands(self):
        if self.engine == 'np':
            self.commands = {'cbm_corr': cbm_stats.corr_fast,
                             'cbm_anova': cbm_stats.anova_np,
                             'cbm_unpaired_ttest': cbm_stats.unpaired_ttest,
                             'cbm_paired_ttest': cbm_stats.paired_ttest,
                             'tbm_unpaired_ttest': tbm_stats.unpaired_ttest,
                             'tbm_paired_ttest': tbm_stats.paired_ttest,
                             'tbm_corr': tbm_stats.corr_fast,
                             'tbm_anova': tbm_stats.anova_np,
                             }

    def define_roi_stats_commands(self):
        if self.engine == 'sm':
            self.roicommands = {'anova': roi_stats.anova_roi_sm,
                                }

    def run(self):
        sys.stdout.write('Running the statistical model. This may take a while...')
        if not self.roi:
            statsresult = self.commands[self.model.analysis_type + '_' + self.model.stat_test](self.model, self.stats_data)
            statsresult.adjust_for_multi_comparisons()
        else:
            statsresult = self.roicommands[self.model.stat_test](self.model, self.stats_data)
        sys.stdout.write('Done.\n')

        return statsresult
