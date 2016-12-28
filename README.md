[BrainSuite] (c) 2016 Statistics Toolbox (bss)
=========
---------
The [BrainSuite] (c) statistics toolbox allows the application of advanced statistical models to surface, image and curve based outputs generated from BrainSuite. This enables population or group modeling of cortical or sulcal morphology. Some features of the toolbox are:

  - a python interface for using [statsmodels] with [pandas] for a pure python implementation
  - Ability to plot graphs, charts and visualizations on surfaces (coming soon)


Download
----

Currently download from https://bitbucket.org/bmapdev/bss/

Requirements (short version)
-----------
* [R] - built as a library with –enable-R-shlib (Default on Windows and Mac OSX)
* [Python] 2.7 
* Base Python packages - virtualenv, pip, numpy, scipy
> ##### **NOTE:** Alternately, install [Canopy] python. Makes life much easier.
* Add on Python packages - [pandas], [statsmodels]

Requirements (long version)
-----------
To stick to a pure python execution, one could skip installing R, and Rpy2. However, in our benchmarks, Rpy2+R currently shows the best performance. 

Thus, to get all the functionality of the toolbox, it is recommended to install the following software on your computer.

* Working [python] installation (We recommend version 2.7) -   
with the following packages:
    * virtualenv, pip, numpy, scipy  

> ##### **NOTE:** Alternately, you could download [Canopy] express, a comprehensive python framework geared towards scientifc computing, available for free.

* [R] - R software for statistical computing (built as a library with –enable-R-shlib)
    
    This is by default on Mac OSX and Windows. 
    
    On Linux, for e.g. in the root directory of the R source, one can do:

    ```sh
sudo ./configure  --enable-R-shlib  
sudo make  
sudo make install  
    ```


* [statsmodels] - pure python module for statistical inference and much more


Installation for Mac OSX/Linux - Approach 1
--------------
To be followed if all the requirements above are satisfied. 

It is recommended to create a virtual python environment in your BrainSuite directory.

For e.g., if your BrainSuite installation is located at /Applications/Brainsuite13a, and the
unzipped bss package is located at ~/bss-0.1dev, then open the terminal and type
```sh
virtualenv --system-site-packages /Applications/Brainsuite13a/bssenv
/Applications/Brainsuite13a/bssenv/bin/python ~/bss-0.1dev/setup.py install
```

Installation for Mac OSX/Linux  - Approach 2
--------------
>####**To be developed.**

Bootstrap everything. Start with a basic python installation

Create a virtualenv in the BrainSuite directory

Install all the packages in virtualenv

Install the bss package in virtualenv


Example for running ANOVA for model comparison
--------------
The source package includes a test directory with sample data. Assuming the unzipped source directory is located at: ~/bmapdev-bss, open the file
```sh
~/bmapdev-bss/bss/test/data/sample1/modelspec.ini
```
and change the respective paths for the variables
```sh
subjectdir, demographics, phenotype_attribute_matrix, atlas_surface
```
to correspond to the paths on your file system. 
Then type,

```sh
/Applications/Brainsuite13a/bssenv/bin/bss_model.py -modelspec
~/bmapdev-bss/bss/test/data/sample1/modelspec.ini -outdir ~/ -statsengine R
```
---
License
----

GPLv2

[BrainSuite]:http://brainsuite.org
[python]:http://www.python.org 
[Canopy]:https://www.enthought.com/products/canopy/
[statsmodels]:http://statsmodels.sourceforge.net
[pandas]:http://pandas.pydata.org