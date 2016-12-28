#! /usr/local/epd/bin/python

"""ROI Statistical analysis"""

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
__copyright__ = "Copyright 2016, Shantanu H. Joshi, David Shattuck, Ahmanson Lovelace Brain Mapping Center" \
                "University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"


from statsmodels.formula.api import ols
import statsmodels.api as sm
from stats_roi_result import StatsRoiResult
from collections import namedtuple
from bss.labeldesc_io import LabelDesc
from sys import stdout


def anova_roi_sm(model, sdata):
    siz = sdata.phenotype_array.shape[1]
    statsresult = StatsRoiResult()

    stdout.write('Computing regressions for ROIs...')
    stdout.flush()

    roi_r_cmd_list = []
    roi_cmd_result_list = []

    for roi_num, roi_idx in enumerate(sdata.roiid):
        stdout.write(str(roi_idx) + ', ')
        stdout.flush()
        fit_full = ols('ROI_' + str(roi_idx) + ' ~ ' + model.fullmodel, data=sdata.demographic_data).fit()
        fit_null = ols('ROI_' + str(roi_idx) + ' ~ ' + model.nullmodel, data=sdata.demographic_data).fit()
        model_diff = sm.stats.anova_lm(fit_null, fit_full)
        # fit_full.tvalues[2]/abs(fit_full.tvalues[2])*model_diff.values[1, 5]

        roi_r_cmd_list.append(generate_r_commands(roi_idx, model))
        roi_cmd_result_list.append(generate_sm_result(fit_full, fit_null, model_diff))

    statsresult.pvalues = 0
    statsresult.cmd_str_list = roi_r_cmd_list
    statsresult.cmd_result_str_list = roi_cmd_result_list
    return statsresult


def generate_r_commands(roi_idx, model):

    cmd_list = []
    rCmd = namedtuple('Cmd', ['text', 'display', 'pander', 'caption'])
    cmd_list.append(rCmd("lm_full <- lm (\'ROI_{0:s} ~ {1:s}\', data=roidataframe)".format(str(roi_idx), model.fullmodel), False, False, ''))
    cmd_list.append(rCmd("summary(lm_full)", False, True, caption=''))
    cmd_list.append(rCmd("lm_null <- lm (\'ROI_{0:s} ~ {1:s}\', data=roidataframe)".format(str(roi_idx), model.nullmodel), False, False, ''))
    cmd_list.append(rCmd("summary(lm_null)", False, False, ''))
    cmd_list.append(rCmd('lm_compare <- anova(lm_full, lm_null)', False, False, ''))
    cmd_list.append(rCmd('lm_compare', False, True, 'Main effect of {0:s} {1:s} on {2:s} controlling for {3:s}'.format(LabelDesc.roilabels[roi_idx], model.roimeasure, model.unique, model.nullmodel)))

    return cmd_list


def generate_sm_result(fit_full, fit_null, model_diff):

    cmd_result = []
    cmd_result.append(fit_full.summary().as_text())
    cmd_result.append('\n')
    cmd_result.append(fit_null.summary().as_text())
    cmd_result.append('\n')
    cmd_result.append(str(model_diff))
    return cmd_result
