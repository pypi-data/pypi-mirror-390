import numpy as np

from extendedstim.Code.LinearCode.LinearCode import LinearCode
from extendedstim.Code.QuantumCode.MajoranaCode import MajoranaCode
from extendedstim.Code.QuantumCode.QuantumCSSCode import QuantumCSSCode
from extendedstim.Math.BinaryArray import BinaryArray as ba
from extendedstim.Physics.MajoranaOperator import MajoranaOperator


class MajoranaCSSCode(MajoranaCode, QuantumCSSCode):

    # %%  USER：===构造方法===
    def __init__(self, generators_x, generators_z, physical_number):
        QuantumCSSCode.__init__(self, generators_x, generators_z, physical_number)

    # %%  USER：===属性方法===
    ##  USER：---求码距---
    @property
    def distance(self):
        return ba.distance(self.check_matrix_x,'random')

    ##  USER：---求码距（x方向）---
    @property
    def distance_x(self):
        return ba.distance(self.check_matrix_x,'mip')

    ##  USER：---求码距（z方向）---
    @property
    def distance_z(self):
        return ba.distance(self.check_matrix_z,'mip')

    ##  USER：---求逻辑算符---
    @property
    def logical_operators(self):
        _=self._logical_operators_x
        return np.append(self._logical_operators_x,self._logical_operators_z)

    ##  USER：---求逻辑算符（x方向）---
    @property
    def logical_operators_x(self):
        matrix = self.check_matrix_x
        codewords = matrix.null_space
        independent_null_basis_list = []
        for vec in codewords:
            rank_before = matrix.rank
            matrix = ba.vstack(matrix, vec)
            if matrix.rank == rank_before + 1:
                independent_null_basis_list.append(vec)
        basis_list = ba.orthogonalize(independent_null_basis_list)
        majorana_logical_operators_x = []
        majorana_logical_operators_z = []
        for i in range(len(basis_list)):
            occupy=basis_list[i].occupy
            temp = MajoranaOperator.HermitianOperatorFromOccupy(occupy,[])
            majorana_logical_operators_x.append(temp)
            temp = MajoranaOperator.HermitianOperatorFromOccupy([],occupy)
            majorana_logical_operators_z.append(temp)
        self._logical_operators_x = np.array(majorana_logical_operators_x, dtype=MajoranaOperator)
        self._logical_operators_z = np.array(majorana_logical_operators_z, dtype=MajoranaOperator)
        return self._logical_operators_x

    ##  USER：---求逻辑算符（z方向）---
    @property
    def logical_operators_z(self):
        _=self._logical_operators_x
        return self._logical_operators_z

    #%%  USER：===静态方法===
    ##  USER：从校验矩阵构造Majorana CSS code
    @staticmethod
    def FromCheckMatrix(check_matrix):
        generators_x = []
        generators_z = []
        for i in range(len(check_matrix)):
            generators_x.append(MajoranaOperator.HermitianOperatorFromVector(check_matrix[i]))
            generators_z.append(MajoranaOperator.HermitianOperatorFromVector(check_matrix[i]))
        physical_number=check_matrix.shape[1]
        return MajoranaCSSCode(generators_x, generators_z, physical_number)

    ##  USER：用一个线性码生成Majorana CSS code
    @staticmethod
    def FromLinearCode(linear_code):
        assert isinstance(linear_code,LinearCode)
        generators_x = []
        generators_z = []
        check_matrix=linear_code.check_matrix
        for i in range(len(check_matrix)):
            occupy=check_matrix[i].occupy
            generators_x.append(MajoranaOperator.HermitianOperatorFromOccupy(occupy,[]))
            generators_z.append(MajoranaOperator.HermitianOperatorFromOccupy([],occupy))
        physical_number=check_matrix.shape[1]
        return MajoranaCSSCode(generators_x, generators_z, physical_number)

    @staticmethod
    def SteaneCode():
        generators_x = [MajoranaOperator([3,4,5,6],[],1),MajoranaOperator([1,2,5,6],[],1),MajoranaOperator([0,2,4,6],[],1)]
        generators_z = [MajoranaOperator([],[3,4,5,6],1),MajoranaOperator([],[1,2,5,6],1),MajoranaOperator([],[0,2,4,6],1)]
        physical_number=7
        result= MajoranaCSSCode(generators_x, generators_z, physical_number)
        result._logical_operators_x=[MajoranaOperator([0,1,2],[],1j)]
        result._logical_operators_z=[MajoranaOperator([], [0, 1, 2], 1j)]
        return result

if __name__ == '__main__':
    code=MajoranaCSSCode.SteaneCode()
    print(code.logical_operators_x[0].occupy_x)
