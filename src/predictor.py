'''
Author: Chen Shi
Date: 2023-12-04 00:37:08
Description: Predictor class
'''

from src.arima import arima_model
from src.config import Config

class Predictor:
    def __init__(self, config:Config, curr_disk_num, reqs_served:int, timers:list, 
                 predicts:list, 
                 predict_groundtruth:list, predict_result:list):
        # the predict list
        self.predicts = predicts
        self.predict_groundtruth = predict_groundtruth
        self.predict_result = predict_result
        
        # number of init disks
        self.num_disks = config.get_min_disks()
        # number of max disks
        self.max_disks = config.get_max_disks()
        # the number of disks in current epoch
        self.curr_disk_num = curr_disk_num
        # the limited average response time
        self.t_up = config.get_t_up()
        self.t_down = config.get_t_down()

        self.n_step = config.get_n_step()
        self.time_interval = config.get_time_interval()
        self.print_stats = config.get_print_stats()

        self.timers = timers
        # 下一个时间间隔的预测请求到达率
        self.lamda = None
        # miu 设置为到上一个时间间隔为止的平均请求服务率
        self.miu = reqs_served / sum(self.timers)
        # the number of disks in next epoch
        self.next_disk_num = self.curr_disk_num

        # get values
        self.get_predicted_arrival_rate()
        self.next_disk_num = self.get_next_disk_num()

        # 待启动磁盘个数
        self.adjust_disk_num = self.next_disk_num - self.curr_disk_num


    '''
    name: get_predicted_arrival_rate
    msg: 下一个时间间隔的预测请求到达率
    param {*} self
    return {*} lamda: predicted arrival rate
    '''
    def get_predicted_arrival_rate(self):
        # 预测下一个时间间隔的 lambda
        self.lamda = arima_model(self.predicts)
        if (self.print_stats == True):
            print('')
            print("预测模型结果:", self.lamda)
        
        # 加入 predict_groundtruth 和 predict_result
        # lambda 小于 0，预测错误，不加入预测结果列表
        if (self.lamda >= 0):
            self.predict_groundtruth.append(self.predicts[-1])
            self.predict_result.append(self.lamda)
            
        # self.lamda = self.lamda / self.time_interval
        self.lamda = self.lamda / ((sum(self.timers) / len(self.timers)))
        if (self.print_stats == True):
            print("平均请求服务率 miu (已处理请求数 / 已经过时间):", self.miu)
            print("预测请求到达率 lambda (请求数 / 单位时间):", self.lamda)
        return self.lamda


    def get_next_disk_num(self):
        # 预测出现错误
        if (self.lamda < 0):
            if (self.print_stats == True):
                print("预测数据无法拟合，预测结果错误")
            return self.next_disk_num

        t = self.curr_disk_num / (self.miu * self.curr_disk_num - self.lamda)
        t = abs(t) * 10000
        if (self.print_stats == True):
            print("初始预测响应时间 t:", t)
        while t > self.t_up:
            # next disk num 存在 RAID 磁盘个数上限
            self.next_disk_num = self.next_disk_num + self.n_step
            if (self.next_disk_num > self.max_disks):
                self.next_disk_num = self.max_disks
                break
            t = self.next_disk_num / (self.miu * self.next_disk_num - self.lamda)
            t = abs(t) * 10000
            if (self.print_stats == True):
                print("添加磁盘后预测响应时间 t:", t)
        while t < self.t_down:
            self.next_disk_num = self.next_disk_num - self.n_step
            # 刚开始创建的是最小的 RAID，所以要保证最少磁盘个数至少是 4
            if (self.next_disk_num < self.num_disks):
                self.next_disk_num = self.num_disks
                break
            t = self.next_disk_num / (self.miu * self.next_disk_num - self.lamda)
            t = abs(t) * 10000
            if (self.print_stats == True):
                print("减少磁盘后预测响应时间 t:", t)
        return self.next_disk_num
    
    
    def get_adjust_disk_num(self):
        return self.adjust_disk_num