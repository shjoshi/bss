[BrainSuite] (c) 2016 Statistics Toolbox (bss)
=========


The [BrainSuite] (c) statistics toolbox allows the application of advanced statistical models to surface, image and curve based outputs generated from BrainSuite. This enables population or group modeling of cortical or sulcal morphology. Some features of the toolbox are:

  - a python interface for using [statsmodels] with [pandas] for a pure python implementation
  - Ability to plot graphs, charts and visualizations on surfaces (coming soon)

T1-weighted MRI image processing and registration steps include cortical surface extraction
and alignment to a reference atlas using [SVReg], which performs surface-constrained volume registration of triangular meshes and image intensities.
BSS is then used to perform population level statistical analysis of various neuroimaging measures.



Features
----
* Volumetric TBM: voxel-wise analysis of the magnitude of the 3D deformation fields representing volumetric shrinking and expansions of MRI images in the atlas space.
* Surface TBM: vertex-wise analysis of the magnitude of the 3D deformation fields representing shrinking and expansions of cortical surfaces in the atlas space.
* ROI-based analysis: analysis of average gray matter thickness, surface area, and gray matter volume over a cortical ROI.
* Masking for hypothesis-driven testing: focal analysis of vertex-wise brain measures masked over an ROI based on a priori hypotheses.
* Deformation-based morphometry for diffusion images: voxel-wise analysis of quantitative diffusion characteristics (e.g., fractional anisotropy, mean diffusivity, radial diffusivity) resampled to a common atlas space using SVReg.

For the above analysis methods, BSS provides functions to fit linear regression models, ANOVA and hypothesis testing on the measures described above. Additionally, it enables testing interaction effects of different variables on brain imaging measures. In addition to testing for multiple comparison using the false discovery rate, BSS now supports permutation testing for multiple hypothesis testing.


Installation
----
Open a command line terminal and type  ``pip install bss``.

Full souce code is available at [github.org/shjoshi/bss].

Dependencies
-----------
The ``pip install bss`` command should install the dependencies.
* [Python] 2.7
* [pandas], [statsmodels], [nibabel], [matplotlib]

Installation tips
-----------
We recommend installing bss in a virtual environment.
See [virtualenv], [conda] etc.

For those who do not have Python installed, we recommend [miniconda].
Install [miniconda] and then run ``pip install bss`` on the command line.


Installation tips
-----------
For usage, please refer to the [tutorials].


License
----

GNU [General Public License] v2.

[BrainSuite]:http://brainsuite.org
[python]:http://www.python.org
[Canopy]:https://www.enthought.com/products/canopy/
[statsmodels]:http://statsmodels.sourceforge.net
[pandas]:http://pandas.pydata.org
[github.org/shjoshi/bss]:https://github.org/shjoshi/bss
[nibabel]: http://nipy.org/nibabel/
[matplotlib]: http://matplotlib.org/
[virtualenv]: https://virtualenv.pypa.io/en/stable/
[conda]: http://conda.pydata.org/docs/using/envs.html
[miniconda]: http://conda.pydata.org/miniconda.html
[tutorials]: http://brainsuite.org/bsstutorials/
[General Public License]: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
[SVReg]: http://brainsuite.org/processing/svreg/
