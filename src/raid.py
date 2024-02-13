'''
Author: Chen Shi
Date: 2023-11-27 16:31:32
Description: Raid class
'''


from common.cerror import Cerror
from src.disk import Disk
from src.node import Node
from src.config import Config


# 只模拟 raid5
class Raid:
    # constructor
    def __init__(self, config:Config):
        self.print_physical = config.get_print_physcial()
        # block size
        self.block_size = config.get_block_size()
        # chunk size
        self.chunk_size = config.get_chunk_size()
        if (self.chunk_size % self.block_size) != 0:
            Cerror(f'chunk 大小({self.chunk_size})必须是 block size ({self.block_size})的倍数: ({self.chunk_size % self.block_size})')
        self.chunk_size = self.chunk_size // self.block_size
        # 当前磁盘个数（初始磁盘个数）
        self.num_disks = config.get_num_disks()
        # 最大磁盘个数
        self.max_disks = config.get_max_disks()
        # raid level (only 5)
        self.raid_level = config.get_raid_level()
        
        self.timing = config.get_timing()
        self.solve = config.get_solve()
        # raid-5 LS/LA
        self.raid5_type = config.get_raid5_type()

        self.num_tracks = config.get_num_tracks()
        self.blocks_per_track = config.get_blocks_per_track()
        self.blocks_per_disk = self.num_tracks * self.blocks_per_track

        # Raid 中维护一张动态二维数组的表，用来存储数据块的一些信息
        # 存储数据块的热度、是否修改标志 等
        self.block_table = []
        
        # 只模拟 raid5
        if self.raid_level == 5:
            self.blocks_in_stripe = (self.num_disks - 1) * self.chunk_size
            self.parity_disk = -1

        # 添加磁盘
        self.disks = []
        for i in range(self.max_disks):
            self.disks.append(Disk(config))

        # 初始化 block table 
        self.init_block_table()

    
    '''
    name: init_disks
    msg: 根据 trace 设置磁盘的初始时间点
    param {*} self
    param {*} timestamp: 时间戳
    param {*} start_disk_index: 要初始化的起始磁盘号
    param {*} init_disks_num: 要初始化的磁盘数
    return {*}
    '''
    def init_disks(self, timestamp, start_disk_index, init_disks_num):
        for i in range(start_disk_index, init_disks_num + start_disk_index):
            self.disks[i].init_disk(timestamp)

    '''
    name: end_disks
    msg: 关闭磁盘，结束状态统计
    param {*} self
    param {*} timestamp: 时间戳
    param {*} start_disk_index: 要关闭的起始磁盘号
    param {*} end_disks_num: 要关闭的磁盘数
    return {*}
    '''
    def end_disks(self, timestamp, start_disk_index, end_disks_num):
        for i in range(start_disk_index, end_disks_num + start_disk_index):
            self.disks[i].end_disk(timestamp)


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
        for r in range(self.blocks_per_disk):
            b_list = []
            # col, num_disks 列
            for c in range(self.num_disks):
                b_node = Node(r, c)
                b_list.append(b_node)
            # 把每行的 b_list 添加到 block table
            self.block_table.append(b_list)
            

    '''
    name: print_block_table
    msg: 打印 block table
    param {*} self
    return {*}
    '''
    def print_block_table(self, interval_num):
        with open('./output/block_table.txt', 'a+') as res_file:
            title = []
            for i in range(self.num_disks):
                title.append('Disk' + str(i) + '  ')
            res_file.writelines("Interval " + str(interval_num) + ":\n")
            title.append('\n')
            res_file.writelines(title)
            # 只打印前 100 行
            for i in range(len(self.block_table)):
                if (i >= 100):
                    break
                write_row = []
                for c in self.block_table[i]:
                    node_info = ''
                    if (c.remap == True):
                        node_info = str('([' + str(c.curr_index['row']) + ', ' + str(c.curr_index['col']) 
                        + '], [' + str(c.remap_index['row']) + ', ' + str(c.remap_index['col']) + '])  ')
                    else:
                        node_info = str('([' + str(c.curr_index['row']) + ', ' + str(c.curr_index['col']) 
                        + '], False)  ')
                    write_row.append(node_info)
                write_row.append('\n')
                res_file.writelines(write_row)
            res_file.writelines('\n')
            res_file.writelines('==========')
            res_file.writelines('\n')


    '''
    name: add_disks
    msg: 添加磁盘。注意，添加磁盘前需要执行一些操作，在 ReorgHandler 中
    param {*} self
    param {*} add_disk_num: 新增磁盘的个数
    param {*} timestamp: 添加磁盘的时间戳
    return {*}
    '''    
    def add_disks(self, add_disk_num, timestamp):
        if (add_disk_num == 0):
            return
        # for i in range(add_disk_num):
        #     self.disks.append(Disk())
        # 初始化刚开始未启动的磁盘
        self.init_disks(timestamp, self.num_disks, add_disk_num)
        # 设置这些磁盘的 latest_req_timestamp
        # for d in range(self.num_disks, self.num_disks + add_disk_num):
        #     self.disks[d].update_latest_req_timestamp(timestamp)
        # print
        for i in range(self.num_disks, self.num_disks + add_disk_num):
            print('启动磁盘', i)
        print('')
        # 修改当前磁盘数量
        self.num_disks += add_disk_num
            


    '''
    name: del_disks
    msg: 删除磁盘。注意删除前需要执行一些操作，在 ReorgHandler 中
    param {*} self
    param {*} del_disk_num: 删除磁盘的个数
    return {*}
    '''    
    def del_disks(self, del_disk_num, timestamp):
        if (del_disk_num == 0):
            return
        if (del_disk_num >= self.num_disks):
            Cerror('the number of disks to be deleted needs to be smaller than current disks')
        # valid
        # for i in range(del_disk_num):
        #     # 在此之前需要数据迁移
        #     # 在 ReorgHandler 中进行
        #     self.disks.pop()
        # 关闭磁盘
        # self.end_disks(timestamp, self.num_disks - del_disk_num, del_disk_num)
        for d in range(self.num_disks - del_disk_num, self.num_disks):
            self.disks[i].hibernate_disk(timestamp)
        # print
        for i in range(self.num_disks - del_disk_num, self.num_disks):
            print('关闭磁盘', i)
        print('')
        # 修改当前磁盘数量
        self.num_disks -= del_disk_num


    '''
    name: get_disk_stats
    msg: 获取磁盘的统计信息
    param {*} self
    param {*} total_time: 运行时间
    param {*} timestamp_interval: 当前的间隔时间戳
    return {*}
    '''
    def get_disk_stats(self, total_time, timestamp_interval):
        # 获取磁盘 IO 信息统计
        print("当前时间戳:", timestamp_interval)
        print("当前启用磁盘数:", self.num_disks)
        print('')
        print("磁盘 I/O 信息统计:")
        for i in range(self.max_disks):
            io_stats = self.disks[i].get_io_stats()
            util_ratio = (100.0 * float(io_stats[4]) / total_time) if total_time > 0.0 else 0.0
            print(f'磁盘{i}- 占用率: {util_ratio:3.2f}  I/Os: {io_stats[0]:5d} (顺序次数: {io_stats[1]} 同一个磁道: {io_stats[2]} 随机次数: {io_stats[3]})')

        print('')
        print("磁盘状态信息统计:")

        # 获取磁盘休眠时间统计
        for i in range(self.max_disks):
            status_stats = self.disks[i].get_status_stats()
            print(f'磁盘{i}- 当前状态: {"活跃" if (status_stats[0] == True) else "休眠"}')
            print("休眠总时长:", status_stats[1] if ((status_stats[0] == True) or (self.disks[i].sleep_timestamp == 0)) else (status_stats[1] + timestamp_interval - self.disks[i].sleep_timestamp))
            # print("休眠总时长:", status_stats[1])
            print("休眠时间点:", status_stats[2])
            print("休眠段时长:", status_stats[3])
            print("磁盘关闭次数:", len(status_stats[2]))
            print("活跃总时长:", status_stats[4] if (status_stats[0] == False) else (status_stats[4] + timestamp_interval - self.disks[i].active_timestamp))
            # print("活跃总时长:", status_stats[4])
            print("活跃时间点:", status_stats[5])
            print("活跃段时长:", status_stats[6])
            print("磁盘启动次数:", len(status_stats[5]))
            print('')

    
    # reqs 都发送完毕后最终磁盘信息统计
    def get_final_disk_stats(self, total_time, timestamp_interval):
        # 获取磁盘 IO 信息统计
        print("当前时间戳:", timestamp_interval)
        print('')
        print("磁盘 I/O 信息统计:")
        for i in range(self.max_disks):
            io_stats = self.disks[i].get_io_stats()
            util_ratio = (100.0 * float(io_stats[4]) / total_time) if total_time > 0.0 else 0.0
            print(f'磁盘{i}- 占用率: {util_ratio:3.2f}  I/Os: {io_stats[0]:5d} (顺序次数: {io_stats[1]} 同一个磁道: {io_stats[2]} 随机次数: {io_stats[3]})')

        print('')
        print("磁盘状态信息统计:")

        # 获取磁盘休眠时间统计
        for i in range(self.max_disks):
            status_stats = self.disks[i].get_status_stats()
            print(f'磁盘{i}- 当前状态: {"活跃" if (status_stats[0] == True) else "休眠"}')
            print("休眠总时长:", status_stats[1])
            print("休眠时间点:", status_stats[2])
            print("休眠段时长:", status_stats[3])
            print("磁盘关闭次数:", len(status_stats[2]))
            print("活跃总时长:", status_stats[4])
            print("活跃时间点:", status_stats[5])
            print("活跃段时长:", status_stats[6])
            print("磁盘启动次数:", len(status_stats[5]))
            print('')


    '''
    name: enqueue
    msg: io requests enqueue. 暂时未用
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
    param {*} timestamp: 时间戳
    param {*} r_or_w: read - 'r', write - 'w'
    param {*} disk_index: 磁盘号
    param {*} offset: 偏移地址
    param {*} new_line: 打印时是否换行
    return {*}
    '''    
    def single_io(self, timestamp, r_or_w, disk_index, offset, new_line = False):
        remap_disk = disk_index
        remap_off = offset
        # 判断是否存在重新映射
        if (self.block_table[offset][disk_index].remap == True):
            # 需要重新映射到新的磁盘上
            remap_disk = self.block_table[offset][disk_index].remap_index['col']
            remap_off = self.block_table[offset][disk_index].remap_index['row']
            if self.print_physical:
                print(f'重新映射: [{disk_index}, {offset}] -> [{remap_disk}, {remap_off}]')
        # write req
        if r_or_w == 'w':
            # 如果要写入的数据块是经过迁移的，修改 modified
            if (self.block_table[offset][disk_index].remap == True):
                self.block_table[offset][disk_index].set_modified(True)
            if self.print_physical:
                print(f'write [disk {disk_index}, offset {offset}] ')
        # read req
        elif r_or_w == 'r':
            if self.print_physical:
                print(f'read [disk {remap_disk}, offset {remap_off}] ')
        
        if new_line:
                print('')
        # I/O 请求发送到指定磁盘
        self.disks[remap_disk].enqueue(remap_off, timestamp)

    '''
    name: partial_write
    msg: 以一个条带中的多个块进行写
    param {*} self
    param {*} stripe: 第几个条带
    param {*} begin: 开始的 blocks 号
    param {*} end: 结束的 blocks 号
    param {*} block_map: 传入 block_mapping_raid5() 函数的生成器
    param {*} parity_map: 传入 parity_mapping_raid5() 函数的生成器
    param {*} timestamp: 时间戳
    return {*}
    '''
    def partial_write(self, stripe, begin, end, block_map, parity_map, timestamp):
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
                self.single_io(timestamp, 'r', disk, off)
                if off not in offList:
                    offList.append(off)
            for i in range(len(offList)):
                # read - 'r', write - 'w'
                self.single_io(timestamp, 'r', pdisk, offList[i], i == (len(offList) - 1))

        else:
            stripe_begin = stripe * self.blocks_in_stripe
            stripe_end = stripe_begin + self.blocks_in_stripe
            for voff in range(stripe_begin, begin):
                (disk, off) = block_map(voff)
                # read - 'r', write - 'w'
                self.single_io(timestamp, 'r', disk, off, (voff == (begin - 1)) and (end == stripe_end))
            for voff in range(end, stripe_end):
                (disk, off) = block_map(voff)
                # read - 'r', write - 'w'
                self.single_io(timestamp, 'r', disk, off, voff == (stripe_end - 1))

        # writes
        offList = []
        for voff in range(begin, end):
            (disk, off) = block_map(voff)
            # read - 'r', write - 'w'
            self.single_io(timestamp, 'w', disk, off)
            if off not in offList:
                offList.append(off)
        for i in range(len(offList)):
            # read - 'r', write - 'w'
            self.single_io(timestamp, 'w', pdisk, offList[i], i == (len(offList) - 1))

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
    def enqueue_raid5(self, addr, size, is_write, timestamp):
        if self.raid_level == 5:
            # 函数生成器，两个对象分别指向两个函数
            (block_map, parity_map) = (self.block_mapping_raid5, self.parity_mapping_raid5)

        # read req
        if not is_write:
            for b in range(addr, addr + size):
                (disk, off) = block_map(b)
                # read - 'r', write - 'w'
                self.single_io(timestamp, 'r', disk, off)
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


    '''
    name: check_disk_status
    msg: 检查该时间间隔内是否有磁盘休眠超时
    param {*} timestamp: 当前时间间隔的时间点
    return {*}
    '''
    def check_disk_status(self, timestamp_interval):
        for d in range(len(self.disks)):
            # 如果休眠超时
            # 刚开始 latest_req_timestamp == 0
            if (timestamp_interval - self.disks[d].latest_req_timestamp >= self.disks[d].sleep_timeout) and (self.disks[d].active == True):
                # 休眠磁盘
                self.disks[d].hibernate_disk(timestamp_interval)

# end Raid class