'''
Author: Chen Shi
Date: 2023-12-11 10:32:25
Description: test
'''

# a_list = []
# for r in range(10):
#     b_list = []
#     # col, num_disks 列
#     for c in range(10):
#         b_list.append(c)
#     # 把每行的 b_list 添加到 block table
#     a_list.append(b_list)

# for r in range(10):
#     for c in range(10):
#         print(str(a_list[r][c]), end = " ")
#     print('')

# count = 0
# for item in a_list:
#     print(str(item) + str(count))
#     count += 1


"""
传值还是传引用问题
"""
# class A:
#     def __init__(self):
#         value = 1

# class B:
#     def __init__(self, a):
#         b_a = A()
#         b_a = a

#     def set_a(self):
#         b_a.value = 2
#         pass

# a = A()

# print("a before", a.value)

# b = B(a)
# b.set_a()

# print("a after", a.value)
# print("b's a", b.b_a.value)

"""
深拷贝
"""
# import copy
# class Test:
#     value = 0

#     def __init__(self, new_val):
#         value = new_val


# a = Test(1)
# b = Test(2)
# c = Test(3)
# tls = [a, b, c]
# tls_dc = copy.deepcopy(tls)
# print("tls", tls[0].value, tls[1].value, tls[2].value)
# print("tls_dc", tls_dc[0].value, tls_dc[1].value, tls_dc[2].value)
# tls.sort(reverse = True, key = lambda x:x.value)
# print("tls", tls[0].value, tls[1].value, tls[2].value)
# print("tls_dc", tls_dc[0].value, tls_dc[1].value, tls_dc[2].value)

# d = tls[0]
# d.value = 10
# e = copy.deepcopy(tls[0])
# e.value = 20
# print("tls[0]", tls[0].value)
# print("d", d.value)
# print("e", e.value)


"""
二维空 list
"""
# ls = [[], [], []]
# print(ls)


# class A:
#     def __init__(self, value):
#         value = value

# a = A(1)
# b = A(2)

# ls = [[a], [b]]

# print(ls[0][0].value)
# print(ls[1][0].value)

# class A:
#     block_table = [[], [], []]

# class B:
#     def __init__(self, a:A):
#         a1 = a
#         a1.block_table[0].append(1)

#         # print(a1.block_table)

# a = A()
# b = B(a)

# print(a.block_table)


"""
csv 测试
"""
# import csv

# read_file = "./trace/hm_min.csv"
# write_file = "./test.csv"

# with open(read_file, 'r') as readfile:
#     with open(write_file, 'w') as writefile:
#         reader = csv.reader(readfile)
#         writer = csv.writer(writefile)

#         count = 1
#         for row in reader:
#             value = (int(row[0]) / 10000000) - 11644473600
#             if (value < 1172188821):
#                 print(value)
#             writer.writerow(row)
#             if (count >= 10):
#                 break
#             count += 1

"""
predictor test
"""
# import random
# import csv

# read_file = "./trace/hm_min.csv"
# write_file = "./test.csv"

# def process_trace_file():
#         # 读取原 trace 文件
#         with open(read_file, 'r') as readfile:
#             with open(write_file, 'w') as writefile:
#                 reader = csv.reader(readfile)
#                 writer = csv.writer(writefile)
#                 writer.writerow(['Timestamp', 'ReqDiskNum', 'Type', 'Offset', 'Size'])
#                 for row in reader:
#                     # 按行读取
#                     # TODO 对 trace 内文件进行处理
#                     # row[0] 时间戳，FILETIME 转换为毫秒级时间戳
#                     c0 = ((int(row[0]) / 10000000) - 11644473600) * 1000.0
#                     # row[2] 请求磁盘号，用 random 随机分配
#                     c1 = random.randint(0, 4)
#                     # row[3] 请求类型，read or write
#                     c2 = True if (row[3] == 'Write') else False
#                     # row[4] 请求地址，缩小
#                     c3 = int(row[4])
#                     while (c3 >= 10000 - (int(row[5]) // 4096)):
#                         c3 = c3 // 1024
#                     # row[5] 请求大小（block size 的倍数）
#                     c4 = int(row[5]) // 4096
#                     writer.writerow([c0, c1, c2, c3, c4])

