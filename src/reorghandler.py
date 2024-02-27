'''
Author: Chen Shi
Date: 2023-12-06 00:51:22
Description: ReorgHandler class. Implement ThinRAID's ES Algorithm
'''


import copy
from src.block import Block
from src.raid import Raid

class ReorgHandler:
    def __init__(self, raid:Raid, power_on_disk_num, hots, timestamp_interval):
        # a RAID instant
        # 直接对 raid 实例进行修改
        self.raid_instant = raid
        # the number of disks to be power on
        self.power_on_disk_num = abs(power_on_disk_num)
        # the number of current disks
        self.curr_disk_num = raid.num_disks
        # hots 为具有两列的二维 list
        # [DiskNumber, Offset]
        self.hots = hots
        # 当前时间戳（时间间隔）
        self.timestamp_interval = timestamp_interval

        # 清空上个时间间隔的数据块热度
        self.clear_hot_blocks()
        # 设置数据块热度
        self.set_hot_blocks()
        # 计算阈值 T
        self.threshold = self.cal_threshold()
        # Chunk Popularity Table
        # 深拷贝，cpt 的修改不影响 block table
        self.cpt = copy.deepcopy(self.raid_instant.block_table)
        # Rank Array
        # [0~10, 10~20, 20~30, 30~40, 40~50, 50~60, 60~70, 70~80, 80~90, 90~100]
        # self.ra = [[], [], [], [], [], [], [], [], [], []]
        # self.ra_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ra = []
        self.ra_values = []
        # TODO rank array 的分级数量要适当修改
        self.ra_num = 10
        for i in range(self.ra_num):
            ls = []
            self.ra.append([])
        for i in range(self.ra_num):
            self.ra_values.append(0)
        # blocks queue that are prepared to migrate
        self.blocks_to_move = []


    '''
    name: clear_hot_blocks
    msg: 清空数据块的热度值
    param {*} self
    return {*}
    '''
    def clear_hot_blocks(self):
        for r in self.raid_instant.block_table:
            for c in r:
                c.hot = 0

    
    '''
    name: set_hot_blocks
    msg: 设置数据块的热度值
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
    name: print_hots
    msg: 打印 hots
    param {*} self
    return {*}
    '''
    def print_hots(self, interval_num):
        with open("./output/hots.txt", 'a+') as res_file:
            title = []
            for i in range(self.curr_disk_num):
                title.append('Disk' + str(i) + '  ')
            res_file.writelines("Interval " + str(interval_num) + ":\n")
            title.append('\n')
            res_file.writelines(title)
            # 只打印前 100 行
            for i in range(len(self.raid_instant.block_table)):
                if (i >= 1000):
                    break
                write_row = []
                for c in self.raid_instant.block_table[i]:
                    block_info = str('([' + str(c.curr_index['row']) + ', ' + str(c.curr_index['col']) + '], ' + str(c.hot) + ')  ')
                    write_row.append(block_info)
                write_row.append('\n')
                res_file.writelines(write_row)
            res_file.writelines('\n')
            res_file.writelines('==========')
            res_file.writelines('\n')


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
                # 如果条带的数据块 hot 值都是 0，不迁移这些数据块
                if (row[col].hot == 0):
                    continue
                block_temp = row[col]
                self.ra[block_temp.hot // (self.ra_num)].append(block_temp)
                self.ra_values[block_temp.hot // (self.ra_num)] += block_temp.hot
        # 3. 从高阶到低阶查找块，直到达到阈值 T
        block_hots_sum = 0
        curr_rank = self.ra_num - 1
        while (curr_rank >= 0 and block_hots_sum <= self.threshold):
            for block_temp in self.ra[curr_rank]:
                # 如果当前热度总和小于阈值
                if ((block_hots_sum + block_temp.hot) <= self.threshold):
                    block_hots_sum += block_temp.hot
                    self.blocks_to_move.append(block_temp)
                # 如果当前热度总和大于阈值
                else:
                    break
            # 一个 rank 的 block 都加入完后，查找下一阶
            curr_rank -= 1
        # 当前启动磁盘个数增加
        # self.curr_disk_num += self.power_on_disk_num
        self.raid_instant.add_disks(self.power_on_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks
        # 4. 迁移数据块
        # block table 添加 k 列
        # for row in self.raid_instant.block_table:
        for r in range(self.raid_instant.blocks_per_disk):
            for i in range(self.power_on_disk_num):
                new_block = Block(r, i + (self.curr_disk_num - self.power_on_disk_num))
                self.raid_instant.block_table[r].append(new_block)
        # 创建一个 list 记录当前每个新加的磁盘上的偏移位置
        # [0, 0, 0, ..., 0]
        power_on_disk_offset = []
        for i in range(self.power_on_disk_num):
            power_on_disk_offset.append(0)
        for block_temp in self.blocks_to_move:
            # randint() 左右都闭区间
            # col = random.randint(self.curr_disk_num - self.power_on_disk_num, self.curr_disk_num - 1)
            # 按以下式子放到某个新添加的磁盘上
            col = (self.curr_disk_num - self.power_on_disk_num) + (block_temp.curr_index['col'] % self.power_on_disk_num)
            row = copy.deepcopy(power_on_disk_offset[col - (self.curr_disk_num - self.power_on_disk_num)]) 
            power_on_disk_offset[col - (self.curr_disk_num - self.power_on_disk_num)] += 1 
            # 迁移数据块需要读写
            self.raid_instant.single_io(self.timestamp_interval, 'r', block_temp.curr_index['col'], block_temp.curr_index['row'])
            # 这里 block 的 data 标志位已置为 1
            self.raid_instant.single_io(self.timestamp_interval, 'w', col, row)
            # 被迁移数据块的 remap 属性修改为 True，修改 remap index
            self.raid_instant.block_table[block_temp.curr_index['row']][block_temp.curr_index['col']].set_remap(True)
            self.raid_instant.block_table[block_temp.curr_index['row']][block_temp.curr_index['col']].set_remap_index(row, col)
            # 迁移到新磁盘上的数据块设置原数据块 old index
            block_temp.set_old_index(block_temp.curr_index['row'], block_temp.curr_index['col'])
            block_temp.has_old = True
            block_temp.set_curr_index(row, col)
            self.raid_instant.block_table[row][col] = block_temp
            # 这里确保 data = 1
            self.raid_instant.block_table[row][col].set_data(1)
                                                        
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
        for row in range(self.raid_instant.blocks_per_disk):
            for col in range(self.curr_disk_num - self.power_on_disk_num, self.curr_disk_num):
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
        # 处理完成后，清空 blocks_to_move 列表
        self.blocks_to_move.clear()
        # 删除磁盘
        self.raid_instant.del_disks(self.power_on_disk_num, self.timestamp_interval)
        self.curr_disk_num = self.raid_instant.num_disks