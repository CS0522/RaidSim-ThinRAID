'''
Author: Chen Shi
Date: 2023-12-05 16:59:07
Description: 
'''
import pandas as pd
import numpy as np
import statsmodels.api as sm

# 数据
data = [625, 5474, 62, 1, 478, 1, 135, 529, 28, 34, 
67, 0, 130, 294, 1751, 0, 10]

def armax_func(data, forecast_num):
    '''
    data 至少要 17 个数据
    '''
    data = pd.Series(data)
    # dta.index = pd.Index(sm.tsa.datetools.dates_from_range('2002','2090'))
    # 模型
    arma_mod70 = sm.tsa.ARMA(data, (1, 0, 0)).fit(disp = False)
    # print(arma_mod70.summary())
    # 返回预测结果、标准误差、置信区间
    (arr1, arr2, arr3) = arma_mod70.forecast(forecast_num)
    print('')
    print("预测结果:", arr1[0])
    return arr1[0]


if __name__ == "__main__":
    armax_func(data, 1)