# # process_trace_file()

# predicts = []
# def read_predicts(file_name = write_file):
#         with open(file_name) as trace_file:
#             # csv.reader
#             reader = csv.reader(trace_file)
#             # 如果有第一行标题，则读取第一行
#             header = next(reader)
#             row_count = 1
#             # 第几个间隔
#             interval_count = 1
#             # 该间隔内的请求数
#             req_interval_count = 0
#             # TODO 时间间隔
#             time_interval = 1000000
#             # 开始时间
#             timestamp_start = 0
#             for row in reader:    
#                 if (row_count == 1):
#                     timestamp_start = float(row[0])
#                 if (float(row[0]) <= timestamp_start + interval_count * time_interval):
#                     # 在时间间隔内的请求数 + 1
#                     req_interval_count += 1
#                 else:
#                     predicts.append(req_interval_count)
#                     # 如果当前这个请求小于下一个时间间隔点
#                     if (float(row[0]) <= timestamp_start + (interval_count + 1) * time_interval):
#                         # 当前的请求属于该时间间隔内
#                         req_interval_count = 1
#                         interval_count += 1
#                     # 如果当前这个请求大于下一个时间间隔点
#                     else:
#                         req_interval_count = 0
#                         interval_count += 1
#                         # 循环直到找到对应时间间隔
#                         while (float(row[0]) > timestamp_start + interval_count * time_interval):
#                             predicts.append(req_interval_count)
#                             interval_count += 1
#                         # 找到了，请求属于当前的时间间隔中
#                         req_interval_count = 1
#                 row_count += 1
#             # for end
#             predicts.append(req_interval_count)
#             print(predicts)

# # read_predicts()

# hots = []
# def read_hots(file_name = write_file):
#     with open (file_name) as trace_file:
#         # csv.reader
#         reader = csv.reader(trace_file)
#         # 如果有第一行标题，则读取第一行
#         header = next(reader)
#         row_count = 1
#         for row in reader:
#             if (row_count == 10):
#                 break
#             for i in range(int(row[4])):
#                 hots.append([int(row[1]), int(row[3]) + i])
#             row_count += 1
#         print(hots)

# read_hots()

# import yaml

# with open('./config.yaml', 'r') as config_file:
#     configs = yaml.load(config_file.read(), Loader = yaml.FullLoader)

#     print(configs)

# ls = [0, 1, 2]

# print(ls[:1])

# import csv

# hots = []
# def read_hots(timestamp_start, time_interval, interval_count, file_name = './trace/test.csv'):
#         with open (file_name) as trace_file:
#             # csv.reader
#             reader = csv.reader(trace_file)
#             # 如果有第一行标题，则读取第一行
#             header = next(reader)
#             for row in reader:
#                 # 在当前时间间隔内时
#                 if (float(row[0]) <= timestamp_start + time_interval * interval_count):
#                     for i in range(int(row[4])):
#                         # hots 为具有两列的二维 list
#                         # [DiskNumber, Offset]
#                         hots.append([int(row[1]), int(row[3]) + i])
#             print(hots)

# read_hots(1172174139434.557, 1000000, 15)

# from src.armax import armax_func
# from src.iocollector import IOCollector

'''
name: get_predicted_arrival_rate
msg: 获取 the predicted arrival rate in next epoch lamda
param {*} self
return {*}
'''
# def get_predicted_arrival_rate(predicts):
#     # 预测下一个时间间隔的 lamda
#     lamda = armax_func(predicts, 1)
#     # lambda = val / time_interval
#     lamda = round(lamda) / 100
#     print("lambda", lamda)
#     # lamda = 10
#     return lamda


