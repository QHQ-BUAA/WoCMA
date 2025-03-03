from Algorithms.Algorithm import *
from Algorithms.Params import get_args
from Algorithms.Indicator_Comparison import *
import os.path

def Algo_Solver(mk_name, jjj):
    mk_f = r'./Instance' + '/' + mk_name + '.pkl'
    n, m, PT, MT, ni, ST, s = Instance(mk_f)
    mm = 2
    args = get_args(n, m, PT, MT, ni, ST, s, mm)
    Algo = Algorithms(args)
    WoCMA_EP = Algo.WoCMA_main(mk_name, jjj)
    MEP_list = quchong(WoCMA_EP)
    txtf_pm = r'.\result' + '/' +'M_' +mk_name +f'_{jjj}' + '.txt'
    print(f"txt path: {txtf_pm}")
    save_to_json(txtf_pm,MEP_list)


if __name__=="__main__":
    for j in range(3):
        for i in range(1,30):
            i=f"{i}"
            print(f"Run {j} time {i}")
            Algo_Solver(i,j)
