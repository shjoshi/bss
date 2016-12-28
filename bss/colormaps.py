#!/usr/local/epd/bin/python
"""
This package generates different colors for statistical maps
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
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'

import numpy as np
from bss import mpl_import
mpl_import.init()
from matplotlib import colors as mpl_colors
from matplotlib import pyplot as pl
from matplotlib import colorbar
from copy import deepcopy
from math_ops import log10_transform
from json import dump, load
from os import path


class Colormap:

    def __init__(self, value_type, attributes):
        if value_type == 'pvalue':
            self.color_dict = self.create_bidirectional_pvalue_colormap(attributes)
        elif value_type == 'corr':
            self.color_dict = self.create_bidirect_corr_colormap(attributes)

        self.attrib_range, self.red_range, self.green_range, self.blue_range = Colormap.make_color_bins(self.color_dict)

    @staticmethod
    def create_pfdr_colormap(min, max):
        """
        Colormap for fdr-adjusted p-values. Assumes adjusted values after significance lie in |p| < 0.05
        """
        # Make the dict object for red, green, and blue
        color_dict = {'red': [(-1.0, 0.7216, 0.7216),
                              (-0.05*1.0001, 0.7216, 0.7216),
                              (-0.05/1.0001, 0.0, 0.0),
                              (0-1e-9, 0.0, 0.0),
                              (0+1e-9, 1.0, 1.0),
                              (0.05/1.0001, 0.7216, 0.7216),
                              (0.05*1.0001, 0.7216, 0.7216),
                              (1.0, 1.0, 1.0)],
                      'green': [(-1.0, 0.7216, 0.7216),
                                (-0.05*1.0001, 0.7216, 0.7216),
                                (-0.05/1.0001, 0.0, 0.0),
                                (0-1e-9, 1.0, 1.0),
                                (0+1e-9, 1.0, 1.0),
                                (0.05/1.0001, 0.0, 0.0),
                                (0.05*1.0001, 0.7216, 0.7216),
                                (1.0, 0.7216, 0.7216)],
                      'blue': [(-1.0, 0.7216, 0.7216),
                               (-0.05*1.0001, 0.7216, 0.7216),
                               (-0.05/1.0001, 1.0, 1.0),
                               (0-1e-9, 1.0, 1.0),
                               (0+1e-9, 0.0, 0.0),
                               (0.05/1.0001, 0.0, 0.0),
                               (0.05*1.0001, 0.7216, 0.7216),
                               (1.0, 0.7216, 0.7216)],
                      }



        return color_dict

    def create_bidirectional_pvalue_colormap(self, attributes, pFDRneg=-0.05, pFDRpos=0.05):
        """
        Colormap for pvalues. Assumes pvalues lie in |p| <= 1
        """

        negmin = -np.min(np.abs(attributes[attributes < 0]))
        if np.abs(negmin) > 0.05:
            negmin = -0.001
        negmax = -np.max(np.abs(attributes[attributes < 0]))
        posmin = np.min(attributes[attributes > 0])
        if posmin > 0.05:
            posmin = 0.001

        posmax = np.max(attributes[attributes > 0])


        neg_range = np.linspace(-1, negmin, 5)
        pos_range = np.linspace(posmin, 1, 5)

        # Make the dict object for red, green, and blue
        color_dict = {'red': [(-1.0, 0.94, 0.94),
                              (-0.0501, 0.94, 0.94),
                              (-0.05, 0.0, 0.0),
                              (negmin, 0.0, 0.0),
                              (posmin, 1.0, 1.0),
                              (0.05, 1.0, 1.0),
                              (0.0501, 0.94, 0.94),
                              (1.0, 0.94, 0.94)],
                      'green': [(-1, 0.94, 0.94),
                                (-0.0501, 0.94, 0.94),
                                (-0.05, 0.0, 0.0),
                                (negmin, 0.794, 0.794),
                                (posmin, 1.0, 1.0),
                                (0.05, 0.0, 0.0),
                                (0.0501, 0.94, 0.94),
                                (1.0, 0.94, 0.94)],
                      'blue': [(-1, 0.94, 0.94),
                               (-0.0501, 0.94, 0.94),
                               (-0.05, 1.0, 1.0),
                               (negmin, 1.0, 1.0),
                               (posmin, 0.0, 0.0),
                               (0.05, 0.0, 0.0),
                               (0.0501, 0.94, 0.94),
                               (1.0, 0.94, 0.94)]
                      }
        return color_dict

    @staticmethod
    def create_bidirectional_log_pvalue_colormap(attributes, pFDRneg=-0.05, pFDRpos=0.05):

        # attributes += np.finfo(float).eps
        pex = -1*np.log10(np.min(np.abs(attributes + np.finfo(float).eps)))*1.0001
        if not pFDRneg:
            pFDRneg = (-10**(-pex))*1.0001
        if not pFDRpos:
            pFDRpos = (10**(-pex))*1.0001

        pFDRneglog = -np.log10(np.abs(pFDRneg))
        pFDRposlog = -np.log10(np.abs(pFDRpos))

        color_dict = Colormap.create_bidirectional_logpvalues_cmap_dict(pex, pFDRneglog, pFDRposlog)

        return color_dict

    @staticmethod
    def create_bidirect_corr_colormap(corrvalues):
        # This will be a colormap from -negative min to positive max

        # Check if all correlations are zero:
        if len(corrvalues[corrvalues == 0]) == len(corrvalues):
            cmin = -1
            cmax = 1
        else:
            if corrvalues[corrvalues < 0].size == 0:  # Check if all correlations are positive
                cmin = 0
            else:
                cmin = np.min((corrvalues[corrvalues < 0]))
            if corrvalues[corrvalues > 0].size == 0:  # Check if all correlations are negative
                cmax = 0
            else:
                cmax = np.max((corrvalues[corrvalues > 0]))

        cex = np.max([np.abs(cmin), np.abs(cmax)])
        csmall = 2.0*cex/256*10

        color_dict = {'red': [(-cex, 0.0, 0.0),
                              (-csmall, 0.0, 0.0),
                              (-csmall/1.0001, 1.0, 1.0),
                              (csmall/1.0001, 1.0, 1.0),
                              (csmall, 1.0, 1.0),
                              (cex, 1.0, 1.0)],
                      'green': [(-cex, 1.0, 1.0),
                                (-csmall, 0.0, 0.0),
                                (-csmall/1.0001, 1.0, 1.0),
                                (csmall/1.0001, 1.0, 1.0),
                                (csmall, 0.0, 0.0),
                                (cex, 1.0, 1.0)],
                      'blue': [(-cex, 1.0, 1.0),
                               (-csmall, 1.0, 1.0),
                               (-csmall/1.0001, 1.0, 1.0),
                               (csmall/1.0001, 1.0, 1.0),
                               (csmall, 0.0, 0.0),
                               (cex, 0.0, 0.0)],
                      }
        return color_dict

    @staticmethod
    def create_bidirect_corr_colormap_wrong(attributes):
        """
        Colormap for correlation. Assumes correlations lie in |r| <= 1
        """

        if np.any(attributes[attributes < 0]):
            negmin = -np.min(np.abs(attributes[attributes < 0]))
        else:
            negmin = 0
        if np.any(attributes[attributes < 0]):
            negmax = -np.max(np.abs(attributes[attributes < 0]))
        else:
            negmax = 0
        if np.any(attributes[attributes > 0]):
            posmin = np.min(attributes[attributes > 0])
        else:
            posmin = 0
        if np.any(attributes[attributes > 0]):
            posmax = np.max(attributes[attributes > 0])
        else:
            posmax = 0

        neg_range = np.linspace(negmax, negmin, 5)
        pos_range = np.linspace(posmin, posmax, 5)

        # Make the dict object for red, green, and blue
        color_dict = {'red': [(neg_range[0], 0.0, 0.0),
                              (neg_range[1], 0.0, 0.0),
                              (neg_range[2], 0.0, 0.0),
                              (neg_range[3], 0.254, 0.254),
                              (neg_range[4], 0.84, 0.84),
                              (pos_range[0], 0.84, 0.84),
                              (pos_range[1], 0.862, 0.862),
                              (pos_range[2], 0.917, 0.917),
                              (pos_range[3], 0.956, 0.956),
                              (pos_range[4], 1.0, 1.0)],
                      'green': [(neg_range[0], 1.0, 1.0),
                                (neg_range[1], 0.5, 0.5),
                                (neg_range[2], 0.0, 0.0),
                                (neg_range[3], 0.082, 0.082),
                                (neg_range[4], 0.84, 0.84),
                                (pos_range[0], 0.84, 0.84),
                                (pos_range[1], 0.0784, 0.0784),
                                (pos_range[2], 0.419, 0.419),
                                (pos_range[3], 0.6862, 0.6862),
                                (pos_range[4], 1.0, 1.0)],
                      'blue': [(neg_range[0], 1.0, 1.0),
                               (neg_range[1], 0.99, 0.99),
                               (neg_range[2], 0.98, 0.98),
                               (neg_range[3], 0.521, 0.521),
                               (neg_range[4], 0.84, 0.84),
                               (pos_range[0], 0.84, 0.84),
                               (pos_range[1], 0.1372, 0.1372),
                               (pos_range[2], 0.07, 0.07),
                               (pos_range[3], 0.0392, 0.0392),
                               (pos_range[4], 0.0, 0.0)]
                      }
        return color_dict


    @staticmethod
    def make_color_bins(color_dict):
        red_color_list = color_dict['red']
        attribute_range = []
        red_range = []
        green_range = []
        blue_range = []

        for i in red_color_list:
            attribute_range.append(i[0])
            red_range.append(i[1])

        for i in color_dict['green']:
            green_range.append(i[1])

        for i in color_dict['blue']:
            blue_range.append(i[1])

        return np.array(attribute_range), np.array(red_range), np.array(green_range), np.array(blue_range)

    @staticmethod
    def get_rgb_from_attribute(attrib_range, red_range, green_range, blue_range, value):

        value = float(value)
        idx1 = np.where((attrib_range <= value) == True)[0][-1]
        idx2 = np.where((attrib_range >= value) == True)[0][0]
        red = (1.0 - value)*red_range[idx1] + value*red_range[idx2]
        green = (1.0 - value)*green_range[idx1] + value*green_range[idx2]
        blue = (1.0 - value)*blue_range[idx1] + value*blue_range[idx2]
        return (red, green, blue)

    @staticmethod
    def get_rgb_list_from_attribute_list(attribute_list, attrib_range, red_range, green_range, blue_range):
        rgb_list = []
        for value in attribute_list:
            rgb_list.append(Colormap.get_rgb_from_attribute(attrib_range, red_range, green_range, blue_range, value))
        return rgb_list

    @staticmethod
    def scale(val, src, dst):
        """
        Scale the given value from the scale of src to the scale of dst.
        """
        return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

    @staticmethod
    def normalize(val, minval, maxval):
        return (val - minval) / float(maxval - minval)

    @staticmethod
    def get_rgb_color_array(value_type, attributes):
        cmap = Colormap(value_type, attributes)
        rgb_list = cmap.get_rgb_list_from_attribute_list(attributes)

        vColor = np.empty((3, len(attributes)))
        for idx, val in enumerate(rgb_list):
            vColor[:, idx] = [val[0], val[1], val[2]]
        vColor = np.ndarray.transpose(vColor)
        return vColor

    @staticmethod
    def exportBrainSuiteLUT(filename, LUT):

        fid = open(filename, 'wt')
        for i in range(0, len(LUT)):
            fid.write("{0:f} {1:f} {2:f}\n".format(float(LUT[i, 0]), float(LUT[i, 1]), float(LUT[i, 2])))

        fid.close()

    @staticmethod
    def create_bidirectional_corr_cmap_dict(cex):
        csmall = 2.0 * cex / 256 * 10

        color_dict = {'red': [(-cex, 0.0, 0.0),
                              (-csmall, 0.0, 0.0),
                              (-csmall / 1.0001, 1.0, 1.0),
                              (csmall / 1.0001, 1.0, 1.0),
                              (csmall, 1.0, 1.0),
                              (cex, 1.0, 1.0)],
                      'green': [(-cex, 1.0, 1.0),
                                (-csmall, 0.0, 0.0),
                                (-csmall / 1.0001, 1.0, 1.0),
                                (csmall / 1.0001, 1.0, 1.0),
                                (csmall, 0.0, 0.0),
                                (cex, 1.0, 1.0)],
                      'blue': [(-cex, 1.0, 1.0),
                               (-csmall, 1.0, 1.0),
                               (-csmall / 1.0001, 1.0, 1.0),
                               (csmall / 1.0001, 1.0, 1.0),
                               (csmall, 0.0, 0.0),
                               (cex, 0.0, 0.0)],
                      }
        return color_dict

    @staticmethod
    def create_bidirectional_tvalues_cmap_dict(tvalues):

        if np.all(tvalues >= 0):  # All tvalues are positive
            # Check if 0 is the minimum element
            if np.min(tvalues) == 0:
                tposmin = np.min(tvalues[tvalues != 0])
            else:
                tposmin = np.min(tvalues)
            tposmax  = np.max(tvalues)
            return Colormap.create_hot_cmap_dict(tposmin, tposmax)

        if np.all(tvalues <= 0):  # All tvalues are negative
            # Check if 0 is the minimum element
            if np.min(tvalues) == 0:
                tnegmin = -1*np.min(np.abs(tvalues[tvalues != 0]))
            else:
                tnegmin = -1*np.min(np.abs(tvalues))
            tnegmax = -1*np.max(np.abs(tvalues))
            return Colormap.create_blue_cmap_dict(tnegmin, tnegmax)

        tnegmin = -1*np.min(np.abs(tvalues[tvalues <= 0]))
        tnegmax = -1*np.max(np.abs(tvalues[tvalues <= 0]))
        tposmin = np.min(np.abs(tvalues[tvalues >= 0]))
        tposmax = np.max(np.abs(tvalues[tvalues >= 0]))

        eps = np.abs(tposmax - tnegmax) / 256.0
        if np.abs(tnegmin) < eps:
            tnegmin = -1*eps

        if tposmin < eps:
            tposmin = eps

        color_dict = {'red': [(tnegmax, 0.0, 0.0),
                              (tnegmin*1.001, 0.0, 0.0),
                              (tnegmin, 1.0, 1.0),
                              (0, 1.0, 1.0),
                              (tposmin, 1.0, 1.0),
                              (tposmin*1.001, 1.0, 1.0),
                              (tposmax, 1.0, 1.0)],
                      'green': [(tnegmax, 1.0, 1.0),
                                (tnegmin*1.001, 0.0, 0.0),
                                (tnegmin, 1.0, 1.0),
                                (0, 1.0, 1.0),
                                (tposmin, 1.0, 1.0),
                                (tposmin*1.001, 0.0, 0.0),
                                (tposmax, 1.0, 1.0)],
                      'blue': [(tnegmax, 1.0, 1.0),
                               (tnegmin*1.001, 1.0, 1.0),
                               (tnegmin, 1.0, 1.0),
                               (0, 1.0, 1.0),
                               (tposmin, 1.0, 1.0),
                               (tposmin*1.001, 0.0, 0.0),
                               (tposmax, 0.0, 0.0)],
                      }
        return color_dict

    @staticmethod
    def create_white_cmap_dict():
        color_dict = {'red': [(0, 1.0, 1.0),
                              (1, 1.0, 1.0)],
                      'green': [(0, 1.0, 1.0),
                                (1, 1.0, 1.0)],
                      'blue': [(0, 1.0, 1.0),
                               (1, 1.0, 1.0)],
                      }
        return color_dict

    @staticmethod
    def create_hot_cmap_dict(minval, maxval):
        color_dict = {'red': [(0, 1.0, 1.0),
                              (minval/1.001, 1.0, 1.0),
                              (minval, 1.0, 1.0),
                              (maxval, 1.0, 1.0)],
                      'green': [(0, 1.0, 1.0),
                                (minval/1.001, 1.0, 1.0),
                                (minval, 0.0, 0.0),
                                (maxval, 1.0, 1.0)],
                      'blue': [(0, 1.0, 1.0),
                               (minval/1.001, 1.0, 1.0),
                               (minval, 0.0, 0.0),
                               (maxval, 0.0, 0.0)],
                      }
        return color_dict

    @staticmethod
    def create_blue_cmap_dict(minval, maxval):
        color_dict = {'red': [(maxval, 0.0, 0.0),
                              (minval*1.001, 0.0, 0.0),
                              (minval, 1.0, 1.0),
                              (0, 1.0, 1.0)],
                      'green': [(maxval, 1.0, 1.0),
                                (minval*1.001, 0.0, 0.0),
                                (minval, 1.0, 1.0),
                                (0, 1.0, 1.0)],
                      'blue': [(maxval, 1.0, 1.0),
                               (minval*1.001, 1.0, 1.0),
                               (minval, 1.0, 1.0),
                               (0, 1.0, 1.0)],
                      }
        return color_dict

    @staticmethod
    def create_bidirectional_logpvalues_cmap_dict(pex, pFDRneglog=1.3010, pFDRposlog=1.3010):
        # Make the dict object for red, green, and blue
        color_dict = {'red': [(-pex, 0.0, 0.0),
                              (-pFDRneglog, 0.0, 0.0),
                              (-pFDRneglog/1.0001, 1.0, 1.0),
                              (pFDRposlog/1.0001, 1.0, 1.0),
                              (pFDRposlog, 1.0, 1.0),
                              (pex, 1.0, 1.0)],
                      'green': [(-pex, 1.0, 1.0),
                                (-pFDRneglog, 0.0, 0.0),
                                (-pFDRneglog/1.0001, 1.0, 1.0),
                                (pFDRposlog/1.0001, 1.0, 1.0),
                                (pFDRposlog, 0.0, 0.0),
                                (pex, 1.0, 1.0)],
                      'blue': [(-pex, 1.0, 1.0),
                               (-pFDRneglog, 1.0, 1.0),
                               (-pFDRneglog/1.0001, 1.0, 1.0),
                               (pFDRposlog/1.0001, 1.0, 1.0),
                               (pFDRposlog, 0.0, 0.0),
                               (pex, 0.0, 0.0)],
                      }
        return color_dict

    @staticmethod
    def exportParaviewCmap(color_dict, filename):
        fid = open(filename, 'wt')
        fid.write('<ColorMap name="bi-direct" space="RGB">\n')

        for i in range(0, len(color_dict['red'])):
            xval, r, g, b = color_dict['red'][i][0], color_dict['red'][i][1], \
                            color_dict['green'][i][1], color_dict['blue'][i][1]
            fid.write('<Point x="{0:f}" o="1" r="{1:f}" g="{2:f}" b="{3:f}"/>\n'.format(float(xval), float(r), float(g), float(b)))

        fid.write('<NaN r="1" g="1" b="0"/>\n')
        fid.write('</ColorMap>\n')
        return None

    @staticmethod
    def exportMayavi2LUT(minval, maxval, filename, lut_length=256):
        x = np.linspace(minval, maxval, 256)
        LUT = Colormap.get_rgb_color_array(value_type='pvalue', attributes=x)
        fid = open(filename, 'wt')
        fid.write('LOOKUP_TABLE UnnamedTable 256\n')
        for i in range(0, len(LUT)):
            fid.write("{0:f} {1:f} {2:f} {3:f}\n".format(float(LUT[i, 0]), float(LUT[i, 1]), float(LUT[i, 2]), 1.0))

        fid.close()
        return None

    # @staticmethod
    # def show_and_save_colorbar(attributes, cmap, cdict, cmap_png_filename):
    #
    #     pex = np.abs(cdict['red'][0][0])
    #     pFDRneglog = cdict['red'][1][0]
    #     pFDRposlog = cdict['red'][4][0]
    #
    # #    zvals = np.reshape(attributes,(6, 27307))
    #     zvals = np.reshape(attributes,(25, 600))
    #
    #     img = plt.imshow(zvals, cmap=cmap,vmin=-pex,vmax=pex)
    #     frame1 = plt.gca()
    #     frame1.axes.get_xaxis().set_visible(False)
    #
    #     plt.rcParams['font.size'] = 32
    #     plt.colorbar(img, cmap=cmap,ticks = [-pex,(-pex + pFDRneglog)/2.0,pFDRneglog,0,pFDRposlog,(pFDRposlog + pex)/2.0,pex],format = '%1.3g' )
    # #    plt.colorbar(cmap=cmap,ticks = [-pex,pFDRneglog,pFDRposlog,pex] )
    #
    #     plt.savefig(cmap_png_filename)

    @staticmethod
    def correlation_to_rgb(attributes):
        cex = np.max(np.abs(attributes))
        if cex == 0:
            cdict = Colormap.create_white_cmap_dict()
        else:
            cdict = Colormap.create_bidirectional_corr_cmap_dict(cex)
            cdict_orig = deepcopy(cdict)
            # Scale the attribute values in cdict from 0 to 1
            for i in range(0, len(cdict['red'])):
                cdict['red'][i] = ((cdict['red'][i][0] + cex) / (2 * cex), cdict['red'][i][1], cdict['red'][i][2])
            for i in range(0, len(cdict['green'])):
                cdict['green'][i] = ((cdict['green'][i][0] + cex) / (2 * cex), cdict['green'][i][1], cdict['green'][i][2])
            for i in range(0, len(cdict['blue'])):
                cdict['blue'][i] = ((cdict['blue'][i][0] + cex) / (2 * cex), cdict['blue'][i][1], cdict['blue'][i][2])

        my_cmap = mpl_colors.LinearSegmentedColormap('my_bi_cmap', cdict, 256)
        my_cmap._init()
        new_attrib_range = Colormap.normalize(attributes, -1 * cex, cex)
        vColor = my_cmap(new_attrib_range)[:, 0:3]
        return vColor, cex, my_cmap

    @staticmethod
    def tvalues_to_rgb(attributes):
        tmin = np.min(attributes)
        tmax = np.max(attributes)
        if 0 == tmin and 0 == tmax:
            cdict = Colormap.create_white_cmap_dict()
        else:
            cdict = Colormap.create_bidirectional_tvalues_cmap_dict(attributes)
            cdict_orig = deepcopy(cdict)
            # Scale the attribute values in cdict from 0 to 1
            red_color_list = cdict['red']
            attribute_range = []

            for i in red_color_list:
                attribute_range.append(i[0])
            tmin = np.min(attribute_range)
            tmax = np.max(attribute_range)

            for i in range(0, len(cdict['red'])):
                cdict['red'][i] = ((cdict['red'][i][0] - tmin) / (tmax - tmin), cdict['red'][i][1], cdict['red'][i][2])
            for i in range(0, len(cdict['green'])):
                cdict['green'][i] = ((cdict['green'][i][0] - tmin) / (tmax - tmin), cdict['green'][i][1], cdict['green'][i][2])
            for i in range(0, len(cdict['blue'])):
                cdict['blue'][i] = ((cdict['blue'][i][0] - tmin) / (tmax - tmin), cdict['blue'][i][1], cdict['blue'][i][2])

        my_cmap = mpl_colors.LinearSegmentedColormap('my_bi_cmap', cdict, 256)
        my_cmap._init()
        new_attrib_range = Colormap.normalize(attributes, tmin, tmax)
        vColor = my_cmap(new_attrib_range)[:, 0:3]
        return vColor, tmin, tmax, my_cmap

    @staticmethod
    def log_pvalues_to_rgb(log_pvalues):
        pex = np.max(np.abs(log_pvalues))
        if pex < -1*np.log10(0.05):
            cdict = Colormap.create_white_cmap_dict()
            pex = -1*np.log10(0.05)*1.00001
        else:
            cdict = Colormap.create_bidirectional_logpvalues_cmap_dict(pex)
            cdict_orig = deepcopy(cdict)
            # Scale the attribute values in cdict from 0 to 1
            for i in range(0, len(cdict['red'])):
                cdict['red'][i] = ((cdict['red'][i][0] + pex) / (2 * pex), cdict['red'][i][1], cdict['red'][i][2])
            for i in range(0, len(cdict['green'])):
                cdict['green'][i] = ((cdict['green'][i][0] + pex) / (2 * pex), cdict['green'][i][1], cdict['green'][i][2])
            for i in range(0, len(cdict['blue'])):
                cdict['blue'][i] = ((cdict['blue'][i][0] + pex) / (2 * pex), cdict['blue'][i][1], cdict['blue'][i][2])

        my_cmap = mpl_colors.LinearSegmentedColormap('my_bi_cmap', cdict, 256)
        my_cmap._init()
        new_attrib_range = Colormap.normalize(log_pvalues, -1 * pex, pex)
        vColor = my_cmap(new_attrib_range)[:, 0:3]
        return vColor, pex, my_cmap

    @staticmethod
    def log_transform_pvalues_to_rgb(pvalues):
        log_pvalues = log10_transform(pvalues)
        vColor, pex, my_cmap = Colormap.log_pvalues_to_rgb(log_pvalues)
        return vColor, pex, my_cmap

    @staticmethod
    def save_colorbar(file, cmap, vmin, vmax, labeltxt):
        fig = pl.figure(figsize=(1.2, 3.1))
        ax1 = fig.add_axes([0.05, 0.05, 0.1, 0.9])
        norm = mpl_colors.Normalize(vmin=vmin, vmax=vmax)
        cb1 = colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='vertical')
        cb1.ax.tick_params(axis='y', labelsize=16)
        cb1.set_clim(vmin=vmin, vmax=vmax)
        cb1.set_label(labeltxt)
        fig.savefig(file)
        jsonfilename = path.splitext(file)[0] + '.json'
        Colormap.save_colormap_to_json(jsonfilename, cmap, vmin, vmax, labeltxt)

    @staticmethod
    def save_colormap_to_json(jsonfile, cmap, vmin, vmax, labeltxt):
        cmap_json_dict = {
            'vmin': vmin,
            'vmax': vmax,
            'labeltxt': labeltxt,
            'cmap_dict': cmap._segmentdata
        }
        with open(jsonfile, 'wt') as fid:
            dump(cmap_json_dict, fid, indent=2)

    @staticmethod
    def load_colormap_from_json(jsonfile):
        with open(jsonfile, 'r') as fid:
            cmap_json_dict = load(fid)

        return cmap_json_dict['cmap_dict'], cmap_json_dict['vmin'], cmap_json_dict['vmax'], cmap_json_dict['labeltxt']
