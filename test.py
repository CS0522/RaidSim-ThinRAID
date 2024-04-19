'''
Author: Chen Shi
Date: 2023-12-11 10:32:25
Description: test
'''

import copy

# 用来放在 block table 中存储 block 的一些信息
class Block:
    def __init__(self, curr_row, curr_col):
        # data 标志位
        # 0, 1
        self.data = 0
        # 热度值
        self.hot = 0
        # 修改标志位
        self.modified = False
        # 是否重新映射
        self.remap = False
        self.curr_index = {'row': curr_row, 'col': curr_col}
        # 新的映射到 block table 的位置
        self.remap_index = {'row': -1, 'col': -1}
        # 是否是被映射的（是否具有原数据块）
        self.has_old = False
        # 如果重新映射，原先的 index
        self.old_index = {'row': -1, 'col': -1}

    # 重写比较函数，lt 是计算 < 符号时
    def __lt__(self, other):
        if (self.hot < other.hot):
            return True
        else:
            return False

    def set_data(self, new_val):
        self.data = new_val

    def set_hot(self, new_val):
        self.hot = new_val

    def set_modified(self, new_val):
        self.modified = new_val

    def set_remap(self, new_val):
        self.remap = new_val

    def set_curr_index(self, curr_row, curr_col):
        self.curr_index['row'] = curr_row
        self.curr_index['col'] = curr_col

    def set_remap_index(self, new_row, new_col):
        self.remap_index['row'] = new_row
        self.remap_index['col'] = new_col

    def set_has_old(self, new_val):
        self.has_old = new_val

    def set_old_index(self, old_row, old_col):
        self.old_index['row'] = old_row
        self.old_index['col'] = old_col


# 模拟测试下 reorghandler
num_disks = 4
power_on_disk_num = 2
stripe_num = 10

ra = []
ra_values = []
ra_num = 10
for i in range(ra_num):
    ls = []
    ra.append(ls)
    ra_values.append(0)

blocks_to_move = []

block_table = []

# 初始化 block_table
def init_block_table():
        for s in range(stripe_num):
            b_list = []
            for d in range(num_disks + power_on_disk_num):
                new_block = Block(s, d)
                if (d < num_disks):
                    new_block.set_data(1)
                b_list.append(new_block)
            block_table.append(b_list)

# print block_table
def print_block_table(mode:str):
    if (mode == "all"):
        """
        (cur_row, cur_col), hot, data, remap, (remap_row, remap_col), has_old, (old_row, old_col)
        """
        print("block_table all info: ")
        for s in range(stripe_num):
            for d in range(num_disks + power_on_disk_num):
                print(f'[cur_index:({block_table[s][d].curr_index["row"]}, {block_table[s][d].curr_index["col"]}), hot:{block_table[s][d].hot}, data:{block_table[s][d].data}, remap:{block_table[s][d].remap}, remap_index:({block_table[s][d].remap_index["row"]}, {block_table[s][d].remap_index["col"]}), has_old:{block_table[s][d].has_old}, old_index:({block_table[s][d].old_index["row"]}, {block_table[s][d].old_index["col"]})]')
            print('')

    elif (mode == "hots"):
        print("block_table hots: ")
        for s in range(stripe_num):
            for d in range(num_disks + power_on_disk_num):
                print(' {:>2d}'.format(block_table[s][d].hot), end = ' ')
            print('')

    elif (mode == "remap"):
        """
        (cur_row, cur_col), hot, remap, (remap_row, remap_col)
        """
        print("block_table remap: ")
        for s in range(stripe_num):
            for d in range(num_disks + power_on_disk_num):
                if (block_table[s][d].remap == True):
                    print(f'[({block_table[s][d].curr_index["row"]}, {block_table[s][d].curr_index["col"]}), {block_table[s][d].hot}, {block_table[s][d].remap}, ({block_table[s][d].remap_index["row"]}, {block_table[s][d].remap_index["col"]})]', end = ' ')
            print('')

# set hots
def set_hots():
    block_table[0][0].hot = 40
    block_table[0][1].hot = 10
    block_table[0][2].hot = 2
    block_table[0][3].hot = 3
    block_table[1][0].hot = 7
    block_table[1][1].hot = 21
    block_table[1][2].hot = 9
    block_table[1][3].hot = 10
    block_table[2][0].hot = 14
    block_table[2][1].hot = 15
    block_table[2][2].hot = 16
    block_table[2][3].hot = 36
    block_table[3][0].hot = 7
    block_table[3][1].hot = 22
    block_table[3][2].hot = 23
    block_table[3][3].hot = 24
    block_table[4][0].hot = 28
    block_table[4][1].hot = 33
    block_table[4][2].hot = 30
    block_table[4][3].hot = 31
    block_table[5][0].hot = 8
    block_table[5][1].hot = 36
    block_table[5][2].hot = 38
    block_table[5][3].hot = 37
    block_table[6][0].hot = 4
    block_table[6][1].hot = 39
    block_table[6][2].hot = 14
    block_table[6][3].hot = 42
    block_table[7][0].hot = 28
    block_table[7][1].hot = 30
    block_table[7][2].hot = 18
    block_table[7][3].hot = 5
    block_table[8][0].hot = 17
    block_table[8][1].hot = 29
    block_table[8][2].hot = 35
    block_table[8][3].hot = 1
    block_table[9][0].hot = 24
    block_table[9][1].hot = 35
    block_table[9][2].hot = 34
    block_table[9][3].hot = 11

