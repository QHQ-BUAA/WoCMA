from Env_JSP_FJSP.Job import Job
from Env_JSP_FJSP.Machine import Machine
from Env_JSP_FJSP.SetupWorker import SetupWorkers
import networkx as nx
import random
import json
from log import SingletonLogger
logger = SingletonLogger.get_logger()


class I_Job_shop:
    def __init__(self,args,J_site):
        self.n= args.n
        self.m=args.m
        self.s = args.s
        self.O_num=args.O_num
        self.PM = args.Processing_Machine
        self.PS = list(range(args.s))
        self.PT = args.Processing_Time
        self.ST = args.Setup_Time
        self.J_site = J_site
        self.reset()

    def reset(self):
        self.C_max = 0      #makespan
        self.C_max_job = None
        self.C_max2 = 0
        self.C_max2_job = None
        self.C_max3 = 0
        self.C_max3_job = None
        self.load=0         # Total load of machines
        self.Jobs=[]
        for i in range(self.n):
            Ji=Job(i,self.PM[i],self.PT[i],self.ST[i])
            self.Jobs.append(Ji)
        self.Machines=[]
        for j in range(self.m):
            Mi=Machine(j)
            self.Machines.append(Mi)
        self.Workers = []
        for i in range(self.s):
            Si = SetupWorkers(i)
            self.Workers.append(Si)

    # decode of chs[i]
    def decode(self,Job,Machine,Worker):
        Ji=self.Jobs[Job]
        o_pt, o_lastend,M_idx,su_t = Ji.get_next_info(Machine,Worker)
        Si = self.Workers[Worker]
        s_windows = Si.Empty_time_window_ss()
        Mi=self.Machines[M_idx-1]
        worker_start,ma_start=Mi.find_start(o_lastend,o_pt,su_t,s_windows,Si)
        end=ma_start+o_pt
        Mi.update(ma_start, end, [Ji.idx, Ji.cur_op],worker_start)
        Si.update([[Ji.idx, Ji.cur_op],Machine],worker_start,worker_start+su_t)
        Ji.update(ma_start, end, Mi.idx,Worker)

        if end>self.C_max:
            self.C_max=end
            self.C_max_job = Job
        elif end>self.C_max2:
            self.C_max2 = end
            self.C_max2_job = Job
        elif end>self.C_max3:
            self.C_max3 = end
            self.C_max3_job = Job

    def enenrgy(self):
        self.energy = 0
        for i in range(len(self.Machines)):
            time_window_start = []
            time_window_end = []
            time_window_start.extend(self.Machines[i].end[:-1])
            time_window_end.extend(self.Machines[i].start[1:])
            len_time_window = [time_window_end[k] - time_window_start[k] for k in range(len(time_window_end))]

            for j in range(len(len_time_window)):
                if len_time_window[j] >= 20:
                    self.energy += 5
                else:
                    self.energy = len_time_window[j]*2 + self.energy

            process_start = []
            process_end = []
            process_start.extend(self.Machines[i].start[:])
            process_end.extend(self.Machines[i].end[:])
            process_time = [process_end[k] - process_start[k] for k in range(len(process_end))]
            for l in range(len(process_time)):
                self.energy += process_time[l]*5
        return self.energy

    def SwapLSRs(self, sub_CHS, part1, part2):
        j1_index = self.J_site.index((part1[0], part1[1]))
        j2_index = self.J_site.index((part2[0], part2[1]))
        w1 = sub_CHS[j1_index]
        w2 = sub_CHS[j2_index]
        if w1 == w2:
            return sub_CHS
        sub_CHS[j1_index] = w2
        sub_CHS[j2_index] = w1
        return sub_CHS


    def find_value_index(self,sub_CHS, part):
        count = 0
        for index, value in enumerate(sub_CHS):
            if value == part[0]:
                count += 1
                if count == part[1]+1:
                    return index
        return None  

    def SwapOps(self, sub_CHS, part1, part2):
        if part1[0] == part2[0]:
            return sub_CHS
        index1 = self.find_value_index(sub_CHS,part1)
        index2 = self.find_value_index(sub_CHS,part2)
        sub_CHS[index1] = part2[0]
        sub_CHS[index2] = part1[0]
        return sub_CHS

    def MoveOpForInsertion(self, sub_CHS, part1, part2):  
        index1 = self.find_value_index(sub_CHS,part1)
        index2 = self.find_value_index(sub_CHS,part2)
        x = min(index1, index2)
        y = max(index1,index2)
        if x + 1 == y and part1[0] != part2[0]: 
            sub_CHS.pop(index1)  

            sub_CHS.insert(index2, part1[0])
            return sub_CHS

        if x + 1 != y and part1[0] in sub_CHS[x+1:y] and part1[0] != part2[0]:
            return sub_CHS
        sub_CHS.pop(index1)

        sub_CHS.insert(index2, part1[0])
        return sub_CHS

    def AdjustFirstAndLastKeyBlocks(self, teOS, critical_block):
        tOS = teOS[:]
        if len(critical_block.items()) >= 2:
            if len(critical_block[0]) >= 3:
                j1 = critical_block[0][-2]
                j2 = critical_block[0][-1]
                tOS = self.MoveOpForInsertion(tOS, j1, j2)
            last_key = list(critical_block)[-1]
            last_value = critical_block[last_key]
            if len(last_value) >= 3:
                j1 = last_value[1]
                j2 = last_value[0]
                tOS = self.MoveOpForInsertion(tOS, j1, j2)
            tempOS = tOS[:]
            return tempOS
        else:
            return tOS

    def AdjustFirst_LastKeyBlocks(self, teOS, teSS, critical_block):
        tOS = teOS[:]
        tSS = teSS[:]
        if len(critical_block.items()) >= 2:
            if len(critical_block[0]) >= 3:
                j1 = critical_block[0][-2]
                j2 = critical_block[0][-1]
                tOS = self.MoveOpForInsertion(tOS, j1, j2)
            last_key = list(critical_block)[-1]
            last_value = critical_block[last_key]
            if len(last_value) >= 3:
                j1 = last_value[1]
                j2 = last_value[0]
                tOS = self.MoveOpForInsertion(tOS, j1, j2)
                index_s = self.J_site.index((j1[0], j1[1]))
                tSS[index_s] = random.randint(0, self.s - 1)
                index_s2 = self.J_site.index((j2[0], j2[1]))
                tSS[index_s2] = random.randint(0, self.s - 1)
            tempOS = tOS[:]
            tempSS = tSS[:]
            return tempOS,tempSS
        else:
            return tOS,tSS

    def AdjustMiddleKeyBlocks(self, teOS, critical_block, c, l): #c:center,l:length
        tOS = teOS[:]
        if l < 4:
            return tOS
        if l % 2 == 0:
            a = l // 2
            for i in range(l):
                if i < a:
                    if i+1 == a:
                        continue
                    j1 = critical_block[c][i+1]
                    j2 = critical_block[c][i]
                    tOS = self.MoveOpForInsertion(tOS, j1, j2)
                elif i > a:
                    if i == l-1:
                        break
                    else:
                        d = i -a
                        j1 = critical_block[c][-d-1]  
                        j2 = critical_block[c][-d]
                        tOS = self.MoveOpForInsertion(tOS, j1, j2)
            temp_OS = tOS[:]
            return temp_OS
        else:
            a = (l - 1) // 2
            for i in range(l):
                if i < a:
                    j1 = critical_block[c][i+1]  
                    j2 = critical_block[c][i]
                    tOS = self.MoveOpForInsertion(tOS, j1, j2)
                elif i > a:
                    if i == l-1:
                        break
                    else:
                        d = i -a
                        j1 = critical_block[c][-d-1]  
                        j2 = critical_block[c][-d]
                        tOS = self.MoveOpForInsertion(tOS, j1, j2)
            temp_OS = tOS[:]
            return temp_OS

    def AdjustMiddleKeyBlocksOps(self, teOS, teSS, critical_block, c, l): #c:center,l:length
        tOS = teOS[:]
        tSS = teSS[:]
        if l < 4:
            return tOS,teSS
        if l % 2 == 0:
            a = l // 2
            for i in range(l):
                if i < a:
                    if i+1 == a:
                        continue
                    j1 = critical_block[c][i+1]
                    j2 = critical_block[c][i]
                    tOS = self.MoveOpForInsertion(tOS, j1, j2)
                    index_s = self.J_site.index((j1[0], j1[1]))
                    tSS[index_s] = random.randint(0, self.s - 1)
                    index_s2 = self.J_site.index((j2[0], j2[1]))
                    tSS[index_s2] = random.randint(0, self.s - 1)
                elif i > a:
                    if i == l-1:
                        break
                    else:
                        d = i -a
                        j1 = critical_block[c][-d-1]  
                        j2 = critical_block[c][-d]
                        tOS = self.MoveOpForInsertion(tOS, j1, j2)
                        index_s = self.J_site.index((j1[0], j1[1]))  
                        tSS[index_s] = random.randint(0, self.s - 1)
                        index_s2 = self.J_site.index((j2[0], j2[1]))  
                        tSS[index_s2] = random.randint(0, self.s - 1)
            temp_OS = tOS[:]
            temp_SS = tSS[:]
            return temp_OS,temp_SS
        else:
            a = (l - 1) // 2
            for i in range(l):
                if i < a:
                    j1 = critical_block[c][i+1]  
                    j2 = critical_block[c][i]
                    tOS = self.MoveOpForInsertion(tOS, j1, j2)
                elif i > a:
                    if i == l-1:
                        break
                    else:
                        d = i -a
                        j1 = critical_block[c][-d-1]  
                        j2 = critical_block[c][-d]
                        tOS = self.MoveOpForInsertion(tOS, j1, j2)
                        index_s = self.J_site.index((j1[0], j1[1]))  
                        tSS[index_s] = random.randint(0, self.s - 1)
                        index_s2 = self.J_site.index((j2[0], j2[1]))  
                        tSS[index_s2] = random.randint(0, self.s - 1)
            temp_OS = tOS[:]
            temp_SS = tSS[:]
            return temp_OS,temp_SS

    def MachineCriticalPath(self):
        G = nx.DiGraph()
        G.add_node('Start', duration=0, max_distance=0)
        G.add_node('End', duration=0, max_distance=0)
        for i in range(len(self.Jobs)):
            for j in range(len(self.Jobs[i].start)):
                dur = self.Jobs[i].end[j] - self.Jobs[i].start[j]
                G.add_node(f"{i}-{j}", duration=dur, max_distance=0)
                if j == 0:
                    G.add_edge('Start', f"{i}-{j}")
                else:
                    G.add_edge(f"{i}-{j-1}", f"{i}-{j}")
                if j == len(self.Jobs[i].start) -1 :
                    G.add_edge(f"{i}-{j}","End")
        for i in range(len(self.Machines)):
            for j in range(len(self.Machines[i]._on) - 1):
                q_j, q_o = self.Machines[i]._on[j]
                h_j, h_o = self.Machines[i]._on[j + 1]
                G.add_edge(f"{q_j}-{q_o}", f"{h_j}-{h_o}")

        for node in nx.topological_sort(G):
            for pred in G.predecessors(node):
                new_distance = G.nodes[pred]['max_distance'] + G.nodes[node]['duration']
                if new_distance > G.nodes[node]['max_distance']:
                    G.nodes[node]['max_distance'] = new_distance

        longest_path = []
        node = 'End'
        while node:
            longest_path.append(node)
            predecessors = list(G.predecessors(node))
            if not predecessors:
                break
            node = max(predecessors, key=lambda x: G.nodes[x]['max_distance'])
        longest_path.reverse()
        return [longest_path]

    def ChangeMachineForOp(self, CHS, critical_path, num_mj):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        temp_MS = MS[:]
        swap_jo = []
        swap_index = []
        for cb in reversed(range(len(critical_path))):
            if cb != 0 and cb != (len(critical_path) - 1):
                parts = critical_path[cb].split("-")
                job = int(parts[0])
                op = int(parts[1])
                index_m = self.J_site.index((job, op)) 
                now_m = temp_MS[index_m]
                m = self.PM[job][op]
                if len(m) > 1:
                    for im in range(len(m)):
                        if im != now_m:
                            swap_jo.append([job,op])
                            swap_index.append(index_m) 
                            break
        if len(swap_index)>=1:
            now_m = temp_MS[swap_index[num_mj]]

            m = self.PM[swap_jo[num_mj][0]][swap_jo[num_mj][1]]
            for si_m in range(len(m)):
                if si_m != now_m:
                    temp_MS[swap_index[num_mj]] = si_m
                    temp_OS = OS[:]
                    temp_OS.extend(temp_MS)
                    temp_OSMS = temp_OS[:]
                    temp_OSMS.extend(SS)
                    temp_OSMSSS = temp_OSMS[:]
                    if num_mj == len(swap_jo) -1:
                        return temp_OSMSSS, num_mj,False
                    else:
                        return temp_OSMSSS,num_mj+1,True
        else:
            return CHS, num_mj + 1, False

    def OpAndLSR(self, CHS, critical_path, num_mj):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        temp_MS = MS[:]
        swap_jo = []
        swap_index = []
        for cb in reversed(range(len(critical_path))):
            if cb != 0 and cb != (len(critical_path) - 1):
                parts = critical_path[cb].split("-")
                job = int(parts[0])
                op = int(parts[1])
                index_m = self.J_site.index((job, op)) 
                SS[index_m] = random.randint(0, self.s - 1)
                now_m = temp_MS[index_m]
                
                m = self.PM[job][op]
                if len(m) > 1:
                    for im in range(len(m)):
                        if im != now_m:
                            swap_jo.append([job,op])
                            swap_index.append(index_m) 
                            break
        if len(swap_index)>=1:
            now_m = temp_MS[swap_index[num_mj]]
            
            m = self.PM[swap_jo[num_mj][0]][swap_jo[num_mj][1]]
            for si_m in range(len(m)):
                if si_m != now_m:
                    temp_MS[swap_index[num_mj]] = si_m
                    temp_OS = OS[:]
                    temp_OS.extend(temp_MS)
                    temp_OSMS = temp_OS[:]
                    temp_OSMS.extend(SS)
                    temp_OSMSSS = temp_OSMS[:]
                    if num_mj == len(swap_jo) -1:
                        return temp_OSMSSS, num_mj,False
                    else:
                        return temp_OSMSSS,num_mj+1,True
        else:
            return CHS, num_mj + 1, False

    def SwapROps(self, CHS, critical_path, num_b, num_j):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        MSSS = list(CHS[self.Len_Op:3 * self.Len_Op])
        ma = []   
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1: 
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp: 
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block
        if num_b <= len(critical_block.items())-1:  
            if num_j <= len(critical_block[num_b])-2:
                j1 = critical_block[num_b][num_j]
                j2 = critical_block[num_b][num_j+1]
                tempOS = self.SwapOps(OS, j1, j2)
                tempOS.extend(MSSS)
                return tempOS, num_b, num_j+1, True 
            else:
                return CHS,num_b+1, 0, True 
        else:
            return CHS,num_b, num_j,False 

    def LSRsAndOps(self, CHS, critical_path, num_b, num_j):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        ma = []  
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path) - 1:
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job, op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp: 
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job, op])
                    critical_block[block_num] = block
        if num_b <= len(critical_block.items()) - 1: 
            if num_j <= len(critical_block[num_b]) - 2:
                j1 = critical_block[num_b][num_j]
                j2 = critical_block[num_b][num_j + 1]
                tempOS = self.SwapOps(OS, j1, j2)
                index_s = self.J_site.index((j1[0], j1[1]))  
                SS[index_s] = random.randint(0, self.s - 1)
                index_s2 = self.J_site.index((j2[0], j2[1])) 
                SS[index_s2] = random.randint(0, self.s - 1)
                tempOS.extend(MS)
                tempOS.extend(SS)
                return tempOS, num_b, num_j + 1, True  
            else:
                return CHS, num_b + 1, 0, True 
        else:
            return CHS, num_b, num_j, False  

    def RSwapOps(self, CHS, critical_path, type):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        tempOS = OS[:]
        MSSS = list(CHS[self.Len_Op:3 * self.Len_Op])
        ma = []   
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1: 
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp:
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block
        if type == 0:
            tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
            tempOS1.extend(MSSS)
            return tempOS1, 1, True 
        elif type == 1:
            if len(critical_block.items()) >= 3:

                max_length = 0
                key_of_max_length = None
                for key, value in critical_block.items():
                  
                    if len(value) > max_length:
                        max_length = len(value)
                        key_of_max_length = key
              
                if key_of_max_length is not None and key_of_max_length != 0 and key_of_max_length != len(critical_block.items())-1:
                    tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
                    tempOS2 = self.AdjustMiddleKeyBlocks(tempOS1, critical_block, key_of_max_length, max_length)
                    tempOS2.extend(MSSS)
                    return tempOS2,2,True
            return CHS,2,True  
        elif type == 2:
            if len(critical_block.items()) >= 3:
                tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
                for cb in range(len(critical_block.items())-1):
                    if cb != 0 and cb != len(critical_block.items())-1:
                        tempOS1 = self.AdjustMiddleKeyBlocks(tempOS1, critical_block, cb, len(critical_block[cb]))
                tempOS1.extend(MSSS)
                return tempOS1, 3, False
            return CHS, 3, False   
        else:
            raise Exception("[RSwapOps] error")


    def SwapOpsAndLSR(self, CHS, critical_path, type):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        tempOS = OS[:]
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        tempSS = SS[:]
        ma = [] 
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1:
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp: 
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block
        if type == 0:
            tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
            tempOS1.extend(MS)
            tempOS1.extend(tempSS)
            return tempOS1, 1, True
        elif type == 1:
            if len(critical_block.items()) >= 3:
              
                max_length = 0
                key_of_max_length = None
                for key, value in critical_block.items():
                  
                    if len(value) > max_length:
                        max_length = len(value)
                        key_of_max_length = key
                
                if key_of_max_length is not None and key_of_max_length != 0 and key_of_max_length != len(critical_block.items())-1:
                    tempOS1,tempSS1 = self.AdjustFirst_LastKeyBlocks(tempOS, tempSS, critical_block)
                    tempOS1.extend(MS)
                    tempOS1.extend(tempSS1)
                    return tempOS1,2,True
            return CHS,2,True  
        elif type == 2:
            if len(critical_block.items()) >= 3:
                tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
                for cb in range(len(critical_block.items())-1):
                    if cb != 0 and cb != len(critical_block.items())-1:
                        tempOS1 = self.AdjustMiddleKeyBlocks(tempOS1, critical_block, cb, len(critical_block[cb]))
                tempOS1.extend(MS)
                tempOS1.extend(tempSS)
                return tempOS1, 3, False
            return CHS, 3, False  
        else:
            raise Exception("[SwapOpsAndLSR] error")

    def SwapLSRAndOpsP(self, CHS, critical_path, type):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        tempOS = OS[:]
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        tempSS = SS[:]
        ma = [] 
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1:
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp:
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block
        if type == 0:
            tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
            tempOS1.extend(MS)
            tempOS1.extend(tempSS)
            return tempOS1, 1, True 
        elif type == 1:
            if len(critical_block.items()) >= 3:
                max_length = 0
                key_of_max_length = None
                for key, value in critical_block.items():
                    if len(value) > max_length:
                        max_length = len(value)
                        key_of_max_length = key

                if key_of_max_length is not None and key_of_max_length != 0 and key_of_max_length != len(critical_block.items())-1:
                    tempOS1,tempSS1 = self.AdjustFirst_LastKeyBlocks(tempOS, tempSS, critical_block)
                    tempOS2,tempSS2 = self.AdjustMiddleKeyBlocksOps(tempOS1, tempSS1, critical_block, key_of_max_length, max_length)
                    tempOS2.extend(MS)
                    tempOS2.extend(tempSS2)
                    return tempOS2,2,True
            return CHS,2,True 
        elif type == 2:
            if len(critical_block.items()) >= 3:
                tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
                for cb in range(len(critical_block.items())-1):
                    if cb != 0 and cb != len(critical_block.items())-1:
                        tempOS1 = self.AdjustMiddleKeyBlocks(tempOS1, critical_block, cb, len(critical_block[cb]))
                tempOS1.extend(MS)
                tempOS1.extend(tempSS)
                return tempOS1, 3, False
            return CHS, 3, False   
        else:
            raise Exception("[SwapLSRAndOpsP] error")

    def SwapLSRAndOpsPP(self, CHS, critical_path, type):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        tempOS = OS[:]
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        tempSS = SS[:]
        ma = []   
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1:
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp:
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block
        if type == 0:
            tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
            tempOS1.extend(MS)
            tempOS1.extend(tempSS)
            return tempOS1, 1, True 
        elif type == 1:
            if len(critical_block.items()) >= 3:
                max_length = 0
                key_of_max_length = None
                for key, value in critical_block.items():
                    if len(value) > max_length:
                        max_length = len(value)
                        key_of_max_length = key
                if key_of_max_length is not None and key_of_max_length != 0 and key_of_max_length != len(critical_block.items())-1:
                    tempOS1,tempSS1 = self.AdjustMiddleKeyBlocksOps(tempOS, tempSS, critical_block, key_of_max_length, max_length)
                    tempOS2,tempSS2 = self.AdjustMiddleKeyBlocksOps(tempOS1, tempSS1, critical_block, key_of_max_length, max_length)
                    tempOS2.extend(MS)
                    tempOS2.extend(tempSS2)
                    return tempOS2,2,True
            return CHS,2,True 
        elif type == 2:
            if len(critical_block.items()) >= 3:
                tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
                for cb in range(len(critical_block.items())-1):
                    if cb != 0 and cb != len(critical_block.items())-1:
                        tempOS1 = self.AdjustMiddleKeyBlocks(tempOS1, critical_block, cb, len(critical_block[cb]))
                tempOS1.extend(MS)
                tempOS1.extend(tempSS)
                return tempOS1, 3, False
            return CHS, 3, False 
        else:
            raise Exception("[SwapLSRAndOpsPP] error")

    def LSRsAndOpsSwap(self, CHS, critical_path, type):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        tempOS = OS[:]
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        tempSS = SS[:]
        ma = [] 
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1: 
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp:
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block
        if type == 0:
            tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
            tempOS1.extend(MS)
            tempOS1.extend(tempSS)
            return tempOS1, 1, True  
        elif type == 1:
            if len(critical_block.items()) >= 3:
                max_length = 0
                key_of_max_length = None
                for key, value in critical_block.items():

                    if len(value) > max_length:
                        max_length = len(value)
                        key_of_max_length = key

                if key_of_max_length is not None and key_of_max_length != 0 and key_of_max_length != len(critical_block.items())-1:
                    tempOS1,tempSS1 = self.AdjustMiddleKeyBlocksOps(tempOS, tempSS, critical_block, key_of_max_length, max_length)
                    tempOS2,tempSS2 = self.AdjustMiddleKeyBlocksOps(tempOS1, tempSS1, critical_block, key_of_max_length, max_length)
                    tempOS2.extend(MS)
                    tempOS2.extend(tempSS2)
                    return tempOS2,2,True
            return CHS,2,True
        elif type == 2:
            if len(critical_block.items()) >= 3:
                tempOS1,tempSS1 = self.AdjustFirst_LastKeyBlocks(tempOS, tempSS, critical_block)
                for cb in range(len(critical_block.items())-1):
                    if cb != 0 and cb != len(critical_block.items())-1:
                        tempOS1 = self.AdjustMiddleKeyBlocks(tempOS1, critical_block, cb, len(critical_block[cb]))
                tempOS1.extend(MS)
                tempOS1.extend(tempSS1)
                return tempOS1, 3, False
            return CHS, 3, False  
        else:
            raise Exception("[LSRsAndOpsSwap] error")

    def LSRsAndOpsSwapP(self, CHS, critical_path, type):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        tempOS = OS[:]
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        tempSS = SS[:]
        ma = []  
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1: 
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if ma == []:
                    ma.append(self.Jobs[job]._on[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._on[op]
                    if ma[-1] != temp:
                        block = []
                        block_num += 1
                    ma.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block
        if type == 0:
            tempOS1 = self.AdjustFirstAndLastKeyBlocks(tempOS, critical_block)
            tempOS1.extend(MS)
            tempOS1.extend(tempSS)
            return tempOS1, 1, True 
        elif type == 1:
            if len(critical_block.items()) >= 3:

                max_length = 0
                key_of_max_length = None
                for key, value in critical_block.items():
                    
                    if len(value) > max_length:
                        max_length = len(value)
                        key_of_max_length = key
             
                if key_of_max_length is not None and key_of_max_length != 0 and key_of_max_length != len(critical_block.items())-1:
                    tempOS1,tempSS1 = self.AdjustMiddleKeyBlocksOps(tempOS, tempSS, critical_block, key_of_max_length, max_length)
                    tempOS2,tempSS2 = self.AdjustMiddleKeyBlocksOps(tempOS1, tempSS1, critical_block, key_of_max_length, max_length)
                    tempOS2.extend(MS)
                    tempOS2.extend(tempSS2)
                    return tempOS2,2,True
            return CHS,2,True
        elif type == 2:
            if len(critical_block.items()) >= 3:
                tempOS1,tempSS1 = self.AdjustFirst_LastKeyBlocks(tempOS, tempSS, critical_block)
                for cb in range(len(critical_block.items())-1):
                    if cb != 0 and cb != len(critical_block.items())-1:
                        tempOS1,tempSS1 = self.AdjustMiddleKeyBlocksOps(tempOS1, tempSS1, critical_block, cb, len(critical_block[cb]))
                tempOS1.extend(MS)
                tempOS1.extend(tempSS1)
                return tempOS1, 3, False
            return CHS, 3, False 
        else:
            raise Exception("[LSRsAndOpsSwapP] error")

    def check_cycle_and_add_edge(self,G, source, target):
        G.add_edge(source, target)
        if list(nx.simple_cycles(G)):
            G.remove_edge(source, target)
            return False
        return True

    def LSRCriticalPath(self):
        G = nx.DiGraph()
        G.add_node('Start', duration=0, max_distance=0)
        G.add_node('End', duration=0, max_distance=0)
        for i in range(len(self.Jobs)):
            for j in range(len(self.Jobs[i].start)):
                dur = self.Jobs[i].end[j] - self.Jobs[i].start[j]
                G.add_node(f"{i}-{j}", duration=dur, max_distance=0)
                if j == 0:
                    G.add_edge('Start', f"{i}-{j}")
                else:
                    G.add_edge(f"{i}-{j-1}", f"{i}-{j}")
                if j == len(self.Jobs[i].start) -1 :
                    G.add_edge(f"{i}-{j}","End")
        for i in range(len(self.Workers)):
            for j in range(len(self.Workers[i].task_job) - 1):
                q_j, q_o = self.Workers[i].task_job[j]
                h_j, h_o = self.Workers[i].task_job[j + 1]
                self.check_cycle_and_add_edge(G, f"{q_j}-{q_o}", f"{h_j}-{h_o}") 
                # G.add_edge(f"{q_j}-{q_o}", f"{h_j}-{h_o}")
        try:
            cycle = nx.find_cycle(G, orientation='original')
            print("Found cycle:", cycle)
            raise Exception("[LSRCriticalPath] error")
        except nx.NetworkXNoCycle:
            absdsa = 1
        for node in nx.topological_sort(G): 
            for pred in G.predecessors(node):
                new_distance = G.nodes[pred]['max_distance'] + G.nodes[node]['duration']
                if new_distance > G.nodes[node]['max_distance']:
                    G.nodes[node]['max_distance'] = new_distance
        longest_path = []
        node = 'End'
        while node:
            longest_path.append(node)
            predecessors = list(G.predecessors(node))
            if not predecessors:
                break
            node = max(predecessors, key=lambda x: G.nodes[x]['max_distance'])
        longest_path.reverse()
        return [longest_path]


    def OpSwapLSR(self, CHS, critical_path, num_wj):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        MS = list(CHS[self.Len_Op:2 * self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        temp_SS = SS[:]
        swap_jo = []
        swap_index = []
        for cb in reversed(range(len(critical_path))):
            if cb != 0 and cb != (len(critical_path) - 1):
                parts = critical_path[cb].split("-")
                job = int(parts[0])
                op = int(parts[1])
                index_w = self.J_site.index((job, op))
                now_w = temp_SS[index_w]
                w = self.PS
                if len(w) > 1:
                    random.shuffle(w)
                    for iw in w:
                        if iw != now_w:
                            swap_jo.append([job,op])
                            swap_index.append(index_w) 
                            break
        if len(swap_index)>=1:
            # for dog in range(len(swap_index)):
            #     for i in range(len(swap_jo)):
            now_w = temp_SS[swap_index[num_wj]]
            w = self.PS
            if len(w) > 1:
                random.shuffle(w)
            for si_w in w:
                if si_w != now_w:
                    temp_SS[swap_index[num_wj]] = si_w
                    temp_OS = OS[:]
                    temp_OS.extend(MS)
                    temp_OSMS = temp_OS[:]
                    temp_OSMS.extend(temp_SS)
                    temp_OSMSSS = temp_OSMS[:]
                    if num_wj == len(swap_jo) -1:
                        return temp_OSMSSS, num_wj,False
                    else:
                        return temp_OSMSSS,num_wj,True

    def SwapTwoLSRsAndOps(self, CHS, critical_path, num_b, num_w):
        self.Len_Op = int(len(CHS) / 3)
        OSMS = list(CHS[0:2 *self.Len_Op])
        SS = list(CHS[2 * self.Len_Op:3 * self.Len_Op])
        tSS = SS[:]
        worker = [] 
        critical_block = {}
        block = []
        block_num = 0
        for j in range(len(critical_path)):
            if j != 0 and j != len(critical_path)-1: 
                parts = critical_path[j].split("-")
                job = int(parts[0])
                op = int(parts[1])
                if worker == []:
                    worker.append(self.Jobs[job]._by[op])
                    block.append([job,op])
                    critical_block[block_num] = block
                else:
                    temp = self.Jobs[job]._by[op]
                    if worker[-1] != temp:  
                        block = []
                        block_num += 1
                    worker.append(temp)
                    block.append([job,op])
                    critical_block[block_num] = block

        if num_b <= len(critical_block.items())-2:
            if num_w == len(critical_block[num_b])-1:
                j1 = critical_block[num_b][num_w]
                j2 = critical_block[num_b+1][0]
                tempSS = self.SwapLSRs(tSS, j1, j2)
                OSMS.extend(tempSS)
                return OSMS, num_b+1, 0, True 
            else:
                return CHS,num_b,num_w+1, True 
        else:
            return CHS,num_b, num_w,False



    def FindLSRLoca(self, CHS, C_max_job, C_max2_job, C_max3_job):
        self.Len_Op = int(len(CHS) / 3)
        OS = list(CHS[0:self.Len_Op])
        cidx_C_max_list = []
        cidx_C_max2_list = []
        cidx_C_max3_list = []
        for cidx,c in enumerate(OS):
            if c == C_max_job:
                cidx_C_max_list.append(cidx)
            elif c == C_max2_job:
                cidx_C_max2_list.append(cidx)
            elif c == C_max3_job:
                cidx_C_max3_list.append(cidx)
        return cidx_C_max_list,cidx_C_max2_list,cidx_C_max3_list
    def ChangeOpsSequence(self, CHS, max_idx, max):
        OS = list(CHS[0:self.Len_Op])
        MSSS = list(CHS[self.Len_Op:3 * self.Len_Op])
        if max == 0 or max == 1:
            return CHS
        else:
            if max_idx == 0:
                target_range = range(0, max)
            else:
                prev_index = OS[max - 1]
                target_range = range(prev_index, max)
            if len(target_range) > 0:
                new_position = random.choice(target_range)
                OS[max], OS[new_position] = OS[new_position], OS[max]
            OS.extend(MSSS)
        return OS
