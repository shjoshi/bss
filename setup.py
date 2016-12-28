#! /usr/local/epd/bin/python
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
__copyright__ = "Copyright 2013, Shantanu H. Joshi Ahmanson-Lovelace Brain Mapping Center, \
                 University of California Los Angeles"
__email__ = "s.joshi@ucla.edu"
__credits__ = 'Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. ' \
              'Inspired by the stats package rshape by Roger P. Woods'


from setuptools import setup
base_dir = 'bss'
setup(
    name='bss',
    version='0.9.2',
    packages=['bss'],
    package_dir={'bss': base_dir, },
    test_suite='nose.collector',
    scripts=['bin/bss_run.py', 'bin/paired_t_test_shape.py', 'bin/bss_create_modelspec.py',
             'bin/bss_resample_surface_to_target.py', 'bin/bss_fdr.py', 'bin/bss_config.py', 'bin/bss_save_roi_mean.py',
             'bin/bss_mean_surface.py', 'bin/bss_save_roistats2csv.py', 'bin/bss_roi.py', 'bin/bss_ops.py',
             'bin/bss_prepare_data_for_cbm.py', 'bin/bss_prepare_data_for_tbm.py', 'bin/bss_export_data.py',
             'bin/bss_prepare_data_for_roi.py', 'bin/bss_write_pvalue_as_color.py', 'bin/bss_convert_surface.py',
             'bin/bss_append_swm_to_roistat.py', 'bin/bss_write_attrib_to_surface.py', 'bin/bss_image_to_shape.py',
             'bin/bss_roi_sphere_to_mask.py'
             ],
    package_data = {'bss': ['conf/*']},
    license='GPLv2',
    exclude_package_data={'': ['.gitignore', '.idea']},
    author='Shantanu H. Joshi, David Shattuck',
    author_email='s.joshi@ucla.edu, shattuck@ucla.edu',
    __credits__='Contributions and ideas: Shantanu H. Joshi, Roger P. Woods, David Shattuck. '
                'Inspired by the stats package rshape by Roger P. Woods',
    description='BrainSuite statistics toolbox',
    install_requires=[
        "patsy>=0.4",
        "scipy>=0.18",
        "numpy>=1.11",
        "pandas>=0.19",
        "statsmodels>=0.6.1",
        "nibabel>=2.1",
        "matplotlib>=1.5.3",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    keywords='BrainSuite statistics',
)
