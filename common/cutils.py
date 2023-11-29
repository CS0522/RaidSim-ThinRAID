'''
Author: Chen Shi
Date: 2023-11-27 12:07:21
Description: 
'''
def convert(_size):
    """
    将字符串的 size 信息转化为 int 类型，单位换算为字节
    例如 4KB 会被转化为 4 * 1024 = 4096 返回出去
    """
    length = len(_size)
    lastchar = _size[length - 1]
    if (lastchar == 'k') or (lastchar == 'K'):
        m = 1024
        nsize = int(_size[0:length - 1]) * m
    elif (lastchar == 'm') or (lastchar == 'M'):
        m = 1024 * 1024
        nsize = int(_size[0:length - 1]) * m
    elif (lastchar == 'g') or (lastchar == 'G'):
        m = 1024 * 1024 * 1024
        nsize = int(_size[0:length - 1]) * m
    else:
        nsize = int(_size)
    return nsize


def main():
    pass


if __name__ == "__main__":
    main()
