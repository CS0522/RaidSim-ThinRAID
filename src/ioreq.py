'''
Author: Chen Shi
Date: 2023-12-03 20:22:51
Description: IO request class
'''


class IOReq:
    # private 
    # time stamp
    timestamp = None
    # req disk number
    disk_num = None
    # read/write
    is_write = None
    # offset
    offset = None 
    # req size
    size = None

    def __init__(self, _timestamp, _disk_num, _is_write, _offset, _size):
        self.timestamp = _timestamp
        self.disk_num = _disk_num
        self.is_write = _is_write
        self.offset = _offset
        self.size = _size

    # def __init__(self):
    #     pass

    # timestamp, disknum, type, offset, size
    def get_info(self):
        return self.timestamp, self.disk_num, self.is_write, self.offset, self.size

    def set_info(self, _timestamp, _disk_num, _is_write, _offset, _size):
        self.timestamp = _timestamp
        self.disk_num = _disk_num
        self.is_write = _is_write
        self.offset = _offset
        self.size = _size