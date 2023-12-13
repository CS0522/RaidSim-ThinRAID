'''
Author: Chen Shi
Date: 2023-11-23 10:48:01
Description: main function
'''

import sys

from src.controller import Controller

# unit: ms; Byte
# default configs
seed            =   0
num_disks       =   4
block_size      =   4096
chunk_size      =   4096
num_reqs        =   20
req_size        =   4096
# 'rand' or 'seq'
workload        =   'rand'
# 0.0 ~ 1.0
write_frac      =   0.0
rand_range      =   20
raid_level      =   5
# 'LS' or 'LA'
raid5_type      =   'LS'
timing          =   False
solve           =   True


# Disk 的 track 数和 blocks_per_track 数
num_tracks      =   100
blocks_per_track=   100


# trace file path
trace_file  =   "./trace/hm_min.csv"


def main():
    save_stdout = sys.stdout
    sys.stdout = open("./output/res.txt", "w", encoding='utf-8')

    ctrl_ = Controller(seed, num_disks, block_size, chunk_size, num_reqs, req_size, workload,
                       write_frac, rand_range, raid_level, raid5_type, timing, solve)
    
    sys.stdout = save_stdout

    return

if __name__ == "__main__":
    main()