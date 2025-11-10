import copy
import random
from multiprocessing import Pool
from extendedstim.Code.LinearCode.LinearCode import LinearCode
from extendedstim.Math.BinaryArray import BinaryArray as ba


class DoubleBicycleCode(LinearCode):
    def __init__(self,n,a_occupy,b_occupy):
        self.a_occupy=copy.deepcopy(a_occupy)
        self.b_occupy=copy.deepcopy(b_occupy)
        self.a_occupy.sort()
        self.b_occupy.sort()
        a_list = [1 if i in self.a_occupy else 0 for i in range(n)]
        b_list = [1 if i in self.b_occupy else 0 for i in range(n)]
        H_up = ba.hstack(C(n, a_list), C(n, b_list), C(n, a_list).T, C(n, b_list).T)
        H_down = ba.hstack(C(n, b_list).T, C(n, a_list).T, C(n, b_list), C(n, a_list))
        H = ba.vstack(H_up, H_down)
        super().__init__(H)

    def __str__(self):
        n=self.number_bit//4
        S_str_a=''
        for i in self.a_occupy:
            S_str_a+=f"S^{{{i}}}_{{{n}}}"
        S_str_b=''
        for i in self.b_occupy:
            S_str_b+=f"S^{{{i}}}_{{{n}}}"
        return S_str_a+ '\n'+S_str_b

    @staticmethod
    def good_code(n):
        if n==23:  # d=14,k=4
            return DoubleBicycleCode(23,[0,9],[21,22])
        elif n==11:  # d=8,k=4
            return DoubleBicycleCode(11,[5,7],[2,7])
        elif n==17:  # d=10,k=4
            return DoubleBicycleCode(17,[2,4],[9,16])
        elif n==36:  # d=12,k=8
            return DoubleBicycleCode(36,[2,19],[1,12])
        else:
            return None

##  构造多项式的变量元
def S(n):
    return ba.shift(n,1)


##  构造cyclic matrix
def C(n,a_list):
    assert len(a_list) == n
    return ba.sum([a*(S(n)**i) for i,a in enumerate(a_list)])


##  搜索满足条件的代码
def search(n):
    for samples in range(10_0000):
        a_occupy = random.sample(range(n), 2)
        b_occupy = random.sample(range(n), 2)
        a_occupy.sort()
        b_occupy.sort()
        a_list = [1 if i in a_occupy else 0 for i in range(n)]
        b_list = [1 if i in b_occupy else 0 for i in range(n)]
        H_up = ba.hstack(C(n, a_list), C(n, b_list), C(n, a_list).T, C(n, b_list).T)
        H_down = ba.hstack(C(n, b_list).T, C(n, a_list).T, C(n, b_list), C(n, a_list))
        H = ba.vstack(H_up, H_down)
        logical_number=H.shape[1] - 2 * H.rank
        if logical_number >=2:
            physical_number = H.shape[1]
            code_distance = ba.distance(H,'random')
            if ba.solve(H, ba.ones(H.shape[1])) is None:
                bb = "odd"
            else:
                bb = "even"
            print(DoubleBicycleCode(n,a_occupy,b_occupy),f"|{physical_number}|{logical_number}|{code_distance}|{bb}|")


##  主函数：搜索
def main_search():
    with Pool(processes=20) as pool:
        results = [pool.apply_async(search, args=(36,)) for case in [1]*20]
        # 等待所有任务完成并获取结果
        final_results = [result.get() for result in results]


if __name__ == '__main__':
    main_search()
