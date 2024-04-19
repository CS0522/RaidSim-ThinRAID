'''
Author: Chen Shi
Date: 2023-12-06 00:51:22
Description: ReorgHandler class. Implement ThinRAID's ES Algorithm
'''

import copy
from src.block import Block
from src.raid import Raid

class ReorgHandler:
    def __init__(self, raid:Raid, adjust_disk_num, timestamp_interval):
        # a RAID instant
        # 直接对 raid 实例进行修改
        self.raid_instant = raid
        # the number of disks to be power on
        self.adjust_disk_num = abs(adjust_disk_num)
        # the number of current disks
        self.curr_disk_num = raid.num_disks
        # 当前时间间隔的时间戳
        self.timestamp_interval = timestamp_interval

        # 计算阈值 T
        self.threshold = self.cal_threshold()
        # Rank Array
        # self.ra = [[], [], [], [], [], [], [], [], [], []]
        # self.ra_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ra = []
        self.ra_values = []
        # TODO rank array 的分级数量要适当修改
        self.ra_num = 1000
        for i in range(self.ra_num):
            ls = []
            self.ra.append(ls)
            self.ra_values.append(0)
        # blocks queue that are prepared to migrate
        self.blocks_to_move = []


    '''
    name: cal_threshold
    msg: 计算阈值 T
    param {*} self
    return {*} threshold
    '''
    def cal_threshold(self):
        # 计算公式
        # T = ( sum{ Dj } / n + k ) * k
        disk_hots = []
        # init
        for i in range(self.curr_disk_num):
            disk_hots.append(0)
        # Dj
        # 10000 行
        for row in self.raid_instant.block_table:
            # 每列求 sum
            for col in range(self.curr_disk_num):
                disk_hots[col] += row[col].hot
        # disk_hots 得到每个磁盘的热度
        # sum{ Dj }
        disk_hots_sum = 0
        for i in range(self.curr_disk_num):
            disk_hots_sum += disk_hots[i]
        # calculate T
        # T = ( sum{ Dj } / n + k ) * k
        threshold = (disk_hots_sum * self.adjust_disk_num) / (self.curr_disk_num + self.adjust_disk_num)

        return threshold
    

    '''
    name: es_algorithm_add
    msg: 当磁盘增加时的数据迁移算法
    param {*} self
    return {*}
    '''
    def es_algorithm_add(self):
        # 1. 查找 Block Table，找到每个条带中热度最高的 k 个块
        # 2. 以热度为标准进行分级，归到相应 Rank Array 中
        # reverse = True，从大到小降序
        # row[0] ~ row[k - 1] 即为热度最高的 k 个块
        for row in self.raid_instant.block_table:
            row_sorted = sorted(row, key = lambda x:x.hot, reverse = True)
            # 这里 adjust_disk_num 可能会超过 curr_disk_num 大小导致越界
            for col in range(self.adjust_disk_num if (self.adjust_disk_num <= self.curr_disk_num) else self.curr_disk_num):
                # 如果条带的数据块 hot 值都是 0，不迁移这些数据块
                if (row_sorted[col].hot == 0):
                    continue
                block_temp1 = row_sorted[col]
                self.ra[block_temp1.hot // (self.ra_num)].append(block_temp1)
                self.ra_values[block_temp1.hot // (self.ra_num)] += block_temp1.hot
        # 3. 从高阶到低阶查找块，直到达到阈值 T
        block_hots_sum = 0
        curr_rank = self.ra_num - 1
        # 达到阈值标志
        found = False
        while (curr_rank >= 0 and block_hots_sum <= self.threshold):
            for block_temp2 in self.ra[curr_rank]:
                # 如果当前热度总和小于阈值
                if ((block_hots_sum + block_temp2.hot) <= self.threshold):
                    block_hots_sum += block_temp2.hot
                    self.blocks_to_move.append(block_temp2)
                # 如果当前热度总和大于阈值
                else:
                    found = True
                    break
            if (found == True):
                break
            # 一个 rank 的 block 都加入完后，查找下一阶
            curr_rank -= 1
        # 当前启动磁盘个数增加
        # self.curr_disk_num += self.adjust_disk_num
        self.raid_instant.add_disks(self.adjust_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks
        # 4. 迁移数据块
        # 创建一个 list 记录当前每个新加的磁盘上的偏移位置
        power_on_disk_offset = []
        for j in range(self.adjust_disk_num):
            power_on_disk_offset.append(0)
        # 用于顺序标记应放置到哪个新添加的磁盘
        block_count = 0
        for block_temp3 in self.blocks_to_move:
            # 按以下式子放到某个新添加的磁盘上
            col = (self.curr_disk_num - self.adjust_disk_num) + (block_count % self.adjust_disk_num)
            row = power_on_disk_offset[block_count % self.adjust_disk_num]
            power_on_disk_offset[block_count % self.adjust_disk_num] += 1 
            block_count += 1
            # 迁移数据块需要读写
            # 这里 block 的 data 标志位已置为 1
            self.raid_instant.single_io(self.timestamp_interval, 'w', col, row)
            # 深拷贝一份新的避免引用
            block_temp3_copy = copy.deepcopy(block_temp3)
            # 被迁移数据块的 remap 属性修改为 True，修改 remap index
            self.raid_instant.block_table[block_temp3.curr_index['row']][block_temp3.curr_index['col']].set_remap(True)
            self.raid_instant.block_table[block_temp3.curr_index['row']][block_temp3.curr_index['col']].set_remap_index(row, col)
            # 迁移到新磁盘上的数据块设置原数据块 old index
            block_temp3_copy.set_old_index(block_temp3.curr_index['row'], block_temp3.curr_index['col'])
            block_temp3_copy.has_old = True
            block_temp3_copy.set_curr_index(row, col)
            self.raid_instant.block_table[row][col] = block_temp3_copy
            # 这里确保 data = 1
            self.raid_instant.block_table[row][col].set_data(1)
                                                        
        # Raid 处理 io 请求的函数中判断是否需要重新映射
        # Raid 处理 io 请求的函数中，写请求写到 remap 的 block，修改其 modified 属性为 True
        

    '''
    name: workload_balance
    msg: 平衡磁盘的工作负载
    param {*} self
    return {*}
    '''
    def workload_balance(self):
        pass


    '''
    name: es_algorithm_del
    msg: 当磁盘关闭时的数据回迁
    param {*} self
    return {*}
    '''
    def es_algorithm_del(self):
        # 遍历新添加的磁盘上的数据块
        for row in range(self.raid_instant.blocks_per_disk):
            for col in range(self.curr_disk_num - self.adjust_disk_num, self.curr_disk_num):
                block_temp = self.raid_instant.block_table[row][col]
                # data = 0，没有数据
                if (block_temp.data == 0):
                    continue
                # 判断是否是迁移数据块
                if (block_temp.has_old == True):
                    # 如果 modified == True，重新执行一次 write request
                    if (self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].modified == True):
                        # write req
                        self.raid_instant.single_io(self.timestamp_interval, 'w', block_temp.old_index['col'], block_temp.old_index['row'])
                        # 修改原数据块
                        self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_modified(False)
                        self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_remap(False)
                        self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_remap_index(-1, -1)
                    # 如果 modified != True，直接用原数据块
                    else:
                        self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_remap(False)
                        self.raid_instant.block_table[block_temp.old_index['row']][block_temp.old_index['col']].set_remap_index(-1, -1)
                # 不是迁移数据块，而是新写入到新添加磁盘上的数据块
                else:
                    pass
                    # trace 工作负载中没有对新添加的磁盘进行写入和读取，所以新添加的磁盘上都是经过迁移的数据块
                # 清理 block_temp，新添加的磁盘上数据块恢复为初始
                block_temp.set_data(0)
                block_temp.set_hot(0)
                block_temp.set_modified(False)
                block_temp.set_remap(False)
                block_temp.set_remap_index(-1, -1)
                block_temp.set_has_old(False)
                block_temp.set_old_index(-1, -1)
        # 处理完成后，清空 blocks_to_move 列表
        self.blocks_to_move.clear()
        # 删除磁盘
        self.raid_instant.del_disks(self.adjust_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks