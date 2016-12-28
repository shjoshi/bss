""" This module implements mathematical operations on images, surfaces, and vector fields
    Also see http://brainsuite.bmap.ucla.edu for the software
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
__copyright__ = "Copyright 2015, Shantanu H. Joshi, Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "s.joshi@g.ucla.edu"

import numpy as np
import scipy.ndimage as ndimage
import nii_io
from nibabel.nifti1 import Nifti1Image
import sys
import dfsio
import excepts
from nimgdata_io import NimgDataio
from xml.dom import minidom


def jacobian(v1, v2, v3):

    [Dxu, Dxv, Dxw] = np.gradient(v1)
    [Dyu, Dyv, Dyw] = np.gradient(v2)
    [Dzu, Dzv, Dzw] = np.gradient(v3)

    detJ3 = Dxu * (Dyv*Dzw - Dyw*Dzv) - Dyu * (Dxv*Dzw - Dxw*Dzv) + Dzu * (Dxv*Dyw - Dxw*Dyv)
    detJ2 = Dxu*Dyv - Dxv*Dyu
    detJ1 = Dxu

    J3 = [Dxv, Dxu, Dxw]
    return detJ3, J3


def jacobian_det_image(in_file, out_file, sigma=0):
    nii = nii_io.readnii(in_file)
    nii_data = nii.get_data()
    if len(nii_data.shape) != 4:
        raise ValueError(' Expecting a 4D file containing vector fields. The dimensions of ' + in_file + ' are ' +
                         str(nii_data.shape) + '.\n')  # TODO: Change this to a custom exception in future
    v1 = nii_data[:, :, :, 0]
    v2 = nii_data[:, :, :, 1]
    v3 = nii_data[:, :, :, 2]
    detJ, J = jacobian(v1, v2, v3)

    detJ_smooth = smooth_image(detJ, sigma)
    detJ_smooth_img = Nifti1Image(detJ_smooth, affine=nii.get_affine(), header=nii.get_header())
    nii_io.writenii(out_file, detJ_smooth_img)


def smooth_image(img_data_in, sigma=0):
    if sigma > 0:
        img_data_out = ndimage.gaussian_filter(img_data_in, sigma)
    else:  # Do not smooth.
        img_data_out = img_data_in
    return img_data_out


def smooth_image_file(in_file, smooth_file, sigma=0):
    img = nii_io.readnii(in_file)
    img_data = img.get_data()
    smooth_img_data = smooth_image(img_data, sigma)
    smooth_img = Nifti1Image(smooth_img_data, affine=img.get_affine(), header=img.get_header())
    nii_io.writenii(smooth_file, smooth_img)


def add(file1, file2, fileout):
    raise NotImplementedError('Add operation is not yet implemented.')


def sub(file1, file2, fileout):
    s1 = dfsio.readdfs(file1)
    s2 = dfsio.readdfs(file2)
    sout = s1
    if not s1.attributes.any() and not s2.attributes.any():
        raise excepts.AttributeMissingError('Missing attributes in {0:s} and/or {1:s}'.format(file1, file2))  # TODO: Change this to a custom exception in future
    if len(s1.attributes) != len(s2.attributes):
        raise excepts.AttributeLengthError('Attribute lengths of {0:s} and {1:s} do not match.\n'.format(file1, file2))
    sout.attributes = s1.attributes - s2.attributes
    dfsio.writedfs(fileout, sout)


def percent_change(file1, file2, fileout):
    s1 = dfsio.readdfs(file1)
    s2 = dfsio.readdfs(file2)
    sout = s1
    if not s1.attributes.any() and not s2.attributes.any():
        raise excepts.AttributeMissingError('Missing attributes in {0:s} and/or {1:s}'.format(file1, file2))  # TODO: Change this to a custom exception in future
    if len(s1.attributes) != len(s2.attributes):
        raise excepts.AttributeLengthError('Attribute lengths of {0:s} and {1:s} do not match.\n'.format(file1, file2))
    sout.attributes = (s1.attributes - s2.attributes)/s1.attributes*100
    dfsio.writedfs(fileout, sout)


def log10_transform(arrayin):
    sign = np.sign(arrayin)
    arrayout = -1*sign*np.log10(np.abs(arrayin) + np.finfo(float).eps)
    return arrayout


def image_to_shape(imagefile, shapefile, outputshapefile, resample):
    NimgDataio.validatetype(imagefile)
    NimgDataio.validatetype(shapefile)

    sys.stdout.write('Reading Image file ' + imagefile + '...')
    img = nii_io.readnii(imagefile)
    sys.stdout.write('Done.\n')

    sys.stdout.write('Reading Shape file ' + shapefile + '...')
    shape = NimgDataio.read_surface(shapefile)
    sys.stdout.write('Done.\n')

    # Scale shape coordinates to image according to pixdim
    pixdim = np.asarray(img.get_header().get_zooms())
    vox_indices = np.rint(shape.vertices / pixdim)
    vox_indices = vox_indices.astype(int)
    imgdim = img.get_header().get_data_shape()
    validate_shape_dimensions(vox_indices, imgdim)

    img_data = img.get_data()
    img_data_ravel = np.ravel(img_data)

    sys.stdout.write('Resampling image values to shape...')
    # Iterate over all shape coordinates (voxel indices) to find the resampled value
    if resample == 'nearest':  # Just use the voxel value
        idx = [np.ravel_multi_index(i, imgdim) for i in vox_indices]
        shape.attributes = img_data_ravel[idx]

    if resample == 'mean':
        # For each voxel index find the voxel neighborhood
        Nbr_list = np.zeros((len(shape.attributes), 18), dtype=np.int)
        for i, v_idx in enumerate(vox_indices):
            Nbr_list[i, :] = get_vox_neighborhood_ravel_index(v_idx[0], v_idx[1], v_idx[2], imgdim)
            shape.attributes[i] = np.mean(img_data_ravel[Nbr_list[i, :]])

    if resample == 'max':
        # For each voxel index find the voxel neighborhood
        Nbr_list = np.zeros((len(shape.attributes), 18), dtype=np.int)
        for i, v_idx in enumerate(vox_indices):
            Nbr_list[i, :] = get_vox_neighborhood_ravel_index(v_idx[0], v_idx[1], v_idx[2], imgdim)
            shape.attributes[i] = np.max(img_data_ravel[Nbr_list[i, :]])

    if outputshapefile:
        dfsio.writedfs(outputshapefile, shape)
    else:
        dfsio.writedfs(shapefile, shape)
    sys.stdout.write('Done.\n')


def validate_shape_dimensions(vertices, imgdim):
    # Calculate bounding box of shape and ensure it lies within the image
    xmin, ymin, zmin = np.min(vertices, 0)
    xmax, ymax, zmax = np.max(vertices, 0)

    if xmin < 0 or ymin < 0 or zmin < 0:
        raise IndexError('\nError: One or more minimum coordinates of shape are lying outside the image dimensions.')
    if xmax > imgdim[0] or ymax > imgdim[1] or zmax > imgdim[2]:
        raise IndexError('\nError: One or more maximum coordinates of shape are lying outside the image dimensions.')


def get_vox_neighborhood(i, j, k, n=18):

    # i, j, k is a voxel index
    # n is the number of adjacent neighbors, default is 18
    Nbrs = []
    Nbrs.append((i+1, j, k))
    Nbrs.append((i-1, j, k))

    Nbrs.append((i, j+1, k))
    Nbrs.append((i, j-1, k))

    Nbrs.append((i, j, k+1))
    Nbrs.append((i, j, k-1))

    Nbrs.append((i+1, j+1, k))
    Nbrs.append((i-1, j-1, k))

    Nbrs.append((i+1, j-1, k))
    Nbrs.append((i-1, j+1, k))

    Nbrs.append((i+1, j, k+1))
    Nbrs.append((i-1, j, k-1))

    Nbrs.append((i+1, j, k-1))
    Nbrs.append((i-1, j, k+1))

    Nbrs.append((i, j+1, k+1))
    Nbrs.append((i, j-1, k-1))

    Nbrs.append((i, j+1, k-1))
    Nbrs.append((i, j-1, k+1))

    return Nbrs


def get_vox_neighborhood_ravel_index(i, j, k, imgdim, n=18):

    # i, j, k is a voxel index
    # n is the number of adjacent neighbors, default is 18
    Nbrs = np.zeros((n, ), dtype=np.int)

    Nbrs[0] = np.ravel_multi_index((i+1, j, k), imgdim)
    Nbrs[1] = np.ravel_multi_index((i-1, j, k), imgdim)

    Nbrs[2] = np.ravel_multi_index((i, j+1, k), imgdim)
    Nbrs[3] = np.ravel_multi_index((i, j-1, k), imgdim)

    Nbrs[4] = np.ravel_multi_index((i, j, k+1), imgdim)
    Nbrs[5] = np.ravel_multi_index((i, j, k-1), imgdim)

    Nbrs[6] = np.ravel_multi_index((i+1, j+1, k), imgdim)
    Nbrs[7] = np.ravel_multi_index((i-1, j-1, k), imgdim)

    Nbrs[8] = np.ravel_multi_index((i+1, j-1, k), imgdim)
    Nbrs[9] = np.ravel_multi_index((i-1, j+1, k), imgdim)

    Nbrs[10] = np.ravel_multi_index((i+1, j, k+1), imgdim)
    Nbrs[11] = np.ravel_multi_index((i-1, j, k-1), imgdim)

    Nbrs[12] = np.ravel_multi_index((i+1, j, k-1), imgdim)
    Nbrs[13] = np.ravel_multi_index((i-1, j, k+1), imgdim)

    Nbrs[14] = np.ravel_multi_index((i, j+1, k+1), imgdim)
    Nbrs[15] = np.ravel_multi_index((i, j-1, k-1), imgdim)

    Nbrs[16] = np.ravel_multi_index((i, j+1, k-1), imgdim)
    Nbrs[17] = np.ravel_multi_index((i, j-1, k+1), imgdim)

    return Nbrs


def roi_sphere_to_mask(roixml, template, mask, roi_num):

    nimg_template = NimgDataio.read_nifi_image_obj(template)
    mask_values = nimg_template.get_data()
    mask_values = np.zeros((1, mask_values.shape[0] * mask_values.shape[1] * mask_values.shape[2]))
    pixdim = np.asarray(nimg_template.get_header().get_zooms())

    doc = minidom.parse(roixml)
    roi_array = doc.getElementsByTagName("ROI")

    if roi_num > len(roi_array):
        raise IndexError('ROI number {0:d} exceeds the number of ROIs {0:d} present in the xml file\n'.
                         format(roi_num, len(roi_array)))

    center = np.array(roi_array[roi_num - 1].getAttribute('voxelposition').split(' ')).astype(np.float)
    center = center*pixdim  # Multiply by pixdim to account for voxel widths
    xc = center[0]; yc = center[1]; zc = center[2]
    radius = float(roi_array[roi_num - 1].getAttribute('radius_mm'))

    x = np.arange(0, nimg_template.shape[0])
    y = np.arange(0, nimg_template.shape[1])
    z = np.arange(0, nimg_template.shape[2])
    [xx, yy, zz] = np.meshgrid(x, y, z, indexing='ij')

    # Multiply by pixdim to account for voxel widths
    xx = np.ndarray.ravel(xx)*pixdim[0]
    yy = np.ndarray.ravel(yy)*pixdim[1]
    zz = np.ndarray.ravel(zz)*pixdim[2]

    # Find distances from all voxels to center
    # If distance > radius set mask value to zero, else set mask value to 1
    dist = (xx - xc) ** 2 + (yy - yc) ** 2 + (zz - zc) ** 2
    idx = np.where(dist <= radius**2)[0]
    mask_values[0, idx] = 1

    NimgDataio.write_nifti_image_from_array(mask, mask_values, nimg_template)

    return
