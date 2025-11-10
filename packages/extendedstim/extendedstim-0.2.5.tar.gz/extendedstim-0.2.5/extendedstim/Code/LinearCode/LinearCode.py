import numpy as np
from extendedstim.Math.BinaryArray import BinaryArray


class LinearCode:
    #%%  USER：构造方法
    def __init__(self,check_matrix):
        ##  ---数据预处理---
        assert isinstance(check_matrix, np.ndarray) or isinstance(check_matrix, list) or isinstance(check_matrix, BinaryArray), "check_matrix必须是01数组"

        ##  ---根据校验矩阵构造对象---
        self.check_matrix = BinaryArray(check_matrix)
        self.number_bit=len(check_matrix[0])
        self.number_checker=len(check_matrix)

    #%%  USER：===属性方法===
    ##  USER：---计算秩---
    @property
    def rank(self):
        return self.check_matrix.rank

    ##  TODO：计算距离
    @property
    def distance(self):
        return 1

    ##  USER：---计算逻辑位数目---
    @property
    def logical_number(self):
        return self.number_bit-self.rank

    ##  USER：---计算码字---
    @property
    def codewords(self):
        return self.check_matrix.null_space

    ##  USER：---计算dual linear code---
    @property
    def dual(self):
        return LinearCode(self.check_matrix.null_space)

    ##  USER：---判断是否dual-containing---
    @property
    def is_dual_containing(self):
        return np.all(self.check_matrix @ self.check_matrix.T == 0)
