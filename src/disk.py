'''
Author: Chen Shi
Date: 2023-11-23 11:15:01
Description: Disk class
'''

from src.config import Config

class Disk:
    # 寻道时间，数据传输时间，调度队列长度
    # TODO 这里 seek time 被设置为固定的
    def __init__(self, config:Config):
        # 单位为 ms
        # 这几个可能用不上
        self.seek_time = config.get_seek_time()
        self.xfer_time = config.get_xfer_time()
        self.queue_len = config.get_queue_len()

        # current location 设置为 -10000，这样第一个 read 都需要 seek
        self.curr_addr = -10000

        # queue
        self.queue = []

        # TODO 磁盘休眠相关
        # 活跃（包含空闲状态，活跃指磁盘在运行） -> 休眠
        # 磁盘当前空闲时长（无 IO 请求进入）：相对
        # 用于判断是否休眠超时、可以进入休眠状态
        self.idle_time = 0
        # 磁盘空闲总时长（不包含休眠）：相对
        self.idle_time_total = 0
        # 磁盘休眠总时长：相对
        self.sleep_time_total = 0
        # 磁盘活跃总时长：相对
        self.active_time_total = 0
        # 磁盘进入空闲状态时间点：绝对
        self.idle_time_points = []
        # 磁盘进入休眠状态时间点：绝对
        self.sleep_time_points = []
        # 磁盘进入活跃状态时间点：绝对
        self.active_time_points = []
        # 每个空闲段的空闲时长：相对
        # 应该都等于一个休眠超时
        # 每个休眠段的休眠时长：相对
        self.sleep_time_periods = []
        # 每个活跃段的活跃时长：相对
        self.active_time_periods = []
        # 进入休眠状态的时间点：绝对
        self.sleep_timestamp = 0
        # 进入活跃状态的时间点：绝对
        self.active_timestamp = 0
        # 最近的 req 的时间：绝对
        self.latest_req_timestamp = 0
        # 磁盘休眠超时
        self.sleep_timeout = config.get_time_interval()
        # 是否活跃磁盘
        self.active = False
        # 是否启用过
        self.spin_up_once = False

        # trace 文件开始时间点
        self.timestamp_start = 0

        # disk specs
        self.num_tracks = config.get_num_tracks()
        self.blocks_per_track = config.get_blocks_per_track()
        self.blocks_per_disk = self.num_tracks * self.blocks_per_track

        # disk stats 统计
        self.count_IO = 0
        self.count_seq = 0
        self.countNseq = 0
        self.count_rand = 0
        self.util_time = 0

    # 获取磁盘统计信息
    def get_io_stats(self):
        return self.count_IO, self.count_seq, self.countNseq, self.count_rand, self.util_time
    
    def get_status_stats(self):
        # 活跃状态
        # 休眠总时长，时间点，段时长
        # 活跃总时长，时间点，段时长
        return self.active, self.sleep_time_total, self.sleep_time_points, self.sleep_time_periods, self.active_time_total, self.active_time_points, self.active_time_periods

    '''
    name: init_disk
    msg: 初始化磁盘操作
    param {*} self
    param {*} timestamp: 时间戳
    return {*}
    '''
    def init_disk(self, timestamp):
        # timestamp 是起始时间点
        self.timestamp_start = timestamp
        self.active_time_points.append(timestamp)
        self.active_timestamp = timestamp
        self.active = True
        # 标记为启用过
        self.spin_up_once = True


    '''
    name: end_disk
    msg: trace 文件结束后关闭磁盘操作
    param {*} self
    param {*} timestamp: 时间戳
    return {*}
    '''
    def end_disk(self, timestamp):
        if (self.spin_up_once == False):
            return
        # 处于活跃状态
        if (self.active == True):
            self.hibernate_disk(timestamp)
        # 处于休眠状态
        else:
            # 增加休眠时长
            self.sleep_time_total += timestamp - self.sleep_timestamp
            self.sleep_time_periods.append(timestamp - self.sleep_timestamp)



    '''
    name: wake_up_disk
    msg: 唤醒磁盘的一些操作
    param {*} self
    param {*} timestamp: 时间戳
    return {*}
    '''
    def wake_up_disk(self, timestamp):
        # 记录进入活跃状态时间点
        self.active_time_points.append(timestamp)
        self.active_timestamp = timestamp
        # 本次休眠时长
        # 如果是 trace 文件刚开始，那么 latest_req_timestamp == 0
        curr_sleep_time = timestamp - self.sleep_timestamp
        # 磁盘休眠总时长增加
        self.sleep_time_total += curr_sleep_time
        # 添加磁盘休眠时间段
        self.sleep_time_periods.append(curr_sleep_time)
        # 记录最新到来的 req
        self.latest_req_timestamp = timestamp


    '''
    name: hibernate_disk
    msg: 休眠磁盘的一些操作
    param {*} self
    param {*} timestamp: 时间戳
    return {*}
    '''
    def hibernate_disk(self, timestamp):
        # 修改活跃状态
        self.active = False
        # 得确保进入休眠状态满足休眠超时
        # 结束活跃状态
        # 记录进入休眠状态时间点
        # 如果这个时间戳超过休眠超时
        if (timestamp - self.latest_req_timestamp > self.sleep_timeout):
            timestamp = self.latest_req_timestamp + self.sleep_timeout
            # 如果是 trace 文件刚开始，那么 latest_req_timestamp == 0
            if (self.latest_req_timestamp == 0):
                timestamp += self.timestamp_start
        self.sleep_timestamp = timestamp
        self.sleep_time_points.append(timestamp)
        # 本次活跃时长
        curr_active_time = timestamp - self.active_timestamp
        # 磁盘活跃总时长增加
        self.active_time_total += curr_active_time
        # 添加磁盘活跃时间段
        self.active_time_periods.append(curr_active_time)
        # 当前空闲时长
        self.idle_time_total += self.idle_time
        self.idle_time = 0


    def update_latest_req_timestamp(self, timestamp):
        self.latest_req_timestamp = timestamp


    # I/O requests arrive
    # TODO 添加休眠、活跃时间统计
    # timestamp 是某个 req 的时间戳
    def enqueue(self, addr, timestamp):
        # 如果是休眠状态，唤醒磁盘
        if (self.active == False):
            self.active = True
            self.wake_up_disk(timestamp)

        # 更新最新到来的 req
        self.update_latest_req_timestamp(timestamp)

        # addr 必须小于一个磁盘上的块数
        assert(addr < self.blocks_per_disk)

        self.count_IO += 1

        # 检查该 I/O 请求是否在当前同一个 track 上
        curr_track = self.curr_addr / self.num_tracks
        new_track = addr / self.num_tracks

        diff = abs(addr - self.curr_addr)

        # on the same track
        # 如果当前 track == 新的 track，或者 addr 的差小于 track 上的 block 数
        if (curr_track == new_track) or (diff < self.blocks_per_track):
            if diff == 1:
                self.count_seq += 1
            else:
                self.countNseq += 1
            self.util_time += (diff * self.xfer_time)
        # on the different tracks
        else:
            self.count_rand += 1
            # 这里 seek time 是被设置为固定的
            self.util_time += (self.xfer_time + self.seek_time)
        # 请求处理后当前磁头位置随之改变
        self.curr_addr = addr

    def get_elapsed(self):
        return self.util_time

# end Disk class