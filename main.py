'''
Author: Chen Shi
Date: 2023-11-23 10:48:01
Description: main function
'''

import sys

from src.controller import Controller
# from test import Controller
from src.config import Config

config_file = './config.yaml'

def main():
    # 创建一个 Config 实例，读取 config.yaml 并保存配置参数，传入 Controller 中 
    config = Config(config_file)

    print('')
    print(f'Currently running: {config.get_trace_name()} trace in {config.get_mode()} mode')
    print('')

    # 写入文件
    save_stdout = sys.stdout
    sys.stdout = open(f'./output/3. optimized/o_{config.get_trace_name()}_{config.get_mode()}.txt', "w", encoding = 'utf-8')
    
    controller = Controller(config)
    
    sys.stdout = save_stdout

    return


if __name__ == "__main__":
    main()
    print('')
    print("Completed")
    print('')