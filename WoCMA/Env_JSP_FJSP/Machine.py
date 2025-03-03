from log import SingletonLogger
logger = SingletonLogger.get_logger()

class Machine:
    def __init__(self, idx):
        self.idx = idx
        self.start = []
        self.end = []
        self.endt = 0
        self.worker_start = []
        self._on = []

    def update(self, s, e, Job,ws):
        self.start.append(s)
        self.start.sort()
        self.end.append(e)
        self.end.sort()
        self.endt = self.end[-1]
        self.worker_start.append(ws)
        self.worker_start.sort()
        idx = self.start.index(s)
        self._on.insert(idx, Job)

    def find_start(self, o_lastend, p_t, s_t, s_windows, Si):
        s_start =s_windows[0]
        s_Tend = s_windows[1]
        s_Twin = s_windows[2]
        M_Tstart,M_Tend,M_Tlen = self.Empty_time_window()
        SSWZuiZao_start = max(self.endt,Si.endt,o_lastend-s_t)
        maZuiZao_start = max(o_lastend,self.endt,SSWZuiZao_start+s_t)
        if M_Tlen is not None and s_Twin is not None:
            for i in range(len(M_Tlen)):
                if M_Tlen[i] >= p_t + s_t:
                    if M_Tstart[i] >= o_lastend:
                        for j in range(len(s_Twin)):
                            if s_Tend[j] >= M_Tstart[i]+ s_t:
                                if s_start[j] <= M_Tstart[i]:
                                    maZuiZao_start = M_Tstart[i] + s_t
                                    SSWZuiZao_start = M_Tstart[i]
                                    break
                                elif M_Tend[i] - s_start[j] >= p_t + s_t and s_Twin[j] >=s_t :
                                    maZuiZao_start = s_start[j] + s_t
                                    SSWZuiZao_start =s_start[j]
                                    break
                        break
                    if M_Tstart[i] < o_lastend:
                        if M_Tend[i] - o_lastend >= p_t:

                            if o_lastend - M_Tstart[i] >= s_t:
                                for j in range(len(s_Twin)):
                                    if s_Tend[j] >= M_Tstart[i]+s_t and s_Twin[j] >= s_t:
                                        if s_Tend[j] >= o_lastend:
                                            maZuiZao_start = o_lastend
                                            SSWZuiZao_start = o_lastend-s_t
                                            break
                                        elif s_Tend[j] <= o_lastend:
                                            maZuiZao_start = o_lastend
                                            SSWZuiZao_start = self.worker_bug2(o_lastend,s_t,s_start,s_Tend,s_Twin)
                                            break
                                break
                            if o_lastend - M_Tstart[i] <= s_t:
                                for j in range(len(s_Twin)):
                                    if s_start[j] <= M_Tstart[i] and s_Tend[j] >= M_Tstart[i] + s_t:
                                        maZuiZao_start = M_Tstart[i] + s_t
                                        SSWZuiZao_start = M_Tstart[i]
                                        break
                                    elif s_start[j] >= M_Tstart[i] and s_start[j]+s_t+p_t<=M_Tend[i] and s_Tend[j] >= s_start[j]+s_t:
                                        maZuiZao_start = s_start[j] + s_t
                                        SSWZuiZao_start = s_start[j]
                                        break
                                break
        return SSWZuiZao_start, maZuiZao_start
    
    def Empty_time_window(self):
        time_window_start = []
        time_window_end = []
        len_time_window = []
        if self.end is None:
            pass
        elif len(self.end) == 1:
            if self.worker_start[0] != 0:
                time_window_start = [0]
                time_window_end = [self.worker_start[0]]
        elif len(self.end) > 1:
            if self.worker_start[0] != 0:
                time_window_start.append(0)
                time_window_end.append(self.worker_start[0])
            time_window_start.extend(self.end[:-1])
            time_window_end.extend(self.worker_start[1:])
        if time_window_end is not None:
            len_time_window = [time_window_end[i] - time_window_start[i] for i in range(len(time_window_end))]
        if len(len_time_window) >= 1:
            zero_indices = [index for index, value in enumerate(len_time_window) if value == 0]
            time_window_start = [value for index, value in enumerate(time_window_start) if index not in zero_indices]
            time_window_end = [value for index, value in enumerate(time_window_end) if index not in zero_indices]
            len_time_window = [value for index, value in enumerate(len_time_window) if index not in zero_indices]
        return time_window_start, time_window_end, len_time_window

    def worker_bug2(self,last_O_end,S_t,SS_Tstart,SS_Tend,SS_Tlen):
        logger.info(f"last_O_end:{last_O_end},S_t:{S_t}")
        logger.info(f"SS_Tstart:{SS_Tstart},SS_Tend:{SS_Tend},SS_Tlen:{SS_Tlen}")
        for k in range(len(SS_Tlen)-1,-1,-1):
            if SS_Tend[k] <= last_O_end and SS_Tstart[k]+S_t <= SS_Tend[k]:
                return SS_Tend[k] - S_t
            elif SS_Tend[k] >= last_O_end and SS_Tstart[k]+S_t <= last_O_end:
                return last_O_end - S_t