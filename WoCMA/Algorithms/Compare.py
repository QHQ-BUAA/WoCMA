
def lexicographic_sorting(pareto_front):
    return sorted(pareto_front, key=lambda x: (x[0], x[1]))

def normalized(pareto):
    normalized_frontier = []
    if len(pareto) == 1:
        return [[1, 1]]
    min_values = [min(x) for x in zip(*pareto)]
    max_values = [max(x) for x in zip(*pareto)]
    for i in range(len(min_values)):
        if max_values[i] - min_values[i] == 0:
            max_values[i] += 1e-9

    for solution in pareto:
        normalized_solution = [(x - min_values[i]) / (max_values[i] - min_values[i]) for i, x in enumerate(solution)]
        normalized_frontier.append(normalized_solution)
    return normalized_frontier

def paixu_gui1hua(my_list):
    arr1 = lexicographic_sorting(my_list)
    arr = normalized(arr1)
    return arr
