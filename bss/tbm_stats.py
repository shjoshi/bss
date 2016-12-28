#! /usr/local/epd/bin/python

"""Statistical analysis for tensor based morphometry (TBM)"""

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

from sys import stdout
import numpy as np
from stats_result import StatsResult
from sys import float_info
import scipy
from patsy import dmatrix
import excepts
from scipy.stats import ttest_ind, ttest_rel


def corr_r_func():

    corr_r_funct_str = {'corr_r_func': '''<- function(x, y, methodstr)
                {
                    return(cor.test(x, y, method=methodstr))
                }
                '''}
    return corr_r_funct_str

def corr_fast(model, sdata):
    def fastColumnWiseCorrcoef(O, P): #P = age_mtx = 1 x n, O = subjects_vertices_mtx = n x m
        n = P.size
        DO = O - (np.einsum('ij->j',O) / np.double(n))
        P -= (np.einsum('i->',P) / np.double(n))
        tmp = np.einsum('ij,ij->j',DO,DO)
        tmp *= np.einsum('i,i->',P,P)
        return np.dot(P, DO) / np.sqrt(tmp)
    def slowColumnWiseCorrcoef(O, P): #P = age_mtx = 1 x n, O = subjects_vertices_mtx = n x m
        n = P.size
        DO = O - (np.sum(O, 0) / np.double(n))
        DP = P - (np.sum(P) / np.double(n))
        DO = DO + float_info.epsilon
        DP = DP + float_info.epsilon
        return np.dot(DP, DO) / np.sqrt(np.sum(DO ** 2, 0) * np.sum(DP ** 2))

    size = sdata.phenotype_array.shape[1]
    statsresult = StatsResult(dim=size)
    O = sdata.phenotype_array + float_info.epsilon
    P = np.array(sdata.demographic_data[model.variable]) + float_info.epsilon
    corr_coeff = slowColumnWiseCorrcoef(O, P)

    num_subjects = sdata.phenotype_array.shape[0]

    tvalue = corr_coeff*np.sqrt((num_subjects-2)/(1-corr_coeff**2))
    statsresult.pvalues = 1-scipy.stats.t.cdf(abs(tvalue), num_subjects-2)
    statsresult.corrvalues = corr_coeff
    statsresult.pvalues = np.sign(corr_coeff)*statsresult.pvalues
    statsresult.pvalues[np.isnan(corr_coeff)] = 1  # Set the p-values with the nan correlations to 1

    statsresult.file_name_string = '_corr_with_' + model.variable

    return statsresult


def anova_np(model, sdata):  # Anova using numpy/scipy
    N = sdata.phenotype_array.shape[0]  # Number of observations
    statsresult = StatsResult(dim=sdata.phenotype_array.shape[1])

    try:

        # Create a design matrix
        X_design_full = dmatrix(model.fullmodel, data=sdata.demographic_data)  # Design matrix for full model
        Xtemp = np.dot(np.linalg.inv(np.dot(X_design_full.T, X_design_full)), X_design_full.T)  # Pre Hat matrix
        beta_full = np.dot(Xtemp, sdata.phenotype_array)  # beta coefficients
        y_full = np.dot(X_design_full, beta_full)  # Predicted response
        RSS_full = np.sum((sdata.phenotype_array - y_full)**2, axis=0)

        X_design_null = dmatrix(model.nullmodel, data=sdata.demographic_data)  # Design matrix for null model
        Xtemp = np.dot(np.linalg.inv(np.dot(X_design_null.T, X_design_null)), X_design_null.T)  # Pre Hat matrix
        beta_null = np.dot(Xtemp, sdata.phenotype_array)  # beta coefficients
        y_null = np.dot(X_design_null, beta_null)  # Predicted response
        RSS_null = np.sum((sdata.phenotype_array - y_null)**2, axis=0)

        np_full = model.nump_full_model()
        np_null = model.nump_null_model()

        Fstat = (RSS_null - RSS_full)/(RSS_full + +np.finfo(float).eps) * (N-np_full-1)/(np_full-np_null)  # F statistic
        model_unique_idx = X_design_full.design_info.term_names.index(model.unique)
        se_full_unique = np.diag(np.sqrt(np.linalg.inv(np.dot(X_design_full.T, X_design_full))))[model_unique_idx] * np.sqrt(RSS_full / (N - np_full - 1))
        tvalue_sign = (beta_full[model_unique_idx, :] + np.finfo(float).eps)/np.absolute(beta_full[model_unique_idx, :] + np.finfo(float).eps)
        pvalues = 1.0 - scipy.stats.f.cdf(Fstat, np_full-np_null, N-np_full-1)  # pvalue under the F distribution
        pvalues[np.isnan(pvalues)] = 1
        statsresult.pvalues = pvalues*tvalue_sign
        statsresult.tvalues = beta_full[model_unique_idx, :]/se_full_unique + np.finfo(float).eps

    except np.linalg.LinAlgError as e:
        raise excepts.ModelFailureError('Error in solving the linear system. Perhaps the data is insufficient to fit the model?\n')

    return statsresult


