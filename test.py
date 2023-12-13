'''
Author: Chen Shi
Date: 2023-12-11 10:32:25
Description: test
'''

# a_list = []
# for r in range(10):
#     b_list = []
#     # col, num_disks 列
#     for c in range(10):
#         b_list.append(c)
#     # 把每行的 b_list 添加到 block table
#     a_list.append(b_list)

# for r in range(10):
#     for c in range(10):
#         print(str(a_list[r][c]), end = " ")
#     print('')

# count = 0
# for item in a_list:
#     print(str(item) + str(count))
#     count += 1


"""
传值还是传引用问题
"""
# class A:
#     def __init__(self):
#         self.value = 1

# class B:
#     def __init__(self, a):
#         self.b_a = A()
#         self.b_a = a

#     def set_a(self):
#         self.b_a.value = 2
#         pass

# a = A()

# print("a before", a.value)

# b = B(a)
# b.set_a()

# print("a after", a.value)
# print("b's a", b.b_a.value)

"""
深拷贝
"""
# import copy
# class Test:
#     value = 0

#     def __init__(self, new_val):
#         self.value = new_val


# a = Test(1)
# b = Test(2)
# c = Test(3)
# tls = [a, b, c]
# tls_dc = copy.deepcopy(tls)
# print("tls", tls[0].value, tls[1].value, tls[2].value)
# print("tls_dc", tls_dc[0].value, tls_dc[1].value, tls_dc[2].value)
# tls.sort(reverse = True, key = lambda x:x.value)
# print("tls", tls[0].value, tls[1].value, tls[2].value)
# print("tls_dc", tls_dc[0].value, tls_dc[1].value, tls_dc[2].value)

# d = tls[0]
# d.value = 10
# e = copy.deepcopy(tls[0])
# e.value = 20
# print("tls[0]", tls[0].value)
# print("d", d.value)
# print("e", e.value)


# """
# 二维空 list
# """
# ls = [[], [], []]
# print(ls)


class A:
    def __init__(self, value):
        self.value = value

a = A(1)
b = A(2)

ls = [[a], [b]]

print(ls[0][0].value)
print(ls[1][0].value)