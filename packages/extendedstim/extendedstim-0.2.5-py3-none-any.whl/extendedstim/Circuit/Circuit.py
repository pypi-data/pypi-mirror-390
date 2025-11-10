import copy
import pymatching
import qiskit
import numpy as np
import stim
import stimbposd
from qiskit.circuit import CircuitError
from qiskit.circuit.library import XGate, ZGate
from tesseract_decoder import tesseract
from extendedstim.Physics.MajoranaOperator import MajoranaOperator
from extendedstim.Physics.PauliOperator import PauliOperator
from extendedstim.Platform.Frame import Frame
from extendedstim.Platform.Platform import Platform
from extendedstim.tools import isinteger, islist


class Circuit:

    #%%  USER：===构造方法===
    def __init__(self)->None:

        ##  用户属性
        self.majorana_number=0  # fermionic sites的数目
        self.pauli_number=0  # qubits的数目
        self.sequence=[]  # 量子线路的操作序列
        self.noise=[]  # 量子线路中噪声的索引

        ##  系统属性
        self._sequence:list[dict]=[]  # 量子线路的操作序列（真实计算使用）
        self._measurements:list[int]=[]  # 量子线路中测量的索引
        self._detectors:list[list[int]]=[]  # 量子线路中测量的结果探测器对self.measurements的索引
        self._observables:list[list[int]]=[]  # 量子线路中可观测量的对self.measurements的索引
        self._dem_str_list: list[list[str]]=[]  # 量子线路错误模型的字符串表示
        self._dem:stim.DetectorErrorModel|None=None  # 量子线路错误模型
        self._reference_circuit:Circuit|None=None  # 参考线路
        self._reference_measurement_sample:list[int]|None=None  # 参考样本的测量值
        self._reference_detector_sample:list[list[int]]|None=None  # 参考样本的检测值
        self._reference_observable_sample:list[list[int]]|None=None  # 参考样本的可观测量值

    #%%  USER：===重载运算符===
    ##  USER：---获取序列中的元素---
    def __getitem__(self, item: int) -> dict:
        return self.sequence[item]

    #%%  USER：===属性方法===
    ##  KEY：---生成无噪声的线路---
    @property
    def reference_circuit(self)->'Circuit':
        if self._reference_circuit is not None:
            return self._reference_circuit
        else:
            ideal_circuit=copy.deepcopy(self)  # 深拷贝操作序列
            for i in range(len(self.noise)):
                ideal_circuit._sequence[self.noise[i]]['p']=0
            return ideal_circuit

    ##  USER：获取参考样本
    @property
    def reference_sample(self):
        if self._reference_measurement_sample is None:
            reference_measurement_sample, reference_detector_sample, reference_observable_sample=self.reference_circuit.execute()
            self._reference_measurement_sample=reference_measurement_sample
            self._reference_detector_sample=reference_detector_sample
            self._reference_observable_sample=reference_observable_sample
            return reference_measurement_sample, reference_detector_sample, reference_observable_sample
        else:
            return self._reference_measurement_sample, self._reference_detector_sample, self._reference_observable_sample

    ##  USER：--生成检测错误模型--
    def detector_error_model(self) -> stim.DetectorErrorModel:
        if self._dem is not None:
            return self._dem
        measurement_sample_origin, detector_sample_origin, observable_sample_origin=self.reference_sample

        ##  执行检验线路的稳定性
        for time in range(5):
            measurement_sample, detector_sample, observable_sample=self.reference_circuit.sample()
            assert np.all(detector_sample==detector_sample_origin), f'原始线路的detector不是稳定的'
            assert np.all(observable_sample==observable_sample_origin), f'原始线路的observable不是稳定的'

        errors=[]
        dem_str=''
        reference_circuit=copy.deepcopy(self.reference_circuit)
        for i in range(len(self.noise)):
            print(i/len(self.noise))

            ##  数据分析
            order=self.noise[i]
            gate_ideal=reference_circuit._sequence[order]
            gate=self._sequence[order]
            assert isinstance(gate_ideal, dict)
            assert isinstance(gate, dict)
            gate_ideal['p']=1.1
            p=gate['p']

            ##  计算错误位置
            measurement_sample, detector_sample, observable_sample=reference_circuit.sample()
            detector_sample_diff=[detector_sample_origin[j]^detector_sample[j] for j in range(len(detector_sample))]
            observable_sample_diff=[observable_sample_origin[j]^observable_sample[j] for j in range(len(observable_sample))]
            errors.append(len(errors))
            detectors_trigger=np.where(np.array(detector_sample_diff)==True)[0]
            observables_trigger=np.where(np.array(observable_sample_diff)==True)[0]

            ##  合成错误语句
            if len(detectors_trigger)>0 or len(observables_trigger)>0:
                temp_error:str=f'error({p}) '
                temp_trigger:str=''
                for index in detectors_trigger:
                    temp_trigger=temp_trigger+f' D{index}'
                for index in observables_trigger:
                    temp_trigger=temp_trigger+f' L{index}'
                temp=temp_error+temp_trigger
                if gate['name']=='M_ERROR':
                    self._dem_str_list.append([temp_error, temp_trigger, 'M_ERROR'])
                else:
                    self._dem_str_list.append([temp_error, temp_trigger, 'G_ERROR'])
                dem_str+=('\n'+temp)
            gate_ideal['p']=0

        ##  返回错误模型
        dem=stim.DetectorErrorModel(dem_str)
        self._dem=dem
        return dem

    #%%  USER：===对象方法===
    ##  USER：---添加量子线路组分操作---
    def append(self, params):
        """""
        {
        'name': str，线路操作的名称
        'target': list or int，操作作用的对象
        'p': float，操作对应的概率，不一定有
        'index': int，测量对应平台上的stabilizers的序号
        'majorana_state': list of MajoranaOperator，强制初始化的majorana state
        'pauli_state': list of PauliOperator，强制初始化的pauli state
        'pauli_number': int，强制初始化的qubits数目
        'majorana_number': int，强制初始化的fermionic sites数目
        }
        支持的线路操作名称：
        'X', 'Y', 'Z', 'H', 'S'：{'name':str,'target':int or list}, single qubit上的qugate
        'X_ERROR', 'Y_ERROR', 'Z_ERROR', 'DEPOLARIZE': {'name':str,'target':int or list}, single qubit上的噪声
        'U', 'V', 'N', 'P'：{'name':str,'target':int or list}, single fermionic site上的fgate
        'U_ERROR', 'V_ERROR', 'N_ERROR', 'FDEPOLARIZE1': {'name':str,'target':int or list}, single fermionic site上的噪声
        'CX', 'CNX', 'CNN', 'BRAID': {'name':str,'target':list}, two qubit or fermionic sites上的gates
        'R','FR': {'name':str,'target':int or list}, single qubit or single fermionic sites上的重置到空态或0态
        'MZ', 'MN': {'name':str,'target':int or list}, single qubit or single fermionic sites上的measurement
        'MPP': {'name':str,'target':list or Operator}, Pauli string operators or Majorana string operators的measurement
        'FORCE'：{'name':str,'pauli_number':int,'majorana_number':int,'pauli_state':list of PauliOperator,'majorana_state':list of MajoranaOperator}, 强制初始化
        'DETECTOR': {'name':str,'target':list of int}，探测器
        'OBSERVABLE_INCLUDE': {'name':str,'target':list of int}，可观测量
        """""

        ##  ---数据预处理---
        assert isinstance(params, dict)
        assert 'name' in params
        name=params["name"]  # 线路操作的名称

        ##  ---添加量子线路操作---
        ##  添加single gate
        if name in ['X', 'Y', 'Z', 'H', 'S', 'X_ERROR', 'Y_ERROR', 'Z_ERROR', 'U', 'V', 'N', 'P', 'U_ERROR', 'V_ERROR', 'N_ERROR']:

            ##  作用在整数index对应目标上
            if isinteger(params['target']):
                self._sequence.append(params.copy())
                self.sequence.append(self._sequence[-1])

            ##  作用在一系列目标上
            elif islist(params['target']):
                for temp in params['target']:
                    params_temp={'name': name, 'target': temp}
                    self.append(params_temp)

        ##  添加two gate
        elif name in ['CX', 'CNX', 'CNN']:

            ##  添加单个two gate
            if islist(params['target']) and len(params['target'])==2 and isinteger(params['target'][0]) and isinteger(params['target'][1]):
                self._sequence.append(params.copy())
                self.sequence.append(self._sequence[-1])

            ##  用单个列表添加多个two gates
            elif islist(params['target']) and isinteger(params['target'][0]):
                for i in range(len(params['target'])//2):
                    params_temp={'name': name, 'target': [params['target'][2*i], params['target'][2*i+1]]}
                    self.append(params_temp)

            ##  用多个列表添加多个two gates
            elif islist(params['target']):
                for temp in params['target']:
                    self.append({'name': name, 'target': temp})

            ##  其他情况抛出异常
            else:
                raise ValueError("CX, CNX, CNN gate must be applied to two")

        ##  添加braid gate
        elif name=='BRAID' or name=='braid':

            if islist(params['target']) and len(params['target'])==2 and isinteger(params['target'][0]) and isinteger(params['target'][1]):
                x=params['target'][0]  # 控制位
                y=params['target'][1]  # 目标位

                ##  控制位等于目标位时，根据verse参数判断是否添加N门
                if x==y and 'verse' not in params:
                    self._sequence.append({'name': 'P', 'target': x})
                    self.sequence.append(self._sequence[-1])
                elif x==y and 'verse' in params and params['verse']==True:
                    self._sequence.append({'name': 'P', 'target': y})
                    self.sequence.append(self._sequence[-1])
                    self._sequence.append({'name': 'N', 'target': y})
                    self.sequence.append(self._sequence[-1])

                ##  一般情况下braid gate作用在两个不同的fermionic sites上
                elif x!=y:
                    self._sequence.append({'name': 'BRAID', 'target': [x, y]})
                    self.sequence.append(self._sequence[-1])

            ##  用单个列表添加多个two gates
            elif islist(params['target']) and isinteger(params['target'][0]):
                for i in range(len(params['target'])//2):
                    params_temp={'name': name, 'target': [params['target'][2*i], params['target'][2*i+1]]}
                    self.append(params_temp)

            ##  用多个列表添加多个two gates
            elif islist(params['target']):
                for temp in params['target']:
                    self.append({'name': name, 'target': temp})

            ##  其他情况抛出异常
            else:
                raise ValueError("CX, CNX, CNN gate must be applied to two")

        ##  添加qubit上的去极化噪声
        elif name=='DEPOLARIZE1':
            assert 'p' in params

            ##  作用在整数index对应目标上
            if isinteger(params['target']):
                self.sequence.append({'name': 'DEPOLARIZE1', 'target': params['target'], 'p': params['p']})
                fix=(1-np.sqrt(1-4*params["p"]/3))/2
                self._sequence.append({'name': 'X_ERROR', 'target': params["target"], 'p': fix})
                self.noise.append(len(self._sequence)-1)
                self._sequence.append({'name': 'Y_ERROR', 'target': params["target"], 'p': fix})
                self.noise.append(len(self._sequence)-1)
                self._sequence.append({'name': 'Z_ERROR', 'target': params["target"], 'p': fix})
                self.noise.append(len(self._sequence)-1)

            ##  作用在一系列目标上
            elif islist(params['target']):
                for temp in params['target']:
                    self.append({'name': params['name'], 'target': temp, 'p': params["p"]})

        ##  添加fermionic site上的去极化噪声
        elif name=='FDEPOLARIZE1':
            assert 'p' in params

            ##  作用在整数index对应目标上
            if isinteger(params['target']):
                self.sequence.append({'name': 'FDEPOLARIZE1', 'target': params['target'], 'p': params['p']})
                fix=(1-np.sqrt(1-4*params["p"]/3))/2
                self._sequence.append({'name': 'U_ERROR', 'target': params["target"], 'p': fix})
                self.noise.append(len(self._sequence)-1)
                self._sequence.append({'name': 'V_ERROR', 'target': params["target"], 'p': fix})
                self.noise.append(len(self._sequence)-1)
                self._sequence.append({'name': 'N_ERROR', 'target': params["target"], 'p': fix})
                self.noise.append(len(self._sequence)-1)

            ##  作用在一系列目标上
            elif islist(params['target']):
                for temp in params['target']:
                    self.append({'name': params['name'], 'target': temp, 'p': params["p"]})

        ##  添加single qubit and single fermionic site上的测量
        elif name=='MZ' or name=='MN':
            target=params['target']

            ##  作用在一系列目标上
            if islist(target):
                for temp in target:
                    dict_temp={'name': name, 'target': temp}
                    self.append(dict_temp)

            ##  作用在整数index对应目标上
            elif isinteger(target):
                if name=='MZ':
                    dict_temp={'name': 'MPP', 'target': PauliOperator([], [target], 1)}
                else:
                    dict_temp={'name': 'MPP', 'target': MajoranaOperator([target], [target], 1j)}
                self.append(dict_temp)

        ##  添加qubit重置
        elif name=='R':
            assert 'target' in params
            target=params['target']

            ##  作用在整数index对应目标上
            if isinteger(target):
                self._sequence.append({'name': name, 'target': target})
                self.sequence.append(self._sequence[-1])
                if target==self.pauli_number:
                    self.pauli_number+=1
                elif target>self.pauli_number or target<0:
                    raise ValueError("R gate target must be consecutive")
                else:
                    pass
            elif islist(target):
                for temp in target:
                    self.append({'name': name, 'target': temp})
            else:
                raise ValueError

        ##  添加fermionic site重置
        elif name=='FR':
            assert 'target' in params
            target=params['target']
            if isinteger(target):
                self._sequence.append({'name': name, 'target': target})
                self.sequence.append(self._sequence[-1])
                if target==self.majorana_number:
                    self.majorana_number=target+1
                elif target>self.majorana_number or target<0:
                    raise ValueError("FR gate target must be consecutive")
                else:
                    pass
            elif islist(target):
                for temp in target:
                    self.append({'name': name, 'target': temp})
            else:
                raise ValueError

        ##  强制初始化
        elif name=='FORCE':
            assert 'majorana_state' in params
            assert 'pauli_state' in params
            assert 'pauli_number' in params
            assert 'majorana_number' in params
            stabilizers_majorana: list[MajoranaOperator]=copy.deepcopy(params["majorana_state"])
            stabilizers_pauli: list[PauliOperator]=copy.deepcopy(params["pauli_state"])
            for i in range(len(stabilizers_majorana)):
                assert len(stabilizers_majorana[i].occupy_x)==0 or np.max(stabilizers_majorana[i].occupy_x)<self.majorana_number
                assert len(stabilizers_majorana[i].occupy_z)==0 or np.max(stabilizers_majorana[i].occupy_z)<self.majorana_number
            for i in range(len(stabilizers_pauli)):
                assert len(stabilizers_pauli[i].occupy_x)==0 or np.max(stabilizers_pauli[i].occupy_x)<self.pauli_number
                assert len(stabilizers_pauli[i].occupy_z)==0 or np.max(stabilizers_pauli[i].occupy_z)<self.pauli_number

            self.pauli_number=params["pauli_number"]
            self.majorana_number=params["majorana_number"]
            self._sequence.append({'name': 'FORCE', 'majorana_state': stabilizers_majorana, 'pauli_state': stabilizers_pauli})
            self.sequence.append(self._sequence[-1])

        ##  添加string算符的测量
        elif name=='MPP':
            assert 'target' in params
            if islist(params['target']):
                for i, temp in enumerate(params['target']):
                    dict_temp={'name': 'MPP', 'target': temp}
                    if 'index' in params:
                        dict_temp['index']=params['index'][i]
                    self.append(dict_temp)
            elif isinstance(params['target'], (PauliOperator, MajoranaOperator)):
                dict_temp={'name': 'MPP', 'target': params['target']}
                if 'index' in params:
                    dict_temp['index']=params['index']
                self._sequence.append(dict_temp)
                self._measurements.append(len(self._sequence)-1)
                if 'p' in params:
                    self._sequence.append({'name': 'M_ERROR', 'p': params["p"]})
                    self.noise.append(len(self._sequence)-1)
                    self.sequence.append({'name': 'MPP', 'target': params['target'], 'p': params["p"]})
                else:
                    self.sequence.append(self._sequence[-1])
            else:
                raise ValueError

        ##  添加监视器
        elif name=='DETECTOR':
            assert 'target' in params
            target=params['target']
            if all(target[i]<0 for i in range(len(target))):
                together=[len(self._measurements)+temp for temp in target]  # 在测量中找到对应索引
                self._detectors.append(together)
                self.sequence.append({'name': 'DETECTOR', 'target': target})
            elif all(target[i]>=0 for i in range(len(target))):
                self._detectors.append([temp for temp in target])
                self.sequence.append({'name': 'DETECTOR', 'target': [-len(self._measurements)+temp for temp in target]})
            else:
                raise ValueError("DETECTOR gate target must be consecutive")

        ##  添加可观测量
        elif name=='OBSERVABLE_INCLUDE':
            assert 'target' in params
            target=params['target']
            if all(target[i]<0 for i in range(len(target))):
                together=[len(self._measurements)+temp for temp in target]  # 在测量中找到索引
                self._observables.append(together)
                self.sequence.append({'name': 'OBSERVABLE_INCLUDE', 'target': target})
            elif all(target[i]>=0 for i in range(len(target))):
                together=[temp for temp in target]  # 在测量中找到索引
                self._observables.append(together)
                self.sequence.append({'name': 'OBSERVABLE_INCLUDE', 'target': [-len(self._measurements)+temp for temp in target]})
            else:
                raise ValueError("OBSERVABLE_INCLUDE gate target must be consecutive")
        else:
            raise NotImplementedError

    ##  USER：---执行线路并返回测量结果---
    def execute(self):

        ##  ---生成量子平台---
        platform=Platform()  # 生成量子平台
        platform.initialize(self.majorana_number, self.pauli_number)  # 初始化一定数目的qubits和fermionic sites
        measurement_sample=np.empty(len(self._measurements), dtype=int)  # 生成测量值的样本数组
        flag_measurement=0

        ##  遍历整个操作序列
        for i, gate in enumerate(self._sequence):
            name=gate['name']

            ##  执行单门
            if name in ['X', 'Y', 'Z', 'H', 'S', 'U', 'V', 'N']:
                target: int=gate['target']
                eval('platform.'+name.lower()+f'({target})')

            ##  执行双门
            elif name in ['CX', 'CNX', 'BRAID', 'CNN']:
                target: list=gate['target']
                eval('platform.'+name.lower()+f'({target[0]},{target[1]})')

            ##  执行重置
            elif name=='R':
                target: int=gate['target']
                platform.reset(target)

            elif name=='FR':
                target: int=gate['target']
                platform.fermionic_reset(target)

            ##  执行误差门
            elif name in ['X_ERROR', 'Y_ERROR', 'Z_ERROR', 'U_ERROR', 'V_ERROR', 'N_ERROR']:
                target: int=gate['target']
                p: float=gate['p']
                eval('platform.'+name.lower()+f'({target},{p})')

            elif name=='M_ERROR':
                p: float=gate['p']
                if np.random.rand()<p:
                    measurement_sample[flag_measurement-1]=-measurement_sample[flag_measurement-1]

            ##  执行测量
            elif name=='MPP':
                target=gate['target']
                if 'index' in gate:
                    measurement_sample[flag_measurement]=platform.measure(target, gate['index'])
                else:
                    measurement_sample[flag_measurement]=platform.measure(target)
                flag_measurement+=1

            ##  执行强制初始化
            elif name=='FORCE':
                assert gate['majorana_state'] is not None
                assert gate['pauli_state'] is not None
                platform.force(gate['majorana_state'], gate['pauli_state'])

            ##  其他类型抛出错误
            else:
                raise ValueError(f"Gate {name} is illegal")

        ##  ---返回可观测的结果---
        detector_sample=np.array([np.all(measurement_sample[self._detectors]==measurement_sample[detector][0])
                                  for detector in self._detectors], dtype=bool)
        observable_sample=np.array([np.all(measurement_sample[self._observables]==measurement_sample[observable][0])
                                  for observable in self._observables], dtype=bool)
        return measurement_sample, detector_sample, observable_sample

    ##  USER：--修改error model的错误几率--
    def noise_amplitude_fix(self, p_noise, p_measure):
        dem_str=''
        for i, temp in enumerate(self._dem_str_list):
            if temp[2]=='G_ERROR':
                temp[0]=f'error({p_noise/3}) '
            elif temp[2]=='M_ERROR':
                temp[0]=f'error({p_measure}) '
            dem_str+=('\n'+temp[0]+temp[1])
            self._dem=stim.DetectorErrorModel(dem_str)

    ##  USER：--生成解码函数--
    def decoder(self, method):
        dem=self.detector_error_model()
        if method=='bposd':
            decoder=stimbposd.bp_osd.BPOSD(model=dem, bp_method='min_sum', max_bp_iters=100)
        elif method=='tesseract':
            config=tesseract.TesseractConfig(dem=dem, det_beam=50)
            decoder=config.compile_decoder()
        elif method=='matching':
            decoder=pymatching.Matching()
            decoder.from_detector_error_model(dem)
        else:
            raise NotImplementedError
        return decoder

    ##  USER：---获取采样---
    def sample(self):
        frame=Frame()
        frame.initialize(self.majorana_number, self.pauli_number)
        reference_measurement_sample, reference_detector_sample, reference_observable_sample=self.reference_sample
        measurement_sample=np.empty(len(self._measurements), dtype=int)  # 生成测量值的样本数组
        flag_measurement=0
        ##  遍历整个操作序列
        for i, gate in enumerate(self._sequence):
            name=gate['name']

            ##  执行单门
            if name in ['X', 'Y', 'Z', 'H', 'S', 'U', 'V', 'N']:
                pass

            ##  执行双门
            elif name in ['CX', 'CNX', 'BRAID', 'CNN']:
                target: list=gate['target']
                eval('frame.'+name.lower()+f'({target[0]},{target[1]})')

            ##  执行重置
            elif name=='R':
                target: int=gate['target']
                frame.reset(target)

            elif name=='FR':
                target: int=gate['target']
                frame.fermionic_reset(target)

            ##  执行误差门
            elif name in ['X_ERROR', 'Y_ERROR', 'Z_ERROR', 'U_ERROR', 'V_ERROR', 'N_ERROR']:
                target: int=gate['target']
                p: float=gate['p']
                eval('frame.'+name.lower()+f'({target},{p})')

            elif name=='M_ERROR':
                p: float=gate['p']
                if np.random.rand()<p:
                    measurement_sample[flag_measurement-1]=-measurement_sample[flag_measurement-1]

            ##  执行测量
            elif name=='MPP':
                target=gate['target']
                measurement_sample[flag_measurement]=frame.measure(target, reference_measurement_sample[flag_measurement])
                flag_measurement+=1

            ##  执行强制初始化
            elif name=='FORCE':
                assert gate['majorana_state'] is not None
                assert gate['pauli_state'] is not None
                frame.force(gate['majorana_state'], gate['pauli_state'])

            ##  其他类型抛出错误
            else:
                raise ValueError(f"Gate {name} is illegal")

        ##  ---返回可观测的结果---
        detector_sample=np.array([np.all(measurement_sample[self._detectors]==measurement_sample[detector][0])
                                  for detector in self._detectors], dtype=bool)
        observable_sample=np.array([np.all(measurement_sample[self._observables]==measurement_sample[observable][0])
                                  for observable in self._observables], dtype=bool)
        return measurement_sample, detector_sample, observable_sample


    ##  USER：--执行线路并返回错误率--
    def experiment(self, sample_number: int, method: str):

        ##  生成线路执行样本和每个样本的预测样本
        dem=self.detector_error_model()  # 错误模型
        sampler=dem.compile_sampler()  # 采样器
        decoder=self.decoder(method)  # 解码器
        detector_data, obs_data, error_data=sampler.sample(shots=sample_number)  # 样本
        predictions=decoder.decode_batch(detector_data)  # 解码器对每个样本的预测

        ##  计算逻辑错误率
        num_errors=0
        for shot in range(sample_number):
            actual_for_shot=obs_data[shot]
            predicted_for_shot=predictions[shot]
            if not np.array_equal(actual_for_shot, predicted_for_shot):
                num_errors+=1

        ##  返回结果
        return num_errors/sample_number

    ##  USER：--生成stim的线路--
    def stim_circuit(self):
        circuit=stim.Circuit()
        flag_measure=0
        for i in range(len(self.sequence)):
            gate=self.sequence[i]
            name=gate['name']
            if name=='X' or name=='Y' or name=='Z' or name=='H' or name=='S' or name=='P':
                circuit.append(name, [gate['target']])

            ##  添加single-qubit上的噪声
            elif name=='X_ERROR' or name=='Y_ERROR' or name=='Z_ERROR':
                circuit.append(name, [gate['target']], gate['p'])

            ##  添加single-fermionic-site gate
            elif name in ['U', 'V', 'N', 'P', 'U_ERROR', 'V_ERROR', 'N_ERROR', 'CNX', 'CNN', 'B', 'braid', 'MN', 'FDEPOLARIZE1', 'FR']:
                raise NotImplementedError('stim只支持pauli circuit')

            ##  添加受控非门
            elif name=='CX':
                target=gate['target']
                circuit.append(name, target)

            ##  添加qubit上的去极化噪声
            elif name=='DEPOLARIZE1':
                target=gate['target']
                circuit.append(name, target, gate['p'])

            ##  强制初始化
            elif name=='FORCE':
                raise NotImplementedError('stim不支持强制初始化')

            ##  添加string算符的测量
            elif name=='MPP':

                ##  求string算符格式化表示
                op: PauliOperator=gate['target']
                occupy_x=op.occupy_x
                occupy_z=op.occupy_z

                ##  简单测量
                if len(occupy_x)==0 and len(occupy_z)==1:
                    if 'p' in gate:
                        circuit.append('MZ', [occupy_z[0]], gate['p'])
                    else:
                        circuit.append('MZ', [occupy_z[0]])
                    continue
                elif len(occupy_x)==1 and len(occupy_z)==0:
                    if 'p' in gate:
                        circuit.append('MX', [occupy_x[0]], gate['p'])
                    else:
                        circuit.append('MX', [occupy_x[0]])
                    continue
                elif len(occupy_x)==1 and len(occupy_z)==1 and occupy_x[0]==occupy_z[0]:
                    if 'p' in gate:
                        circuit.append('MY', [occupy_z[0]], gate['p'])
                    else:
                        circuit.append('MY', [occupy_z[0]])
                    continue

                ##  string operator测量
                op_str=''
                for i in range(self.pauli_number):
                    if i in occupy_x and i in occupy_z:
                        op_str+='Y'
                    elif i in occupy_z:
                        op_str+='Z'
                    elif i in occupy_x:
                        op_str+='X'
                    else:
                        op_str+='_'
                if 'p' in gate:
                    circuit.append('MPP', [stim.PauliString(op_str)], gate['p'])
                else:
                    circuit.append('MPP', [stim.PauliString(op_str)])

            ##  添加qubit重置
            elif name=='R':
                circuit.append('R', [gate['target']])

            ##  检测器
            elif name=='DETECTOR':
                circuit.append(name, [stim.target_rec(temp) for temp in gate['target']])

            ##  添加可观测量
            elif name=='OBSERVABLE_INCLUDE':
                circuit.append(name, [stim.target_rec(temp) for temp in gate['target']], flag_measure)
                flag_measure+=1
            else:
                raise NotImplementedError
        return circuit

    ##  USER：--绘制线路图--
    def draw(self, filename):

        # 绘制一个带有barriers和更多寄存器中，绘制一个新的电路
        F=qiskit.QuantumRegister(self.majorana_number, name='F')  # fermionic sites
        Q=qiskit.QuantumRegister(self.pauli_number, name='Q')  # qubits
        C=qiskit.ClassicalRegister(1, name='C')  # 经典寄存器
        A=qiskit.QuantumRegister(1, name='A')  # 无含义的ancilla
        circuit_qiskit=qiskit.QuantumCircuit(F, Q, C, A)
        braid=qiskit.circuit.ControlledGate(name='braid', num_qubits=2, params=[], label=None, num_ctrl_qubits=1, base_gate=XGate())
        cnn=qiskit.circuit.ControlledGate(name='CNN', num_qubits=2, params=[], label=None, num_ctrl_qubits=1, base_gate=ZGate())
        cnx=qiskit.circuit.ControlledGate(name='CNX', num_qubits=2, params=[], label=None, num_ctrl_qubits=1, base_gate=XGate())
        x_error=qiskit.circuit.Gate('X_ERROR', 1, label='X', params=[])
        y_error=qiskit.circuit.Gate('Y_ERROR', 1, label='Y', params=[])
        z_error=qiskit.circuit.Gate('Z_ERROR', 1, label='Z', params=[])
        u_error=qiskit.circuit.Gate('U_ERROR', 1, label='U', params=[])
        v_error=qiskit.circuit.Gate('V_ERROR', 1, label='V', params=[])
        n_error=qiskit.circuit.Gate('N_ERROR', 1, label='N', params=[])
        reset=qiskit.circuit.Gate('reset', 1, label=None, params=[])
        n=qiskit.circuit.Gate('N', 1, label='N', params=[])
        dep=qiskit.circuit.Gate('DEPOLARIZE', 1, label='D', params=[])

        ##  遍历电路序列，添加到qiskit电路中
        for gate in self.sequence:
            if gate['name']=='R':
                circuit_qiskit.append(reset, [Q[gate['target']]])
            elif gate['name']=='FR':
                circuit_qiskit.append(reset, [F[gate['target']]])
            elif gate['name']=='X':
                circuit_qiskit.x(Q[gate['target']])
            elif gate['name']=='Y':
                circuit_qiskit.y(Q[gate['target']])
            elif gate['name']=='Z':
                circuit_qiskit.z(Q[gate['target']])
            elif gate['name']=='H':
                circuit_qiskit.h(Q[gate['target']])
            elif gate['name']=='S':
                circuit_qiskit.s(Q[gate['target']])
            elif gate['name']=='N':
                circuit_qiskit.append(n, [F[gate['target']]])
            elif gate['name']=='CX':
                circuit_qiskit.cx(Q[gate['target'][0]], Q[gate['target'][1]])
            elif gate['name']=='braid':
                circuit_qiskit.append(braid, [F[gate['target'][0]], F[gate['target'][1]]])
            elif gate['name']=='CNN':
                circuit_qiskit.append(cnn, [F[gate['target'][0]], F[gate['target'][1]]])
            elif gate['name']=='CNX':
                circuit_qiskit.append(cnx, [F[gate['target'][0]], Q[gate['target'][1]]])
            elif gate['name']=='X_ERROR':
                circuit_qiskit.append(x_error, [Q[gate['target']]])
            elif gate['name']=='Y_ERROR':
                circuit_qiskit.append(y_error, [Q[gate['target']]])
            elif gate['name']=='Z_ERROR':
                circuit_qiskit.append(z_error, [Q[gate['target']]])
            elif gate['name']=='U_ERROR':
                circuit_qiskit.append(u_error, [F[gate['target']]])
            elif gate['name']=='V_ERROR':
                circuit_qiskit.append(v_error, [F[gate['target']]])
            elif gate['name']=='N_ERROR':
                circuit_qiskit.append(n_error, [F[gate['target']]])
            elif gate['name']=='DEPOLARIZE1':
                circuit_qiskit.append(dep, [Q[gate['target']]])
            elif gate['name']=='FDEPOLARIZE1':
                circuit_qiskit.append(dep, [F[gate['target']]])
            elif gate['name']=='MPP':
                op=gate['target']
                if isinstance(op, MajoranaOperator):
                    f_flag_x=op.occupy_x
                    f_flag_z=op.occupy_z
                    f_flag_n=np.intersect1d(f_flag_x, f_flag_z)
                    f_flag_x=np.setdiff1d(f_flag_x, f_flag_n)
                    f_flag_z=np.setdiff1d(f_flag_z, f_flag_n)
                    f=np.concatenate([f_flag_x, f_flag_z, f_flag_n])
                    if len(f)>1:
                        mppx=qiskit.circuit.ControlledGate(name='MPPX', num_qubits=len(f)+1, params=[], label=None, num_ctrl_qubits=len(f),
                                                           base_gate=XGate())
                        circuit_qiskit.append(mppx, F[f.tolist()]+[A[0]])
                        circuit_qiskit.measure(A[0], C[0])
                    else:
                        circuit_qiskit.measure(F[f[0]], C[0])
                elif isinstance(op, PauliOperator):
                    p_flag_x=op.occupy_x
                    p_flag_z=op.occupy_z
                    p_flag_y=np.intersect1d(p_flag_x, p_flag_z)
                    p_flag_x=np.setdiff1d(p_flag_x, p_flag_y)
                    p_flag_z=np.setdiff1d(p_flag_z, p_flag_y)
                    p=np.concatenate([p_flag_x, p_flag_y, p_flag_z])
                    if len(p)>1:
                        mppx=qiskit.circuit.ControlledGate(name='MPPX', num_qubits=len(p)+1, params=[], label=None, num_ctrl_qubits=len(p),
                                                           base_gate=XGate())
                        circuit_qiskit.append(mppx, Q[p.tolist()]+[A[0]])
                        circuit_qiskit.measure(A[0], C[0])
                    else:
                        circuit_qiskit.measure(Q[p[0]], C[0])
                else:
                    raise CircuitError("cannot set parameters on immutable base gate")
        ##  格式化颜色
        red='#E77081'
        blue='#5375CD'
        green='#00857B'
        grey='#8C92AC'
        purple='#5D548C'
        orange='#F15D22'
        pink='#FFACC5'
        cyan='#C9DCC4'

        ##  绘制线路
        circuit_qiskit.draw(output='mpl', filename=filename, style={
            'displaycolor': {'cx': None, 'cy': None, 'cz': None,
                             'X_ERROR': red, 'Y_ERROR': red, 'Z_ERROR': red,
                             'U_ERROR': red, 'V_ERROR': red, 'N_ERROR': red,
                             'R': cyan, 'measure': grey,
                             'x': blue, 'y': blue, 'z': blue, 's': blue, 'N': blue, 'U': blue, 'V': blue,
                             'CNN': blue, 'CNX': purple, 'braid': pink,
                             'MPPX': grey
                             },
            'fontsize': 12
        })

    ##  USER：---复制函数---
    def copy(self):
        return copy.deepcopy(self)


class Detector:
    def __init__(self,measurement_indices:list)->None:
        self.indices=np.array(measurement_indices,dtype=int)

    def __getitem__(self,index):
        return self.indices[index]

    def __setitem__(self,index,value):
        self.indices[index] = value