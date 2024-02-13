'''
Author: Chen Shi
Date: 2023-12-03 19:45:37
Description: IOCollector class
'''

import csv
from src.ioreq import IOReq
from src.config import Config
import random

raw_file = "./trace/hm_min.csv"
process_file = "./trace/hm_processed.csv"

class IOCollector:
    def __init__(self, config:Config):
        self.raw_file = config.get_raw_file()
        self.process_file = config.get_process_file()
        # 当前磁盘块的数量
        self.num_disks = config.get_num_disks()
        # requests queue
        self.reqs = []
        # for predictor
        self.predicts = []
        # for reorg handler
        self.hots = []
        # 时间间隔
        self.time_interval = config.get_time_interval()

        self.num_tracks = config.get_num_tracks()
        self.blocks_per_track = config.get_blocks_per_track()

        self.block_size = config.get_block_size()

        # TODO process raw trace file 
        # self.process_trace_file()

        # read trace
        self.read_io(self.process_file)
        # 时间戳开始时间点，时间间隔个数
        self.timestamp_start, self.interval_count = self.read_predicts(self.process_file)
        # self.read_hots(self.timestamp_start, self.time_interval, self.interval_count)


    '''
    name: process_trace_file
    msg: 处理原始 trace 文件，得到修改的 trace 文件
    param {*} self
    return {*}
    '''
    def process_trace_file(self):
        # 读取原 trace 文件并修改，然后创建一个新 trace 文件
        # 获取中位数
        mid_addr = 0
        max_addr = 0
        with open(self.raw_file, 'r') as readfile:
            reader = csv.reader(readfile)
            addr_lst = []
            for r in reader:
                addr_lst.append(int(r[4]))
            addr_lst.sort()
            mid_addr = addr_lst[(len(addr_lst) - 1) // 2]
            max_addr = addr_lst[len(addr_lst) - 1]
        half_mid_addr = mid_addr // (self.num_disks // 2)

        with open(self.raw_file, 'r') as readfile:
            with open(self.process_file, 'w', newline = '') as writefile:
                reader = csv.reader(readfile)
                writer = csv.writer(writefile)
                for row in reader:
                    # 按行读取
                    # 对 trace 内文件进行处理
                    # row[0]: 时间戳，FILETIME 转换为毫秒级时间戳
                    c0 = ((int(row[0]) / 10000000) - 11644473600) * 1000.0
                    # TODO row[2]: 请求磁盘号，每份地址归为一个磁盘
                    # c1 = random.randint(0, self.num_disks - 1)
                    c1 = (self.num_disks - 1) if (int(row[4]) // (half_mid_addr) >= self.num_disks) else (int(row[4]) // (half_mid_addr))
                    # row[3]: 请求类型，read or write
                    c2 = True if (row[3] == 'Write') else False
                    # row[4]: 请求地址，按比例缩小
                    c3 = int((self.num_tracks * self.blocks_per_track) * float(int(row[4]) / max_addr))
                    while (c3 >= (self.num_tracks * self.blocks_per_track) - (int(row[5]) // self.block_size)):
                        c3 -= 1
                    # while (c3 >= 10000 - (int(row[5]) // 4096)):
                    #     c3 = c3 // 1024
                    # row[5]: 请求大小，block size 的倍数
                    c4 = int(row[5]) // self.block_size
                    writer.writerow([c0, c1, c2, c3, c4])


    '''
    name: read_io
    msg: read processed trace file and turn it into IOReq class
    param {*} self
    param {*} file_name: processed trace file; file path
    return {*}
    '''    
    def read_io(self, file_name = process_file):
        with open(file_name) as trace_file:
            # csv.reader
            reader = csv.reader(trace_file)
            # 如果有第一行标题，则读取第一行
            # header = next(reader)
            # count = 1
            # timestamp_start = 0
            for row in reader:
                # count += 1
                # create a new instant of IOReq
                # print("row:")
                # print(row)
                ioreq = IOReq(float(row[0]), int(row[1]), True if (row[2] == 'True') else False, int(row[3]), int(row[4]))
                # test
                # print(ioreq.timestamp, ioreq.disk_num, ioreq.is_write, ioreq.offset, ioreq.size)
                # append into list
                self.reqs.append(ioreq)

    
    '''
    name: read_predicts
    msg: read processed trace file and get predicts list for Predictor 
    param {*} self
    param {*} file_name: processed trace file; file path
    return {*}
    '''
    def read_predicts(self, file_name = process_file):
        with open(file_name) as trace_file:
            # csv.reader
            reader = csv.reader(trace_file)
            # 如果有第一行标题，则读取第一行
            # header = next(reader)
            row_count = 1
            # 第几个间隔
            interval_count = 1
            # 该间隔内的请求数
            req_interval_count = 0
            # 开始时间
            timestamp_start = 0
            for row in reader:    
                if (row_count == 1):
                    timestamp_start = float(row[0])
                if (float(row[0]) <= timestamp_start + interval_count * self.time_interval):
                    # 在时间间隔内的请求数 + 1
                    req_interval_count += 1
                else:
                    self.predicts.append(req_interval_count)
                    # 如果当前这个请求小于下一个时间间隔点
                    if (float(row[0]) <= timestamp_start + (interval_count + 1) * self.time_interval):
                        # 当前的请求属于该时间间隔内
                        req_interval_count = 1
                        interval_count += 1
                    # 如果当前这个请求大于下一个时间间隔点
                    else:
                        req_interval_count = 0
                        interval_count += 1
                        # 循环直到找到对应时间间隔
                        while (float(row[0]) > timestamp_start + interval_count * self.time_interval):
                            self.predicts.append(req_interval_count)
                            interval_count += 1
                        # 找到了，请求属于当前的时间间隔中
                        req_interval_count = 1
                row_count += 1
            # for end
            self.predicts.append(req_interval_count)
            # 返回时间戳开始时间点，时间间隔个数
            return timestamp_start, (interval_count + 1)

    
    '''
    name: read_hots
    msg: read processed trace file and get hots list for ReorgHandler
         这里是在一个时间间隔内的 hots，到下一个时间间隔需要更新 hots
    param {*} self
    param {*} timestamp_start: 时间戳开始的时候
    param {*} time_interval: 时间间隔
    param {*} interval_count: 当前的第几个时间间隔
    param {*} file_name: processed trace file; file path
    return {*}
    '''
    def read_hots(self, timestamp_start, time_interval, interval_count, file_name = process_file):
        # 先清空 hots 列表
        self.hots = []
        with open (file_name) as trace_file:
            # csv.reader
            reader = csv.reader(trace_file)
            # 如果有第一行标题，则读取第一行
            # header = next(reader)
            for row in reader:
                # 在当前时间间隔内时
                if (float(row[0]) <= timestamp_start + time_interval * interval_count):
                    for i in range(int(row[4])):
                        # hots 为具有两列的二维 list
                        # [DiskNumber, Offset]
                        self.hots.append([int(row[1]), int(row[3]) + i])
            # print(self.hots)


    def get_reqs(self):
        return self.reqs
    
    def get_predicts(self):
        return self.predicts
    
    def get_hots(self):
        return self.hots
    
    def get_interval_count(self):
        return self.interval_count
    
    def get_timestamp_start(self):
        return self.timestamp_start
    
    def get_time_interval(self):
        return self.time_interval


if __name__ == "__main__":
    iocollector = IOCollector() 