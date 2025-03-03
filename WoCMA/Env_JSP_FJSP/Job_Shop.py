from Env_JSP_FJSP.Job import Job
from Env_JSP_FJSP.Machine import Machine
from Env_JSP_FJSP.SetupWorker import SetupWorkers

class Job_shop:
    def __init__(self,args):
        self.n= args.n
        self.m=args.m
        self.s = args.s
        self.O_num=args.O_num
        self.PM = args.Processing_Machine
        self.PT = args.Processing_Time
        self.ST = args.Setup_Time
        self.reset()

    def reset(self):
        self.C_max = 0      #makespan
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
        if end>self.C_max:  # update makespan
            self.C_max=end

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