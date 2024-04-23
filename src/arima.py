'''
Author: Chen Shi
Date: 2023-12-05 16:59:07
Description: ARIMA model
'''

import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller as ADF
from statsmodels.stats.diagnostic import acorr_ljungbox
import statsmodels.tsa.stattools as st


# 测验数据
data = [10, 20, 13, 109, 1, 18, 232, 22, 0, 17, 14, 0, 288, 13, 0, 54, 7237]

data = pd.Series(data)

# ADF 检验
def adf_check(data):
    adf_data = ADF(data)
    print(adf_data)
    return adf_data[1]


# 差分平稳化处理
def make_stable(data):
    data_diff1 = data.diff(1)
    data_diff1.dropna(inplace = True)
    data_diff1.plot()
    plt.title('Data Diff 1')
    return data_diff1


# 白噪声检验，白噪声检验也成为纯随机性检验。如果数据是纯随机性数据，那在进行数据分析就没有意义了
def random_check(data):
    print(acorr_ljungbox(data, boxpierce = False))


# 用 BIC 选出 p、q 值
def get_order(data):
    order = st.arma_order_select_ic(data, max_ar = 2, max_ma = 2, ic = ['aic','bic'])
    return order.bic_min_order


# arima
def arima_model(data, order = (0, 1), forecast_num = 1):
    data = pd.Series(data)
    # 模型
    arma = sm.tsa.ARIMA(data, (order[0], 0, order[1])).fit(disp = False)
    # 返回预测结果、标准误差、置信区间
    (arr1, arr2, arr3) = arma.forecast(forecast_num)
    # print(arr1[0])
    return arr1[0]


if __name__ == "__main__":
    # 得到平稳性序列
    diff_count = 0
    adf_p = adf_check(data)
    data_diff = data
    # while (adf_p >= 0.05):
    #     data_diff = make_stable(data_diff)
    #     diff_count += 1
    #     adf_p = adf_check(data_diff)
    # # 序列平稳
    # print('diff_count:', diff_count)
    # # 随机性检验
    # random_check(data_diff)
    # # 得到 p、q 值来构造模型
    # order = get_order(data_diff)
    # print('order:', order)
    # ARMA
    arima_model(data_diff, (0, 1), 1)