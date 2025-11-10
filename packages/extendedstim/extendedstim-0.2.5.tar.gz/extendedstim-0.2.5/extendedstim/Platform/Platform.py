import copy
import numpy as np

from extendedstim.Math.BinaryArray import BinaryArray as ba
from extendedstim.Physics.MajoranaOperator import MajoranaOperator
from extendedstim.Physics.PauliOperator import PauliOperator
from extendedstim.tools import *


class Platform:

    # %%  USER：===构造方法===
    def __init__(self):
        self.pauli_number = 0
        self.majorana_number = 0
        self.stabilizers_pauli = []
        self.stabilizers_majorana = []

    # %%  USER：===对象方法===
    ##  USER：---初始化平台，定义fermionic sites和qubits数目---
    def initialize(self, majorana_number, pauli_number):

        ##  ---数据预处理---
        assert isinteger(majorana_number) and majorana_number >= 0
        assert isinteger(pauli_number) and pauli_number >= 0

        ##  ---定义平台初态---
        ##  定义平台qubits和fermionic sites分别的数目
        self.pauli_number = pauli_number
        self.majorana_number = majorana_number

        ##  初始化状态，平台处于完全混态
        for i in range(majorana_number):
            if np.random.rand() < 0.5:
                self.stabilizers_majorana.append(MajoranaOperator([i], [i], 1j))
            else:
                self.stabilizers_majorana.append(MajoranaOperator([i], [i], -1j))
            self.stabilizers_pauli.append(PauliOperator([], [], 1))
        for i in range(pauli_number):
            if np.random.rand() < 0.5:
                self.stabilizers_pauli.append(PauliOperator([], [i], 1))
            else:
                self.stabilizers_pauli.append(PauliOperator([], [i], -1))
            self.stabilizers_majorana.append(MajoranaOperator([], [], 1))

    ##  USER：---强制初始化---
    def force(self,majorana_state,pauli_state):
        self.stabilizers_majorana = copy.deepcopy(majorana_state)
        self.stabilizers_pauli = copy.deepcopy(pauli_state)

    ##  USER：---测量算符op，返回测量结果，随机坍缩---
    def measure(self,op,*args):

        ##  ---数据预处理---
        assert op.is_hermitian

        ##  ---测量算符op，返回测量结果，随机坍缩---
        ##  如果没有指定stabilizers的测量位置，那么需要真正计算
        if len(args) == 0:
            if isinstance(op,MajoranaOperator):
                return self.measure_majorana(op,None)
            elif isinstance(op,PauliOperator):
                return self.measure_pauli(op,None)
            else:
                raise NotImplementedError

        ##  如果指定了stabilizers的测量位置，那么可以直接读出coff
        elif len(args) == 1:
            if isinstance(op,MajoranaOperator):
                return self.measure_majorana(op,args[0])
            elif isinstance(op,PauliOperator):
                return self.measure_pauli(op,args[0])
            else:
                raise NotImplementedError

        ##  抛出异常
        else:
            raise NotImplementedError

    ##  KEY：---测量算符Pauli operator，返回测量结果，随机坍缩---
    def measure_pauli(self, op,index):
        if index is None:
            first_pauli = None
            first_index = -1
            for i in range(len(self.stabilizers_pauli)):
                commute_flag = PauliOperator.commute(op,self.stabilizers_pauli[i])
                if not commute_flag:
                    if first_index == -1:
                        first_pauli = self.stabilizers_pauli[i]
                        first_index = i
                    else:
                        self.stabilizers_pauli[i] = self.stabilizers_pauli[i] @ first_pauli
                        self.stabilizers_majorana[i]=self.stabilizers_majorana[i] @ self.stabilizers_majorana[first_index]
            if first_index == -1:
                matrix_pauli = PauliOperator.get_matrix(self.stabilizers_pauli, self.pauli_number)
                matrix_majorana = MajoranaOperator.get_matrix(self.stabilizers_majorana, self.majorana_number)
                matrix = ba.hstack(matrix_majorana, matrix_pauli)
                vector_majorana = ba.zeros(self.majorana_number * 2)
                vector_pauli = op.get_vector(self.pauli_number)
                vector = ba.hstack(vector_majorana, vector_pauli)
                result = ba.solve(matrix, vector)
                op_mul_pauli = PauliOperator([], [], 1)
                op_mul_majorana = MajoranaOperator([], [], 1)
                for i in range(len(result)):
                    if result[i] == 1:
                        op_mul_majorana = op_mul_majorana @ self.stabilizers_majorana[i]
                        op_mul_pauli = op_mul_pauli @ self.stabilizers_pauli[i]
                coff = op_mul_pauli.coff * op_mul_majorana.coff
                if coff == op.coff:
                    return 1
                else:
                    return -1
            else:
                if np.random.rand() < 0.5:
                    self.stabilizers_pauli[first_index] = op.copy()
                    self.stabilizers_majorana[first_index] = MajoranaOperator([], [], 1)
                    return 1
                else:
                    self.stabilizers_pauli[first_index] = -op.copy()
                    self.stabilizers_majorana[first_index] = MajoranaOperator([], [], 1)
                    return -1
        else:
            if self.stabilizers_pauli[index].coff==op.coff:
                return 1
            else:
                return -1

    ##  KEY：---测量算符Majorana operator，返回测量结果，随机坍缩---
    def measure_majorana(self, op,index):
        if index is None:
            first_majorana = None
            first_index = -1
            for i in range(len(self.stabilizers_majorana)):
                commute_flag = MajoranaOperator.commute(op,self.stabilizers_majorana[i])
                if not commute_flag:
                    if first_index == -1:
                        first_majorana = self.stabilizers_majorana[i]
                        first_index = i
                    else:
                        self.stabilizers_majorana[i] = self.stabilizers_majorana[i] @ first_majorana
                        self.stabilizers_pauli[i] = self.stabilizers_pauli[i] @ self.stabilizers_pauli[first_index]
            if first_index == -1:
                matrix_pauli = PauliOperator.get_matrix(self.stabilizers_pauli, self.pauli_number)
                matrix_majorana = MajoranaOperator.get_matrix(self.stabilizers_majorana, self.majorana_number)
                matrix = ba.hstack(matrix_majorana, matrix_pauli)
                vector_majorana = op.get_vector(self.majorana_number)
                vector_pauli = ba.zeros(self.pauli_number*2)
                vector = ba.hstack(vector_majorana, vector_pauli)
                result = ba.solve(matrix, vector)
                op_mul_pauli = PauliOperator([], [], 1)
                op_mul_majorana = MajoranaOperator([], [], 1)
                for i in range(len(result)):
                    if result[i] == 1:
                        op_mul_majorana = op_mul_majorana @ self.stabilizers_majorana[i]
                        op_mul_pauli = op_mul_pauli @ self.stabilizers_pauli[i]
                coff = op_mul_pauli.coff * op_mul_majorana.coff
                if coff == op.coff:
                    return 1
                else:
                    return -1
            else:
                if np.random.rand() < 0.5:
                    self.stabilizers_pauli[first_index] = PauliOperator([], [], 1)
                    self.stabilizers_majorana[first_index] = op.copy()
                    return 1
                else:
                    self.stabilizers_pauli[first_index] = PauliOperator([], [], 1)
                    self.stabilizers_majorana[first_index] = -op.copy()
                    return -1
        else:
            if self.stabilizers_majorana[index].coff==op.coff:
                return 1
            else:
                return -1

    ##  USER：---检测平台是否在op的本征空间，返回结果或本征值---
    def detect(self,op):
        ##  ---数据预处理---
        assert isinstance(op,PauliOperator) or isinstance(op,MajoranaOperator)
        assert op.is_hermitian

        ##  ---检测平台是否在op的本征空间，返回结果或本征值---
        matrix_pauli = PauliOperator.get_matrix(self.stabilizers_pauli, self.pauli_number)
        matrix_majorana = MajoranaOperator.get_matrix(self.stabilizers_majorana, self.majorana_number)
        matrix = ba.hstack(matrix_majorana, matrix_pauli)
        if isinstance(op, MajoranaOperator):
            vector_majorana = op.get_vector(self.majorana_number)
            vector_pauli = ba.zeros(self.pauli_number * 2)
            vector = ba.hstack(vector_majorana, vector_pauli)
        elif isinstance(op, PauliOperator):
            vector_majorana = ba.zeros(self.majorana_number*2)
            vector_pauli = op.get_vector(self.pauli_number)
            vector = ba.hstack(vector_majorana, vector_pauli)
        else:
            raise NotImplementedError

        ##  方程有解说明在本征态内，反之存在反对易的stabilizers
        result = ba.solve(matrix, vector)
        coff=None
        if result is not None:
            op_mul_pauli = PauliOperator([], [], 1)
            op_mul_majorana = MajoranaOperator([], [], 1)
            for i in range(len(result)):
                if result[i] == 1:
                    op_mul_majorana = op_mul_majorana @ self.stabilizers_majorana[i]
                    op_mul_pauli = op_mul_pauli @ self.stabilizers_pauli[i]
            coff = op_mul_pauli.coff * op_mul_majorana.coff

        ##  ---返回结果---
        if result is None:
            return None
        elif coff == op.coff:
            return 1
        else:
            return -1

    ##  USER：---X门，作用于qubit_index---
    def x(self, qubit_index: int):

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ---X门作用---
        for i in range(len(self.stabilizers_pauli)):
            if self.stabilizers_pauli[i].is_exist_occupy_z(qubit_index) is not None:
                self.stabilizers_pauli[i].coff = -self.stabilizers_pauli[i].coff

    ##  USER：---Y门，作用于qubit_index---
    def y(self, qubit_index: int):

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ---Y门作用---
        for i in range(len(self.stabilizers_pauli)):
            if self.stabilizers_pauli[i].is_exist_occupy_x(qubit_index) is not None:
                self.stabilizers_pauli[i].coff = -self.stabilizers_pauli[i].coff
            if self.stabilizers_pauli[i].is_exist_occupy_z(qubit_index) is not None:
                self.stabilizers_pauli[i].coff = -self.stabilizers_pauli[i].coff

    ##  USER：---Z门，作用于qubit_index---
    def z(self, qubit_index: int):

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ---Z门作用---
        for i in range(len(self.stabilizers_pauli)):
            if self.stabilizers_pauli[i].is_exist_occupy_x(qubit_index) is not None:
                self.stabilizers_pauli[i].coff = -self.stabilizers_pauli[i].coff

    ##  USER：---Hadamard gate，作用于qubit_index---
    def h(self, qubit_index: int):

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0 <= qubit_index < self.pauli_number

        ##  ---Hadamard门作用---
        for i, stabilizer in enumerate(self.stabilizers_pauli):
            assert isinstance(stabilizer, PauliOperator)
            left, middle, right = stabilizer.split(qubit_index)
            if len(middle.occupy_x) == 0 and len(middle.occupy_z) == 0:
                continue
            elif len(middle.occupy_x) == 1 and len(middle.occupy_z) == 1:
                continue
            elif len(middle.occupy_x) == 0 and len(middle.occupy_z) == 1:
                middle.occupy_x = [qubit_index]
                middle.occupy_z = []
            elif len(middle.occupy_x) == 1 and len(middle.occupy_z) == 0:
                middle.occupy_x = []
                middle.occupy_z = [qubit_index]
            else:
                raise ValueError
            self.stabilizers_pauli[i] = left @ middle @ right

    ##  USER：---S门，作用于pauli_index---
    def s(self, pauli_index: int):

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0 <= pauli_index < self.pauli_number

        ##  ---S门作用---
        for i, stabilizer in enumerate(self.stabilizers_pauli):
            assert isinstance(stabilizer, PauliOperator)
            left, middle, right = stabilizer.split(pauli_index)
            if len(middle.occupy_x) == 0:
                continue
            elif len(middle.occupy_x) == 1 and len(middle.occupy_z) == 0:
                middle.occupy_z = [pauli_index]
                middle.coff = 1j
            elif len(middle.occupy_x) == 1 and len(middle.occupy_z) == 1:
                middle.occupy_z = []
                middle.coff = 1j
            else:
                raise ValueError
            self.stabilizers_pauli[i] = left @ middle @ right

    ##  USER：---gamma门，作用于majorana_index---
    def u(self, majorana_index: int):

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---gamma门作用---
        op = MajoranaOperator([majorana_index], [], 1)
        for i, stabilizer in enumerate(self.stabilizers_majorana):
            if not MajoranaOperator.commute(stabilizer, op):
                stabilizer.coff = -stabilizer.coff

    ##  USER：---gamma_prime门，作用于majorana_index---
    def v(self, majorana_index: int):

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---gamma_prime门作用---
        op = MajoranaOperator([], [majorana_index], 1)
        for i, stabilizer in enumerate(self.stabilizers_majorana):
            if not MajoranaOperator.commute(stabilizer, op):
                stabilizer.coff = -stabilizer.coff

    ##  USER：---i*gamma*gamma_prime门，作用于majorana_index---
    def n(self, majorana_index: int):

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---i*gamma*gamma_prime门作用---
        op = MajoranaOperator([majorana_index], [majorana_index], 1j)
        for i, stabilizer in enumerate(self.stabilizers_majorana):
            if not MajoranaOperator.commute(stabilizer, op):
                stabilizer.coff = -stabilizer.coff

    ##  USER：---P门，作用于majorana_index---
    def p(self, majorana_index: int):

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---P门作用---
        for i, stabilizer in enumerate(self.stabilizers_majorana):
            left, middle, right = stabilizer.split(majorana_index)
            if len(middle.occupy_x) == 0 and len(middle.occupy_z) == 0:
                continue
            elif len(middle.occupy_x) == 1 and len(middle.occupy_z) == 0:
                middle.occupy_z = [majorana_index]
                middle.occupy_x=[]
            elif len(middle.occupy_x) == 0 and len(middle.occupy_z) == 1:
                middle.occupy_x = [majorana_index]
                middle.occupy_z = []
                middle.coff = -1
            else:
                raise ValueError
            self.stabilizers_majorana[i] = left @ middle @ right

    ##  USER：---CNOT门，作用于control_index,target_index，两者是qubits，前者是控制位---
    def cx(self, control_index, target_index):

        ##  ---数据预处理---
        assert isinteger(control_index) and 0 <= control_index < self.pauli_number
        assert isinteger(target_index) and 0 <= target_index < self.pauli_number

        ##  ---CNOT门作用---
        for i, stabilizer in enumerate(self.stabilizers_pauli):
            assert isinstance(stabilizer, PauliOperator)
            left, middle, right = stabilizer.split(control_index)
            if len(middle.occupy_x) == 1:
                middle = PauliOperator([control_index, target_index], [], 1)
            if target_index > control_index:
                right_left, right_middle, right_right = right.split(target_index)
                if len(right_middle.occupy_z) == 1:
                    right_middle = PauliOperator([], [control_index, target_index], 1)
                self.stabilizers_pauli[i] = left @ middle @ right_left @ right_middle @ right_right
            elif target_index < control_index:
                left_left, left_middle, left_right = left.split(target_index)
                if len(left_middle.occupy_z) == 1:
                    left_middle = PauliOperator([], [control_index, target_index], 1)
                self.stabilizers_pauli[i] = left_left @ left_middle @ left_right @ middle @ right
            else:
                raise ValueError

    ##  USER：---CN-NOT门，作用于control_index,target_index，前者是fermionic site控制位，后者是qubit目标位---
    def cnx(self, control_index, target_index):

        ##  ---数据预处理---
        assert isinteger(control_index) and 0 <= control_index < self.majorana_number
        assert isinteger(target_index) and 0 <= target_index < self.pauli_number

        ##  ---CN-NOT门作用---
        for i in range(len(self.stabilizers_pauli)):
            if i==19:
                pass
            stabilizer_pauli = self.stabilizers_pauli[i]
            stabilizer_majorana = self.stabilizers_majorana[i]
            left_control, middle_control, right_control = stabilizer_majorana.split(control_index)
            left_target, middle_target, right_target = stabilizer_pauli.split(target_index)
            majorana_product = PauliOperator([], [], 1)
            pauli_product = MajoranaOperator([], [], 1)
            if len(middle_control.occupy_x) == 1:
                majorana_product = PauliOperator([target_index], [], 1)
            if len(middle_control.occupy_z) == 1:
                majorana_product = majorana_product @ PauliOperator([target_index], [], 1)
            if len(middle_target.occupy_z) == 1:
                pauli_product = MajoranaOperator([control_index], [control_index], 1j)
            self.stabilizers_pauli[i] = majorana_product @ left_target @ middle_target @ right_target
            self.stabilizers_majorana[i] = left_control @ middle_control @ right_control @ pauli_product

    ##  USER：---CN-N门，作用于control_index,target_index，前者是fermionic site控制位，后者是fermionic site目标位---
    def cnn(self, control_index, target_index):

        ##  ---数据预处理---
        assert isinteger(control_index) and 0 <= control_index < self.majorana_number
        assert isinteger(target_index) and 0 <= target_index < self.majorana_number

        ##  ---CN-N门作用---
        for i in range(len(self.stabilizers_majorana)):
            stabilizer_majorana = self.stabilizers_majorana[i]
            if control_index < target_index:
                left_control, middle_control, right_control = stabilizer_majorana.split(control_index)
                left_target, middle_target, right_target = right_control.split(target_index)

                middle_control_zero=MajoranaOperator([],[],1)
                middle_control_one=MajoranaOperator([],[],1)
                if len(middle_control.occupy_x) == 1:
                    middle_control_zero = MajoranaOperator([control_index], [], 1)@MajoranaOperator([target_index], [target_index], 1j)
                if len(middle_control.occupy_z) == 1:
                    middle_control_one = MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [target_index], 1j)
                middle_control = middle_control_zero@middle_control_one

                middle_target_zero=MajoranaOperator([],[],1)
                middle_target_one=MajoranaOperator([],[],1)
                if len(middle_target.occupy_x) == 1:
                    middle_target_zero = MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([target_index], [], 1)
                if len(middle_target.occupy_z) == 1:
                    middle_target_one= MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([], [target_index], 1)
                middle_target = middle_target_zero@middle_target_one

                stabilizer_majorana=left_control@middle_control@left_target@middle_target@right_target

            elif target_index < control_index:
                left_control, middle_control, right_control = stabilizer_majorana.split(control_index)
                left_target, middle_target, right_target = left_control.split(target_index)

                middle_control_zero=MajoranaOperator([],[],1)
                middle_control_one=MajoranaOperator([],[],1)
                if len(middle_control.occupy_x) == 1:
                    middle_control_zero = MajoranaOperator([control_index], [], 1)@MajoranaOperator([target_index], [target_index], 1j)
                if len(middle_control.occupy_z) == 1:
                    middle_control_one = MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [target_index], 1j)
                middle_control = middle_control_zero@middle_control_one

                middle_target_zero=MajoranaOperator([],[],1)
                middle_target_one=MajoranaOperator([],[],1)
                if len(middle_target.occupy_x) == 1:
                    middle_target_zero = MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([target_index], [], 1)
                if len(middle_target.occupy_z) == 1:
                    middle_target_one= MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([], [target_index], 1)
                middle_target = middle_target_zero@middle_target_one

                stabilizer_majorana=left_target@middle_target@right_target@middle_control@right_control
            else:
                raise ValueError
            self.stabilizers_majorana[i] = stabilizer_majorana

    ##  USER：---Braid门，前者是fermionic site控制位，后者是fermionic site目标位---
    def braid(self,control_index,target_index,*args):
        for i in range(len(self.stabilizers_pauli)):
            stabilizer_majorana = self.stabilizers_majorana[i]
            if control_index < target_index:
                left_control, middle_control, right_control = stabilizer_majorana.split(control_index)
                left_target, middle_target, right_target = right_control.split(target_index)

                if len(middle_control.occupy_z) == 1:
                    middle_control = middle_control@MajoranaOperator([],[control_index],1)@MajoranaOperator([target_index], [], -1)
                if len(middle_target.occupy_x) == 1:
                    middle_target = MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index],[],1)@middle_target

                stabilizer_majorana=left_control@middle_control@left_target@middle_target@right_target
            elif target_index < control_index:
                left_control, middle_control, right_control = stabilizer_majorana.split(control_index)
                left_target, middle_target, right_target = left_control.split(target_index)

                if len(middle_control.occupy_z) == 1:
                    middle_control = middle_control@MajoranaOperator([],[control_index],1)@MajoranaOperator([target_index], [], -1)
                if len(middle_target.occupy_x) == 1:
                    middle_target =MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index],[],1)@middle_target

                stabilizer_majorana=left_target@middle_target@right_target@middle_control@right_control
            else:
                if len(args) == 0 or args[0]==0:
                    self.p(control_index)
                elif len(args) == 1 and args[0]==1:
                    self.p(control_index)
                    self.n(control_index)
            self.stabilizers_majorana[i] =stabilizer_majorana

    ##  USER：---执行pauli_index上的X-error---
    def x_error(self, pauli_index, p):
        if np.random.rand() < p:
            self.x(pauli_index)

    ##  USER：---执行pauli_index上的Y-error---
    def y_error(self, pauli_index, p):
        if np.random.rand() < p:
            self.y(pauli_index)

    ##  USER：---执行pauli_index上的Z-error---
    def z_error(self, pauli_index, p):
        if np.random.rand() < p:
            self.z(pauli_index)

    ##  USER：---执行majorana_index上的U-error---
    def u_error(self, majorana_index, p):
        if np.random.rand() < p:
            self.u(majorana_index)

    ##  USER：---执行majorana_index上的V-error---
    def v_error(self, majorana_index, p):
        if np.random.rand() < p:
            self.v(majorana_index)

    ##  USER：---执行majorana_index上的N-error---
    def n_error(self, majorana_index, p):
        if np.random.rand() < p:
            self.n(majorana_index)

    ##  KEY：---将系统在op上重置为0---
    def clear(self, op):

        ##  判断算符类型
        if isinstance(op, PauliOperator):
            stabilizers_now = self.stabilizers_pauli
        elif isinstance(op, MajoranaOperator):
            stabilizers_now = self.stabilizers_majorana
        else:
            raise NotImplementedError
        assert op.is_hermitian

        ##  假装测量
        first_pauli = None
        first_index = -1
        for i in range(len(stabilizers_now)):
            if isinstance(op, PauliOperator):
                commute_flag = PauliOperator.commute(op, stabilizers_now[i])
            elif isinstance(op, MajoranaOperator):
                commute_flag = MajoranaOperator.commute(op, stabilizers_now[i])
            else:
                raise NotImplementedError

            if not commute_flag:
                if first_index == -1:
                    first_pauli = stabilizers_now[i]
                    first_index = i
                else:
                    stabilizers_now[i] = stabilizers_now[i] @ first_pauli
        if first_index == -1:
            matrix_pauli = PauliOperator.get_matrix(self.stabilizers_pauli, self.pauli_number)
            matrix_majorana = MajoranaOperator.get_matrix(self.stabilizers_majorana, self.majorana_number)
            if self.pauli_number == 0 and self.majorana_number != 0:
                matrix = matrix_majorana
            elif self.majorana_number == 0 and self.pauli_number != 0:
                matrix = matrix_pauli
            elif self.pauli_number != 0 and self.majorana_number != 0:
                matrix = ba.hstack(matrix_majorana, matrix_pauli)
            else:
                raise NotImplementedError

            if isinstance(op, MajoranaOperator):
                vector_majorana = op.get_vector(self.majorana_number)
                vector_pauli = ba.zeros(self.pauli_number * 2)
                vector = ba.hstack(vector_majorana, vector_pauli)
            else:
                vector_majorana = ba.zeros(self.majorana_number * 2)
                vector_pauli = op.get_vector(self.pauli_number)
                vector = ba.hstack(vector_majorana, vector_pauli)
            result = ba.solve(matrix, vector)
            op_mul_pauli = None
            op_mul_majorana = None
            flag = None
            for i in range(len(result)):
                if result[i] == 1:
                    if op_mul_pauli is None:
                        flag = i
                        op_mul_pauli = self.stabilizers_pauli[i]
                        op_mul_majorana = self.stabilizers_majorana[i]
                    else:
                        op_mul_pauli = op_mul_pauli @ self.stabilizers_pauli[i]
                        op_mul_majorana = op_mul_majorana @ self.stabilizers_majorana[i]
            if op_mul_pauli.coff * op_mul_majorana.coff == op.coff:
                pass
            else:
                assert flag is not None
                self.stabilizers_pauli[flag].coff = -self.stabilizers_pauli[flag].coff
        else:
            if isinstance(op, MajoranaOperator):
                self.stabilizers_majorana[first_index] = op.copy()
                self.stabilizers_pauli[first_index] = PauliOperator([],[],1)
            elif isinstance(op, PauliOperator):
                self.stabilizers_pauli[first_index] = op.copy()
                self.stabilizers_majorana[first_index] = MajoranaOperator([],[],1)

    ##  USER：---将系统在pauli_index上重置为0态---
    def reset(self, pauli_index):

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0 <= pauli_index < self.pauli_number

        ##  ---重置0态---
        op = PauliOperator([], [pauli_index], 1)
        self.clear(op)

    ##  USER：---将系统在majorana_index上重置为空态---
    def fermionic_reset(self, majorana_index):

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0 <= majorana_index < self.majorana_number

        ##  ---重置空态---
        op = MajoranaOperator([majorana_index], [majorana_index], 1j)
        self.clear(op)
