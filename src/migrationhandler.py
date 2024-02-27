'''
Author: Chen Shi
Date: 2024-02-26 10:46:49
Description: MigrationHandler class. Implement random migration between disks in conventional algorithm
'''


import copy
from src.block import Block
from src.raid import Raid

class MigrationHandler:
    def __init__(self, raid:Raid, power_on_disk_num, timestamp_interval):
        # a RAID instant
        # 直接对 raid 实例进行修改
        self.raid_instant = raid
        # the number of disks to be power on
        self.power_on_disk_num = abs(power_on_disk_num)
        # the number of current disks
        self.curr_disk_num = raid.num_disks
        # 当前时间戳（时间间隔）
        self.timestamp_interval = timestamp_interval


    '''
    name: random_add
    msg: 添加磁盘后随即迁移
    param {*} self
    return {*}
    '''
    def random_add(self):
        # 当前启动磁盘个数增加
        self.raid_instant.add_disks(self.power_on_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks
        # 迁移数据块
        # block table 添加 k 列
        for r in range(self.raid_instant.blocks_per_disk):
            for i in range(self.power_on_disk_num):
                new_block = Block(r, i + (self.curr_disk_num - self.power_on_disk_num))
                self.raid_instant.block_table[r].append(new_block)
        # 创建一个 list 记录当前每个新加的磁盘上的偏移位置
        # [0, 0, 0, ..., 0]
        power_on_disk_offset = []
        for i in range(self.power_on_disk_num):
            power_on_disk_offset.append(0)
        # 迁移 count_IO 次数最高的 k 个磁盘
        disks_count_IOs = {}
        for d in range(self.curr_disk_num - self.power_on_disk_num):
            disks_count_IOs[d] = self.raid_instant.disks[d].count_IO
        # 排序，取前 k 个待迁移磁盘号
        disks_count_IOs_sorted = sorted(disks_count_IOs.keys())
        migrate_disks_index = []
        for key in disks_count_IOs_sorted:
            migrate_disks_index.append(int(key))
            if (len(migrate_disks_index) >= self.power_on_disk_num):
                break
        # 迁移待迁移磁盘上一半的数据块到新磁盘上
        for r in range(self.raid_instant.blocks_per_disk // 2, self.raid_instant.blocks_per_disk):
            for c in migrate_disks_index:
                # 按以下式子放到某个新添加的磁盘上
                col = (self.curr_disk_num - self.power_on_disk_num) + (c % self.power_on_disk_num)
                row = copy.deepcopy(power_on_disk_offset[col - (self.curr_disk_num - self.power_on_disk_num)]) 
                power_on_disk_offset[col - (self.curr_disk_num - self.power_on_disk_num)] += 1 
                # 迁移数据块需要读写
                self.raid_instant.single_io(self.timestamp_interval, 'r', c, r)
                self.raid_instant.single_io(self.timestamp_interval, 'w', col, row)
                # 被迁移数据块的 remap 属性修改为 True，修改 remap index
                self.raid_instant.block_table[r][c].set_remap(True)
                self.raid_instant.block_table[r][c].set_remap_index(row, col)
                # 迁移到新磁盘上的数据块设置原数据块 old index
                self.raid_instant.block_table[row][col].set_old_index(r, c)
                self.raid_instant.block_table[row][col].has_old = True
                self.raid_instant.block_table[row][col].set_curr_index(row, col)

    
    '''
    name: random_del
    msg: 删除磁盘后全部迁移
    param {*} self
    return {*}
    '''
    def random_del(self):
        # 遍历新添加的磁盘上的数据块
        for row in range(self.raid_instant.blocks_per_disk):
            for col in range(self.curr_disk_num - self.power_on_disk_num, self.curr_disk_num):
                block_temp = self.raid_instant.block_table[row][col]
                # 判断是否是迁移数据块
                if (block_temp.has_old == True):
                    # write req
                    self.raid_instant.single_io(self.timestamp_interval, 'w', block_temp.old_index['col'], block_temp.old_index['row'])
                    # 修改原数据块
                    self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_modified(False)
                    self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_remap(False)
                    self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_remap_index(-1, -1)
                # 不是迁移数据块，而是新写入到新添加磁盘上的数据块
                else:
                    pass
                    # trace 工作负载中没有对新添加的磁盘进行写入和读取，所以新添加的磁盘上都是经过迁移的数据块
        # 删除磁盘
        self.raid_instant.del_disks(self.power_on_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks