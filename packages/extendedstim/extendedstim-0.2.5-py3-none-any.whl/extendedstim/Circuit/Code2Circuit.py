from extendedstim.Code.QuantumCode.MajoranaCode import MajoranaCode
from extendedstim.Circuit.Circuit import Circuit
from extendedstim.Code.QuantumCode.MajoranaCSSCode import MajoranaCSSCode
from extendedstim.Code.QuantumCode.PauliCSSCode import PauliCSSCode
from extendedstim.Code.QuantumCode.PauliCode import PauliCode
from extendedstim.tools import *


#%%  USER：===将量子码转换为量子线路===
def Code2Circuit(code,p_noise,p_measure,noise_model,cycle_number):
    ##  ---数据预处理---
    assert isreal(p_noise) and 0<=p_noise<=1
    assert isreal(p_measure) and 0<=p_measure<=1
    assert isinteger(cycle_number) and cycle_number>=0
    assert isinstance(code,MajoranaCode) or isinstance(code,PauliCode)

    ##  ---根据量子码类型选择不同的处理函数---
    ##  处理现象级噪声
    if noise_model=='phenomenological':
        if isinstance(code,MajoranaCSSCode):
            return MajoranaCSSCode2PhenomenologicalCircuit(code,p_noise,p_measure,cycle_number)
        elif isinstance(code,PauliCSSCode):
            return PauliCSSCode2PhenomenologicalCircuit(code,p_noise,p_measure,cycle_number)
        elif isinstance(code,MajoranaCode):
            raise NotImplementedError
        elif isinstance(code,PauliCode):
            raise NotImplementedError
        else:
            raise NotImplementedError

    ##  处理电路级噪声
    elif noise_model=='circuit-level':
        if isinstance(code,MajoranaCSSCode):
            return MajoranaCSSCode2CircuitLevelCircuit(code,p_noise,p_measure,cycle_number)
        elif isinstance(code,PauliCSSCode):
            return PauliCSSCode2CircuitLevelCircuit(code,p_noise,p_measure,cycle_number)
        elif isinstance(code,MajoranaCode):
            raise NotImplementedError
        elif isinstance(code,PauliCode):
            raise NotImplementedError
        else:
            raise NotImplementedError

    ##  其他类型抛出异常
    else:
        raise ValueError('noise_model must be phenomenological, circuit-level, or code-capacity')


#%%  KEY：===将Majorana CSS code转换为现象级噪声下的测试线路===
def MajoranaCSSCode2PhenomenologicalCircuit(code,p_noise,p_measure,cycle_number:int):

    ##  ---数据预处理---
    assert isinstance(code,MajoranaCSSCode)
    stabilizers_x=code.generators_x
    stabilizers_z=code.generators_z
    logical_x=code.logical_operators_x
    logical_z=code.logical_operators_z

    ##  获取logical operators
    logical_occupy=[]
    for i in range(len(logical_x)):
        logical_occupy.append(1j*logical_x[i]@logical_z[i])

    majorana_number=code.physical_number
    stabilizer_number = len(stabilizers_x) + len(stabilizers_z)

    ##  ---生成线路---
    ##  初始化
    circuit = Circuit()
    circuit.append({'name':'FR','target':range(code.physical_number)})

    ##  第一轮测量假设完美的初始化
    observable_include= []  # 记录可观测量的索引
    for i,logical_operator in enumerate(logical_occupy):
        circuit.append({"name":"MPP","target":logical_operator})
        observable_include.append(len(circuit._measurements)-1)
    for i,stabilizer in enumerate(stabilizers_x):
        circuit.append({"name":"MPP","target":stabilizer})
    for i,stabilizer in enumerate(stabilizers_z):
        circuit.append({"name":"MPP","target":stabilizer})

    ##  循环多轮，多轮测量错误与量子噪声信道
    for _ in range(cycle_number):

        ##  量子噪声信道
        for i in range(majorana_number):
            circuit.append({"name":"FDEPOLARIZE1","target":i,"p":p_noise})

        ##  测量稳定子
        for i,stabilizer in enumerate(stabilizers_x):
            circuit.append({"name":"MPP","target":stabilizer,'p':p_measure})
        for i,stabilizer in enumerate(stabilizers_z):
            circuit.append({"name":"MPP","target":stabilizer,'p':p_measure})

        ##  添加探测器
        for i in range(stabilizer_number):
            circuit.append({"name":"DETECTOR","target":[-i - 1, -i - stabilizer_number-1]})

    ##  最后一轮测量稳定子，假设没有噪声
    for i,stabilizer in enumerate(stabilizers_x):
        circuit.append({"name":"MPP","target":stabilizer})
    for i,stabilizer in enumerate(stabilizers_z):
        circuit.append({"name":"MPP","target":stabilizer})

    ##  测量逻辑算符
    for i,logical_operator in enumerate(logical_occupy):
        circuit.append({"name":"MPP","target":logical_operator})
        circuit.append({"name":"OBSERVABLE_INCLUDE","target":[len(circuit._measurements)-1, observable_include[i]]})

    ##  ---返回线路---
    return circuit


