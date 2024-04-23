'''
Author: Chen Shi
Date: 2024-04-21 16:35:54
Description: 统计 trace 文件数据
'''

import csv

def cal_write_ratio(trace: str):
    count_req = 0
    count_write_req = 0
    with open(f'./trace/{trace}_processed.csv', 'r') as trace_file:
        reader = csv.reader(trace_file)
        for row in reader:
            count_req += 1
            r_or_w = True if (row[2] == 'True') else False
            if (r_or_w == True):
                count_write_req += 1
    # calculate write ratio
    write_ratio = count_write_req / count_req
    print('req num:', count_req)
    print('write req num:', count_write_req)
    print(f'{trace} write ratio: {write_ratio * 100:.2f}%')
    return write_ratio


def cal_avg_req_size(trace: str):
    req_size_total = 0
    count_req = 0
    with open(f'./trace/{trace}_processed.csv', 'r') as trace_file:
        reader = csv.reader(trace_file)
        for row in reader:
            count_req += 1
            req_size_total += int(row[4])
    # calculate average request size
    req_size_total *= 512
    req_size_total /= 1024
    avg_req_size = req_size_total / count_req
    print(f'{trace} avg req size: {avg_req_size:.2f} KB')
    return avg_req_size


def record_stats():
    traces = ['hm_0', 'hm_1', 'mds_0', 'mds_1', 'prn_0', 'proj_0', 'proj_3']

    with open('./trace/trace_stats.txt', 'w') as stats_file:
        for trace in traces:
            line1 = trace + ':'
            line2 = f'{trace} write ratio: {cal_write_ratio(trace) * 100:.2f}%'
            line3 = f'{trace} avg req size: {cal_avg_req_size(trace):.2f} KB'

            stats_file.writelines([line1 + '\n', line2 + '\n', line3 + '\n', '\n'])


record_stats()