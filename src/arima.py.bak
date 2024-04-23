'''
Author: Chen Shi
Date: 2023-12-05 16:59:07
Description: 
'''

import pandas as pd
import numpy as np
import statsmodels.api as sm

# 测验数据
data = [0, 0, 0, 0, 0, 18, 232, 22, 0, 17, 14, 0, 0, 13, 0, 0, 7237]

def armax_func(data, forecast_num):
    '''
    data 至少要 17 个数据
    '''
    data = pd.Series(data)
    # 模型
    arma_mod70 = sm.tsa.ARMA(data, (1, 0, 0)).fit(disp = False)
    # print(arma_mod70.summary())
    # 返回预测结果、标准误差、置信区间
    (arr1, arr2, arr3) = arma_mod70.forecast(forecast_num)
    return arr1[0]


if __name__ == "__main__":
    armax_func(data, 1)