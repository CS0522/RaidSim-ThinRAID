'''
Author: Chen Shi
Date: 2023-11-27 16:31:32
Description: Raid class
'''


from common.cerror import Cerror
from src.disk import Disk
from src.node import Node


# 只模拟 raid5
class Raid:
    # constructor
    def __init__(self, block_size = 4096, chunk_size = 4096, num_disks = 4, 
                 raid_level = 5, raid5_type = 'LS', timing = False, 
                solve = True):
        self.print_physical = True
        # block size
        self.block_size = block_size
        # chunk size
        self.chunk_size = chunk_size // self.block_size
        # 当前磁盘个数
        self.num_disks = num_disks
        # raid level (only 5)
        self.raid_level = raid_level
        
        self.timing = timing
        self.solve = solve
        # raid-5 LS/LA
        self.raid5_type = raid5_type

        # Raid 中维护一张动态二维数组的表，用来存储数据块的一些信息
        # 存储数据块的热度、是否修改标志 等
        self.block_table = []


        if (chunk_size % self.block_size) != 0:
            Cerror(f'chunk 大小({self.chunk_size})必须是 block size ({self.block_size})的倍数: ({self.chunk_size % self.block_size})')
        
        # 只模拟 raid5
        if self.raid_level == 5:
            self.blocks_in_stripe = (self.num_disks - 1) * self.chunk_size
            self.parity_disk = -1

        # 添加磁盘
        self.disks = []
        for i in range(self.num_disks):
            self.disks.append(Disk())

        # 初始化 block table 
        self.init_block_table()


    '''
    name: init_block_table
    msg: 初始化 block table
    param {*} self
    return {*}
    '''
    def init_block_table(self):
        # 一个 disk 默认 100 个 track，每个 track 有 100 个 block
        # row, 100 * 100 行
        # TODO 需要修改
        for r in range(10000):
            b_list = []
            # col, num_disks 列
            for c in range(self.num_disks):
                b_node = Node(r, c)
                b_list.append(b_node)
            # 把每行的 b_list 添加到 block table
            self.block_table.append(b_list)
        # print
        # print(self.block_table)


    '''
    name: add_disks
    msg: 添加磁盘。注意，添加磁盘前需要执行一些操作，在 ReorgHandler 中
    param {*} self
    param {*} add_disk_num: 新增磁盘的个数
    return {*}
    '''    
    def add_disks(self, add_disk_num = 2):
        if (add_disk_num == 0):
            return
        self.num_disks += add_disk_num
        for i in range(add_disk_num):
            self.disks.append(Disk())


    '''
    name: del_disks
    msg: 删除磁盘。注意删除前需要执行一些操作，在 ReorgHandler 中
    param {*} self
    param {*} del_disk_num: 删除磁盘的个数
    return {*}
    '''    
    def del_disks(self, del_disk_num = 2):
        if (del_disk_num == 0):
            return
        if (del_disk_num >= self.num_disks):
            Cerror('the number of disks to be deleted needs to be smaller than current disks')
        # valid
        self.num_disks -= del_disk_num
        for i in range(del_disk_num):
            # 在此之前需要数据迁移
            # 在 ReorgHandler 中进行
            self.disks.pop()


    '''
    name: get_disk_stats
    msg: 获取磁盘的统计信息
    param {*} self
    param {*} total_time: 运行时间
    return {*}
    '''
    def get_disk_stats(self, total_time):
        for i in range(self.num_disks):
            stats = self.disks[i].get_stats()
            
            # res = (exp1) if (condition) else (exp2)
            util_ratio = (100.0 * float(stats[4]) / total_time) if total_time > 0.0 else 0.0

            print(f'磁盘{i}- 占用率: {util_ratio:3.2f}  I/Os: {stats[0]:5d} (顺序次数: {stats[1]} 同一个磁道: {stats[2]} 随机次数: {stats[3]})')


    '''
    name: enqueue
    msg: I/O 请求到来
    param {*} self
    param {*} addr: 逻辑地址
    param {*} size: 大小
    param {*} is_write: 是否写请求
    return {*}
    '''
    def enqueue(self, addr, size, is_write):
        # print logical operations
        if not self.timing:
            if self.solve:
                if is_write:
                    print(f'logical write addr: {addr} size: {size * self.block_size}')
                else:
                    print(f'logical read addr: {addr} size: {size * self.block_size}')
                if not self.solve:
                    print('logical read/write?')
            else:
                print('physical operation?')

        # print physical operations
        # 感觉不需要单独设置 print physical
        # if not self.timing and self.solve:
        #     self.print_physical = True
        # else:
        #     self.print_physical = False

        if self.raid_level == 5:
            # raid5 级别下处理 I/O 请求
            self.enqueue_raid5(addr, size, is_write)


    '''
    name: get_elapsed
    msg: return final completion time
    param {*} self
    return {*} t_max: 运行时间
    '''    
    def get_elapsed(self):
        t_max = 0.0
        for i in range(self.num_disks):
            t = self.disks[i].get_elapsed()
            if t > t_max:
                t_max = t
        return t_max
    
    '''
    name: single_io
    msg: 单个 I/O 请求发送到指定 disk 上
    param {*} self
    param {*} r_or_w: read - 'r', write - 'w'
    param {*} disk_index: 磁盘号
    param {*} offset: 偏移地址
    param {*} new_line: 打印时是否换行
    return {*}
    '''    
    def single_io(self, r_or_w, disk_index, offset, new_line = False):
        if self.print_physical:
            # write req
            if r_or_w == 'w':
                # 如果要写入的数据块是经过迁移的，修改 modified
                if (self.block_table[offset][disk_index].remap == True):
                    self.block_table[offset][disk_index].set_modified(True)
                print(f'write [disk {disk_index}, offset {offset}] ')
            # read req
            elif r_or_w == 'r':
                print(f'read [disk {disk_index}, offset {offset}] ')
            
            if new_line:
                print('')
        # I/O 请求发送到指定磁盘
        self.disks[disk_index].enqueue(offset)

    '''
    name: partial_write
    msg: 以一个条带中的多个块进行写
    param {*} self
    param {*} stripe: 第几个条带
    param {*} begin: 开始的 blocks 号
    param {*} end: 结束的 blocks 号
    param {*} block_map: 传入 block_mapping_raid5() 函数的生成器
    param {*} parity_map: 传入 parity_mapping_raid5() 函数的生成器
    return {*}
    '''
    def partial_write(self, stripe, begin, end, block_map, parity_map):
        # 写请求的块数
        num_writes = end - begin
        # 这里 parity_map 会传入一个函数生成器（理解为一个指向函数的对象）
        pdisk = parity_map(stripe)

        # TODO 搞清楚啥意思
        if (num_writes + 1) <= (self.blocks_in_stripe - num_writes):
            offList = []
            for voff in range(begin, end):
                (disk, off) = block_map(voff)
                # read - 'r', write - 'w'
                self.single_io('r', disk, off)
                if off not in offList:
                    offList.append(off)
            for i in range(len(offList)):
                # read - 'r', write - 'w'
                self.single_io('r', pdisk, offList[i], i == (len(offList) - 1))

        else:
            stripe_begin = stripe * self.blocks_in_stripe
            stripe_end = stripe_begin + self.blocks_in_stripe
            for voff in range(stripe_begin, begin):
                (disk, off) = block_map(voff)
                # read - 'r', write - 'w'
                self.single_io('r', disk, off, (voff == (begin - 1)) and (end == stripe_end))
            for voff in range(end, stripe_end):
                (disk, off) = block_map(voff)
                # read - 'r', write - 'w'
                self.single_io('r', disk, off, voff == (stripe_end - 1))

        # writes
        offList = []
        for voff in range(begin, end):
            (disk, off) = block_map(voff)
            # read - 'r', write - 'w'
            self.single_io('w', disk, off)
            if off not in offList:
                offList.append(off)
        for i in range(len(offList)):
            # read - 'r', write - 'w'
            self.single_io('w', pdisk, offList[i], i == (len(offList) - 1))

    '''
    name: mapping_raid5
    msg: 先定义一个函数，后面定义几个函数（功能基本相同）分别获取返回值；
         一个请求到来，对该请求的块号进行 mapping；
         私有
    param {*} self
    param {*} block_num: ？
    return {*} disk
    return {*} pdisk
    return {*} doff
    '''
    def __mapping_raid5(self, block_num):
        # TODO 搞清楚表示的啥意思
        cnum = block_num // self.chunk_size
        coff = block_num % self.chunk_size
        ddsk = cnum // (self.num_disks - 1)
        doff = (ddsk * self.chunk_size) + coff
        disk = cnum % (self.num_disks - 1)
        col = (ddsk % self.num_disks)
        pdisk = (self.num_disks - 1) - col

        if (self.raid5_type == 'LS'):
            disk = (disk - col) % self.num_disks
        elif (self.raid5_type == 'LA'):
            if disk >= pdisk:
                disk += 1
        else:
            Cerror('Error: no such RAID layout')
        
        assert(disk != pdisk)
        # 判断是否存在重新映射
        if (self.block_table[doff][disk].remap == True):
            # 需要重新映射到新的磁盘上
            remap_disk = self.block_table[doff][disk].remap_index['col']
            remap_doff = self.block_table[doff][disk].remap_index['row']
            return remap_disk, pdisk, remap_doff
        else:
            return disk, pdisk, doff
    

    def block_mapping_raid5(self, b_num):
        (disk, pdisk, doff) = self.__mapping_raid5(b_num)
        return disk, doff
    

    def parity_mapping_raid5(self, p_num):
        # TODO 这是什么意思
        (disk, pdisk, doff) = self.__mapping_raid5(p_num * self.blocks_in_stripe)
        return pdisk
    

    '''
    name: enqueue_raid5
    msg: raid5 级别的 I/O 请求处理
    param {*} addr: 地址
    param {*} size: 大小
    param {*} is_write: 是否写请求
    return {*}
    '''
    def enqueue_raid5(self, addr, size, is_write):
        if self.raid_level == 5:
            # 函数生成器，两个对象分别指向两个函数
            (block_map, parity_map) = (self.block_mapping_raid5, self.parity_mapping_raid5)

        # read req
        if not is_write:
            for b in range(addr, addr + size):
                (disk, off) = block_map(b)
                # read - 'r', write - 'w'
                self.single_io('r', disk, off)
        # write req
        # write 1 stripe at a time
        else:
            # 可能有多个 stripes
            begin_stripe = addr // self.blocks_in_stripe
            end_stripe = (addr + size - 1) // self.blocks_in_stripe

            # 剩余要写块数
            remain_blocks = size
            # 开始的块
            start_block = addr
            # 结束的块
            # 原先代码中无此行
            end_block = start_block + remain_blocks
            # 1 stripe at a time
            for curr_stripe in range(begin_stripe, end_stripe + 1):
                end_of_curr_stripe = (curr_stripe + 1) * self.blocks_in_stripe

                if (remain_blocks >= self.blocks_in_stripe):
                    end_block = start_block + self.blocks_in_stripe
                else:
                    end_block = start_block + remain_blocks

                if (end_block >= end_of_curr_stripe):
                    end_block = end_of_curr_stripe

                # partial write
                self.partial_write(curr_stripe, start_block, end_block, block_map, parity_map)

                remain_blocks -= (end_block - start_block)
                start_block = end_block
                # for loop end

        # for all cases, print this for pretty-ness in mapping mode
        if self.timing == False and self.print_physical:
            print('')

# end Raid class