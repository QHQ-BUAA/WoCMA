
class SetupWorkers:
    def __init__(self, worker_index):
        self.Worker_index = worker_index
        self.setup_time = []
        self.Processed = []
        self.start = []
        self.end = []
        self.endt = 0
        self.task_job = []
        self.task_machines = []

    def Empty_time_window_ss(self):
        time_window_start = []
        time_window_end = []
        len_time_window = []
        if self.end is None:
            pass
        elif len(self.end) == 1:
            if self.start[0] != 0:
                time_window_start = [0]
                time_window_end = [self.start[0]]
        elif len(self.end) > 1:
            if self.start[0] != 0:
                time_window_start.append(0)
                time_window_end.append(self.start[0])
            time_window_start.extend(self.end[:-1])
            time_window_end.extend(self.start[1:])
        if time_window_end is not None:
            len_time_window = [time_window_end[i] - time_window_start[i] for i in range(len(time_window_end))]
        if len(len_time_window) >= 1:
            zero_indices = [index for index, value in enumerate(len_time_window) if value == 0]
            time_window_start = [value for index, value in enumerate(time_window_start) if index not in zero_indices]
            time_window_end = [value for index, value in enumerate(time_window_end) if index not in zero_indices]
            len_time_window = [value for index, value in enumerate(len_time_window) if index not in zero_indices]
        return time_window_start, time_window_end, len_time_window
    # endregion

    def update(self,assigned_task,start_time,end_time):
        self.Processed.append(1)
        a = self.PanDuanWeiZhi(self.start, start_time)
        if a == 0:
            self.task_job.append(assigned_task[0])
            self.task_machines.append(assigned_task[1])
            self.setup_time.append(end_time-start_time)
            self.start.append(start_time)
            self.end.append(end_time)
            self.endt = end_time
        else:
            if a == -1:
                a=0
            self.task_job.insert(a,assigned_task[0])
            self.task_machines.insert(a,assigned_task[1])
            self.setup_time.insert(a,end_time-start_time)
            self.start.insert(a, start_time)
            self.end.insert(a, end_time)
            self.endt = self.end[-1]

    def PanDuanWeiZhi(self,list,start_time):
        if len(list) >= 1:
            for i in range(len(list)-1, -1, -1):
                if start_time >= list[i]:
                    if i < len(list)-1:
                        return i + 1
                    else:
                        return 0
                elif 0<=start_time<list[0]:
                    return -1
        else:
            return 0