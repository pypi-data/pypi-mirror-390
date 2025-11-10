import copy
from abc import abstractmethod, ABC
import numpy as np
from extendedstim.Math.BinaryArray import BinaryArray as ba
from extendedstim.tools import isinteger, islist


class Operator(ABC):

    #%%  USER：===构造方法===
    def __init__(self, occupy_x, occupy_z, coff):
        assert islist(occupy_x)
        assert islist(occupy_z)
        occupy_x=copy.deepcopy(occupy_x)
        occupy_z=copy.deepcopy(occupy_z)
        self.occupy_x = np.asarray(occupy_x, dtype=int)
        self.occupy_z = np.asarray(occupy_z, dtype=int)
        self.occupy_x.sort()
        self.occupy_z.sort()
        self.coff = coff

    #%%  USER：===重载运算符===
    ##  USER：---矩阵乘法---
    @abstractmethod
    def __matmul__(self, other):
        pass

    ##  USER：---右矩阵乘法---
    @abstractmethod
    def __rmatmul__(self, other):
        pass

    ##  USER：---左标量乘法---
    @abstractmethod
    def __mul__(self, other):
        pass

    ##  USER：---右标量乘法---
    @abstractmethod
    def __rmul__(self, other):
        pass

    ##  USER：---字符串表示---
    @abstractmethod
    def __str__(self):
        pass

    ##  USER：---相等判断---
    @abstractmethod
    def __eq__(self, other):
        pass

    ##  USER：---取负---
    @abstractmethod
    def __neg__(self):
        pass

    #%%  USER：属性方法
    ##  USER：---算符的权重---
    @property
    def weight(self)->int:
        return len(self.occupy_x) + len(self.occupy_z)

    ##  USER：---判断算符是否是厄米算符---
    @property
    @abstractmethod
    def is_hermitian(self)->bool:
        pass

    ##  USER：---求算符的对偶算符---
    @property
    @abstractmethod
    def dual(self):
        pass

    #%%  USER：===对象方法===
    ##  USER：---更换索引方式---
    @abstractmethod
    def index_map(self, index):
        assert isinstance(index, np.ndarray) or isinstance(index, list)
        assert len(index) >= max(self.occupy_x.max(), self.occupy_z.max()) + 1
        x = np.array([index[i] for i in self.occupy_x], dtype=int)
        z = np.array([index[i] for i in self.occupy_z], dtype=int)
        return x, z, self.coff

    ##  USER：---获取向量表示---
    def get_vector(self, number):
        assert isinteger(number)
        vector = ba.zeros(number * 2)
        vector[self.occupy_x * 2] = 1
        vector[self.occupy_z * 2 + 1] = 1
        return vector

    ##  USER：---检查是否存在量子位上的算符占据---
    def is_exist_occupy_x(self, index):
        assert isinteger(index)
        occupy = np.where(self.occupy_x == index)[0]
        if len(occupy) == 0:
            return None
        return occupy[0]

    ##  USER：---检查是否存在量子位上的算符占据---
    def is_exist_occupy_z(self, index):
        assert isinteger(index)
        occupy = np.where(self.occupy_z == index)[0]
        if len(occupy) == 0:
            return None
        return occupy[0]

    ##  USER：---复制算符---
    @abstractmethod
    def copy(self):
        pass

    ##  USER：---将算符在index位置切分---
    @abstractmethod
    def split(self, index):
        assert isinteger(index)
        left_x=[temp for temp in self.occupy_x if temp < index]
        left_z=[temp for temp in self.occupy_z if temp < index]
        right_x=[temp for temp in self.occupy_x if temp > index]
        right_z=[temp for temp in self.occupy_z if temp > index]
        if self.is_exist_occupy_x(index) is not None and self.is_exist_occupy_z(index) is not None:
            middle_x=[index]
            middle_z=[index]
        elif self.is_exist_occupy_x(index) is not None:
            middle_x=[index]
            middle_z=[]
        elif self.is_exist_occupy_z(index) is not None:
            middle_x=[]
            middle_z=[index]
        else:
            middle_x=[]
            middle_z=[]
        return left_x, left_z, middle_x, middle_z, right_x, right_z

    #%%  USER：静态方法
    ##  USER：---求多个算符的矩阵表示---
    @staticmethod
    def get_matrix(ops, number):
        assert islist(ops)
        matrix = None
        for i, op in enumerate(ops):
            vector = op.get_vector(number)
            if i == 0:
                matrix = vector
            else:
                matrix = ba.vstack(matrix, vector)
        return matrix

    # %%  USER：静态方法
    ##  USER：---定义一个厄米算符，从占据处表示---
    @staticmethod
    @abstractmethod
    def HermitianOperatorFromOccupy(occupy_x, occupy_z):
        pass

    ##  USER：---定义一个厄米算符，从向量表示---
    @staticmethod
    @abstractmethod
    def HermitianOperatorFromVector(vector):
        pass

    ##  USER：---检查两个算符是否对易---
    @staticmethod
    @abstractmethod
    def commute(A,B):
        pass
