__author__ = 'CompAdmin2'

import sys

from bss.nii_io import readnii, writenii


# valid file path to read from and to write to
fread1 = './data/sample1/2467264.nii.gz'
fwrite1 = './data/sample1/2467264_copy.nii.gz'
img1 = readnii(fread1)
img1_copy = readnii(fread1)
writenii(fwrite1,img1)

# non-existent file path to load from, invalid type for image to write from
fread2 = './data/sample1/0000000.nii.gz'
fwrite2 = './data/sample1/0000000_copy.nii.gz'
img2 = readnii(fread2)
writenii(fwrite2,img2)
sys.stdout.write('\n')

# invalid file path to write to
fread3 = './data/sample1/2467264.nii.gz'
fwrite3 = './data/sample2/2467264_copy.nii.gz'
img3 = readnii(fread3)
writenii(fwrite3,img3)
sys.stdout.write('\n')

# invalid file type to read
fread4 = './data/sample1/lena.png'
fwrite4 = './data/sample1/lena_copy.png'
img4 = readnii(fread4)
