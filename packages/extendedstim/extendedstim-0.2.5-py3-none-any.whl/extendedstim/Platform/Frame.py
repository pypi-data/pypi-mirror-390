import numpy as np
from extendedstim.Math.BinaryArray import BinaryArray as ba
from extendedstim.Physics.MajoranaOperator import MajoranaOperator
from extendedstim.Physics.PauliOperator import PauliOperator
from extendedstim.tools import isinteger


class Frame:

    # %%  USER：===构造方法===
    def __init__(self):
        self.pauli_number=0
        self.majorana_number=0
        self.pauli_frame=None
        self.majorana_frame=None

    # %%  USER：===对象方法===
    ##  USER：---初始化平台，定义fermionic sites和qubits数目---
    def initialize(self, majorana_number, pauli_number):

        ##  ---数据预处理---
        assert isinteger(majorana_number) and majorana_number>=0
        assert isinteger(pauli_number) and pauli_number>=0

        ##  ---定义平台初态---
        ##  定义平台qubits和fermionic sites分别的数目
        self.pauli_number=pauli_number
        self.majorana_number=majorana_number
        self.pauli_frame=PauliOperator([],[],1)
        self.majorana_frame=MajoranaOperator([],[],1)

    ##  USER：---强制初始化---
    def force(self, majorana_state:list[MajoranaOperator], pauli_state:list[PauliOperator]):
        for stabilizer in majorana_state:
            if np.random.rand()>0.5:
                self.majorana_frame=stabilizer@self.majorana_frame
        for stabilizer in pauli_state:
            if np.random.rand()>0.5:
                self.pauli_frame=stabilizer@self.pauli_frame

    ##  USER：---测量算符op，返回测量结果，随机坍缩---
    def measure(self, op,reference_value):

        ##  ---数据预处理---
        assert op.is_hermitian
        assert reference_value==1 or reference_value==-1

        ##  ---测量算符op，返回测量结果，随机坍缩---
        if isinstance(op, MajoranaOperator):
            if MajoranaOperator.commute(op, self.majorana_frame):
                result=reference_value
            else:
                result=-reference_value
            if np.random.rand()>0.5:
                self.majorana_frame=op@self.majorana_frame
            return result
        elif isinstance(op, PauliOperator):
            if PauliOperator.commute(op, self.pauli_frame):
                result=reference_value
            else:
                result=-reference_value
            if np.random.rand()>0.5:
                self.pauli_frame=op@self.pauli_frame
            return result
        else:
            raise ValueError

    ##  USER：---X门，作用于qubit_index---
    def x(self, qubit_index: int):
        pass

    ##  USER：---Y门，作用于qubit_index---
    def y(self, qubit_index: int):
        pass

    ##  USER：---Z门，作用于qubit_index---
    def z(self, qubit_index: int):
        pass

    ##  USER：---Hadamard gate，作用于qubit_index---
    def h(self, qubit_index: int):

        ##  ---数据预处理---
        assert isinteger(qubit_index) and 0<=qubit_index<self.pauli_number

        ##  ---Hadamard门作用---
        left, middle, right=self.pauli_frame.split(qubit_index)
        if len(middle.occupy_x)==0 and len(middle.occupy_z)==1:
            middle.occupy_x=[qubit_index]
            middle.occupy_z=[]
        elif len(middle.occupy_x)==1 and len(middle.occupy_z)==0:
            middle.occupy_x=[]
            middle.occupy_z=[qubit_index]
        self.pauli_frame=left@middle@right

    ##  USER：---S门，作用于pauli_index---
    def s(self, pauli_index: int):

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0<=pauli_index<self.pauli_number

        ##  ---S门作用---
        left, middle, right=self.pauli_frame.split(pauli_index)
        if len(middle.occupy_x)==1 and len(middle.occupy_z)==0:
            middle.occupy_z=[pauli_index]
            middle.coff=1j
        elif len(middle.occupy_x)==1 and len(middle.occupy_z)==1:
            middle.occupy_z=[]
            middle.coff=1j
        self.pauli_frame=left@middle@right

    ##  USER：---gamma门，作用于majorana_index---
    def u(self, majorana_index: int):
        pass

    ##  USER：---gamma_prime门，作用于majorana_index---
    def v(self, majorana_index: int):
        pass

    ##  USER：---i*gamma*gamma_prime门，作用于majorana_index---
    def n(self, majorana_index: int):
        pass

    ##  USER：---P门，作用于majorana_index---
    def p(self, majorana_index: int):

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0<=majorana_index<self.majorana_number

        ##  ---P门作用---
        left, middle, right=self.majorana_frame.split(majorana_index)
        if len(middle.occupy_x)==0 and len(middle.occupy_z)==0:
            pass
        elif len(middle.occupy_x)==1 and len(middle.occupy_z)==0:
            middle.occupy_z=[majorana_index]
            middle.occupy_x=[]
        elif len(middle.occupy_x)==0 and len(middle.occupy_z)==1:
            middle.occupy_x=[majorana_index]
            middle.occupy_z=[]
            middle.coff=-1
        else:
            raise ValueError
        self.majorana_frame=left@middle@right

    ##  USER：---CNOT门，作用于control_index,target_index，两者是qubits，前者是控制位---
    def cx(self, control_index, target_index):

        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.pauli_number
        assert isinteger(target_index) and 0<=target_index<self.pauli_number

        ##  ---CNOT门作用---
        left, middle, right=self.pauli_frame.split(control_index)
        if len(middle.occupy_x)==1:
            middle=PauliOperator([control_index, target_index], [], 1)
        if target_index>control_index:
            right_left, right_middle, right_right=right.split(target_index)
            if len(right_middle.occupy_z)==1:
                right_middle=PauliOperator([], [control_index, target_index], 1)
            self.pauli_frame=left@middle@right_left@right_middle@right_right
        elif target_index<control_index:
            left_left, left_middle, left_right=left.split(target_index)
            if len(left_middle.occupy_z)==1:
                left_middle=PauliOperator([], [control_index, target_index], 1)
            self.pauli_frame=left_left@left_middle@left_right@middle@right
        else:
            raise ValueError

    ##  USER：---CN-NOT门，作用于control_index,target_index，前者是fermionic site控制位，后者是qubit目标位---
    def cnx(self, control_index, target_index):

        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.majorana_number
        assert isinteger(target_index) and 0<=target_index<self.pauli_number

        ##  ---CN-NOT门作用---
        left_control, middle_control, right_control=self.majorana_frame.split(control_index)
        left_target, middle_target, right_target=self.pauli_frame.split(target_index)
        majorana_product=PauliOperator([], [], 1)
        pauli_product=MajoranaOperator([], [], 1)
        if len(middle_control.occupy_x)==1:
            majorana_product=PauliOperator([target_index], [], 1)
        if len(middle_control.occupy_z)==1:
            majorana_product=majorana_product@PauliOperator([target_index], [], 1)
        if len(middle_target.occupy_z)==1:
            pauli_product=MajoranaOperator([control_index], [control_index], 1j)
        self.pauli_frame=majorana_product@left_target@middle_target@right_target
        self.majorana_frame=left_control@middle_control@right_control@pauli_product

    ##  USER：---CN-N门，作用于control_index,target_index，前者是fermionic site控制位，后者是fermionic site目标位---
    def cnn(self, control_index, target_index):

        ##  ---数据预处理---
        assert isinteger(control_index) and 0<=control_index<self.majorana_number
        assert isinteger(target_index) and 0<=target_index<self.majorana_number

        ##  ---CN-N门作用---
        if control_index<target_index:
            left_control, middle_control, right_control=self.majorana_frame.split(control_index)
            left_target, middle_target, right_target=right_control.split(target_index)

            middle_control_zero=MajoranaOperator([], [], 1)
            middle_control_one=MajoranaOperator([], [], 1)
            if len(middle_control.occupy_x)==1:
                middle_control_zero=MajoranaOperator([control_index], [], 1)@MajoranaOperator([target_index], [target_index], 1j)
            if len(middle_control.occupy_z)==1:
                middle_control_one=MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [target_index], 1j)
            middle_control=middle_control_zero@middle_control_one

            middle_target_zero=MajoranaOperator([], [], 1)
            middle_target_one=MajoranaOperator([], [], 1)
            if len(middle_target.occupy_x)==1:
                middle_target_zero=MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([target_index], [], 1)
            if len(middle_target.occupy_z)==1:
                middle_target_one=MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([], [target_index], 1)
            middle_target=middle_target_zero@middle_target_one

            self.majorana_frame=left_control@middle_control@left_target@middle_target@right_target

        elif target_index<control_index:
            left_control, middle_control, right_control=self.majorana_frame.split(control_index)
            left_target, middle_target, right_target=left_control.split(target_index)

            middle_control_zero=MajoranaOperator([], [], 1)
            middle_control_one=MajoranaOperator([], [], 1)
            if len(middle_control.occupy_x)==1:
                middle_control_zero=MajoranaOperator([control_index], [], 1)@MajoranaOperator([target_index], [target_index], 1j)
            if len(middle_control.occupy_z)==1:
                middle_control_one=MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [target_index], 1j)
            middle_control=middle_control_zero@middle_control_one

            middle_target_zero=MajoranaOperator([], [], 1)
            middle_target_one=MajoranaOperator([], [], 1)
            if len(middle_target.occupy_x)==1:
                middle_target_zero=MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([target_index], [], 1)
            if len(middle_target.occupy_z)==1:
                middle_target_one=MajoranaOperator([control_index], [control_index], 1j)@MajoranaOperator([], [target_index], 1)
            middle_target=middle_target_zero@middle_target_one
            self.majorana_frame=left_target@middle_target@right_target@middle_control@right_control
        else:
            raise ValueError

    ##  USER：---Braid门，前者是fermionic site控制位，后者是fermionic site目标位---
    def braid(self, control_index, target_index, *args):
        if control_index<target_index:
            left_control, middle_control, right_control=self.majorana_frame.split(control_index)
            left_target, middle_target, right_target=right_control.split(target_index)

            if len(middle_control.occupy_z)==1:
                middle_control=middle_control@MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [], -1)
            if len(middle_target.occupy_x)==1:
                middle_target=MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [], 1)@middle_target

            self.majorana_frame=left_control@middle_control@left_target@middle_target@right_target
        elif target_index<control_index:
            left_control, middle_control, right_control=self.majorana_frame.split(control_index)
            left_target, middle_target, right_target=left_control.split(target_index)

            if len(middle_control.occupy_z)==1:
                middle_control=middle_control@MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [], -1)
            if len(middle_target.occupy_x)==1:
                middle_target=MajoranaOperator([], [control_index], 1)@MajoranaOperator([target_index], [], 1)@middle_target
            self.majorana_frame=left_target@middle_target@right_target@middle_control@right_control
        else:
            if len(args)==0 or args[0]==0:
                self.p(control_index)
            elif len(args)==1 and args[0]==1:
                self.p(control_index)
                self.n(control_index)

    ##  USER：---执行pauli_index上的X-error---
    def x_error(self, pauli_index, p):
        if np.random.rand()<p:
            self.pauli_frame=self.pauli_frame@PauliOperator([pauli_index], [], 1)

    ##  USER：---执行pauli_index上的Y-error---
    def y_error(self, pauli_index, p):
        if np.random.rand()<p:
            self.pauli_frame=self.pauli_frame@PauliOperator([pauli_index], [pauli_index], 1j)

    ##  USER：---执行pauli_index上的Z-error---
    def z_error(self, pauli_index, p):
        if np.random.rand()<p:
            self.pauli_frame=self.pauli_frame@PauliOperator([], [pauli_index], 1)

    ##  USER：---执行majorana_index上的U-error---
    def u_error(self, majorana_index, p):
        if np.random.rand()<p:
            self.majorana_frame=self.majorana_frame@MajoranaOperator([majorana_index], [], 1)

    ##  USER：---执行majorana_index上的V-error---
    def v_error(self, majorana_index, p):
        if np.random.rand()<p:
            self.majorana_frame=self.majorana_frame@MajoranaOperator([], [majorana_index], 1)

    ##  USER：---执行majorana_index上的N-error---
    def n_error(self, majorana_index, p):
        if np.random.rand()<p:
            self.majorana_frame=self.majorana_frame@MajoranaOperator([majorana_index], [majorana_index], 1j)

    ##  USER：---将系统在pauli_index上重置为0态---
    def reset(self, pauli_index):

        ##  ---数据预处理---
        assert isinteger(pauli_index) and 0<=pauli_index<self.pauli_number

        ##  ---重置0态---
        self.pauli_frame.occupy_x=np.delete(self.pauli_frame.occupy_x, np.where(self.pauli_frame.occupy_x==pauli_index))
        self.pauli_frame.occupy_z=np.delete(self.pauli_frame.occupy_z, np.where(self.pauli_frame.occupy_z==pauli_index))
        if np.random.rand()<0.5:
            self.pauli_frame=self.pauli_frame@PauliOperator([], [pauli_index], 1)

    ##  USER：---将系统在majorana_index上重置为空态---
    def fermionic_reset(self, majorana_index):

        ##  ---数据预处理---
        assert isinteger(majorana_index) and 0<=majorana_index<self.majorana_number

        ##  ---重置空态---
        self.majorana_frame.occupy_x=np.delete(self.majorana_frame.occupy_x, np.where(self.majorana_frame.occupy_x==majorana_index))
        self.majorana_frame.occupy_z=np.delete(self.majorana_frame.occupy_z, np.where(self.majorana_frame.occupy_z==majorana_index))
        if np.random.rand()<0.5:
            self.majorana_frame=self.majorana_frame@MajoranaOperator([majorana_index], [majorana_index], 1j)
