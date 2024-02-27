'''
Author: Chen Shi
Date: 2023-12-07 17:08:59
Description: Block class.
'''


# 用来放在 block table 中存储 block 的一些信息
class Block:
    def __init__(self, curr_row, curr_col):
        # data 标志位
        # 0, 1
        self.data = 0
        # 热度值
        self.hot = 0
        # 修改标志位
        self.modified = False
        # 是否重新映射
        self.remap = False
        self.curr_index = {'row': curr_row, 'col': curr_col}
        # 新的映射到 block table 的位置
        self.remap_index = {'row': -1, 'col': -1}
        # 是否是被映射的（是否具有原数据块）
        self.has_old = False
        # 如果重新映射，原先的 index
        self.old_index = {'row': -1, 'col': -1}

    def set_data(self, new_val):
        self.data = new_val

    def set_hot(self, new_val):
        self.hot = new_val

    def set_modified(self, new_val):
        self.modified = new_val

    def set_remap(self, new_val):
        self.remap = new_val

    def set_curr_index(self, curr_row, curr_col):
        self.curr_index['row'] = curr_row
        self.curr_index['col'] = curr_col

    def set_remap_index(self, new_row, new_col):
        self.remap_index['row'] = new_row
        self.remap_index['col'] = new_col

    def set_has_old(self, new_val):
        self.has_old = new_val

    def set_old_index(self, old_row, old_col):
        self.old_index['row'] = old_row
        self.old_index['col'] = old_col

    def get_info(self):
        return self.hot, self.modified, self.remap, self.curr_index, self.remap_index, self.has_old, self.old_index