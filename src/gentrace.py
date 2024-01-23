'''
Author: Chen Shi
Date: 2024-01-18 15:28:51
Description: 生成 trace 文件
'''
import csv
import random

file = "./trace/generated.csv"

def gen_trace():
    with open(file, 'w', newline = '') as trace_file:
        writer = csv.writer(trace_file)
        for i in range(10000):
            c0 = i
            c1 = random.randint(0, 3)
            c2 = True if (random.randint(0, 1)) else False
            c3 = random.randint(0, 1000)
            c4 = random.randint(1, 4) * 4
            writer.writerow([c0, c1, c2, c3, c4])

gen_trace()