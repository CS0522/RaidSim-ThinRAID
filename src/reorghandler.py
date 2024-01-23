'''
Author: Chen Shi
Date: 2023-12-06 00:51:22
Description: ReorgHandler class. Implement ThinRAID's ES Algorithm
'''

# TODO 数据块热度暂时使用 random

import copy
import random
from src.node import Node
from src.raid import Raid

class ReorgHandler:
    def __init__(self, raid:Raid, power_on_disk_num, hots):
        # a RAID instant
        # 直接对 raid 实例进行修改
        self.raid_instant = raid
        # the number of disks to be power on
        self.power_on_disk_num = power_on_disk_num
        # the number of current disks
        self.curr_disk_num = raid.num_disks
        # hots 为具有两列的二维 list
        # [DiskNumber, Offset]
        self.hots = hots

        # 设置数据块热度
        self.set_hot_blocks()
        # 计算阈值 T
        self.threshold = self.cal_threshold()
        # Chunk Popularity Table
        # 深拷贝，cpt 的修改不影响 block table
        self.cpt = copy.deepcopy(self.raid_instant.block_table)
        # Rank Array
        # [0~10, 10~20, 20~30, 30~40, 40~50, 50~60, 60~70, 70~80, 80~90, 90~100]
        self.ra = [[], [], [], [], [], [], [], [], [], []]
        self.ra_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # blocks queue that are prepared to migrate
        self.blocks_to_move = []

    
    '''
    name: set_hot_blocks
    msg: 设置磁盘块的热度值
    param {*} self
    return {*}
    '''
    def set_hot_blocks(self):
        for r in self.hots:
            # r[0] 是请求的磁盘，r[1]是该磁盘上的偏移地址
            # r[1] 作为 row，r[0] 作为 col
            # 该位置的数据块热度值 + 1
            self.raid_instant.block_table[r[1]][r[0]].hot += 1


    '''
    name: update_hot_blocks
    msg: 更新磁盘块的热度值
    param {*} self
    param {*} new_hots: new hots list
    return {*}
    '''
    def update_hot_blocks(self, new_hots):
        self.hots = new_hots
        self.set_hot_blocks()


    '''
    name: cal_threshold
    msg: 计算阈值 T
    param {*} self
    return {*} threshold
    '''
    def cal_threshold(self):
        # 计算公式
        # T = ( sum{Dj} / n + k ) * k
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
        # sum{Dj}
        disk_hots_sum = 0
        for i in range(self.curr_disk_num):
            disk_hots_sum += disk_hots[i]
        # calculate T
        # T = ( sum{Dj} / n + k ) * k
        threshold = (disk_hots_sum * self.power_on_disk_num) / (self.curr_disk_num + self.power_on_disk_num)

        return threshold
    

    '''
    name: es_algorithm_add
    msg: 当磁盘增加时的数据迁移算法
    param {*} self
    return {*}
    '''
    def es_algorithm_add(self):
        # 1. 查找 CPT 表，找到条带中热度最高的 k 个块
        # reverse = True，从大到小降序
        # row[0]~row[k - 1] 即为热度最高的 k 个块
        for row in self.cpt:
            row.sort(reverse = True, key = lambda x:x.hot)
        # 2. 以热度为标准进行分级，归到相应 Rank Array 中
        for row in self.cpt:
            # 这里 power_on_disk_num 可能会超过 curr_disk_num 大小导致越界
            for col in range(self.power_on_disk_num if (self.power_on_disk_num <= self.curr_disk_num) else self.curr_disk_num):
                node_temp = row[col]
                # TODO 10 -> 100
                self.ra[node_temp.hot // 100].append(node_temp)
                self.ra_values[node_temp.hot // 100] += node_temp.hot
        # 3. 从高阶到低阶查找块，直到达到阈值 T
        block_hots_sum = 0
        curr_rank = 9
        while (curr_rank >= 0 and block_hots_sum <= self.threshold):
            for node_temp in self.ra[curr_rank]:
                # 如果当前热度总和小于阈值
                if ((block_hots_sum + node_temp.hot) <= self.threshold):
                    block_hots_sum += node_temp.hot
                    self.blocks_to_move.append(node_temp)
                # 如果当前热度总和大于阈值
                else:
                    break
            # 一个 rank 的 block 都加入完后，查找下一阶
            curr_rank -= 1
        # 当前启动磁盘个数增加
        # self.curr_disk_num += self.power_on_disk_num
        self.raid_instant.add_disks(self.power_on_disk_num)
        self.curr_disk_num = self.raid_instant.num_disks
        # 4. 迁移数据块
        # block table 添加 k 列
        # for row in self.raid_instant.block_table:
        for r in range(10000):
            for i in range(self.power_on_disk_num):
                new_node = Node(r, i + (self.curr_disk_num - self.power_on_disk_num))
                self.raid_instant.block_table[r].append(new_node)
        # 被迁移数据块随机放在新添加的磁盘上
        # 创建一个 list 记录当前每个新加的磁盘上的偏移位置
        # [0, 0, 0, ..., 0]
        power_on_disk_offset = []
        for i in range(self.power_on_disk_num):
            power_on_disk_offset.append(0)
        for node_temp in self.blocks_to_move:
            # randint() 左右都闭区间
            # col = random.randint(self.curr_disk_num - self.power_on_disk_num, self.curr_disk_num - 1)
            # TODO 按以下式子放到某个新添加的磁盘上
            col = (self.curr_disk_num - self.power_on_disk_num) + (node_temp.curr_index['col'] % self.power_on_disk_num)
            # print("self.curr_disk_num", self.curr_disk_num)
            # print("self.power_on_disk_num", self.power_on_disk_num)
            # print("self.curr_disk_num - 1", self.curr_disk_num - 1)
            # print("col:", col)
            # print("power_on_disk_offset.length:", len(power_on_disk_offset))
            row = copy.deepcopy(power_on_disk_offset[col - (self.curr_disk_num - self.power_on_disk_num)]) 
            power_on_disk_offset[col - (self.curr_disk_num - self.power_on_disk_num)] += 1 
            # 被迁移数据块的 remap 属性修改为 True，修改 remap index
            self.raid_instant.block_table[node_temp.curr_index['row']][node_temp.curr_index['col']].set_remap(True)
            self.raid_instant.block_table[node_temp.curr_index['row']][node_temp.curr_index['col']].set_remap_index(row, col)
            # 迁移到新磁盘上的数据块设置原数据块 old index
            node_temp.set_old_index(node_temp.curr_index['row'], node_temp.curr_index['col'])
            node_temp.has_old = True
            node_temp.set_curr_index(row, col)
            self.raid_instant.block_table[row][col] = node_temp
                                                        
        # Raid 类处理 io 请求的函数中判断是否需要重新映射
        # Raid 类处理 io 请求的函数中，写请求写到 remap 的 block，修改 modified 属性为 True
        

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
        for row in range(10000):
            for col in range(self.curr_disk_num - self.power_on_disk_num, self.curr_disk_num):
                node_temp = self.raid_instant.block_table[row][col]
                # 判断是否是迁移数据块
                if (node_temp.has_old == True):
                    # 如果 modified == True，重新执行一次 write request
                    if (self.raid_instant.block_table[node_temp.old_index['row']][node_temp.old_index['col']].modified == True):
                        # write req
                        self.raid_instant.single_io('w', node_temp.old_index['col'], node_temp.old_index['row'])
                        # 修改原数据块
                        self.raid_instant.block_table[node_temp.old_index['row']][node_temp.old_index['col']].set_modified(False)
                        self.raid_instant.block_table[node_temp.old_index['row']][node_temp.old_index['col']].set_remap(False)
                        self.raid_instant.block_table[node_temp.old_index['row']][node_temp.old_index['col']].set_remap_index(-1, -1)
                    # 如果 modified != True，直接用原数据块
                    else:
                        self.raid_instant.block_table[node_temp.old_index['row']][node_temp.old_index['col']].set_remap(False)
                        self.raid_instant.block_table[node_temp.old_index['row']][node_temp.old_index['col']].set_remap_index(-1, -1)
                # 不是迁移数据块，而是新写入到新添加磁盘上的数据块
                else:
                    self.raid_instant.enqueue(int(random.random() * self.raid_instant.rand_range), 1, True)
        # 处理完成后，清空 blocks_to_move 列表
        self.blocks_to_move.clear()
        # 删除磁盘
        self.raid_instant.del_disks(self.power_on_disk_num)
        self.curr_disk_num = self.raid_instant.num_disks