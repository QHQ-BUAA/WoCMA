import matplotlib.pyplot as plt
import numpy as np
import os.path

def Gantt_Ma(JS, title, g_name, g_jjj):
    M =[ 'navajowhite','lightsalmon','yellow', 'orange', 'green', 'purple', 'pink', 'cyan',  'peachpuff', 'powderblue','lime',
    'magenta', 'gold', 'silver',  'orangered', 'plum', 'peru', 'navy', 'salmon', 'coral', 'chartreuse', 'aquamarine', 'khaki',
    'olive', 'sienna', 'violet', 'wheat', 'turquoise', 'tomato', 'hotpink', 'royalblue', 'slateblue', 'darkviolet',
    'deepskyblue', 'springgreen', 'mediumslateblue', 'darkcyan', 'navajowhite', 'goldenrod', 'darkgreen', 'palegoldenrod',
    'lightblue', 'red',  'steelblue','thistle', 'cadetblue','teal', 'indigo',
    'moccasin', 'burlywood', 'ghostwhite','blue',]
    num_repeats = 10000
    M = M * num_repeats

    Machines = JS.Machines
    Jobs = JS.Jobs
    plt.figure(figsize=(20, 10))
    for i in range(len(Machines)):
        Machine = Machines[i]
        Start_time = Machine.start
        End_time = Machine.end
        Worker_Start_time = Machine.worker_start
        Worker_End_time = Machine.start
        for i_1 in range(len(End_time)):
            color = M[Machine._on[i_1][0]]
            plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.6, left=Start_time[i_1], color=color,
                     edgecolor='black',linewidth=0.5)
            text_x = Start_time[i_1] + (End_time[i_1] - Start_time[i_1]) / 2
            text_y = i
            plt.text(
                x=text_x,
                y=text_y,
                s=f'{Machine._on[i_1][0]+1}',
                fontsize=12,
                fontfamily='Times New Roman',
                verticalalignment='center',
                horizontalalignment='center'
            )

            color2 = M[30+Jobs[Machine._on[i_1][0]]._by[Machine._on[i_1][1]]]
            plt.barh(i, width=Worker_End_time[i_1] - Worker_Start_time[i_1], height=0.6, left=Worker_Start_time[i_1], color=color2)

            worker_text_x = Worker_Start_time[i_1] + (Worker_End_time[i_1] - Worker_Start_time[i_1]) / 2
            worker_text_y = i
            plt.text(
                x=worker_text_x,
                y=worker_text_y,
                s=f'{Jobs[Machine._on[i_1][0]]._by[Machine._on[i_1][1]]}',
                fontsize=12,
                fontfamily='Times New Roman',
                verticalalignment='center',
                horizontalalignment='center'
            )
    plt.yticks(np.arange(i + 1), np.arange(1, i + 2), fontsize=14, fontfamily='Times New Roman')
    plt.xticks(fontsize=14, fontfamily='Times New Roman')
    plt.title(title, fontfamily='Times New Roman')
    plt.ylabel('Machines', fontfamily='Times New Roman')
    plt.xlabel('Time(s)', fontfamily='Times New Roman')
    floder = "pic"
    name = f"{g_name}_{g_jjj}_{title}.svg"
    floder_name = os.path.join(floder, name)
    plt.savefig(floder_name, dpi=500, format='svg')