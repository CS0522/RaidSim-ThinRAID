'''
Author: Chen Shi
Date: 2023-11-29 23:11:49
Description: Controller class
'''

import random

from common.cerror import Cerror
from src.raid import Raid

class Controller:
    '''
    name: __init__
    msg: main.py 中实例化 Controller 的对象，并传入配置参数
    param {*} self
    param {*} seed: 随机种子
    param {*} num_disks: the number of disks in RAID
    param {*} block_size: block size
    param {*} chunk_size: chunk size
    param {*} num_reqs: the number of io requests
    param {*} req_size: request size
    param {*} workload: 'rand' or 'seq'
    param {*} write_frac: the ratio of write reqs in all reqs
    param {*} rand_range: random 工作负载下的请求范围
    param {*} raid_level: only 5
    param {*} raid5_type: raid 5 layout, LS/LA
    param {*} timing: 是否有新的调度事件
    return {*}
    '''
    def __init__(self, seed = 0, num_disks = 6, block_size = 4096, chunk_size = 4096, num_reqs = 10, 
                 req_size = 4096, workload = 'rand', write_frac = 0.5, rand_range = 10000, 
                 raid_level = 5, raid5_type = 'LS', timing = False, reverse = False, solve = False):
        self.seed = seed
        self.num_disks = num_disks
        self.block_size = block_size
        self.chunk_size = chunk_size
        self.num_reqs = num_reqs
        self.req_size = req_size
        self.workload = workload
        self.write_frac = write_frac
        self.rand_range = rand_range
        self.raid_level = raid_level
        self.raid5_type = raid5_type
        self.timing = timing
        self.reverse = reverse
        self.solve = solve

        # 检查参数并格式化
        self.check_args()

        # Raid 实例
        self.raid_instant = Raid(self.block_size, self.chunk_size, self.num_disks, 
                                 self.raid_level, self.raid5_type, 
                                 self.timing, self.reverse, self.solve)
        
        # 生成请求
        self.gen_reqs()


    '''
    name: check_args
    msg: 检查参数并格式化
    param {*} self
    return {*}
    '''
    def check_args(self): 
        random.seed(self.seed)

        # write requests' frac must be legal
        assert(self.write_frac >= 0 and self.write_frac <= 1.0)

        # req size must be valid
        if (self.req_size % self.block_size != 0):
            Cerror(f'请求块大小 {self.req_size} 需为块大小 {self.block_size} 的倍数')
        self.req_size = self.req_size // self.block_size

        # workload type must be valid
        if (self.workload != 'rand' and self.workload != 'seq'):
            Cerror(f'工作负载类型输入错误，必须是 \'rand\' 或 \'seq\'')

        # raid level only 5
        assert(self.raid_level == 5)

        # num disks must be at least 2
        if (self.num_disks < 2):
            Cerror(f'RAID-5 需要至少 2 个磁盘，但当前磁盘个数为 {self.num_disks}')

        # raid5 type must be valid
        if (self.raid_level == 5 and self.raid5_type != 'LS' and self.raid5_type != 'LA'):
            Cerror(f'RAID-5 不支持该 Layout')
    

    '''
    name: show_args
    msg: 打印输出 configs
    param {*} self
    return {*}
    '''
    def show_args(self): 
        print('ARG block size',     self.block_size)
        print('ARG seed',           self.seed)
        print('ARG num disks',      self.num_disks)
        print('ARG chunk size',     self.chunk_size)
        print('ARG num requests',   self.num_reqs)
        print('ARG req size',       self.req_size)
        print('ARG workload',       self.workload)
        print('ARG write frac',     self.write_frac)
        print('ARG random range',   self.rand_range)
        print('ARG raid level',     self.raid_level)
        print('ARG raid5 layout',   self.raid5_type)
        print('ARG reverse',        self.reverse)
        print('ARG timing',         self.timing)

    
    '''
    name: gen_reqs
    msg: generate requests
    param {*} self
    return {*}
    '''
    def gen_reqs(self):
        # TODO 需要修改为从 trace 文件获取
        # 生成请求
        off = 0
        for req in range(self.num_reqs):
            blk = None
            # sequential workload
            if self.workload == 'seq':
                blk = off
                off += self.req_size
            # random workload
            elif self.workload == 'rand':
                blk = int(random.random() * self.rand_range)

            # write req
            if random.random() < self.write_frac:
                self.raid_instant.enqueue(blk, self.req_size, True)
            # read req
            else:
                self.raid_instant.enqueue(blk, self.req_size, False)

        eplased_time = self.raid_instant.get_elapsed()

        # if not self.timing:
        #     return

        if self.solve:
            self.raid_instant.get_disk_stats(eplased_time)
            print(f'Eplased time: {eplased_time} ms')