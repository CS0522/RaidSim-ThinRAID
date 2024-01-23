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