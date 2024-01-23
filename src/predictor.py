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

    def __init__(self, config:Config, predicts, curr_disk_num):
        # the predict array
        self.predicts = predicts
        # number of init disks
        self.num_disks = config.get_num_disks()
        # number of max disks
        self.max_disks = config.get_max_disks()
        # the number of disks in current epoch
        self.curr_disk_num = curr_disk_num
        # the limited average response time
        self.t_up = config.get_t_up()
        self.t_down = config.get_t_down()
        # N_step
        self.n_step = config.get_n_step()
        self.time_interval = config.get_time_interval()
        # the predicted arrival rate in next epoch lamda
        self.lamda = None
        # average service time
        # 设置为固定值
        # 测试 rand 工作负载平均服务时间为 10 ms 左右
        # 单位为 ms
        self.miu = config.get_miu()
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
        self.lamda = armax_func(self.predicts, 1)
        self.lamda = self.lamda / self.time_interval
        print("预测到达率 lambda:", self.lamda)
        return self.lamda


    def get_next_disk_num(self):
        t = self.curr_disk_num / (self.miu * self.curr_disk_num - self.lamda)
        t = abs(t)
        print("初始预测响应时间 t:", t)
        while t > self.t_up:
            # next disk num 存在 RAID 磁盘个数上限
            self.next_disk_num = self.next_disk_num + self.n_step
            if (self.next_disk_num > self.max_disks):
                self.next_disk_num = self.max_disks
                break
            t = self.next_disk_num / (self.miu * self.next_disk_num - self.lamda)
            t = abs(t)
            print("添加磁盘后预测响应时间 t:", t)
        while t < self.t_down:
            self.next_disk_num = self.next_disk_num - self.n_step
            # 刚开始创建的是最小的 RAID，所以要保证最少磁盘个数至少是 4
            if (self.next_disk_num < self.num_disks):
                self.next_disk_num = self.num_disks
                break
            t = self.next_disk_num / (self.miu * self.next_disk_num - self.lamda)
            t = abs(t)
            print("减少磁盘后预测响应时间 t:", t)
        return self.next_disk_num
    
    def get_power_on_disk_num(self):
        return self.power_on_disk_num