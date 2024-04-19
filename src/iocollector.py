'''
Author: Chen Shi
Date: 2023-12-03 19:45:37
Description: IOCollector class
'''

import csv
from src.ioreq import IOReq
from src.config import Config

raw_file = "./trace/hm_min.csv"
process_file = "./trace/hm_processed.csv"

class IOCollector:
    def __init__(self, config:Config):
        self.raw_file = config.get_raw_file()
        self.process_file = config.get_process_file()
        self.processed = config.get_processed()
        # 初始（最小）磁盘数量
        self.min_disks = config.get_min_disks()
        # 最大磁盘数量
        self.max_disks = config.get_max_disks()
        # raid 模式
        self.mode = config.get_mode()
        # requests queue
        self.reqs = []
        # 时间间隔
        self.time_interval = config.get_time_interval()

        self.num_tracks = config.get_num_tracks()
        self.blocks_per_track = config.get_blocks_per_track()

        self.block_size = config.get_block_size()

        # 处理 raw trace file 
        if (self.processed == False):
            self.process_trace_file()

        # read trace
        self.timestamp_start, self.interval_num = self.read_io(self.process_file)


    '''
    name: process_trace_file
    msg: 处理原始 trace 文件，得到修改的 trace 文件
    param {*} self
    return {*}
    '''
    def process_trace_file(self):
        # 读取原 trace 文件并修改，然后创建一个新 trace 文件
        max_addr = 0
        with open(self.raw_file, 'r') as readfile:
            reader = csv.reader(readfile)
            addr_lst = []
            for r in reader:
                addr_lst.append(int(r[4]))
            addr_lst.sort()
            max_addr = addr_lst[-1]

        with open(self.raw_file, 'r') as readfile:
            with open(self.process_file, 'w', newline = '') as writefile:
                reader = csv.reader(readfile)
                writer = csv.writer(writefile)
                for row in reader:
                    # 按行读取
                    # 对 trace 内文件进行处理
                    # row[0]: 时间戳，FILETIME 转换为毫秒级时间戳
                    c0 = ((int(row[0]) / 10000000) - 11644473600) * 1000.0
                    # row[2]: 请求磁盘号，直接对整个 RAID 逻辑磁盘
                    c1 = 0
                    # row[3]: 请求类型，read or write
                    c2 = True if (row[3] == 'Write') else False
                    # row[4]: 请求地址范围，按比例缩小
                    # 2 * 10000 * rate
                    # 避免越界
                    c3 = int((self.num_tracks * self.blocks_per_track * 2) * float(int(row[4]) / max_addr))
                    # row[5]: 请求大小，block size 的倍数
                    c4 = int(row[5]) // self.block_size
                    writer.writerow([c0, c1, c2, c3, c4])

    
    '''
    name: read_io
    msg: read processed trace file, get io reqs
    param {*} self
    param {*} file_name: processed trace file path
    return {*} timestamp_start: 起始时间戳
    return {*} interval_num: 间隔个数
    '''
    def read_io(self, file_name = process_file):
        with open(file_name) as trace_file:
            # csv.reader
            reader = csv.reader(trace_file)
            # 如果有第一行标题，则读取第一行
            # header = next(reader)
            row_count = 1
            # 第几个间隔
            interval_num = 1
            # 开始时间
            timestamp_start = 0
            
            for row in reader:
                # timestamp_start    
                if (row_count == 1):
                    timestamp_start = float(row[0])

                # read io
                ioreq = IOReq(float(row[0]), int(row[1]), True if (row[2] == 'True') else False, int(row[3]), int(row[4]))
                # append into list
                self.reqs.append(ioreq)
                
                # interval_num
                # 大于当前时间间隔，循环查找
                while (float(row[0]) > timestamp_start + interval_num * self.time_interval):
                    interval_num += 1
                # 退出循环，属于当前时间间隔
                
                row_count += 1
            # end
            # 返回时间戳开始时间点，时间间隔个数
            return timestamp_start, interval_num


    def get_reqs(self):
        return self.reqs
    
    def get_interval_num(self):
        return self.interval_num
    
    def get_timestamp_start(self):
        return self.timestamp_start


if __name__ == "__main__":
    # 创建一个 Config 实例，读取 config.yaml 并保存配置参数，传入 Controller 中 
    config = Config('../config.yaml')
    iocollector = IOCollector(config)