'''
Author: Chen Shi
Date: 2023-11-29 23:11:49
Description: Controller class
'''


import random

from common.cerror import Cerror
from src.raid import Raid
from src.config import Config
from src.iocollector import IOCollector
from src.predictor import Predictor
from src.reorghandler import ReorgHandler

class Controller:
    '''
    name: __init__
    msg: main.py 中实例化 Controller 的对象，并传入配置参数
    param {*} self
    param {*} config: 保存配置参数的类
    return {*}
    '''
    def __init__(self, config:Config):
        self.seed = config.get_seed()
        self.num_disks = config.get_num_disks()
        self.block_size = config.get_block_size()
        self.chunk_size = config.get_chunk_size()
        self.num_reqs = config.get_num_reqs()
        self.req_size = config.get_req_size()
        self.workload = config.get_workload()
        self.write_frac = config.get_write_frac()
        self.rand_range = config.get_rand_range()
        self.raid_level = config.get_raid_level()
        self.raid5_type = config.get_raid5_type()
        self.timing = config.get_timing()
        self.solve = config.get_solve()

        self.raw_file = config.get_raw_file()
        self.process_file = config.get_process_file()

        # 检查参数并格式化
        self.check_args()

        # Raid 实例
        self.raid_instant = Raid(config)
        
        # 生成请求
        # self.gen_reqs()
        
        # 读取 I/O 请求
        # ioreqs, predicts, hots
        io_collector = IOCollector(self.raid_instant.num_disks, config.get_raw_file(), config.get_process_file())
        # 获取时间间隔个数
        interval_count = io_collector.get_interval_count()
        # 获取时间戳开始时间点
        timestamp_start = io_collector.get_timestamp_start()
        # 获取时间间隔时长
        time_interval = io_collector.get_time_interval()
        # 获取 predicts 列表
        predicts = io_collector.get_predicts()
        # TODO for 循环时间间隔
        # TODO 前 n 个时间间隔需不需要预测？
        for i in range(interval_count):
            # 每个时间间隔都要更新一次 hots 列表
            io_collector.read_hots(timestamp_start, time_interval, i + 1, self.process_file)
            # 对于每个 interval，每次 predictor 预测的 list 为 predicts 的截取
            predict_temp = predicts[:(i + 1)]
            # predictor 工作负载预测得到待启动磁盘数
            predictor = Predictor(config, predict_temp, self.raid_instant.num_disks, 
                                  config.get_t_up(), config.get_t_down(), config.get_n_step())
            power_on_disk_num = predictor.get_power_on_disk_num()
            # 数据迁移模块的实例化
            reorghandler = ReorgHandler(self.raid_instant, power_on_disk_num, io_collector.get_hots())
            # 如果 power_on_disk_num 大于 0，则存在待启动磁盘，需要进行数据迁移
            if (power_on_disk_num > 0):
                # TODO
                reorghandler.es_algorithm_add()
            # 如果 power_on_disk_num 等于 0，下一个时间间隔不需要启动磁盘进行数据迁移
            elif (power_on_disk_num == 0):
                # TODO
                pass
            # 如果 power_on_disk_num 小于 0，则需要关闭磁盘，需要进行数据迁移
            # 要保证磁盘个数必须为 config 中的 num_disks 以上
            else:
                # TODO
                reorghandler.es_algorithm_del()


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
        pass

    
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