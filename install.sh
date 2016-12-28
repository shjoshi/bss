#!/usr/bin/env bash
# Install Script for BrainSuite statistical toolbox for Linux/MacOSX
# This file is a part of the BrainSuite statistical toolbox

#Copyright (C) Shantanu H. Joshi, Garrett Reynolds, David Shattuck,
#Brain Mapping Center, University of California Los Angeles

#Bss is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#Bss is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#
#__author__ = "Shantanu H. Joshi, Garrett Reynolds, Jonathan Pierce"
#__copyright__ = "Copyright 2014 Shantanu H. Joshi, Garrett Reynolds, Jonathan Pierce, David Shattuck,
#				  Ahmanson Lovelace Brain Mapping Center, University of California Los Angeles"
#__email__ = "sjoshi@bmap.ucla.edu"

message_if_failed() {
    #print out message and quit if last command failed
    if [ $? -ne 0 ]; then 
        echo -e >&2 $1
        exit 2
    fi
}
if [ $# -ne 1 ]
  then
    echo "usage: $0 <full path of the install directory>"
    echo "Install the BrainSuite Statistical toolbox in the specified directory."
    exit 0
fi

echo "This will install the BrainSuite Statistics toolbox. "
echo "This will also install a mini version of anaconda python, R, rpy2, and statsmodels."
# Check if curl exists
curl --help >> /dev/null
curl_exists=$?
if [ ${curl_exists} != 0 ]; then
    printf "\nThe program curl is not installed. Please install curl and retry installing the toolbox.\n"
    exit 0
fi

export bss_install_dir=$1
orig_dir=`pwd`
if [ -d "$bss_install_dir" ]; then
	echo "Directory $bss_install_dir exists. Aborting installation."
	exit 0
fi
mkdir "$bss_install_dir"
mkdir "$bss_install_dir"/"tmp"
if [[ `uname` == "Darw"* ]]; then bss_platform="MacOSX" ; else bss_platform="Linux" ; fi
curl -O https://repo.continuum.io/miniconda/Miniconda2-latest-${bss_platform}-x86_64.sh
bash Miniconda2-latest-${bss_platform}-x86_64.sh -b -f -p ${bss_install_dir}; rm Miniconda2-latest-${bss_platform}-x86_64.sh
${bss_install_dir}/bin/conda config --add channels r --add channels bss --add channels conda-forge
echo -n "Installing BrainSuite statistical toolbox...This may take a few minutes..." | tee -a ${bss_install_dir}/tmp/install.log
${bss_install_dir}/bin/conda install bss -y | tee -a ${bss_install_dir}/tmp/install.log
echo "install.packages('pander',  repos='http://cran.us.r-project.org')" | ${bss_install_dir}/bin/R --no-save
echo export PATH=${bss_install_dir}/bin/:\${PATH} | tee -a ~/.bashrc ~/.bash_profile; source ~/.bashrc; source ~/.bash_profile


printf "BrainSuite statistical toolbox was installed successfully.\n" | tee -a ${install_dir}/tmp/install.log
printf "Cleaning up temporary files..." | tee -a ${install_dir}/tmp/install.log
rm -r ${bss_install_dir}/pkgs/
rm -r ${bss_install_dir}/tmp/Miniconda2-${VER}-${platform}-x86_64.sh

printf "Done.\n\n" | tee -a ${bss_install_dir}/tmp/install.log


printf "Try running\n ${bss_install_dir}/bin/bss_run.py -h \n" | tee -a ${bss_install_dir}/tmp/install.log
printf "It should display help and then exit.\n\n\n" | tee -a ${bss_install_dir}/tmp/install.log

exit 0
