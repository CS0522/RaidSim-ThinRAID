'''
Author: Chen Shi
Date: 2023-11-23 11:15:01
Description: Disk class
'''


class Disk:
    # 寻道时间，数据传输时间，调度队列长度
    # TODO 这里 seek time 被设置为固定的
    def __init__(self, seek_time = 10, xfer_time = 0.1, queue_len = 8, 
                 num_tracks = 100, blocks_per_track = 100):
        # 单位为 ms 
        self.seek_time = seek_time
        self.xfer_time = xfer_time
        self.queue_len = queue_len

        # current location 设置为 -10000，这样第一个 read 都需要 seek
        self.curr_addr = -10000

        # queue
        self.queue = []

        # disk specs
        self.num_tracks = num_tracks
        self.blocks_per_track = blocks_per_track
        self.blocks_per_disk = self.num_tracks * self.blocks_per_track

        # disk stats 统计
        self.count_IO = 0
        self.count_seq = 0
        self.countNseq = 0
        self.count_rand = 0
        self.util_time = 0

        # 是否活跃磁盘
        self.active = True

    # 获取统计信息
    def get_stats(self):
        return self.count_IO, self.count_seq, self.countNseq, self.count_rand, self.util_time
    
    # I/O 请求到来
    def enqueue(self, addr):
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