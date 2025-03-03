import numpy as np
from pymoo.indicators.hv import HV
import openpyxl
import json


def lexicographic_sorting(pareto_front):
    # # Sort by the first objective function
    # sorted_pareto_front = sorted(pareto_front, key=lambda x: x[0])
    # # Sort by the second objective function
    # i = 0
    # while i < len(sorted_pareto_front) - 1:
    #     j = i + 1
    #     while j < len(sorted_pareto_front) and sorted_pareto_front[j][0] == sorted_pareto_front[i][0]:
    #         j += 1
    #     sorted_pareto_front[i:j] = sorted(sorted_pareto_front[i:j], key=lambda x: x[1])
    #     i = j
    return sorted(pareto_front, key=lambda x: (x[0], x[1]))

def normalized(pareto):
    normalized_frontier = []
    if len(pareto) == 1:
        return [[1, 1]]  # If there is only one solution, return directly
    # Extract minimum and maximum values
    min_values = [min(x) for x in zip(*pareto)]
    max_values = [max(x) for x in zip(*pareto)]
    # Check if any objective function has the same maximum and minimum values
    for i in range(len(min_values)):
        if max_values[i] - min_values[i] == 0:
            max_values[i] += 1e-9  # Avoid division by zero
    # Normalize
    for solution in pareto:
        normalized_solution = [(x - min_values[i]) / (max_values[i] - min_values[i]) for i, x in enumerate(solution)]
        normalized_frontier.append(normalized_solution)
    return normalized_frontier

def quchong(pareto_points):
    # Convert fitness to array
    arr2 = []
    for i in pareto_points:
        temp_fit = i.fitness
        arr2.append(temp_fit)
    ##########Remove duplicates
    my_set = set(map(tuple, arr2))
    # Convert set back to list
    my_list = list(map(list, my_set))
    return my_list

def paixu_gui1hua(my_list):
    arr1 = lexicographic_sorting(my_list)  # Sort, first by the first objective function, then by the second objective function if the first is the same
    arr = normalized(arr1)
    return arr

def hypervolume_pymoo(pareto_points):
    fp = paixu_gui1hua(pareto_points)
    print(f"fp:{fp}")
    ref_point = [1.2, 1.2]
    # for i in range(len(max_values1)):
    #     temp_ref = max_values1[i] + 1
    #     ref_point.append(temp_ref)
    ind = HV(ref_point=ref_point)
    hv_arr = np.array(fp)  # Convert to array
    HV_Value = ind(hv_arr)
    return HV_Value

def is_dominated(sol1, sol2):
    """
    Determine if solution sol1 is dominated by solution sol2.
    If sol2 is not worse than sol1 in all dimensions, and better than sol1 in at least one dimension, then sol1 is dominated by sol2.
    """
    less_than = False
    for a, b in zip(sol1, sol2):
        if a < b:
            return False
        elif a > b:
            less_than = True
    return less_than


def calculate_c_metric(set_a, set_b):
    dominate_count = 0
    for sol_b in set_b:
        for sol_a in set_a:
            if is_dominated(sol_b, sol_a):
                dominate_count += 1
                break
    return dominate_count / len(set_b)


def save_excel_pymoo(gd, row, column, file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    # Write data to the specified cell
    sheet.cell(row=row, column=column).value = gd
    # Save workbook
    workbook.save(file_path)

def save_to_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f) 