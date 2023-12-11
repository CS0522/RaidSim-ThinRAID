'''
Author: Chen Shi
Date: 2023-12-06 00:51:22
Description: ReorgHandler class. Implement ThinRAID's ES Algorithm
'''

# TODO 数据块热度暂时使用 random

class ReorgHandler:
    def __init__(self, raid, power_on_disk_num):
        # a RAID instant
        self.raid_instant = raid
        # the number of disks to be power on
        self.power_on_disk_num = power_on_disk_num
        # 