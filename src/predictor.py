'''
Author: Chen Shi
Date: 2023-12-04 00:37:08
Description: Predictor class
'''


# from src.iocollector import IOCollector
from src.armax import armax_func
from src.config import Config

class Predictor:
    # io requests queue
    predicts = []

    def __init__(self, config:Config, predicts, curr_disk_num, t_up, t_down, n_step = 2):
        # the predict array
        self.predicts = predicts
        # number of init disks
        self.num_disks = config.get_num_disks()
        # the number of disks in current epoch
        self.curr_disk_num = curr_disk_num
        # the limited average response time
        self.t_up = t_up
        self.t_down = t_down
        # N_step
        self.n_step = n_step
        # the predicted arrival rate in next epoch lamda
        self.lamda = None
        # average service time
        # 设置为固定值
        # 测试 rand 工作负载平均服务时间为 10 ms 左右
        # 单位为 ms
        self.miu = 10
        # the number of disks in next epoch
        self.next_disk_num = self.curr_disk_num

        # get values
        self.get_predicted_arrival_rate()
        self.next_disk_num = self.get_next_disk_num()

        # 待启动磁盘个数
        self.power_on_disk_num = self.next_disk_num - self.curr_disk_num

    '''
    name: get_predicted_arrival_rate
    msg: 获取 the predicted arrival rate in next epoch lamda
    param {*} self
    return {*}
    '''
    def get_predicted_arrival_rate(self):
        # 预测下一个时间间隔的 lamda
        # self.lamda = armax_func(self.predicts, 1)
        self.lamda = 10
        return self.lamda


    def get_next_disk_num(self):
        t = self.curr_disk_num / (self.miu * self.curr_disk_num) - self.lamda
        print(t)
        while t > self.t_up:
            self.next_disk_num = self.next_disk_num + self.n_step
            t = self.next_disk_num / (self.miu * self.next_disk_num - self.lamda)
            print(t)
        while t < self.t_down:
            self.next_disk_num = self.next_disk_num - self.n_step
            # 刚开始创建的是最小的 RAID，所以要保证最少磁盘个数至少是 4
            if (self.next_disk_num < self.num_disks):
                self.next_disk_num = self.num_disks
                break
            t = self.next_disk_num / (self.miu * self.next_disk_num - self.lamda)
        return self.next_disk_num
    
    def get_power_on_disk_num(self):
        return self.power_on_disk_num