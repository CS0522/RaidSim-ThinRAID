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
from src.migrationhandler import MigrationHandler

class Controller:
    '''
    name: __init__
    msg: main.py 中实例化 Controller 的对象，并传入 Config 实例
    param {*} self
    param {*} config: 保存配置参数的类
    return {*}
    '''
    def __init__(self, config:Config):
        self.seed = config.get_seed()
        self.num_disks = config.get_num_disks()
        self.max_disks = config.get_max_disks()
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

        # predictor
        self.t_up = config.get_t_up()
        self.t_down = config.get_t_down()
        self.n_step = config.get_n_step()

        self.time_interval = config.get_time_interval()
        self.miu = config.get_miu()

        self.mode = config.get_mode()

        # 检查参数并格式化
        self.check_args()

        # Raid 实例
        self.raid_instant = Raid(config)
        
        # 打印输出当前配置
        config.print_args()

        # 读取 trace 文件
        # ioreqs, predicts, hots
        print("读取 trace 文件...")
        print("生成 I/O 请求...")
        io_collector = IOCollector(config)
        # 获取时间间隔个数
        interval_count = io_collector.get_interval_count()
        # 获取时间戳开始时间点
        timestamp_start = io_collector.get_timestamp_start()
        # 计算时间戳结束时间点
        timestamp_end = timestamp_start + self.time_interval * interval_count
        # raid 内的磁盘的 init_disk() 设置时间戳开始时间点
        self.raid_instant.init_disks(timestamp_start, 0, self.num_disks)
        # 获取时间间隔时长
        # time_interval = io_collector.get_time_interval()
        # 获取 predicts 列表
        predicts = io_collector.get_predicts()
        # print("Predicts:")
        # print(predicts)
        # 获取 io requests
        reqs = io_collector.get_reqs()
        reqs_num = len(reqs)
        print("I/O 请求总数:", reqs_num)
        # 打印 predicts
        # print('')
        # print('全部预测数据:')
        # print(predicts)
        # for 循环时间间隔
        # 前 16 个时间间隔不需要预测
        # 因为 ARMAX 模型至少需要 16 个数据
        for i in range(interval_count):
            # 当前 interval 内的 requests
            reqs_interval = []
            j = 0
            while (j < len(reqs)):
                if (reqs[j].timestamp <= timestamp_start + self.time_interval * (i + 1)):
                    reqs_interval.append(reqs[j])
                    # 删除首元素
                    del reqs[0:1]
                    continue
                j += 1
            # 发送当前时间间隔内的 reqs
            print('')
            print("==========")
            print('')
            print("Interval", i + 1)
            print('')
            self.gen_reqs(reqs_interval, timestamp_start + self.time_interval * (i + 1))
            # TODO 每个间隔的 reqs 发送后循环检查每个磁盘是否休眠超时
            # self.raid_instant.check_disk_status(timestamp_start + self.time_interval * (i + 1))
            
            # conventional
            if (self.mode == 'conventional'):
                continue
            
            # thinraid
            elif (self.mode == 'thinraid'):
                # 每个时间间隔都要更新一次 hots
                # 上一个时间间隔的 hots 都需要清空
                io_collector.read_hots(timestamp_start, self.time_interval, i + 1, self.process_file)
                hots = io_collector.get_hots()

                # TODO FOR DEBUG
                if (i > 30):
                    break

                power_on_disk_num = 0
                # 前 16 个时间间隔不需要预测
                # 因为 ARMAX 模型至少需要 16 个数据
                if (i > 15):
                    # 对于每个 interval，每次 predictor 预测的 list 为 predicts 的截取
                    predict_temp = predicts[(i - 16):(i + 1)]
                    # predictor 工作负载预测得到待启动磁盘数
                    # TODO 如果下一个间隔为 0，则不预测
                    power_on_disk_num = 0
                    if (predict_temp[len(predict_temp) - 1] != 0):
                        predictor = Predictor(config, predict_temp, self.raid_instant.num_disks)
                        power_on_disk_num = predictor.get_power_on_disk_num()
                    # 打印 predict_temp
                    print('')
                    print("预测数据:")
                    print(predict_temp)

                # 数据迁移模块的实例化
                reorghandler = ReorgHandler(self.raid_instant, power_on_disk_num, hots, timestamp_start + self.time_interval * (i + 1))
                # 打印 hots
                reorghandler.print_hots(i + 1)
                # 打印 block table
                self.raid_instant.print_block_table(i + 1)

                # 如果 power_on_disk_num 大于 0，则存在待启动磁盘，需要进行数据迁移
                if (power_on_disk_num > 0):
                    # TODO
                    print('')
                    print("当前活动磁盘数:", self.raid_instant.num_disks)
                    print("待启动磁盘数:", power_on_disk_num)
                    print("进行数据迁移...")
                    reorghandler.es_algorithm_add()
                # 如果 power_on_disk_num 等于 0，下一个时间间隔不需要启动磁盘进行数据迁移
                elif (power_on_disk_num == 0):
                    # TODO
                    pass
                # 如果 power_on_disk_num 小于 0，则需要关闭磁盘，需要进行数据迁移
                # 要保证磁盘个数必须为 config 中的 num_disks 以上
                else:
                    # TODO
                    print('')
                    print("当前活动磁盘数:", self.raid_instant.num_disks)
                    print("待关闭磁盘数:", abs(power_on_disk_num))
                    print("进行数据迁移...")
                    reorghandler.es_algorithm_del()

            # TODO no migration algorithm
            elif (self.mode == 'no migration algorithm'):
                # TODO 不用算法，直接添加磁盘随机迁移

                # TODO FOR DEBUG
                if (i > 30):
                    break

                power_on_disk_num = 0
                # 前 16 个时间间隔不需要预测
                # 因为 ARMAX 模型至少需要 16 个数据
                if (i > 15):
                    # 对于每个 interval，每次 predictor 预测的 list 为 predicts 的截取
                    predict_temp = predicts[(i - 16):(i + 1)]
                    # predictor 工作负载预测得到待启动磁盘数
                    # TODO 如果下一个间隔为 0，则不预测
                    power_on_disk_num = 0
                    if (predict_temp[len(predict_temp) - 1] != 0):
                        predictor = Predictor(config, predict_temp, self.raid_instant.num_disks)
                        power_on_disk_num = predictor.get_power_on_disk_num()
                    # 打印 predict_temp
                    print('')
                    print("预测数据:")
                    print(predict_temp)

                # 随机迁移模块的实例化
                migrationhandler = MigrationHandler(self.raid_instant, power_on_disk_num, timestamp_start + self.time_interval * (i + 1))

                # 如果 power_on_disk_num 大于 0，则存在待启动磁盘，需要进行数据迁移
                if (power_on_disk_num > 0):
                    # TODO
                    print('')
                    print("当前活动磁盘数:", self.raid_instant.num_disks)
                    print("待启动磁盘数:", power_on_disk_num)
                    print("进行数据迁移...")
                    migrationhandler.random_add()
                    
                # 如果 power_on_disk_num 等于 0，下一个时间间隔不需要启动磁盘进行数据迁移
                elif (power_on_disk_num == 0):
                    # TODO
                    pass
                # 如果 power_on_disk_num 小于 0，则需要关闭磁盘，需要进行数据迁移
                # 要保证磁盘个数必须为 config 中的 num_disks 以上
                else:
                    # TODO
                    print('')
                    print("当前活动磁盘数:", self.raid_instant.num_disks)
                    print("待关闭磁盘数:", abs(power_on_disk_num))
                    print("进行数据迁移...")
                    migrationhandler.random_del()
            
            # TODO no power control policy
            elif (self.mode == 'no power control policy'):
                # 每个时间间隔都要更新一次 hots
                # 上一个时间间隔的 hots 都需要清空
                io_collector.read_hots(timestamp_start, self.time_interval, i + 1, self.process_file)
                hots = io_collector.get_hots()

                # TODO FOR DEBUG
                if (i > 30):
                    break

                power_on_disk_num = 0
                # no power control policy
                if (i > 15):
                # TODO 根据什么进行增减磁盘操作
                # TODO 根据每个磁盘的 count_IO 次数？
                    # count_IOs = []
                    # for d in range(self.num_disks):
                    #     io_stats = self.raid_instant.disks[d].get_io_stats()
                    #     count_IOs.append(io_stats[0])
                    # # 计算极差
                    # count_IOs.sort()
                    # # 极差很小且 count_io 数很大，则新添加 n_step 个磁盘
                    # if (abs(count_IOs[self.num_disks - 1] - count_IOs[0]) <= 1000) and (count_IOs[0] >= (reqs_num / 10)):
                    #     power_on_disk_num = 0 + self.n_step
                    # # 极差很大，则减少 n_step 个磁盘
                    # if (abs(count_IOs[self.num_disks - 1] - count_IOs[0]) >= (reqs_num / 10)):
                    #     power_on_disk_num = 0 - self.n_step

                # TODO 根据每个磁盘的休眠段个数？
                    for d in range(self.num_disks):
                        status_stats = self.raid_instant.disks[d].get_status_stats()
                        # 存在仍没有休眠过的磁盘，则新添加 n_step 个磁盘
                        if (len(status_stats[2]) < 1):
                            power_on_disk_num = 0 + self.n_step
                            break
                        # 存在休眠次数超过间隔数的 1/2 的磁盘，则减少 n_step 个磁盘
                        if (len(status_stats[2]) >= (i / 2)):
                            power_on_disk_num = 0 - self.n_step
                            break
                    

                # 数据迁移模块的实例化
                reorghandler = ReorgHandler(self.raid_instant, power_on_disk_num, hots, timestamp_start + self.time_interval * (i + 1))
                # 打印 hots
                reorghandler.print_hots(i + 1)
                # 打印 block table
                self.raid_instant.print_block_table(i + 1)

                # 如果 power_on_disk_num 大于 0，则存在待启动磁盘，需要进行数据迁移
                if (power_on_disk_num > 0):
                    # TODO
                    print('')
                    print("当前活动磁盘数:", self.raid_instant.num_disks)
                    print("待启动磁盘数:", power_on_disk_num)
                    print("进行数据迁移...")
                    reorghandler.es_algorithm_add()
                # 如果 power_on_disk_num 等于 0，下一个时间间隔不需要启动磁盘进行数据迁移
                elif (power_on_disk_num == 0):
                    # TODO
                    pass
                # 如果 power_on_disk_num 小于 0，则需要关闭磁盘，需要进行数据迁移
                # 要保证磁盘个数必须为 config 中的 num_disks 以上
                else:
                    # TODO
                    print('')
                    print("当前活动磁盘数:", self.raid_instant.num_disks)
                    print("待关闭磁盘数:", abs(power_on_disk_num))
                    print("进行数据迁移...")
                    reorghandler.es_algorithm_del()

        # 关闭磁盘
        self.raid_instant.end_disks(timestamp_end, 0, self.max_disks)

        # 获取最终磁盘统计信息
        print('')
        print('==========')
        print('')
        print("磁盘信息统计结果:")
        print('')
        elapsed_time = self.raid_instant.get_elapsed()
        self.raid_instant.get_final_disk_stats(elapsed_time, timestamp_end)


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
    param {*} timestamp_interval: 间隔时间
    return {*}
    '''
    def gen_reqs(self, reqs:list, timestamp_interval):
        # 需要修改为从 trace 文件获取
        for r in reqs:
            # 请求大小
            for i in range(r.size):
                # TODO 增加 timestamp 参数
                self.raid_instant.single_io(r.timestamp, 'r' if (r.is_write == False) else 'w', r.disk_num, r.offset + i)
            
        # 间隔内所有的 reqs 发送完后循环检查每个磁盘是否休眠超时
        self.raid_instant.check_disk_status(timestamp_interval)

        eplased_time = self.raid_instant.get_elapsed()

        # if self.solve:
        print('')
        # 获取磁盘的各种信息统计
        self.raid_instant.get_disk_stats(eplased_time, timestamp_interval)
        print('')
        # print(f'Eplased time: {eplased_time} ms')

