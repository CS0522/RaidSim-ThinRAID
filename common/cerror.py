'''
Author: Chen Shi
Date: 2023-11-27 12:07:21
Description: 
'''
class MyCoreError(Exception):
    pass


class Cerror:
    def __init__(self, info):
        print(f'error: {info}')
        raise MyCoreError(info)


# useful instead of assert
def cassert(cond, _str='错误'):
    if not cond:
        mess = f'终止::{_str}'
        print(mess)
        raise MyCoreError(mess)
    # else:
    #     print(_str)
    return


def main():
    pass


if __name__ == "__main__":
    main()