#%%  KEY：===将Majorana CSS code转换为线路级噪声下的测试线路===
def MajoranaCSSCode2CircuitLevelCircuit(code,p_noise,p_measure,cycle_number:int):

    ##  ---数据预处理---
    ##  获取稳定子
    stabilizers_x=code.generators_x
    stabilizers_z=code.generators_z

    ##  获取逻辑算符
    logical_x=code.logical_operators_x
    logical_z=code.logical_operators_z
    logical_occupy=[1j*logical_x[temp]@logical_z[temp] for temp in range(len(logical_x))]  # 粒子数算符组作为逻辑算符组

    ##  获取数目
    majorana_number=code.physical_number
    stabilizer_number = len(stabilizers_x) + len(stabilizers_z)
    pauli_number=stabilizer_number

    ##  ---生成线路---
    ##  初始化
    circuit = Circuit()
    circuit.append({'name':'FR','target':range(majorana_number)})
    circuit.append({'name':'R','target':range(pauli_number)})

    ##  第一轮测量假设完美的初始化
    observable_include= []  # 记录可观测量的索引
    for i,logical_operator in enumerate(logical_occupy):
        circuit.append({"name":"MPP","target":logical_operator})
        observable_include.append(len(circuit._measurements)-1)
    for i,stabilizer in enumerate(stabilizers_x):
        circuit.append({"name":"MPP","target":stabilizer})
    for i,stabilizer in enumerate(stabilizers_z):
        circuit.append({"name":"MPP","target":stabilizer})

    ##  添加第一轮噪声
    for i in range(majorana_number):
        circuit.append({"name": "FDEPOLARIZE1", "target": i, "p": p_noise})
    for i in range(pauli_number):
        circuit.append({"name": "DEPOLARIZE1", "target": i, "p": p_noise})

    ##  循环多轮，多轮测量错误与量子噪声信道
    for _ in range(cycle_number):

        ##  添加稳定子测量
        for i,stabilizer in enumerate(stabilizers_x):
            sequence_temp=syndrome_majorana_css_measurement_circuit(stabilizer, i, 'x', p_noise, p_measure)
            for temp in sequence_temp:
                circuit.append(temp)
        for i,stabilizer in enumerate(stabilizers_z):
            sequence_temp=syndrome_majorana_css_measurement_circuit(stabilizer, i + len(stabilizers_x), 'z', p_noise, p_measure)
            for temp in sequence_temp:
                circuit.append(temp)

        ##  添加检测器
        for i in range(stabilizer_number):
            circuit.append({"name":"DETECTOR","target":[-i - 1, -i - stabilizer_number-1]})

    ##  最后一轮测量假设是没有噪声的
    ##  添加稳定子测量
    for i,stabilizer in enumerate(stabilizers_x):
        circuit.append({"name":"MPP","target":stabilizer})
    for i,stabilizer in enumerate(stabilizers_z):
        circuit.append({"name":"MPP","target":stabilizer})

    ##  添加检测器
    for i in range(stabilizer_number):
        circuit.append({"name": "DETECTOR", "target": [-i - 1, -i - stabilizer_number - 1]})

    ##  测量逻辑算符
    for i,logical_operator in enumerate(logical_occupy):
        circuit.append({"name":"MPP","target":logical_operator})
        circuit.append({"name":"OBSERVABLE_INCLUDE","target":[len(circuit._measurements)-1, observable_include[i]]})

    ##  ---返回线路---
    return circuit