# def get_next_disk_num(curr_disk_num, lamda, miu = 0.1, t_up = 15, t_down = 5, n_step = 2):
#     next_disk_num  = curr_disk_num
#     t = curr_disk_num / (miu * curr_disk_num - lamda)
#     t = abs(t)
#     # t *= 100
#     print("t", t)
#     while t > t_up:
#         next_disk_num = next_disk_num + n_step
#         if (next_disk_num > 10):
#             next_disk_num = 10
#             break
#         t = next_disk_num / (miu * next_disk_num - lamda)
#         t = abs(t)
#         # t *= 100
#         print("t", t)
#     while t < t_down:
#         next_disk_num = next_disk_num - n_step
#         # 刚开始创建的是最小的 RAID，所以要保证最少磁盘个数至少是 4
#         if (next_disk_num < 4):
#             next_disk_num = 4
#             break
#         t = next_disk_num / (miu * next_disk_num - lamda)
#         t = abs(t)
#         # t *= 100
#     return next_disk_num

# predicts = [10, 20, 11, 12, 22, 13, 14, 15, 16, 11, 12, 13, 16, 10, 9, 8, 7]

# io_collector = IOCollector(4, 100, "./trace/hm_min.csv", "./trace/hm_processed.csv")

# predicts = io_collector.get_predicts()

# print("predicts", predicts)

# lamda = get_predicted_arrival_rate(predicts)

# next_disk_num = get_next_disk_num(6, lamda)

# print("next disk num", next_disk_num)


"""
测试 10000 * 10 的 table 的 deep copy
"""
# import copy

# block_table = []

# class Node:
#     timestamp = 100.0
#     disk_num = 10
#     is_write = False
#     offset = 100
#     req_size = 1

# for i in range(10000):
#     row = []
#     for j in range(10):
#         node_temp = Node()
#         row.append(node_temp)
#     block_table.append(row)

# print(block_table)

# blk_copy = copy.copy(block_table)
# blk_deep_copy = copy.deepcopy(block_table)

# print("copy:")
# print(blk_copy)

# print("deep copy:")
# print(blk_deep_copy)

