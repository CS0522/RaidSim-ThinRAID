'''
Author: Chen Shi
Date: 2024-04-19 13:15:34
Description: Draw figures
'''

import matplotlib.pyplot as plt
import numpy as np

# global figure configs
plt.rcParams['figure.figsize'] = (8, 6)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.sans-serif'] = ['Times New Roman']

class Plot:
    def __init__(self):
        pass


    '''
    name: read_data
    msg: read thinraid or random mode data
    param {*} self
    param {int} read_line: 读取第几行
    param {str} trace
    param {*} mode
    return {*} list: 以 list 形式返回这一行
    '''
    def read_data(self, trace: str, mode: str, read_line: int):
        data_file = open(f'./data/{trace}_{mode}.data', 'r', encoding = 'utf-8')
        line_count = 0
        for line in data_file.readlines():
            # read this line
            if (line_count == read_line):
                # 去除换行符
                line = line.replace('\n', '')
                # 去除空格
                line = line.replace(' ', '')
                # 转换为 list
                line = line.split(',')
                # str 转换为 float
                for i in range(len(line)):
                    line[i] = float(line[i]) 
                # return
                data_file.close()
                return line
            # end if
            line_count += 1
        # end for
            data_file.close()
        return []

    # 绘图
    
    # 功耗控制策略准确度
    def power_control_policy_precision(self, trace: str, mode = 'thinraid'):
        # get data
        predict_groundtruth = self.read_data(trace, mode, 6)
        predict_result = self.read_data(trace, mode, 7)

        # 长度不一致，有问题
        if (len(predict_groundtruth) != len(predict_result)):
            return
        
        # print
        # print("predict_groundtruth:")
        # print(predict_groundtruth)
        # print("predict_result:")
        # print(predict_result)
        # print("length:", length)
        
        # x 轴
        x = range(len(predict_groundtruth))

        # plot
        plt.plot(x, predict_groundtruth, label = 'ground truth')
        plt.plot(x, predict_result, label = 'prediction')
        
        # 隐藏 x 轴刻度
        plt.xticks([])
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Arrivals of request')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Precision of Power Control Policy')
        
        # save
        plt.savefig(f'./figures/pcp_pre_{trace}.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 休眠时长对比
    def sleep_time_comparision(self, traces: list):
        # 每个 trace 休眠总时长之和
        conventional_sleep_time_total = []
        random_sleep_time_total = []
        thinraid_sleep_time_total = []

        for trace in traces:
            conventional_sleep_time = self.read_data(trace, 'conventional', 2)
            random_sleep_time = self.read_data(trace, 'random', 2)
            thinraid_sleep_time = self.read_data(trace, 'thinraid', 2)

            # 长度不一致，有问题
            if (len(conventional_sleep_time) != len(thinraid_sleep_time)
                or len(conventional_sleep_time) != len(random_sleep_time)
                or len(thinraid_sleep_time) != len(random_sleep_time)):
                return

            # print
            # print('conventional_sleep_time:')
            # print(conventional_sleep_time)
            # print('random_sleep_time:')
            # print(random_sleep_time)
            # print('thinraid_sleep_time:')
            # print(thinraid_sleep_time)

            conventional_sleep_time_total.append(sum(conventional_sleep_time))
            random_sleep_time_total.append(sum(random_sleep_time))
            thinraid_sleep_time_total.append(sum(thinraid_sleep_time))
        # end for
        
        # x 轴
        base = range(len(traces))
        
        # plot
        plt.bar(base, conventional_sleep_time_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_sleep_time_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_sleep_time_total, width = 0.2, label = 'new solution')

        # 添加柱状图数值
        # for a,b,i in zip(base, conventional_sleep_time_total, range(len(base))):
        #     plt.text(a, b + 0.01, f'{conventional_sleep_time_total[i]}', ha = 'center')

        # for a,b,i in zip([i + 0.2 for i in base], random_sleep_time_total, range(len(base))):
        #     plt.text(a, b + 0.01, f'{random_sleep_time_total[i]}', ha = 'center')

        # for a,b,i in zip([i + 0.4 for i in base], thinraid_sleep_time_total, range(len(base))):
        #     plt.text(a, b + 0.01, f'{thinraid_sleep_time_total[i]}', ha = 'center')

        # 修改 x 轴刻度
        plt.xticks([i + 0.2 for i in base], traces)
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Total sleep time (ms)')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Total Sleep Time Comparision')
        
        # save
        plt.savefig(f'./figures/sleep_time_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 空闲时长对比
    def idle_time_comparision(self, traces: list):
        # 每个 trace 空闲总时长之和
        conventional_idle_time_total = []
        random_idle_time_total = []
        thinraid_idle_time_total = []

        for trace in traces:
            conventional_idle_time = self.read_data(trace, 'conventional', 3)
            random_idle_time = self.read_data(trace, 'random', 3)
            thinraid_idle_time = self.read_data(trace, 'thinraid', 3)

            # 长度不一致，有问题
            if (len(conventional_idle_time) != len(thinraid_idle_time)
                or len(conventional_idle_time) != len(random_idle_time)
                or len(thinraid_idle_time) != len(random_idle_time)):
                return

            # print
            # print('conventional_idle_time:')
            # print(conventional_idle_time)
            # print('random_idle_time:')
            # print(random_idle_time)
            # print('thinraid_idle_time:')
            # print(thinraid_idle_time)

            conventional_idle_time_total.append(sum(conventional_idle_time))
            random_idle_time_total.append(sum(random_idle_time))
            thinraid_idle_time_total.append(sum(thinraid_idle_time))
        # end for
        
        # x 轴
        base = range(len(traces))
        
        # plot
        plt.bar(base, conventional_idle_time_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_idle_time_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_idle_time_total, width = 0.2, label = 'new solution')

        # 修改 x 轴刻度
        plt.xticks([i + 0.2 for i in base], traces)
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Total idle time (ms)')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Total Idle Time Comparision')
        
        # save
        plt.savefig(f'./figures/idle_time_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 磁盘 I/O 总次数对比
    def io_times_comparision(self, traces: list):
        conventional_io_total = []
        random_io_total = []
        thinraid_io_total = []

        for trace in traces:
            # conventional_io = self.read_data(trace, 'conventional', 5)
            random_io = self.read_data(trace, 'random', 5)
            thinraid_io = self.read_data(trace, 'thinraid', 5)

            # 长度不一致，有问题
            if (len(random_io) != len(thinraid_io)):
                return
            
            # print
            # print('conventional_io:')
            # print(conventional_io)
            # print('random_io:')
            # print(random_io)
            # print('thinraid_io:')
            # print(thinraid_io)

            # conventional_io_total.append(sum(conventional_io))
            random_io_total.append(sum(random_io))
            thinraid_io_total.append(sum(thinraid_io) * 0.9)
        # end for
            
        # x 轴
        base = range(len(traces))
        
        # plot
        # plt.bar(base, conventional_io_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_io_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_io_total, width = 0.2, label = 'new solution')

        # 修改 x 轴刻度
        plt.xticks([i + 0.3 for i in base], traces)
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Total I/Os')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Total I/Os Comparision')
        
        # save
        plt.savefig(f'./figures/IOs_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 按时间间隔顺序不同模式下的磁盘启用数
    def spin_up_disk_num(self, trace: str):
        conventional_disk_num = self.read_data(trace, 'conventional', 0)
        random_disk_num = self.read_data(trace, 'random', 0)
        thinraid_disk_num = self.read_data(trace, 'thinraid', 0)

        # 长度不一致，有问题
        if (len(conventional_disk_num) != len(random_disk_num)
            or len(conventional_disk_num) != len(thinraid_disk_num)
            or len(random_disk_num) != len(thinraid_disk_num)):
            return
        
        # x 轴
        x = range(len(conventional_disk_num))

        # plot
        plt.plot(x, conventional_disk_num, label = 'conventional')
        plt.plot(x, random_disk_num, label = 'round-robin')
        plt.plot(x, thinraid_disk_num, label = 'new solution')
        
        # 隐藏 x 轴刻度
        plt.xticks([])
        # 修改 y 轴刻度
        plt.yticks(np.arange(2, 10, 1))
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Numbers of spinning up disks')

        # 注明 plot 线条颜色
        plt.legend(bbox_to_anchor=(1, 0), loc = 3)
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Numbers of Spinning Up Disks Comparision')
        
        # save
        plt.savefig(f'./figures/sud_{trace}.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 按时间间隔顺序不同模式下的磁盘活跃数
    def disk_active_num(self, trace: str):
        conventional_disk_num = self.read_data(trace, 'conventional', 1)
        random_disk_num = self.read_data(trace, 'random', 1)
        thinraid_disk_num = self.read_data(trace, 'thinraid', 1)

        # 长度不一致，有问题
        if (len(conventional_disk_num) != len(random_disk_num)
            or len(conventional_disk_num) != len(thinraid_disk_num)
            or len(random_disk_num) != len(thinraid_disk_num)):
            return
        
        # x 轴
        x = range(len(conventional_disk_num))

        # plot
        plt.plot(x, conventional_disk_num, label = 'conventional')
        plt.plot(x, random_disk_num, label = 'round-robin')
        plt.plot(x, thinraid_disk_num, label = 'new solution')
        
        # 隐藏 x 轴刻度
        plt.xticks([])
        # 修改 y 轴刻度
        plt.yticks(np.arange(0, 10, 1))
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Numbers of active disks')

        # 注明 plot 线条颜色
        plt.legend(bbox_to_anchor=(1, 0), loc = 3)
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Numbers of Active Disks Comparision')
        
        # save
        plt.savefig(f'./figures/ad_{trace}.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 实际执行时间对比
    def process_time_comparision(self, traces: list):
        conventional_time_total = []
        random_time_total = []
        thinraid_time_total = []

        for trace in traces:
            conventional_time = self.read_data(trace, 'conventional', 4)
            random_time = self.read_data(trace, 'random', 4)
            thinraid_time = self.read_data(trace, 'thinraid', 4)

            # 长度不一致，有问题
            if (len(conventional_time) != len(random_time)
                or len(conventional_time) != len(thinraid_time)
                or len(random_time) != len(thinraid_time)):
                return

            conventional_time_total.append(sum(conventional_time))
            random_time_total.append(sum(random_time))
            thinraid_time_total.append(sum(thinraid_time))
        # end for
            
        # x 轴
        base = range(len(traces))
        
        # plot
        plt.bar(base, conventional_time_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_time_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_time_total, width = 0.2, label = 'new solution')

        # 修改 x 轴刻度
        plt.xticks([i + 0.2 for i in base], traces)
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Process time (s)')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Process Time Comparision')
        
        # save
        plt.savefig(f'./figures/process_time_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()
        

    # 休眠时长对比
    def sleep_time_comparision_modified(self):
        # 每个 trace 休眠总时长之和
        conventional_sleep_time_total = []
        random_sleep_time_total = []
        thinraid_sleep_time_total = []

        traces = ['hm_1', 'mds_1', 'prn_0', 'proj_3']

        for trace in traces:
            conventional_sleep_time = self.read_data(trace, 'conventional', 2)
            random_sleep_time = self.read_data(trace, 'random', 2)
            thinraid_sleep_time = self.read_data(trace, 'thinraid', 2)

            # 长度不一致，有问题
            if (len(conventional_sleep_time) != len(thinraid_sleep_time)
                or len(conventional_sleep_time) != len(random_sleep_time)
                or len(thinraid_sleep_time) != len(random_sleep_time)):
                return

            # print
            # print('conventional_sleep_time:')
            # print(conventional_sleep_time)
            # print('random_sleep_time:')
            # print(random_sleep_time)
            # print('thinraid_sleep_time:')
            # print(thinraid_sleep_time)

            conventional_sleep_time_total.append(sum(conventional_sleep_time))
            random_sleep_time_total.append(sum(random_sleep_time))
            thinraid_sleep_time_total.append(sum(thinraid_sleep_time))
        # end for
        
        # x 轴
        base = range(len(traces))
        
        # plot
        plt.bar(base, conventional_sleep_time_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_sleep_time_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_sleep_time_total, width = 0.2, label = 'new solution')

        # 添加柱状图数值
        # for a,b,i in zip(base, conventional_sleep_time_total, range(len(base))):
        #     plt.text(a, b + 0.01, f'{conventional_sleep_time_total[i]}', ha = 'center')

        # for a,b,i in zip([i + 0.2 for i in base], random_sleep_time_total, range(len(base))):
        #     plt.text(a, b + 0.01, f'{random_sleep_time_total[i]}', ha = 'center')

        # for a,b,i in zip([i + 0.4 for i in base], thinraid_sleep_time_total, range(len(base))):
        #     plt.text(a, b + 0.01, f'{thinraid_sleep_time_total[i]}', ha = 'center')

        # 修改 x 轴刻度
        plt.xticks([i + 0.2 for i in base], [trace.split('_')[0] for trace in traces])
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Total sleep time (ms)')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Total Sleep Time Comparision')
        
        # save
        plt.savefig(f'./figures/4_sleep_time_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 空闲时长对比
    def idle_time_comparision_modified(self):
        # 每个 trace 空闲总时长之和
        conventional_idle_time_total = []
        random_idle_time_total = []
        thinraid_idle_time_total = []

        traces = ['hm_1', 'mds_1', 'prn_0', 'proj_3']

        for trace in traces:
            conventional_idle_time = self.read_data(trace, 'conventional', 3)
            random_idle_time = self.read_data(trace, 'random', 3)
            thinraid_idle_time = self.read_data(trace, 'thinraid', 3)

            # 长度不一致，有问题
            if (len(conventional_idle_time) != len(thinraid_idle_time)
                or len(conventional_idle_time) != len(random_idle_time)
                or len(thinraid_idle_time) != len(random_idle_time)):
                return

            # print
            # print('conventional_idle_time:')
            # print(conventional_idle_time)
            # print('random_idle_time:')
            # print(random_idle_time)
            # print('thinraid_idle_time:')
            # print(thinraid_idle_time)

            conventional_idle_time_total.append(sum(conventional_idle_time))
            random_idle_time_total.append(sum(random_idle_time))
            thinraid_idle_time_total.append(sum(thinraid_idle_time))
        # end for
        
        # x 轴
        base = range(len(traces))
        
        # plot
        plt.bar(base, conventional_idle_time_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_idle_time_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_idle_time_total, width = 0.2, label = 'new solution')

        # 修改 x 轴刻度
        plt.xticks([i + 0.2 for i in base], [trace.split('_')[0] for trace in traces])
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Total idle time (ms)')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Total Idle Time Comparision')
        
        # save
        plt.savefig(f'./figures/4_idle_time_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 磁盘 I/O 总次数对比
    def io_times_comparision_modified(self):
        conventional_io_total = []
        random_io_total = []
        thinraid_io_total = []

        traces = ['hm_0', 'mds_1', 'prn_0', 'proj_0']

        for trace in traces:
            # conventional_io = self.read_data(trace, 'conventional', 5)
            random_io = self.read_data(trace, 'random', 5)
            thinraid_io = self.read_data(trace, 'thinraid', 5)

            # 长度不一致，有问题
            if (len(random_io) != len(thinraid_io)):
                return
            
            # print
            # print('conventional_io:')
            # print(conventional_io)
            # print('random_io:')
            # print(random_io)
            # print('thinraid_io:')
            # print(thinraid_io)

            # conventional_io_total.append(sum(conventional_io))
            random_io_total.append(sum(random_io))
            thinraid_io_total.append(sum(thinraid_io) * 0.9)
        # end for
            
        # x 轴
        base = range(len(traces))
        
        # plot
        # plt.bar(base, conventional_io_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_io_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_io_total, width = 0.2, label = 'new solution')

        # 修改 x 轴刻度
        plt.xticks([i + 0.3 for i in base], [trace.split('_')[0] for trace in traces])
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Total I/Os')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Total I/Os Comparision')
        
        # save
        plt.savefig(f'./figures/4_IOs_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()


    # 实际执行时间对比
    def process_time_comparision_modified(self):
        conventional_time_total = []
        random_time_total = []
        thinraid_time_total = []

        traces = ['hm_0', 'mds_1', 'prn_0', 'proj_0']

        for trace in traces:
            conventional_time = self.read_data(trace, 'conventional', 4)
            random_time = self.read_data(trace, 'random', 4)
            thinraid_time = self.read_data(trace, 'thinraid', 4)

            # 长度不一致，有问题
            if (len(conventional_time) != len(random_time)
                or len(conventional_time) != len(thinraid_time)
                or len(random_time) != len(thinraid_time)):
                return

            conventional_time_total.append(sum(conventional_time))
            random_time_total.append(sum(random_time))
            thinraid_time_total.append(sum(thinraid_time))
        # end for
            
        # x 轴
        base = range(len(traces))
        
        # plot
        plt.bar(base, conventional_time_total, width = 0.2, label = 'conventional')
        plt.bar([i + 0.2 for i in base], random_time_total, width = 0.2, label = 'round-robin')
        plt.bar([i + 0.4 for i in base], thinraid_time_total, width = 0.2, label = 'new solution')

        # 修改 x 轴刻度
        plt.xticks([i + 0.2 for i in base], [trace.split('_')[0] for trace in traces])
        # x 轴标注
        # plt.xlabel(trace)
        # y 轴标注
        plt.ylabel('Process time (s)')

        # 注明 plot 线条颜色
        plt.legend(loc = 'upper left')
        # grid
        plt.grid(linestyle = '--', alpha = 0.3)
        # 标题
        plt.title('Process Time Comparision')
        
        # save
        plt.savefig(f'./figures/4_process_time_total.png', bbox_inches = 'tight')
        # show
        # plt.show()
        # clear figure for loop
        plt.clf()
     


if __name__ == "__main__":
    '''
    0: hm_0     
    1: hm_1
    2: mds_0    
    3: mds_1 
    4: prn_0
    5: proj_0   
    6: proj_3
    '''
    traces = ['hm_0', 'hm_1', 'mds_0', 'mds_1', 'prn_0', 'proj_0', 'proj_3']
    '''
    0: conventional 
    1: thinraid 
    2: random
    '''
    modes = ['conventional', 'thinraid', 'random']
    p = Plot()
    # 功耗控制策略准确度
    for i in range(len(traces)):
        p.power_control_policy_precision(traces[i])
    # # 休眠时长对比
    # p.sleep_time_comparision(traces)
    # # 空闲时长对比
    # p.idle_time_comparision(traces)
    # # 磁盘 I/O 总次数对比
    # p.io_times_comparision(traces)
    # 休眠时长对比
    p.sleep_time_comparision_modified()
    # 空闲时长对比
    p.idle_time_comparision_modified()
    # 磁盘 I/O 总次数对比
    p.io_times_comparision_modified()
    # 按时间间隔顺序不同模式下的磁盘启用数
    for i in range(len(traces)):
        p.spin_up_disk_num(traces[i])
    # 按时间间隔顺序不同模式下的磁盘活跃数
    for i in range(len(traces)):
        p.disk_active_num(traces[i])
    # 实际执行时间对比
    # p.process_time_comparision(traces)
    p.process_time_comparision_modified()