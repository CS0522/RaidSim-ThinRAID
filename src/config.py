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
        self.__num_disks = configs['num_disks']
        self.__block_size = configs['block_size']
        self.__chunk_size = configs['chunk_size']
        self.__num_reqs = configs['num_reqs'] 
        self.__req_size = configs['req_size']
        # 'rand' or 'seq'
        self.__workload = configs['workload']
        # 0.0 ~ 1.0
        self.__write_frac = configs['write_frac']
        self.__rand_range = configs['rand_range']
        self.__raid_level = configs['raid_level']
        # 'LS' or 'LA'
        self.__raid5_type = configs['raid5_type']
        self.__timing = configs['timing']
        self.__solve = configs['solve']
        
        # Disk
        self.__num_tracks = configs['num_tracks']
        self.__blocks_per_track = configs['blocks_per_track']
        self.__seek_time = configs['seek_time']
        self.__xfer_time = configs['xfer_time']
        self.__queue_len = configs['queue_len']

        # trace file path
        self.__raw_file = configs['raw_file']
        self.__process_file = configs['process_file']

        # predictor 
        self.__t_up = configs['t_up']
        self.__t_down = configs['t_down']
        self.__n_step = configs['n_step']
        

    def get_seed(self):
        return self.__seed

    def get_num_disks(self):
        return self.__num_disks
    
    def get_block_size(self):
        return self.__block_size
    
    def get_chunk_size(self):
        return self.__chunk_size
    
    def get_num_reqs(self):
        return self.__num_reqs
    
    def get_req_size(self):
        return self.__req_size
    
    def get_workload(self):
        return self.__workload
    
    def get_write_frac(self):
        return self.__write_frac
    
    def get_rand_range(self):
        return self.__rand_range
    
    def get_raid_level(self):
        return self.__raid_level
    
    def get_raid5_type(self):
        return self.__raid5_type
    
    def get_timing(self):
        return self.__timing
    
    def get_solve(self):
        return self.__solve
    
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
    
    def get_t_up(self):
        return self.__t_up
    
    def get_t_down(self):
        return self.__t_down
    
    def get_n_step(self):
        return self.__n_step