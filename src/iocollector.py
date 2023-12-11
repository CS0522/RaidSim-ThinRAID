'''
Author: Chen Shi
Date: 2023-12-03 19:45:37
Description: IOCollector class
'''

import csv
from ioreq import IOReq

filename = "./trace/hm_min.csv"

class IOCollector:
    def __init__(self, file_name = filename):
        # requests queue
        self.reqs = []
        # for predictor
        self.predicts = []

        # read trace
        self.read_io(file_name)
        self.read_predicts(file_name)

    '''
    name: read_io
    msg: read IO trace file
    param {*} self
    param {*} file_name: file name of the trace file. input its path
    return {*}
    '''    
    def read_io(self, file_name = filename):
        with open(file_name) as trace_file:
            # csv.reader
            csv_reader = csv.reader(trace_file)
            # 如果有第一行标题，则读取第一行
            # header = next(csv_reader)
            count = 1
            timestamp_start = 0
            for row in csv_reader:
                # 要处理一下
                # timestamp: 记录相对时间
                # type: 转换为 is_write bool 型变量
                # TODO offset: 如何处理
                if (count == 1):
                    timestamp_start = row[0]
                # timestamp
                r1 = (int(row[0]) - int(timestamp_start))
                # disk number
                r2 = row[2]
                # type, read or write
                r3 = True if (row[3] == 'Write') else False
                # offset
                r4 = row[4]
                # size
                r5 = row[5]

                count += 1

                # create a new instant of IOReq
                ioreq = IOReq(r1, r2, r3, r4, r5)
                # test
                print(ioreq.timestamp, ioreq.disk_num, ioreq.is_write, ioreq.offset, ioreq.size)
                # append into list
                self.reqs.append(ioreq)

    # TODO
    def read_predicts(self, file_name = filename):
        with open(file_name) as trace_file:
            # csv.reader
            csv_reader = csv.reader(trace_file)
            # 如果有第一行标题，则读取第一行
            # header = next(csv_reader)
            row_count = 1
            # 第几个间隔
            interval_count = 0
            # 该间隔内的请求数
            req_interval_count = 0
            # 时间间隔
            time_interval = 0
            # 开始时间
            timestamp_start = 0
            for row in csv_reader:
                if (row_count == 1):
                    timestamp_start = int(row[0])
                    time_interval = timestamp_start / 10000000
                    row_count += 1
                    interval_count += 1
                    req_interval_count += 1
                    continue
                if ((int(row[0]) - timestamp_start) <= interval_count * time_interval):
                    req_interval_count += 1
                else:
                    self.predicts.append(req_interval_count)
                    # print(req_interval_count)
                    req_interval_count = 0
                    interval_count += 1
                row_count += 1
            # print(self.predicts)


    # get io reqs queue
    def get_reqs(self):
        return self.reqs
    
    def get_predicts(self):
        return self.predicts


if __name__ == "__main__":
    iocollector = IOCollector(filename) 