#%%  KEY：===将Pauli CSS code转换为现象级噪声下的测试线路===
def PauliCSSCode2PhenomenologicalCircuit(code,p_noise,p_measure,cycle_number:int):

    ##  ---数据预处理---
    ##  获取稳定子
    stabilizers_x=code.generators_x
    stabilizers_z=code.generators_z

    ##  获取逻辑算符
    logical_x=code.logical_operators_x
    logical_z=code.logical_operators_z

    ##  获取数目
    stabilizer_number = len(stabilizers_x) + len(stabilizers_z)
    data_number=code.physical_number
    pauli_number=data_number+stabilizer_number

    ##  ---生成线路---
    ##  初始化
    circuit_x=Circuit()
    circuit_z=Circuit()
    circuit_x.append({'name': 'R', 'target': range(pauli_number)})
    circuit_z.append({'name': 'R', 'target': range(pauli_number)})

    ##  第一轮测量假设完美的初始化
    observable_include = []  # 记录可观测量的索引
    for i in range(len(logical_x)):
        circuit_x.append({"name": "MPP", "target": logical_x[i]})
        circuit_z.append({"name": "MPP", "target": logical_z[i]})
        observable_include.append(len(circuit_x._measurements)-1)
    for i, stabilizer in enumerate(stabilizers_x):
        circuit_x.append({"name": "MPP", "target": stabilizer})
        circuit_z.append({"name": "MPP", "target": stabilizer})
    for i, stabilizer in enumerate(stabilizers_z):
        circuit_z.append({"name": "MPP", "target": stabilizer})
        circuit_x.append({"name": "MPP", "target": stabilizer})

    ##  循环多轮，多轮测量错误与量子噪声信道
    for _ in range(cycle_number):

        ##  量子噪声信道
        for i in range(pauli_number):
            circuit_x.append({"name": "DEPOLARIZE1", "target": i, "p":p_noise})
            circuit_z.append({"name": "DEPOLARIZE1", "target": i, "p":p_noise})

        ##  测量稳定子
        for i, stabilizer in enumerate(stabilizers_x):
            circuit_x.append({"name": "MPP", "target": stabilizer, 'p': p_measure})
            circuit_z.append({"name": "MPP", "target": stabilizer, 'p': p_measure})
        for i, stabilizer in enumerate(stabilizers_z):
            circuit_x.append({"name": "MPP", "target": stabilizer, 'p': p_measure})
            circuit_z.append({"name": "MPP", "target": stabilizer, 'p': p_measure})

        ##  添加探测器
        for i in range(stabilizer_number):
            circuit_x.append({"name": "DETECTOR", "target": [-i-1, -i-stabilizer_number-1]})
            circuit_z.append({"name": "DETECTOR", "target": [-i-1, -i-stabilizer_number-1]})

    ##  最后一轮测量稳定子，假设没有噪声
    for i, stabilizer in enumerate(stabilizers_x):
        circuit_x.append({"name": "MPP", "target": stabilizer})
        circuit_z.append({"name": "MPP", "target": stabilizer})
    for i, stabilizer in enumerate(stabilizers_z):
        circuit_x.append({"name": "MPP", "target": stabilizer})
        circuit_z.append({"name": "MPP", "target": stabilizer})

    ##  测量逻辑算符
    for i in range(len(logical_x)):
        circuit_x.append({"name": "MPP", "target": logical_x[i]})
        circuit_z.append({"name": "MPP", "target": logical_z[i]})
        circuit_x.append({"name": "OBSERVABLE_INCLUDE", "target": [len(circuit_x._measurements)-1, observable_include[i]]})
        circuit_z.append({"name": "OBSERVABLE_INCLUDE", "target": [len(circuit_z._measurements)-1, observable_include[i]]})

    ##  ---返回线路---
    return circuit_x, circuit_z


#%%  KEY：===将Pauli CSS code转换为电路级噪声下的测试线路===
def PauliCSSCode2CircuitLevelCircuit(code,p_noise,p_measure,cycle_number:int):
    ##  ---数据预处理---
    ##  获取稳定子
    stabilizers_x=code.generators_x
    stabilizers_z=code.generators_z

    ##  获取逻辑算符
    logical_x=code.logical_operators_x
    logical_z=code.logical_operators_z

    ##  获取数目
    stabilizer_number = len(stabilizers_x) + len(stabilizers_z)
    data_number=code.physical_number
    pauli_number=data_number+stabilizer_number

    ##  ---生成线路---
    ##  强制初始化
    circuit_x = Circuit()
    circuit_z = Circuit()
    circuit_x.append({'name':'R','target':range(data_number)})
    circuit_z.append({'name':'R','target':range(data_number)})

    ##  第一轮测量假设完美的初始化
    observable_include = []  # 记录可观测量的索引
    for i in range(len(logical_x)):
        circuit_x.append({"name": "MPP", "target": logical_x[i]})
        circuit_z.append({"name": "MPP", "target": logical_z[i]})
        observable_include.append(len(circuit_x._measurements)-1)
    for i, stabilizer in enumerate(stabilizers_x):
        circuit_x.append({"name": "MPP", "target": stabilizer})
        circuit_z.append({"name": "MPP", "target": stabilizer})
    for i, stabilizer in enumerate(stabilizers_z):
        circuit_z.append({"name": "MPP", "target": stabilizer})
        circuit_x.append({"name": "MPP", "target": stabilizer})

    ##  施加第一轮噪声
    for i in range(pauli_number):
        circuit_z.append({"name": "DEPOLARIZE1", "target": i, "p": p_noise})

    ##  循环多轮，多轮测量错误与量子噪声信道
    for _ in range(cycle_number):

        ##  测量稳定子
        for i, stabilizer in enumerate(stabilizers_x):
            sequence_temp = syndrome_pauli_css_measurement_circuit(stabilizer, i + data_number, 'x', p_noise, p_measure)
            for temp in sequence_temp:
                circuit_z.append(temp)
                circuit_x.append(temp)
        for i, stabilizer in enumerate(stabilizers_z):
            sequence_temp = syndrome_pauli_css_measurement_circuit(stabilizer, i + data_number + len(stabilizers_x), 'z', p_noise, p_measure)
            for temp in sequence_temp:
                circuit_z.append(temp)
                circuit_x.append(temp)

        ##  添加检测器
        for i in range(stabilizer_number):
            circuit_z.append({"name": "DETECTOR", "target": [-i - 1, -i - stabilizer_number - 1]})
            circuit_x.append({"name": "DETECTOR", "target": [-i - 1, -i - stabilizer_number - 1]})

    ##  最后一轮测量假设是没有噪声的
    ##  测量稳定子
    for i, stabilizer in enumerate(stabilizers_x):
        circuit_z.append({"name": "MPP", "target": stabilizer})
        circuit_x.append({"name": "MPP", "target": stabilizer})
    for i, stabilizer in enumerate(stabilizers_z):
        circuit_z.append({"name": "MPP", "target": stabilizer})
        circuit_x.append({"name": "MPP", "target": stabilizer})

    ##  添加检测器
    for i in range(stabilizer_number):
        circuit_z.append({"name": "DETECTOR", "target": [-i - 1, -i - stabilizer_number - 1]})
        circuit_x.append({"name": "DETECTOR", "target": [-i - 1, -i - stabilizer_number - 1]})

    ##  测量逻辑算符
    for i in range(len(logical_x)):
        circuit_z.append({"name": "MPP", "target": logical_z[i]})
        circuit_x.append({"name": "MPP", "target": logical_x[i]})
        circuit_z.append({"name": "OBSERVABLE_INCLUDE", "target": [len(circuit_z._measurements)-1, observable_include[i]]})
        circuit_x.append({"name": "OBSERVABLE_INCLUDE", "target": [len(circuit_x._measurements)-1, observable_include[i]]})

    ##  ---返回线路---
    return circuit_x, circuit_z


