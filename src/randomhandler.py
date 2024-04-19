'''
Author: Chen Shi
Date: 2024-02-26 10:46:49
Description: RandomHandler class. Implement random migration between disks in conventional algorithm
'''

import copy
from src.block import Block
from src.raid import Raid

class RandomHandler:
    def __init__(self, raid:Raid, adjust_disk_num, timestamp_interval):
        # a RAID instant
        # 直接对 raid 实例进行修改
        self.raid_instant = raid
        # the number of disks to be power on
        self.adjust_disk_num = abs(adjust_disk_num)
        # the number of current disks
        self.curr_disk_num = raid.num_disks
        # blocks per disk
        self.blocks_per_disks = self.raid_instant.blocks_per_disk
        # block table copy
        self.bt_cp = copy.deepcopy(self.raid_instant.block_table)
        # 当前时间戳（时间间隔）
        self.timestamp_interval = timestamp_interval
        # 待迁移数据块
        self.blocks_to_move = []


    '''
    name: random_add
    msg: 添加磁盘后随即迁移
    param {*} self
    return {*}
    '''
    def random_add(self):
        # 当前启动磁盘个数增加
        self.raid_instant.add_disks(self.adjust_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks
        # 创建一个 list 记录当前磁盘上的偏移位置
        # [0, 0, 0, ..., 0]
        disks_offset = []
        for i in range(self.curr_disk_num):
            disks_offset.append(0)

        # 随机迁移数据块
        block_count = 0
        for r in range(self.raid_instant.blocks_per_disk):
            for c in range(self.curr_disk_num):
                block_temp = self.raid_instant.block_table[r][c]
                # 没有数据不迁移
                # if (block_temp.data == 0):
                #     continue
                # 按以下式子随机迁移放到磁盘上
                col = block_count % self.curr_disk_num
                row = disks_offset[col]
                # 当前磁盘已满
                while (row >= self.blocks_per_disks):
                    col = (col + 1) % self.curr_disk_num
                    row = disks_offset[col] 
                disks_offset[col] = (disks_offset[col] + 1) % self.blocks_per_disks
                block_count += 1
                # 迁移数据块需要读写
                # self.raid_instant.single_io(self.timestamp_interval, 'r', block_temp.curr_index['col'], block_temp3.curr_index['row'])
                # 这里 block 的 data 标志位已置为 1
                self.raid_instant.single_io(self.timestamp_interval, 'w', col, row)
                # deepcopy 一份新的避免引用
                # block_temp_copy = copy.deepcopy(block_temp)
                # 被迁移数据块的 remap 属性修改为 True，修改 remap index
                self.raid_instant.block_table[block_temp.curr_index['row']][block_temp.curr_index['col']].set_remap(True)
                self.raid_instant.block_table[block_temp.curr_index['row']][block_temp.curr_index['col']].set_remap_index(row, col)
                self.raid_instant.block_table[block_temp.curr_index['row']][block_temp.curr_index['col']].set_data(0)
                # 这里确保 data = 1
                self.raid_instant.block_table[row][col].set_data(1)

    
    '''
    name: random_del
    msg: 删除磁盘后全部迁移
    param {*} self
    return {*}
    '''
    def random_del(self):
        # 创建一个 list 记录当前磁盘上的偏移位置
        # [0, 0, 0, ..., 0]
        disks_offset = []
        for i in range(self.curr_disk_num):
            disks_offset.append(0)
        # 遍历所有数据块，随机迁移
        block_count = 0
        for r in range(self.raid_instant.blocks_per_disk):
            for c in range(self.curr_disk_num):
                block_temp = self.raid_instant.block_table[r][c]
                # 没有数据不迁移
                # if (block_temp.data == 0):
                #     continue
                # 按以下式子放到磁盘上
                col = block_count % (self.curr_disk_num - self.adjust_disk_num)
                row = disks_offset[col]
                # 当前磁盘已满
                while (row >= self.blocks_per_disks):
                    col = (col + 1) % (self.curr_disk_num - self.adjust_disk_num)
                    row = disks_offset[col]
                disks_offset[col] = (disks_offset[col] + 1) % self.blocks_per_disks
                block_count += 1
                # 迁移数据块需要读写
                # self.raid_instant.single_io(self.timestamp_interval, 'r', block_temp.curr_index['col'], block_temp3.curr_index['row'])
                # 这里 block 的 data 标志位已置为 1
                # 校验块的计算省略，校验块重新写入的 io 包含在这里
                self.raid_instant.single_io(self.timestamp_interval, 'w', col, row)
                # 取消映射
                self.raid_instant.block_table[row][col].set_remap(False)
                self.raid_instant.block_table[row][col].set_remap_index(-1, -1)
                self.raid_instant.block_table[row][col].set_data(1)
        # 删除磁盘
        self.raid_instant.del_disks(self.adjust_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks