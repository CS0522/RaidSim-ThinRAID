'''
Author: Chen Shi
Date: 2023-11-29 23:11:49
Description: Controller class
'''

import random
import time

from common.cerror import Cerror
from src.raid import Raid
from src.config import Config
from src.iocollector import IOCollector
from src.predictor import Predictor
from src.reorghandler import ReorgHandler
from src.randomhandler import RandomHandler

class Controller:
    '''
    name: __init__
    msg: main.py 中实例化 Controller 的对象，并传入 Config 实例
    param {*} self
    param {*} config: 保存配置参数的类
    return {*}
    '''
    def __init__(self, config:Config):
        self.config = config
        self.seed = config.get_seed()
        self.min_disks = config.get_min_disks()
        self.max_disks = config.get_max_disks()
        self.block_size = config.get_block_size()
        self.chunk_size = config.get_chunk_size()
        self.req_size = config.get_req_size()
        self.raid_level = config.get_raid_level()
        self.raid5_type = config.get_raid5_type()
        self.print_logical = config.get_print_logical()
        self.print_stats = config.get_print_stats()

        self.raw_file = config.get_raw_file()
        self.process_file = config.get_process_file()

        # predictor
        self.t_up = config.get_t_up()
        self.t_down = config.get_t_down()
        self.n_step = config.get_n_step()

        self.time_interval = config.get_time_interval()

        self.mode = config.get_mode()

        self.debug = config.get_debug()

        # Raid 实例
        self.raid_instant = Raid(config, self.max_disks if (self.mode == "conventional") else self.min_disks)
        self.num_disks = self.raid_instant.num_disks

        # 用于记录 predictor 的预测数据准确度
        self.predict_groundtruth = []
        self.predict_result = []
        # 用于给 predictor 预测数据，列表长度维持在 16
        self.predicts = []

        # 用于记录每个时间间隔实际花费的进程时间
        self.timers = []

        # 检查参数并格式化
        self.check_args()
        
        # 打印输出当前配置
        config.print_args()

        # 读取 trace 文件
        # ioreqs
        print("读取 trace 文件...")
        print("生成 I/O 请求...")
        iocollector = IOCollector(self.config)
        # 获取时间间隔个数
        self.interval_num = iocollector.get_interval_num()
        # 获取时间戳开始时间点
        self.timestamp_start = iocollector.get_timestamp_start()
        # 计算时间戳结束时间点
        self.timestamp_end = self.timestamp_start + self.time_interval * self.interval_num
        
        # raid 初始化
        # conventional，用最大磁盘数量
        if (self.mode == "conventional"):
            self.raid_instant.init_disks(self.timestamp_start, 0, self.max_disks)
        # thinraid 等其他模式，用最小磁盘数量
        else:
            self.raid_instant.init_disks(self.timestamp_start, 0, self.min_disks)
        
        # 获取 io requests
        reqs = iocollector.get_reqs()
        reqs_num = len(reqs)
        print("I/O 请求总数:", reqs_num)
        
        # 已经处理的 reqs 个数
        self.reqs_served = 0
        # 各个时间间隔的 reqs 个数
        self.reqs_interval = 0
        # 当前第几个时间间隔
        # 前 16 个时间间隔不需要预测
        # 因为 ARMAX 模型至少需要 16 个数据
        self.interval_count = 1

        # print
        if (self.print_stats == True):
                print('')
                print("==========")
                print('')
                print("Interval", self.interval_count)
                print('')

        # 记录开始时间
        self.timer_start = time.process_time()

        # 循环 reqs 中的每个请求
        for r in reqs:
            # 找到该 req 属于哪个时间间隔
            # 可能跨过多个时间间隔
            while (r.timestamp > self.timestamp_start + self.interval_count * self.time_interval):
                # 再执行到达时间间隔操作
                self.interval_operations(self.timestamp_start + self.interval_count * self.time_interval)
                # 进入下一时间间隔
                self.interval_count += 1
                
                # print
                if (self.print_stats == True):
                    # print('')
                    print("==========")
                    print('')
                    print("Interval", self.interval_count)
                    print('')
            
            # 循环退出，req 属于该时间间隔
            # 发送 req
            self.raid_instant.enqueue(r.timestamp, r.offset, r.size, r.is_write)
            # 该时间间隔的请求数增加
            self.reqs_interval += 1

        # 请求全部处理完后
        while (self.interval_count <= self.interval_num):
            # 执行到达该时间间隔操作
            self.interval_operations(self.timestamp_start + self.interval_count * self.time_interval)

            self.interval_count += 1

        # 关闭磁盘
        self.raid_instant.end_disks(self.timestamp_end, 0, self.max_disks)

        # 获取最终磁盘统计信息
        print('')
        print('==========')
        print('')
        print("磁盘信息统计结果:")
        print('')
        elapsed_time = self.raid_instant.get_elapsed()
        self.raid_instant.get_final_disk_stats(elapsed_time, self.timestamp_end)

        # 预测数据信息
        if (self.mode != 'conventional'):
            self.predict_groundtruth.pop(0)
            self.predict_result.pop()
            print(f'Predict Groundtruth: (length = {len(self.predict_groundtruth)})')
            print(self.predict_groundtruth)
            print(f'Predict Result: (length = {len(self.predict_result)})')
            print(self.predict_result)

        # timer
        print('')
        print(f'RAID 模拟运行时长(s): {sum(self.timers)} (length = {len(self.timers)})')
        print(self.timers)


    
    '''
    name: interval_operations
    msg: 到达时间间隔后执行一系列操作
    param {*} self
    param {*} timestamp_interval: 时间间隔的时间戳
    return {*}
    '''
    def interval_operations(self, timestamp_interval):
        # 记录该时间间隔时间
        timer_interval = time.process_time()
        interval_cost_time = timer_interval - self.timer_start - (sum(self.timers) if (len(self.timers) != 0) else 0.0)
        self.timers.append(interval_cost_time)
            
        # 间隔内所有的 reqs 发送完后循环检查每个磁盘是否休眠超时
        self.raid_instant.check_disk_status(timestamp_interval)

        # 获取磁盘的各种信息统计
        eplased_time = self.raid_instant.get_elapsed()
        self.raid_instant.get_disk_stats(eplased_time, timestamp_interval)

        # 添加预测数据
        if (self.interval_count == 1):
            self.predicts.append(self.reqs_interval)
        else:
            if (self.interval_count > 16):
                # 维持 predicts 长度为 16
                self.predicts.pop(0)
            self.predicts.append(self.reqs_interval)
        
        self.reqs_served += self.reqs_interval
        self.reqs_interval = 0

        # conventional mode
        if (self.mode == 'conventional'):
            pass

        # thinraid mode
        if (self.mode == 'thinraid'):
            if (self.interval_count > 16):
                adjust_disk_num = 0
                """
                Predictor 工作负载预测
                """
                # 如果下一个间隔为 0，则不预测
                if (self.predicts[-1] != 0):
                    # Predictor 传入实际执行时间来计算 miu
                    predictor = Predictor(self.config, self.raid_instant.num_disks, 
                                          self.reqs_served, self.timers, 
                                          self.predicts, 
                                          self.predict_groundtruth, self.predict_result)
                    adjust_disk_num = predictor.get_adjust_disk_num()
                # 打印 predicts
                if (self.print_stats == True):
                    print('')
                    print("预测数据:")
                    print(self.predicts)
                    print('')

                """
                ReOrgHandler 数据迁移
                """
                reorghandler = ReorgHandler(self.raid_instant, adjust_disk_num, timestamp_interval)
                # 如果 adjust_disk_num 大于 0，则存在待启动磁盘，需要进行数据迁移
                if (adjust_disk_num > 0):
                    if (self.print_stats == True):
                        print('')
                        print("当前活动磁盘数:", self.raid_instant.num_disks)
                        print("待启动磁盘数:", adjust_disk_num)
                        print("进行数据迁移...")
                    reorghandler.es_algorithm_add()
                # 如果 adjust_disk_num 等于 0，下一个时间间隔不需要启动磁盘进行数据迁移
                elif (adjust_disk_num == 0):
                    pass
                # 如果 adjust_disk_num 小于 0，则需要关闭磁盘，需要进行数据迁移
                # 要保证磁盘个数必须为 config 中的 num_disks 以上
                else:
                    if (self.print_stats == True):
                        print('')
                        print("当前活动磁盘数:", self.raid_instant.num_disks)
                        print("待关闭磁盘数:", abs(adjust_disk_num))
                        print("进行数据迁移...")
                    reorghandler.es_algorithm_del()
            # end if
        
        # random
        if (self.mode == 'random'):
            # TODO 
            if (self.interval_count > 16):
                adjust_disk_num = 0
                """
                Predictor 负载预测
                """
                # 如果下一个间隔为 0，则不预测
                if (self.predicts[-1] != 0):
                    # Predictor 传入实际执行时间来计算 miu
                    predictor = Predictor(self.config, self.raid_instant.num_disks, 
                                          self.reqs_served, self.timers, 
                                          self.predicts, 
                                          self.predict_groundtruth, self.predict_result)
                    adjust_disk_num = predictor.get_adjust_disk_num()
                # 打印 predicts
                if (self.print_stats == True):
                    print('')
                    print("预测数据:")
                    print(self.predicts)
                    print('')

                """
                RandomHandler 数据迁移
                """
                randomhandler = RandomHandler(self.raid_instant, adjust_disk_num, timestamp_interval)
                # 如果 adjust_disk_num 大于 0，则存在待启动磁盘，需要进行数据迁移
                if (adjust_disk_num > 0):
                    if (self.print_stats == True):
                        print('')
                        print("当前活动磁盘数:", self.raid_instant.num_disks)
                        print("待启动磁盘数:", adjust_disk_num)
                        print("进行数据迁移...")
                    randomhandler.random_add()
                # 如果 adjust_disk_num 等于 0，下一个时间间隔不需要启动磁盘进行数据迁移
                elif (adjust_disk_num == 0):
                    pass
                # 如果 adjust_disk_num 小于 0，则需要关闭磁盘，需要进行数据迁移
                # 要保证磁盘个数必须为 config 中的 num_disks 以上
                else:
                    if (self.print_stats == True):
                        print('')
                        print("当前活动磁盘数:", self.raid_instant.num_disks)
                        print("待关闭磁盘数:", abs(adjust_disk_num))
                        print("进行数据迁移...")
                    randomhandler.random_del()
            # end if
        # end mode
        
        # 清理时间间隔内的数据块热度
        self.raid_instant.clear_hots()


    '''
    name: check_args
    msg: 检查参数并格式化
    param {*} self
    return {*}
    '''
    def check_args(self): 
        random.seed(self.seed)

        # req size must be valid
        if (self.req_size % self.block_size != 0):
            Cerror(f'请求块大小 {self.req_size} 需为块大小 {self.block_size} 的倍数')
        self.req_size = self.req_size // self.block_size

        # raid level only 5
        assert(self.raid_level == 5)

        # num disks must be at least 2
        if (self.num_disks < 2):
            Cerror(f'RAID-5 需要至少 2 个磁盘，但当前磁盘个数为 {self.num_disks}')

        # raid5 type must be valid
        if (self.raid_level == 5 and self.raid5_type != 'LS' and self.raid5_type != 'LA'):
            Cerror(f'RAID-5 不支持该 Layout')
    