# Independent samples t-test
def unpaired_ttest(model, sdata):

    if len(set(sdata.demographic_data[model.hypothesis_group])) > 2:
        raise excepts.ModelFailureError('For a 2-sample t-test, the number of distinct '
                                        'elements in the column {0:s} in your demographics csv must be exactly 2.\n'.format(model.hypothesis_group))

    group1 = list(set(sdata.demographic_data[model.hypothesis_group]))[0]
    group2 = list(set(sdata.demographic_data[model.hypothesis_group]))[1]
    idx_group1 = np.where(sdata.demographic_data[model.hypothesis_group] == group1)
    idx_group2 = np.where(sdata.demographic_data[model.hypothesis_group] == group2)
    tvalues, pvalues = ttest_ind(sdata.phenotype_array[idx_group1[0], :], sdata.phenotype_array[idx_group2[0], :])
    statsresult = StatsResult(dim=sdata.phenotype_array.shape[1])
    statsresult.pvalues = np.sign(tvalues)*pvalues
    statsresult.tvalues = tvalues
    return statsresult


# Dependent (paired) samples t-test
def paired_ttest(model, sdata):

    if len(set(sdata.demographic_data[model.hypothesis_pair_id])) > 2:
        raise excepts.ModelFailureError('For a 2-sample t-test, the number of distinct '
                                        'elements in the column {0:s} in your demographics csv must be exactly 2.\n'.format(model.hypothesis_group))

    pair1 = list(set(sdata.demographic_data[model.hypothesis_pair_id]))[0]
    pair2 = list(set(sdata.demographic_data[model.hypothesis_pair_id]))[1]

    list1 = sdata.demographic_data[sdata.demographic_data[model.hypothesis_pair_id] == pair1][model.hypothesis_group].values.tolist()
    list2 = sdata.demographic_data[sdata.demographic_data[model.hypothesis_pair_id] == pair2][model.hypothesis_group].values.tolist()

    # Check if the group values for both pairs match exactly
    if len(list1) != len(list2):
        raise excepts.DemographicsDataError('Mismatch in pairs for data grouped by {0:s} and {1:s} in {2:s}.\n'
                                            'Please check the demographics csv file for missing data or duplicate entries.\n'
                                            .format(model.hypothesis_group, model.hypothesis_pair_id, model.demographics))

    # Elements of list1 and list2 should match exactly
    if cmp(list1, list2) != 0:
        raise excepts.DemographicsDataError('Mismatch in pairs for data grouped by {0:s} and {1:s} in {2:s}.\n'
                                            'Please check the demographics csv file for missing data or duplicate entries.\n'.
                                            format(model.hypothesis_group, model.hypothesis_pair_id, model.demographics))

    idx_pair1 = np.where(sdata.demographic_data[model.hypothesis_pair_id] == pair1)
    idx_pair2 = np.where(sdata.demographic_data[model.hypothesis_pair_id] == pair2)

    tvalues, pvalues = ttest_rel(sdata.phenotype_array[idx_pair1[0], :], sdata.phenotype_array[idx_pair2[0], :])
    statsresult = StatsResult(dim=sdata.phenotype_array.shape[1])
    statsresult.pvalues = np.sign(tvalues)*pvalues
    statsresult.tvalues = tvalues
    return statsresult