# import random
# print(random.randint(4, 7))

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
    msg: main.py 中实例化 Controller 的对象，并传入 Config 实例
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

        # predictor
        self.t_up = config.get_t_up()
        self.t_down = config.get_t_down()
        self.n_step = config.get_n_step()

        self.time_interval = config.get_time_interval()
        self.miu = config.get_miu()

        self.thinraid = config.get_thinraid()

        # 检查参数并格式化
        self.check_args()

        # Raid 实例
        self.raid_instant = Raid(config)
        
        # 生成请求
        # self.gen_reqs()
        
        # 读取 I/O 请求
        # ioreqs, predicts, hots
        print("读取 I/O 请求...")
        io_collector = IOCollector(self.raid_instant.num_disks, self.time_interval, self.raw_file, self.process_file)
        # 是否开启 thinraid 数据迁移算法
        print("是否启用 thinraid:", self.thinraid)
        if (self.thinraid == False):
            print("生成 I/O 请求...")
            print('')
            print("==========")
            print('')
            self.gen_reqs(io_collector.get_reqs())
        else:
            print("生成 I/O 请求...")
            # 获取时间间隔个数
            interval_count = io_collector.get_interval_count()
            # 获取时间戳开始时间点
            timestamp_start = io_collector.get_timestamp_start()
            # 获取时间间隔时长
            time_interval = io_collector.get_time_interval()
            # 获取 predicts 列表
            predicts = io_collector.get_predicts()
            # print("Predicts:")
            # print(predicts)
            # 获取 io requests
            reqs = io_collector.get_reqs()
            # for 循环时间间隔
            # 前 16 个时间间隔不需要预测
            # 因为 ARMAX 模型至少需要 16 个数据
            for i in range(interval_count):
                # 当前 interval 内的 io requests
                reqs_interval = []
                # for r in reqs:
                #     if (r.timestamp <= timestamp_start + time_interval * (i + 1)):
                #         reqs_interval.append(r)
                #         # 删除首元素
                #         del reqs[0:1]
                j = 0
                while (j < len(reqs)):
                    if (reqs[j].timestamp <= timestamp_start + time_interval * (i + 1)):
                        reqs_interval.append(reqs[j])
                        # 删除首元素
                        del reqs[0:1]
                        continue
                    j += 1
                # 发送当前时间间隔内的请求
                print('')
                print("==========")
                print('')
                print("Interval", i + 1)
                print('')
                self.gen_reqs(reqs_interval)
                # 打印 block table
                self.raid_instant.print_block_table(i + 1)
                # 每个时间间隔都要更新一次 hots 列表
                io_collector.read_hots(timestamp_start, time_interval, i + 1, self.process_file)
                hots = io_collector.get_hots()
                # print("Hots:")
                # print(hots)
                # 前 16 个时间间隔不需要预测
                # 因为 ARMAX 模型至少需要 16 个数据
                power_on_disk_num = 0
                # 调试用
                # if (i > 30):
                #     break
                if (i > 15):
                    # 对于每个 interval，每次 predictor 预测的 list 为 predicts 的截取
                    # predict_temp = predicts[:(i + 1)]
                    # predictor 工作负载预测得到待启动磁盘数
                    # TODO 如果当前间隔的 reqs_interval 为空，则不预测
                    # if (len(reqs_interval) != 0):
                    # predictor = Predictor(config, predict_temp, self.raid_instant.num_disks)
                    power_on_disk_num = 0
                    if (i == 18):
                        power_on_disk_num = 4
                    if (i == 24):
                        power_on_disk_num = -2
                    if (i == 26):
                        power_on_disk_num = -2
                    # 打印 predict_temp
                    # print('')
                    # print("predict_temp:")
                    # # 每 10 个换行输出
                    # print('[ ', end = '')
                    # for i in range(len(predict_temp)):
                    #     if (i % 9 == 0 and i != 0):
                    #         print(predict_temp[i], end = ' \n')
                    #         continue
                    #     print(predict_temp[i], end = ' ')
                    # print(']')
                # 数据迁移模块的实例化
                reorghandler = ReorgHandler(self.raid_instant, power_on_disk_num, hots)
                # 打印 hots
                reorghandler.print_hots(i + 1)
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
    def gen_reqs(self, reqs:list):
        # 需要修改为从 trace 文件获取
        for r in reqs:
            # 请求大小
            for i in range(r.size):
                self.raid_instant.single_io('r' if (r.is_write == False) else 'w', r.disk_num, r.offset + i)

        eplased_time = self.raid_instant.get_elapsed()

        # if not self.timing:
        #     return

        if self.solve:
            # print('')
            # print("==========")
            print('')
            self.raid_instant.get_disk_stats(eplased_time)
            print('')
            print(f'Eplased time: {eplased_time} ms')
            # print('')
            # print("==========")
            # print('')


"""
测试 predicts
"""
class Test:
    def __init__(self):
        # num_disks, time_interval, raw_file, processed_file
        io_collector = IOCollector(4, 50000, "./trace/hm_1.csv", "./trace/hm_1_processed.csv")
        # 获取时间间隔个数
        interval_count = io_collector.get_interval_count()
        # 获取时间戳开始时间点
        timestamp_start = io_collector.get_timestamp_start()
        # 获取时间间隔时长
        time_interval = io_collector.get_time_interval()
        print("time_interval:")
        print(time_interval)
        # 获取 predicts 列表
        predicts = io_collector.get_predicts()
        print("Predicts:")
        print(predicts)
        # 获取 io requests
        reqs = io_collector.get_reqs()

tst = Test()