# %%  KEY：===生成Majorana CSS stabilizer测量线路===
def syndrome_majorana_css_measurement_circuit(stabilizer, qubit_index, type, p_noise, p_measure):

    ##  ———数据预处理———
    sequence = []  # 线路序列
    flag = True  # 门类型标志

    ##  将qubit置于负号匹配
    sequence.append({'name': 'X', 'target': qubit_index})
    sequence.append({'name': 'DEPOLARIZE1', 'target': qubit_index, 'p': p_noise})

    ##  判断稳定子类型
    if type == 'x' or type == 'X':
        occupy=stabilizer.occupy_x
    elif type == 'z' or type == 'Z':
        occupy=stabilizer.occupy_z
    else:
        raise ValueError

    ##  ---生成纠缠线路---
    ##  生成前一半线路
    for j in range(len(occupy)):
        majorana_index_now = occupy[j]

        ##  最后一位与qubit作用CNX gate
        if j == len(occupy) - 1:
            sequence.append({'name': 'CNX', 'target': [majorana_index_now, qubit_index], })
            sequence.append({'name': 'FDEPOLARIZE1', 'target': majorana_index_now, 'p': p_noise})
            sequence.append({'name': 'DEPOLARIZE1', 'target': qubit_index, 'p': p_noise})
            break

        majorana_index_down = occupy[j + 1]  # 后一个fermionic site
        ##  作用braid gate
        if flag:
            ##  根据稳定子类型选择braid形式
            if type == 'X' or type == 'x':
                order_target = [majorana_index_down, majorana_index_now]
            elif type == 'Z' or type == 'z':
                order_target = [majorana_index_now, majorana_index_down]
            else:
                raise ValueError

            ##  添加braid gate
            sequence.append({"name": "BRAID", "target": order_target, })
            sequence.append({'name': 'FDEPOLARIZE1', 'target': order_target, 'p': p_noise})
            flag = False

        ##  作用CNN gate
        else:
            sequence.append({'name': 'CNN', 'target': [majorana_index_now, majorana_index_down], })
            sequence.append({'name': 'FDEPOLARIZE1', 'target': [majorana_index_now, majorana_index_down], 'p': p_noise})
            flag = True

    ##  生成syndrome extraction circuit的另一半
    flag = True
    for j in range(len(occupy) - 1):
        majorana_index_now = occupy[-1 - j]  # 当前的fermionic site
        majorana_index_up = occupy[-1 - j - 1]  # 上一个fermionic site

        ##  作用braid gate
        if flag:
            if type == 'X' or type == 'x':
                order_target = [majorana_index_now, majorana_index_up]
            elif type == 'Z' or type == 'z':
                order_target = [majorana_index_up, majorana_index_now]
            else:
                raise ValueError
            sequence.append({'name': 'N', 'target': [majorana_index_now]})
            sequence.append({'name': 'FDEPOLARIZE1', 'target': majorana_index_now, 'p': p_noise})
            sequence.append({'name': 'BRAID', 'target': order_target})
            sequence.append({'name': 'FDEPOLARIZE1', 'target': order_target, 'p': p_noise})
            sequence.append({'name': 'N', 'target': [majorana_index_now]})
            sequence.append({'name': 'FDEPOLARIZE1', 'target': majorana_index_now, 'p': p_noise})
            flag = False

        ##  作用CNN gate
        else:
            sequence.append({'name': 'CNN', 'target': [majorana_index_now, majorana_index_up]})
            sequence.append({'name': 'FDEPOLARIZE1', 'target': [majorana_index_now, majorana_index_up], 'p': p_noise})
            flag = True

    ##  在qubit上测量结果并重置
    sequence.append({'name': 'MZ', 'target': qubit_index, 'p': p_measure})
    sequence.append({'name': 'R', 'target': qubit_index})
    sequence.append({'name': 'DEPOLARIZE1', 'target': qubit_index, 'p': p_noise})

    ##  ———返回线路序列———
    return sequence


#%%  KEY：===生成Pauli CSS stabilizer测量线路===
def syndrome_pauli_css_measurement_circuit(stabilizer, qubit_index, type, p_noise, p_measure):

    ##  ———数据预处理———
    sequence = []  # 线路序列

    ##  判断稳定子类型
    if type == 'x' or type == 'X':
        occupy=stabilizer.occupy_x
    elif type == 'z' or type == 'Z':
        occupy=stabilizer.occupy_z
    else:
        raise ValueError

    ##  ---生成纠缠线路---
    for j in range(len(occupy)):
        if type == 'Z' or type == 'z':
            sequence.append({'name': 'CX', 'target': [occupy[j], qubit_index]})
            sequence.append({'name': 'DEPOLARIZE1', 'target': [occupy[j], qubit_index], 'p': p_noise})
        elif type == 'X' or type == 'x':
            sequence.append({'name': 'H', 'target': qubit_index})
            sequence.append({'name': 'DEPOLARIZE1', 'target': qubit_index, 'p': p_noise})
            sequence.append({'name': 'CX', 'target': [qubit_index,occupy[j]]})
            sequence.append({'name': 'DEPOLARIZE1', 'target': [occupy[j],qubit_index], 'p': p_noise})
            sequence.append({'name': 'H', 'target': qubit_index})
            sequence.append({'name': 'DEPOLARIZE1', 'target': qubit_index, 'p': p_noise})
        else:
            raise ValueError

    ##  在qubit上测量结果并重置
    sequence.append({'name': 'MZ', 'target': qubit_index, 'p': p_measure})
    sequence.append({'name': 'R', 'target': qubit_index})
    sequence.append({'name': 'DEPOLARIZE1', 'target': qubit_index, 'p': p_noise})

    ##  ———返回线路序列———
    return sequence
