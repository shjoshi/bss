__author__ = 'sjoshi'

from shapestats import paired_t_test_shape

sample1 = '/Volumes/Users/sjoshi/Desktop/lh_DE_FS_hippo_edit_041413_Controls_T1_T2_only2.txt'
sample2 = '/Volumes/Users/sjoshi/Desktop/lh_DE_FS_hippo_edit_041413_Controls_T1_T2_only.txt'
sample1 = '/Volumes/Users/sjoshi/Desktop/stats/sample1.txt'
sample2 = '/Volumes/Users/sjoshi/Desktop/stats/sample2.txt'


output_shape = '/Volumes/Users/sjoshi/Desktop/lh_stat.dfs'
output_log = []

paired_t_test_shape.paired_t_test(sample1, sample2, output_shape, output_log)

