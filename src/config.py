'''
Author: Chen Shi
Date: 2023-12-18 14:44:55
Description: Config class to save config
'''


import yaml

class Config:
    def __init__(self, file_name = './config.yaml'):
        self.read_configs(file_name)


    '''
    name: read_configs
    msg: 读取 config.yaml 配置文件
    param {*} self
    param {*} file_name: 配置文件路径
    return {*}
    '''
    def read_configs(self, file_name = './config.yaml'):
        with open(file_name, 'r') as config_file:
            configs = yaml.load(config_file.read(), Loader = yaml.FullLoader)
            # print(configs)
        # unit: ms; Byte
        # default configs
        self.__seed = configs['seed']
        self.__min_disks = configs['min_disks']
        self.__max_disks = configs['max_disks']
        self.__block_size = configs['block_size']
        self.__chunk_size = configs['chunk_size']
        self.__req_size = configs['req_size']
        self.__raid_level = configs['raid_level']
        # 'LS' or 'LA'
        self.__raid5_type = configs['raid5_type']
        self.__print_logical = configs['print_logical']
        self.__print_physical = configs['print_physical']
        self.__print_stats = configs['print_stats']
        
        # Disk
        self.__num_tracks = configs['num_tracks']
        self.__blocks_per_track = configs['blocks_per_track']
        self.__seek_time = configs['seek_time']
        self.__xfer_time = configs['xfer_time']
        self.__queue_len = configs['queue_len']
        # self.__sleep_timeout = configs['sleep_timeout']

        # trace file path
        self.__raw_file = configs['raw_file']
        self.__process_file = '/'.join([self.__raw_file.split('/')[0], self.__raw_file.split('/')[1], 
                                '.'.join([self.__raw_file.split('/')[2].split('.')[0] + '_processed', 
                                          self.__raw_file.split('/')[2].split('.')[1]])])
        self.__processed = configs['processed']

        self.__time_interval = configs['time_interval']
        # self.__miu = configs['miu']

        # predictor 
        self.__t_up = configs['t_up']
        self.__t_down = configs['t_down']
        self.__n_step = configs['n_step']

        # raid mode
        self.__mode = configs['mode']

        # DEBUG
        self.__debug = configs['debug']

    
    def print_args(self):
        # unit: ms; Byte
        # default configs
        print("** CONFIGS **")
        print('')
        print("最小磁盘数:", self.__min_disks)
        print("最大磁盘数:", self.__max_disks)
        print("数据块大小:", self.__block_size)
        print("磁盘块大小:", self.__chunk_size)
        print("RAID 级别:", self.__raid_level)
        print("打印磁盘信息:", self.__print_stats)
        print('')
        
        # Disk
        # print("磁盘休眠超时:", self.__sleep_timeout)
        print("磁盘磁道数:", self.__num_tracks)
        print("每个磁道数据块数:", self.__blocks_per_track)
        print('')

        # trace file path
        print("原始 trace 文件:", self.__raw_file)
        print("处理 trace 文件:", self.__process_file)
        print('')

        print("时间窗口(ms):", self.__time_interval)

        # predictor 
        print("预测响应阈值上界(ms):", self.__t_up)
        print("预测响应阈值下界(ms):", self.__t_down)
        print("添加磁盘步长:", self.__n_step)
        print('')

        # raid mode
        print("RAID 模式:", self.__mode)
        
        print('')
        print("*************")
        print('')
        

    def get_seed(self):
        return self.__seed

    def get_min_disks(self):
        return self.__min_disks
    
    def get_max_disks(self):
        return self.__max_disks
    
    def get_block_size(self):
        return self.__block_size
    
    def get_chunk_size(self):
        return self.__chunk_size
    
    def get_req_size(self):
        return self.__req_size
    
    def get_raid_level(self):
        return self.__raid_level
    
    def get_raid5_type(self):
        return self.__raid5_type
    
    def get_print_logical(self):
        return self.__print_logical
    
    def get_print_physcial(self):
        return self.__print_physical
    
    def get_print_stats(self):
        return self.__print_stats
    
    def get_num_tracks(self):
        return self.__num_tracks

    def get_blocks_per_track(self):
        return self.__blocks_per_track
    
    def get_seek_time(self):
        return self.__seek_time
    
    def get_xfer_time(self):
        return self.__xfer_time
    
    def get_queue_len(self):
        return self.__queue_len

    def get_raw_file(self):
        return self.__raw_file

    def get_process_file(self):
        return self.__process_file
    
    def get_trace_name(self):
        file_name = str(self.get_raw_file())
        trace_name = file_name.split('/')[2].split('.')[0]
        return trace_name
    
    def get_processed(self):
        return self.__processed
    
    def get_time_interval(self):
        return self.__time_interval
    
    # def get_miu(self):
    #     return self.__miu
    
    def get_t_up(self):
        return self.__t_up
    
    def get_t_down(self):
        return self.__t_down
    
    def get_n_step(self):
        return self.__n_step
    
    def get_mode(self):
        return self.__mode
    
    def get_debug(self):
        return self.__debug