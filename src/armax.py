'''
Author: Chen Shi
Date: 2023-12-05 16:59:07
Description: 
'''
import pandas as pd
import numpy as np
import statsmodels.api as sm

# 数据
data = [-612,277,377,-3266,-950,2336,
        1459,-829,1191,238,-2965,-1764,-85,
        5312,3,-1342,1733,-4106,-1461,3186,
        -92,411,-650,118,-2676,-469,3051,1122,
        -329,247,866,-2548,-1414,3125,371,274,
        533,-175,-2332,-1388,3060,1369,676,-806,
        522,-2199,-2511,3901,-36,920,-1108,2175,
        -2333,-1105,3029,-31,2305,1302,2761,-4775,
        -3201,7769,-1214,1817,-5271,971,-2446]

def armax_func(data, forecast_num):
    '''
    data 至少要 17 个数据
    '''
    data = pd.Series(data)
    # dta.index = pd.Index(sm.tsa.datetools.dates_from_range('2002','2090'))
    # 模型
    arma_mod70 = sm.tsa.ARMA(data, (7, 0)).fit(disp = False)
    # print(arma_mod70.summary())
    # 返回预测结果、标准误差、置信区间
    (arr1, arr2, arr3) = arma_mod70.forecast(forecast_num)
    print('')
    print("预测结果:", arr1[0])
    return arr1[0]