# calculate threshold
def cal_threshold():
        # 计算公式
        # T = ( sum{Dj} / n + k ) * k
        disk_hots = []
        # init
        for i in range(num_disks):
            disk_hots.append(0)
        # Dj
        # 10000 行
        for row in block_table:
            # 每列求 sum
            for col in range(num_disks):
                disk_hots[col] += row[col].hot
        # disk_hots 得到每个磁盘的热度
        # sum{Dj}
        disk_hots_sum = 0
        for i in range(num_disks): 
            disk_hots_sum += disk_hots[i]
        # calculate T
        # T = ( sum{Dj} / n + k ) * k
        threshold = (disk_hots_sum * power_on_disk_num) / (num_disks + power_on_disk_num)

        return threshold

# es add algorithm
def algorithm_add(threshold):
    global num_disks
    global power_on_disk_num
    global block_table
    global ra
    global ra_num
    global ra_values
    # 1. search top-k blocks of each stripe
    # 2. classify these blocks
    for row in block_table:
            row_sorted = sorted(row, key = lambda x:x.hot, reverse = True)
            # 这里 power_on_disk_num 可能会超过 curr_disk_num 大小导致越界
            for col in range(power_on_disk_num if (power_on_disk_num <= num_disks) else num_disks):
                # 如果条带的数据块 hot 值都是 0，不迁移这些数据块
                if (row_sorted[col].hot == 0):
                    continue
                block_temp1 = row_sorted[col]
                ra[block_temp1.hot // (ra_num)].append(block_temp1)
                ra_values[block_temp1.hot // (ra_num)] += block_temp1.hot
    # print RA
    print("rank array: ")
    for l in range(len(ra)):
        print(f'ra{l}: ', end = '')
        for l1 in range(len(ra[l])):
            print(ra[l][l1].hot, end = ' ')
        print('')
    print('')

    # 3. from high index to low index, until the sum exceed T
    block_hots_sum = 0
    curr_rank = ra_num - 1
    found = False
    while (curr_rank >= 0 and block_hots_sum <= threshold):
            for block_temp2 in ra[curr_rank]:
                # 如果当前热度总和小于阈值
                if ((block_hots_sum + block_temp2.hot) <= threshold):
                    block_hots_sum += block_temp2.hot
                    blocks_to_move.append(block_temp2)
                # 如果当前热度总和大于阈值
                else:
                    found = True
                    break
            # 找到了，退出循环
            if (found == True):
                break
            # 一个 rank 的 block 都加入完后，查找下一阶
            curr_rank -= 1
    # 打印 blocks_to_move
    print("blocks_to_move: ")
    for l in range(len(blocks_to_move)):
        print(blocks_to_move[l].hot, end = ' ')
    print('\n')

    curr_disk_num = num_disks + power_on_disk_num
    # 4. migrate the blocks
    # 创建一个 list 记录当前每个新加的磁盘上的偏移位置
    # [0, 0, 0, ..., 0]
    power_on_disk_offset = []
    for j in range(power_on_disk_num):
        power_on_disk_offset.append(0)
    # 用于顺序标记应放置到哪个新添加的磁盘
    block_count = 0
    for block_temp3 in blocks_to_move:
        # randint() 左右都闭区间
        # col = random.randint(self.curr_disk_num - self.power_on_disk_num, self.curr_disk_num - 1)
        # 按以下式子放到某个新添加的磁盘上
        col = (curr_disk_num - power_on_disk_num) + (block_count % power_on_disk_num)
        row = power_on_disk_offset[block_count % power_on_disk_num]
        power_on_disk_offset[block_count % power_on_disk_num] += 1
        block_count += 1
        # 迁移数据块需要读写
        # self.raid_instant.single_io(self.timestamp_interval, 'r', block_temp3.curr_index['col'], block_temp3.curr_index['row'])
        # 这里 block 的 data 标志位已置为 1
        # self.raid_instant.single_io(self.timestamp_interval, 'w', col, row)
        # copy 一份新的避免引用
        block_temp3_copy = copy.deepcopy(block_temp3)
        # 被迁移数据块的 remap 属性修改为 True，修改 remap index
        block_table[block_temp3.curr_index['row']][block_temp3.curr_index['col']].set_remap(True)
        block_table[block_temp3.curr_index['row']][block_temp3.curr_index['col']].set_remap_index(row, col)
        # print_block_table("all")
        # 迁移到新磁盘上的数据块设置原数据块 old index
        block_temp3_copy.set_old_index(block_temp3.curr_index['row'], block_temp3.curr_index['col'])
        block_temp3_copy.has_old = True
        block_temp3_copy.set_curr_index(row, col)
        block_table[row][col] = block_temp3_copy
        # 这里确保 data = 1
        block_table[row][col].set_data(1)


if __name__ == "__main__":
    # init_block_table()
    # set_hots()
    # print('')
    # print_block_table("hots")
    # threshold = cal_threshold()
    # print('')
    # print("threshold:", threshold)
    # print('')
    # algorithm_add(threshold)
    # print_block_table("all")
    
    str1 = './trace/hm_1.csv'
    str2 = '/'.join([str1.split('/')[0], str1.split('/')[1], 
                     '.'.join([str1.split('/')[2].split('.')[0] + '_processed', str1.split('/')[2].split('.')[1]])])
    print(str2)
