#! /usr/local/epd/bin/python

"""Output specification and formatting for vertex wise statistical results"""

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

import numpy as np
import os
import dfsio
import sys
import colormaps
from nimgdata_io import NimgDataio
import nibabel as nib
from math_ops import log10_transform


class StatsNimgOutput(object):

    def __init__(self, outdir, outprefix, statsresult, mask_idx=np.array([]), dim=0):
        self.outdir = outdir
        self.outprefix = outprefix
        self.statsresult = statsresult
        self.mask_idx = mask_idx

    def save(self, atlas_filename):
        sys.stdout.write('Saving output files...\n')
        nimg_data_type = NimgDataio.validatetype(atlas_filename)

        if nimg_data_type == 'surface':
            self.save_surface(atlas_filename)
        elif nimg_data_type == 'nifti_image':
            self.save_nifti_image(atlas_filename)
        else:
            raise TypeError('Error: Unsupported data type. Supported data types are: ' + ', '.join(NimgDataio.datatype.keys()) + '.\n')
        sys.stdout.write('Done.\n')

    def save_surface(self, atlas_filename):

        s1 = dfsio.readdfs(atlas_filename)
        if self.mask_idx.any():
            pvalues = np.ones(s1.vertices.shape[0])
            pvalues[self.mask_idx] = self.statsresult.pvalues
            self.statsresult.pvalues = pvalues
            tvalues = np.zeros(s1.vertices.shape[0])
            tvalues[self.mask_idx] = self.statsresult.tvalues
            self.statsresult.tvalues = tvalues
        s1.attributes = self.statsresult.pvalues
        # print s1.attributes

        if len(s1.attributes) == s1.vertices.shape[0]:
            # Also write color to the field
            self.statsresult.pvalues = log10_transform(self.statsresult.pvalues)
            s1.vColor, pex, cmap = colormaps.Colormap.log_pvalues_to_rgb(self.statsresult.pvalues)
            s1.attributes = self.statsresult.pvalues
            dfsio.writedfs(os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues.dfs'), s1)
            colormaps.Colormap.save_colorbar(file=os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues_cbar.pdf'),
                                             cmap=cmap, vmin=-1*pex, vmax=pex, labeltxt='Unadjusted p-values')
            s1.attributes = self.statsresult.tvalues
            s1.vColor, tmin, tmax, cmap_tvalues = colormaps.Colormap.tvalues_to_rgb(self.statsresult.tvalues)
            dfsio.writedfs(os.path.join(self.outdir, self.outprefix + '_atlas_tvalues_all.dfs'), s1)
            colormaps.Colormap.save_colorbar(file=os.path.join(self.outdir, self.outprefix + '_atlas_tvalues_all_cbar.pdf'),
                                             cmap=cmap_tvalues, vmin=tmin, vmax=tmax, labeltxt='t-values (all)')
            self.statsresult.tvalues[np.abs(self.statsresult.pvalues) <= -1 * np.log10(0.05)] = 0
            s1.vColor, tmin, tmax, cmap_tvalues = colormaps.Colormap.tvalues_to_rgb(self.statsresult.tvalues)
            s1.attributes = self.statsresult.tvalues
            dfsio.writedfs(os.path.join(self.outdir, self.outprefix + '_atlas_tvalues.dfs'), s1)
            colormaps.Colormap.save_colorbar(file=os.path.join(self.outdir, self.outprefix + '_atlas_tvalues_cbar.pdf'),
                                             cmap=cmap_tvalues, vmin=tmin, vmax=tmax, labeltxt='t-values (unadjusted)')
            LUT = cmap_tvalues._lut[0:256, 0:3]
            colormaps.Colormap.exportBrainSuiteLUT(os.path.join(self.outdir, self.outprefix + '_atlas_tvalues_cbar.lut'), LUT)

            with open(os.path.join(self.outdir, self.outprefix + '_unadjusted_pvalue_range.txt'), "wt") as text_file:
                text_file.write("Log P-value range: -{0:s} to +{1:s}\n".format(str(pex), str(pex)))
                text_file.write("P-value range: {0:s} to +{1:s}\n".format(str(-1*10**(-1*pex)), str(10**(-1*pex))))

            if len(self.statsresult.pvalues_adjusted) > 0:
                if self.mask_idx.any():
                    pvalues = np.ones(s1.vertices.shape[0])
                    pvalues[self.mask_idx] = self.statsresult.pvalues_adjusted
                    self.statsresult.pvalues_adjusted = pvalues

                s1.attributes = self.statsresult.pvalues_adjusted
                self.statsresult.pvalues_adjusted = log10_transform(self.statsresult.pvalues_adjusted)
                s1.vColor, pex, cmap = colormaps.Colormap.log_pvalues_to_rgb(self.statsresult.pvalues_adjusted)
                s1.attributes = self.statsresult.pvalues_adjusted
                dfsio.writedfs(os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues_adjusted.dfs'), s1)
                colormaps.Colormap.save_colorbar(file=os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues_adjusted_cbar.pdf'),
                    cmap=cmap, vmin=-1 * pex, vmax=pex, labeltxt='Adjusted p-values')
                self.statsresult.tvalues[np.abs(self.statsresult.pvalues_adjusted) < -1 * np.log10(0.05)] = 0
                s1.vColor, tmin, tmax, cmap_tvalues = colormaps.Colormap.tvalues_to_rgb(self.statsresult.tvalues)
                s1.attributes = self.statsresult.tvalues
                dfsio.writedfs(os.path.join(self.outdir, self.outprefix + '_atlas_tvalues_adjusted.dfs'), s1)
                colormaps.Colormap.save_colorbar(file=os.path.join(self.outdir, self.outprefix + '_atlas_tvalues_adjusted_cbar.pdf'),
                                                 cmap=cmap_tvalues, vmin=tmin, vmax=tmax, labeltxt='t-values (adjusted)')
                LUT = cmap_tvalues._lut[0:256, 0:3]
                colormaps.Colormap.exportBrainSuiteLUT(os.path.join(self.outdir, self.outprefix + '_atlas_tvalues_adjusted_cbar.lut'), LUT)

                with open(os.path.join(self.outdir, self.outprefix + '_adjusted_pvalue_range.txt'), "wt") as text_file:
                    text_file.write("Log P-value range: -{0:s} to +{1:s}\n".format(str(pex), str(abs(pex))))
                    text_file.write("P-value range: {0:s} to +{1:s}\n".format(str(-1*10**(-1*pex)), str(10**(-1*pex))))
        else:
            sys.stdout.write('Error: Dimension mismatch between the p-values and the number of vertices. '
                             'Quitting without saving.\n')

        if len(self.statsresult.corrvalues) > 0:
            if self.mask_idx.any():
                corrvalues = np.zeros(s1.vertices.shape[0])
                corrvalues[self.mask_idx] = self.statsresult.corrvalues
                self.statsresult.corrvalues = corrvalues

            s1.attributes = self.statsresult.corrvalues
            s1.vColor, cex, cmap = colormaps.Colormap.correlation_to_rgb(self.statsresult.corrvalues)
            dfsio.writedfs(os.path.join(self.outdir, self.outprefix + '_corr.dfs'), s1)
            colormaps.Colormap.save_colorbar(file=os.path.join(self.outdir, self.outprefix + '_corr_cbar.pdf'),
                                             cmap=cmap, vmin=-1 * cex, vmax=cex, labeltxt='Correlations (unadjusted)')
            with open(os.path.join(self.outdir, self.outprefix + '_corr_range.txt'), "wt") as text_file:
                text_file.write("Correlation values range: -{0:s} to +{1:s}\n".format(str(cex), str(cex)))

            # Also write color to the field
            self.statsresult.corrvalues[np.abs(self.statsresult.pvalues_adjusted) < -1*np.log10(0.05)] = 0
            s1.attributes = self.statsresult.corrvalues
            s1.vColor, cex, cmap = colormaps.Colormap.correlation_to_rgb(self.statsresult.corrvalues)
            dfsio.writedfs(os.path.join(self.outdir, self.outprefix + '_corr_adjusted.dfs'), s1)
            colormaps.Colormap.save_colorbar(file=os.path.join(self.outdir, self.outprefix + '_corr_adjusted_cbar.pdf'),
                                             cmap=cmap, vmin=-1 * cex, vmax=cex, labeltxt='Correlations (adjusted)')
            with open(os.path.join(self.outdir, self.outprefix + '_adjusted_corr_range.txt'), "wt") as text_file:
                text_file.write("Adjusted Correlation values range: {0:s} to +{1:s}\n".format(str(cex), str(cex)))

        sys.stdout.write('Done.\n')

    def save_nifti_image(self, atlas_filename):
        nimg_atlas_nifti_obj = NimgDataio.read_nifi_image_obj(atlas_filename)
        nifti_img = nimg_atlas_nifti_obj.get_data()
        nifti_img_siz = nifti_img.shape[0]*nifti_img.shape[1]*nifti_img.shape[2]

        if len(self.statsresult.pvalues) > 0:
            if self.mask_idx.any():
                pvalues = np.ones(nifti_img.size)
                pvalues[self.mask_idx] = self.statsresult.pvalues
                self.statsresult.pvalues = pvalues

            self.statsresult.pvalues = log10_transform(self.statsresult.pvalues)
            cdict_pvalues, pex, cmap = colormaps.Colormap.log_pvalues_to_rgb(self.statsresult.pvalues)
            LUT = cmap._lut[0:256, 0:3]
            colormaps.Colormap.exportBrainSuiteLUT(os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues.lut'), LUT)

            # Write pvalues as a nifti image
            NimgDataio.write_nifti_image_from_array(os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues.nii.gz'),
                                                    self.statsresult.pvalues, nimg_atlas_nifti_obj)

            if len(self.statsresult.pvalues_adjusted) > 0:
                if self.mask_idx.any():
                    pvalues = np.ones(nifti_img.size)
                    pvalues[self.mask_idx] = self.statsresult.pvalues_adjusted
                    self.statsresult.pvalues_adjusted = pvalues

                self.statsresult.pvalues_adjusted = log10_transform(self.statsresult.pvalues_adjusted)
                cdict_pvalues, pex, cmap = colormaps.Colormap.log_pvalues_to_rgb(self.statsresult.pvalues_adjusted)
                LUT = cmap._lut[0:256, 0:3]
                colormaps.Colormap.exportBrainSuiteLUT(os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues_adjusted.lut'), LUT)

                # Write adjusted pvalues as a nifti image
                NimgDataio.write_nifti_image_from_array(os.path.join(self.outdir, self.outprefix + '_atlas_log_pvalues_adjusted.nii.gz'),
                                                        self.statsresult.pvalues_adjusted, nimg_atlas_nifti_obj)

        if len(self.statsresult.corrvalues) > 0:
            if self.mask_idx.any():
                corrvalues = np.zeros(nifti_img.size)
                corrvalues[self.mask_idx] = self.statsresult.corrvalues
                self.statsresult.corrvalues = corrvalues

            # cdict_corrvalues = colormaps.Colormap.create_bidirect_corr_colormap(self.statsresult.corrvalues)
            vColor, cex, cmap = colormaps.Colormap.correlation_to_rgb(self.statsresult.corrvalues)
            LUT = cmap._lut[0:256, 0:3]
            colormaps.Colormap.exportBrainSuiteLUT(os.path.join(self.outdir, self.outprefix + '_corrvalues.lut'), LUT)

            # Write correlations as a nifti image
            NimgDataio.write_nifti_image_from_array(os.path.join(self.outdir, self.outprefix + '_corr.nii.gz'),
                                                    self.statsresult.corrvalues, nimg_atlas_nifti_obj)

            self.statsresult.corrvalues[np.abs(self.statsresult.pvalues_adjusted) < -1*np.log10(0.05)] = 0
            # cdict_corrvalues = colormaps.Colormap.create_bidirect_corr_colormap(self.statsresult.corrvalues)
            vColor, cex, cmap = colormaps.Colormap.correlation_to_rgb(self.statsresult.corrvalues)
            LUT = cmap._lut[0:256, 0:3]
            colormaps.Colormap.exportBrainSuiteLUT(os.path.join(self.outdir, self.outprefix + '_corrvalues_adjusted.lut'), LUT)

            # Write adjusted correlations as a nifti image
            NimgDataio.write_nifti_image_from_array(os.path.join(self.outdir, self.outprefix + '_corr_adjusted.nii.gz'),
                                                    self.statsresult.corrvalues, nimg_atlas_nifti_obj)
