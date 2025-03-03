#utf-8
import copy
from Algorithms.utils import *
from Algorithms.Popi import *
from Algorithms.I_popi import *
from utils.timer import timer
from utils.Gantt import Gantt_Ma

class Algorithms:
    def __init__(self ,args):
        self.means_m =args.means_m
        self.args =args
        self.s = args.s
        self.N_elite =args.N_elite
        self.Pop_size =args.pop_size
        self.gene_size =args.gene_size
        self.pc_max =args.pc_max
        self.pm_max =args.pm_max
        self.pc_min = args.pc_min
        self.pm_min = args.pm_min
        self.pc = args.pc_max
        self.pm = args.pm_max
        self. T =args.T
        if self.means_m >1:
            self.p_GS =args.p_GS
            self.p_LS = args.p_LS
            self.p_RS = args.p_RS
            self.p_WGS = args.p_WGS
            self.p_WLS = args.p_WLS
        if self.means_m >1:
            self.Chromo_setup()
        self.Best_JS =None
        self.Best_Cmax =1e+20
        self.C_end =[]
        self.Pop = []
        self._lambda = bi_VGM(self.args.H)
        self._z =[]
        self.gannt1 = []
        self.gannt2 = []



    def Chromo_setup(self):
        self.os_list = []
        for i in range(len(self.args.O_num)):
            self.os_list.extend([i for _ in range(self.args.O_num[i])])
        self.half_len_chromo =len(self.os_list)
        self.ms_list =[]
        self.J_site =[]
        for i in range(len(self.args.Processing_Machine)):
            for j in range(len(self.args.Processing_Machine[i])):
                self.ms_list.append(len(self.args.Processing_Machine[i][j]))
                self.J_site.append((i ,j))

    def Chromo_setup_0(self):
        self.os_list = []
        for i in range(len(self.args.O_num)):
            self.os_list.extend([i for _ in range(self.args.O_num[i])])

    def random_initial(self):
        for i in range(int(self.p_RS *self.Pop_size)):
            Pop_i =[]
            random.shuffle(self.os_list)
            Pop_i.extend(copy.copy(self.os_list))
            ms =[]
            for j in self.ms_list:
                ms.append(random.randint(0 , j -1))
            Pop_i.extend(ms)
            ss = [random.randint(0, self.s-1) for _ in range(sum(self.args.O_num))]
            Pop_i.extend(ss)
            Pop_i =Popi(self.args ,Pop_i ,self.J_site ,self.half_len_chromo)
            if self._z==[]:
                self._z =copy.deepcopy(Pop_i.fitness)
            else:
                for j in range(2):
                    if self._z[j ] >Pop_i.fitness[j]:
                        self._z[j ] =copy.deepcopy(Pop_i.fitness[j])
                        if j == 0:
                            self.gannt1 =copy.deepcopy(Pop_i)
                        if j == 1:
                            self.gannt2 = copy.deepcopy(Pop_i)
            self.Pop.append(Pop_i)

    def GS_initial(self):
        for i in range(int(self.p_GS *self.Pop_size)):
            Machine_load =[0 ] *self.args.m
            Job_op =[0 ] *self.args.n
            Pop_i = []
            random.shuffle(self.os_list)
            Pop_i.extend(copy.copy(self.os_list))
            ms =[0 ] *len(Pop_i)
            ss = [0 ] *len(Pop_i)
            for pi in Pop_i:
                MLoad_op =[Machine_load[self.args.Processing_Machine[pi][Job_op[pi]][_ ] -1 ] +
                           self.args.Processing_Time[pi][Job_op[pi]][_] for _ in range(len(self.args.Processing_Machine[pi][Job_op[pi]]))]
                Worker_load = self.args.Setup_Time[pi][Job_op[pi]]
                min_sum = float('inf')
                min_index = (-1, -1)
                for ssi, a in enumerate(MLoad_op):
                    for ssj, b in enumerate(Worker_load[ssi]):
                        current_sum = a + b
                        if current_sum < min_sum:
                            min_sum = current_sum
                            min_index = (ssi, ssj)
                m_idx = min_index[0]
                w_idx = min_index[1]
                ms[self.J_site.index((pi ,Job_op[pi])) ] =m_idx
                ss[self.J_site.index((pi ,Job_op[pi]))] = w_idx
                Machine_load[self.args.Processing_Machine[pi][Job_op[pi]][m_idx] - 1] =min_sum
                Job_op[pi]+=1
            Pop_i.extend(ms)
            Pop_i.extend(ss)
            Pop_i =Popi(self.args ,Pop_i ,self.J_site ,self.half_len_chromo)
            if self._z==[]:
                self._z =copy.deepcopy(Pop_i.fitness)
            else:
                for j in range(2):
                    if self._z[j ] >Pop_i.fitness[j]:
                        self._z[j ] =copy.deepcopy(Pop_i.fitness[j])
                        if j == 0:
                            self.gannt1 =copy.deepcopy(Pop_i)
                        if j == 1:
                            self.gannt2 = copy.deepcopy(Pop_i)
            self.Pop.append(Pop_i)

    def LS_initial(self):
        ms =[0 ] *len(self.J_site)
        ss =[0 ] *len(self.J_site)
        for i in range(len(self.args.Processing_Time)):
            Machine_load = [0] * self.args.m
            for j in range(len(self.args.Processing_Time[i])):
                MLoad_op =[Machine_load[self.args.Processing_Machine[i][j][_ ] -1 ] +
                           self.args.Processing_Time[i][j][_] for _ in range(len(self.args.Processing_Machine[i][j]))]
                Worker_load = self.args.Setup_Time[i][j]
                min_sum = float('inf')
                min_index = (-1, -1)
                for sii, a in enumerate(MLoad_op):
                    for sjj, b in enumerate(Worker_load[sii]):
                        current_sum = a + b
                        if current_sum < min_sum:
                            min_sum = current_sum
                            min_index = (sii, sjj)
                m_idx = min_index[0]
                w_idx = min_index[1]
                ms[self.J_site.index((i ,j)) ] =m_idx
                ss[self.J_site.index((i ,j))] = w_idx
                Machine_load[self.args.Processing_Machine[i][j][m_idx] - 1] =min_sum
        for i in range(self.Pop_size-int(self.p_GS *self.Pop_size)-int(self.p_RS *self.Pop_size)-int(self.p_WGS *self.Pop_size)-int(self.p_WLS *self.Pop_size)):
            Pop_i = []
            random.shuffle(self.os_list)
            Pop_i.extend(copy.copy(self.os_list))
            Pop_i.extend(ms)
            Pop_i.extend(ss)
            Pop_i =Popi(self.args ,Pop_i ,self.J_site ,self.half_len_chromo)
            if self._z==[]:
                self._z =copy.deepcopy(Pop_i.fitness)
            else:
                for j in range(2):
                    if self._z[j ] >Pop_i.fitness[j]:
                        self._z[j ] =copy.deepcopy(Pop_i.fitness[j])
                        if j == 0:
                            self.gannt1 =copy.deepcopy(Pop_i)
                        if j == 1:
                            self.gannt2 = copy.deepcopy(Pop_i)
            self.Pop.append(Pop_i)

    def worker_GS_initial(self):
        for i in range(int(self.p_WGS *self.Pop_size)):
            Machine_load =[0 ] *self.args.m
            Worker_load = [0 ] *self.args.s
            Job_op =[0 ] *self.args.n
            Pop_i = []
            random.shuffle(self.os_list)
            Pop_i.extend(copy.copy(self.os_list))
            ms =[0 ] *len(Pop_i)
            ss = [0 ] *len(Pop_i)
            for pi in Pop_i:
                MLoad_op =[Machine_load[self.args.Processing_Machine[pi][Job_op[pi]][_ ] -1 ] +
                           self.args.Processing_Time[pi][Job_op[pi]][_] for _ in range(len(self.args.Processing_Machine[pi][Job_op[pi]]))]
                m_idx = MLoad_op.index(min(MLoad_op))
                WLoad_op =[Worker_load[_] +
                           self.args.Setup_Time[pi][Job_op[pi]][m_idx][_] for _ in range(len(self.args.Setup_Time[pi][Job_op[pi]][m_idx]))]
                w_idx = WLoad_op.index(min(WLoad_op))
                ms[self.J_site.index((pi ,Job_op[pi])) ] =m_idx
                ss[self.J_site.index((pi ,Job_op[pi]))] = w_idx
                Worker_load[w_idx] =min(WLoad_op)
                Job_op[pi]+=1
            Pop_i.extend(ms)
            Pop_i.extend(ss)
            Pop_i =Popi(self.args ,Pop_i ,self.J_site ,self.half_len_chromo)
            if self._z==[]:
                self._z =copy.deepcopy(Pop_i.fitness)
            else:
                for j in range(2):
                    if self._z[j ] >Pop_i.fitness[j]:
                        self._z[j ] =copy.deepcopy(Pop_i.fitness[j])
                        if j == 0:
                            self.gannt1 =copy.deepcopy(Pop_i)
                        if j == 1:
                            self.gannt2 = copy.deepcopy(Pop_i)
            self.Pop.append(Pop_i)

    def  worker_LS_initial(self):
        ms =[0 ] *len(self.J_site)
        ss =[0 ] *len(self.J_site)
        for i in range(len(self.args.Processing_Time)):
            Machine_load = [0] * self.args.m
            Worker_load = [0] * self.args.s
            for j in range(len(self.args.Processing_Time[i])):
                MLoad_op =[Machine_load[self.args.Processing_Machine[i][j][_ ] -1 ] +
                           self.args.Processing_Time[i][j][_] for _ in range(len(self.args.Processing_Machine[i][j]))]
                m_idx = MLoad_op.index(min(MLoad_op))
                WLoad_op =[Worker_load[_] +
                           self.args.Setup_Time[i][j][m_idx][_] for _ in range(len(self.args.Setup_Time[i][j][m_idx]))]
                w_idx = WLoad_op.index(min(WLoad_op))
                ms[self.J_site.index((i ,j)) ] =m_idx
                ss[self.J_site.index((i ,j))] = w_idx
                Worker_load[w_idx] = min(WLoad_op)
        for i in range(int(self.p_WLS *self.Pop_size)):
            Pop_i = []
            random.shuffle(self.os_list)
            Pop_i.extend(copy.copy(self.os_list))
            Pop_i.extend(ms)
            Pop_i.extend(ss)
            Pop_i =Popi(self.args ,Pop_i ,self.J_site ,self.half_len_chromo)
            if self._z==[]:
                self._z =copy.deepcopy(Pop_i.fitness)
            else:
                for j in range(2):
                    if self._z[j ] >Pop_i.fitness[j]:
                        self._z[j ] =copy.deepcopy(Pop_i.fitness[j])
                        if j == 0:
                            self.gannt1 =copy.deepcopy(Pop_i)
                        if j == 1:
                            self.gannt2 = copy.deepcopy(Pop_i)
            self.Pop.append(Pop_i)


    '''
    (1)POX
    (2)Job_based_Crossover
    '''

    # POX:precedence preserving order-based crossover
    def POX(self ,p1, p2):
        jobsRange = range(0, self.args.n)
        sizeJobset1 = random.randint(1, self.args.n)
        jobset1 = random.sample(jobsRange, sizeJobset1)
        o1 = []
        p1kept = []
        for i in range(len(p1)):
            e = p1[i]
            if e in jobset1:
                o1.append(e)
            else:
                o1.append(-1)
                p1kept.append(e)
        o2 = []
        p2kept = []
        for i in range(len(p2)):
            e = p2[i]
            if e in jobset1:
                o2.append(e)
            else:
                o2.append(-1)
                p2kept.append(e)
        for i in range(len(o1)):
            if o1[i] == -1:
                o1[i] = p2kept.pop(0)
        for i in range(len(o2)):
            if o2[i] == -1:
                o2[i] = p1kept.pop(0)
        return o1, o2

    def Job_Crossover(self ,p1 ,p2):
        jobsRange = range(0, self.args.n)
        sizeJobset1 = random.randint(0, self.args.n)
        jobset1 = random.sample(jobsRange, sizeJobset1)
        jobset2 = [item for item in jobsRange if item not in jobset1]
        o1 = []
        p1kept = []
        for i in range(len(p1)):
            e = p1[i]
            if e in jobset1:
                o1.append(e)
                p1kept.append(e)
            else:
                o1.append(-1)
        o2 = []
        p2kept = []
        for i in range(len(p2)):
            e = p2[i]
            if e in jobset2:
                o2.append(e)
                p2kept.append(e)
            else:
                o2.append(-1)
        for i in range(len(o1)):
            if o1[i] == -1:
                o1[i] = p2kept.pop(0)
        for i in range(len(o2)):
            if o2[i] == -1:
                o2[i] = p1kept.pop(0)
        return o1 ,o2

    '''
    swap_mutation
    NB_mutation: neigborhood mutation
    '''
    def swap_mutation(self ,p):
        pos1 = random.randint(0, len(p) - 1)
        pos2 = random.randint(0, len(p) - 1)
        if pos1 == pos2:
            return p
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1
        offspring = p[:pos1] + [p[pos2]] + \
                    p[pos1 + 1:pos2] + [p[pos1]] + \
                    p[pos2 + 1:]
        return offspring

    
    def MB_mutation(self ,p1):
        D = len(p1)
        c1 = p1.copy()
        r = np.random.uniform(size=D)
        for idx1, val in enumerate(p1):
            if r[idx1] <= self.pm:
                idx2 = np.random.choice(np.delete(np.arange(D), idx1))
                c1[idx1], c1[idx2] = c1[idx2], c1[idx1]
        return c1

    
    def Crossover_Machine(self, CHS1, CHS2):
        T_r = [j for j in range(self.half_len_chromo)]
        r = random.randint(1, self.half_len_chromo)
        random.shuffle(T_r)
        R = T_r[0:r]
        for i in R:
            K, K_2 = CHS1[i], CHS2[i]
            CHS1[i], CHS2[i] = K_2, K
        return CHS1, CHS2

    
    def Mutation_Machine(self ,CHS):
        T_r = [j for j in range(self.half_len_chromo)]
        r = random.randint(1, self.half_len_chromo)
        random.shuffle(T_r)
        R = T_r[0:r]
        for i in R:
            O_site =self.J_site[i]
            pt =self.args.Processing_Time[O_site[0]][O_site[1]]
            pt_find =pt[0]
            len_pt =len(pt ) -1
            k , m =1 ,0
            while k< len_pt:
                if pt_find > pt[k]:
                    pt_find = pt[k]
                    m = k
                k += 1
            CHS[i] = m
        return CHS

    
    def operator_NoFlexible(self, chs1, chs2):
        p1, p2 = chs1.CHS, chs2.CHS
        if random.random() < self.pc:  # wether crossover
            if random.random() < 0.5:
                p1, p2 = self.POX(p1, p2)
            else:
                p1, p2 = self.Job_Crossover(p1, p2)
        if random.random() < self.pm:  # wether chs1 mutation
            if random.random() < 0.5:
                p1 = self.swap_mutation(p1)
            else:
                p1 = self.MB_mutation(p1)
        if random.random() < self.pm:  # wether chs2 mutation
            if random.random() < 0.5:
                p2 = self.swap_mutation(p2)
            else:
                p2 = self.MB_mutation(p2)
        P1, P2 = Popi(self.args, p1, self.J_site, self.half_len_chromo), Popi(self.args, p2, self.J_site,
                                                                              self.half_len_chromo)
        return P1, P2

    
    def operator_Flexible(self, chs1, chs2):
        p1, p2 = chs1.CHS, chs2.CHS
        if random.random() < self.pc:  # wether crossover
            if random.random() < 0.5:
                p11, p21 = self.POX(p1[0:self.half_len_chromo], p2[0:self.half_len_chromo])
            else:
                p11, p21 = self.Job_Crossover(p1[0:self.half_len_chromo], p2[0:self.half_len_chromo])
            p12, p22 = self.Crossover_Machine(p1[self.half_len_chromo:], p2[self.half_len_chromo:])
            p11.extend(p12)
            p1 = p11
            p21.extend(p22)
            p2 = p21
        if random.random() < self.pm:  # wether chs1 mutation
            if random.random() < 0.5:
                p11 = self.swap_mutation(p1[0:self.half_len_chromo])
            else:
                p11 = self.MB_mutation(p1[0:self.half_len_chromo])
            p12 = self.Mutation_Machine(p1[self.half_len_chromo:])
            p11.extend(p12)
            p1 = p11
        if random.random() < self.pm:  # wether chs2 mutation
            if random.random() < 0.5:
                p21 = self.swap_mutation(p2[0:self.half_len_chromo])
            else:
                p21 = self.MB_mutation(p2[0:self.half_len_chromo])
            p22 = self.Mutation_Machine(p2[self.half_len_chromo:])
            p21.extend(p22)
            p2 = p21
        P1, P2 = Popi(self.args, p1, self.J_site, self.half_len_chromo), Popi(self.args, p2, self.J_site,
                                                                              self.half_len_chromo)
        return P1, P2

    def WoCMA_main(self, g_name, g_jjj):
        # ----------------------------------Initialization---------------------------------
        num_LS = 12
        c_lambda = np.full(num_LS, 1 / num_LS)
        SOF_juhe = np.zeros((num_LS, 3))

        # to obtain Populations and weight vectors
        self.Pop_size = len(self._lambda)
        self.Pop=[]
        if self.means_m > 1:
            self.random_initial()
            self.GS_initial()
            self.worker_GS_initial()
            self.worker_LS_initial()
            self.LS_initial()  # Local Initial

        B = Neighbor(self._lambda, self.T)
        EP = []
        # ----------------------------------Iteration---------------------------------
        for gi in range(self.gene_size):
            print(f"WoCMA,No. {gi+1}")
            self.pc = self.pc_max - ((self.pc_max - self.pc_min) / self.gene_size) * gi
            self.pm = self.pm_max - ((self.pm_max - self.pm_min) / self.gene_size) * gi
            for i in range(len(self.Pop)):
                # Randomly select two indexes k,l from B(i)
                j = random.randint(0, self.T - 1)
                k = random.randint(0, self.T - 1)

                if self.means_m > 1:
                    pop1, pop2 = self.operator_Flexible(self.Pop[B[i][j]], self.Pop[B[i][k]])
                else:
                    pop1, pop2 = self.operator_NoFlexible(self.Pop[B[i][j]], self.Pop[B[i][k]])
                if Dominate(pop1, pop2):
                    y = pop1
                else:
                    y = pop2
                # update of the reference point z
                for zi in range(len(self._z)):
                    if self._z[zi] > y.fitness[zi]:
                        self._z[zi] = y.fitness[zi]
                        if zi == 0:
                            self.gannt1 = copy.deepcopy(y)
                        else:
                            self.gannt2 = copy.deepcopy(y)
                # update of Neighboring solutions
                for bi in range(len(B[i])):
                    Ta = Tchebycheff(self.Pop[B[i][bi]], self._z, self._lambda[B[i][bi]])
                    Tb = Tchebycheff(y, self._z, self._lambda[B[i][bi]])
                    if Tb < Ta:
                        self.Pop[B[i][j]] = y
                        break
            soe_juhe = np.zeros((num_LS, 4))
            sum_soe_prob = 0
            pop_pool = Roulette_Wheel_Selection(len(self.Pop), c_lambda)
            for j in range(len(pop_pool)):
                for k in pop_pool[j]:
                    Ipopi = I_popi(self.args, self.Pop[k].CHS, self.Pop[k].fitness, self.J_site, self.half_len_chromo,j)
                    if Ipopi.SOF == 1:
                        self.Pop[k] = Ipopi
                        soe_juhe[j][0] += 1
                        for zi in range(len(self._z)):
                            if self._z[zi] > Ipopi.fitness[zi]:
                                self._z[zi] = Ipopi.fitness[zi]
                                if zi == 0:
                                    self.gannt1 = copy.deepcopy(Ipopi)
                                else:
                                    self.gannt2 = copy.deepcopy(Ipopi)
                        # region Update of EP
                        if EP == []:
                            EP.append(Ipopi)
                        else:
                            dominateY = False
                            _remove = []
                            for ei in range(len(EP)):
                                if Dominate(Ipopi, EP[ei]):
                                    _remove.append(EP[ei])
                                elif Dominate(EP[ei], Ipopi):
                                    dominateY = True
                                    break
                            # add y to EP if no vectors in EP dominated y
                            if not dominateY:
                                EP.append(Ipopi)
                                for rem in range(len(_remove)):
                                    EP.remove(_remove[rem])
                    else:
                        soe_juhe[j][1] += 1
                    soe_juhe[j][2] += 1
                    if k == pop_pool[j][-1]:
                        soe_juhe[j][3] = soe_juhe[j][0]/soe_juhe[j][2]
                        sum_soe_prob += soe_juhe[j][3]
                    # endregion
            soe_juhe[:, 3] /= sum_soe_prob
            SOF_juhe[:, :3] += soe_juhe[:, :3]
            c_lambda += soe_juhe[:, 3]
            c_lambda /= c_lambda.sum()
            c_lambda = np.round(c_lambda, 2)

            c_lambda = np.maximum(c_lambda, 0.1)
            c_lambda /= c_lambda.sum()

            c_lambda = np.round(c_lambda, 2)
            c_lambda[0] += 1.0 - c_lambda.sum()
        try:
            Gantt_Ma(self.gannt1.JS, "Min_Cmax", g_name, g_jjj)
        except:
            Gantt_Ma(self.gannt1.IJS, "Min_Cmax", g_name, g_jjj)
        try:
            Gantt_Ma(self.gannt2.JS, "Min_Energy", g_name, g_jjj)
        except:
            Gantt_Ma(self.gannt2.IJS, "Min_Energy", g_name, g_jjj)
        return EP
    # endregion

