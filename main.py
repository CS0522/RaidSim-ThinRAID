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
    save_stdout = sys.stdout
    sys.stdout = open("./output/res.txt", "w", encoding='utf-8')
    with open("./output/block_table.txt", "w") as block_table_txt:
        block_table_txt.truncate(0)
    with open("./output/hots.txt", "w") as hots_txt:
        hots_txt.truncate(0)

    # 创建一个 Config 实例，读取 config.yaml 并保存配置参数，传入 Controller 中 
    config = Config(config_file)
    
    controller = Controller(config)
    
    sys.stdout = save_stdout

    return

if __name__ == "__main__":
    main()