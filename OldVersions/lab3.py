import json
from collections import defaultdict, deque
import sys

class RedirectPrint:
    def __init__(self, filename: str):
        self.filename = filename
        self.original_stdout = sys.stdout

    def __enter__(self):
        self.file = open(self.filename, 'w')
        sys.stdout = self.file
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        sys.stdout = self.original_stdout
        with open(self.filename, 'r') as f:
            print(f.read())

class Graph:
    def __init__(self):
        self.graph = defaultdict(set)

    def add_edge(self, u, v):
        self.graph[u].add(v)
        self.graph[v].add(u)

    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = set()

    def remove_edge(self, u, v):
        self.graph[u].discard(v)
        self.graph[v].discard(u)

    def count_nodes_and_edges(self):
        num_nodes = len(self.graph)
        num_edges = sum(len(neighbors) for neighbors in self.graph.values()) // 2
        return num_nodes, num_edges

    def has_cycles(self):
        cycles = []
        cycles_set = set()
        global_visited = set()

        def add_cycle(neighbor, path):
            def rotate(arr):
                min_index = arr.index(min(arr))
                arr = arr[min_index:] + arr[:min_index]
                return arr

            cycle_start_index = path.index(neighbor)
            cycle = path[cycle_start_index:]
            cycle_set = tuple(rotate(cycle))
            if cycle_set not in cycles_set:
                cycles_set.add(cycle_set)
                cycles.append(cycle + [cycle[0]])

        def dfs_iter(start):
            visited = set()
            stack = deque([(start, None, 0)])
            path = []
            while stack:
                current_node, parent_node, depth = stack.pop()
                if depth < len(path):
                    for i in path[depth:]:
                        visited.discard(i)
                    path = path[:depth]
                visited.add(current_node)
                global_visited.add(current_node)
                path.append(current_node)
                for neighbor in self.graph[current_node]:
                    if neighbor not in visited:
                        stack.append((neighbor, current_node, depth + 1))
                    elif parent_node != neighbor:
                        add_cycle(neighbor, path)

        for node in self.graph:
            if node not in global_visited:
                dfs_iter(node)

        return sorted(cycles)

    def validate_graph_conditions(self):
        visited = set()
        components = []

        def dfs(node):
            stack = deque([node])
            component_nodes = 0
            component_edges = 0
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    component_nodes += 1
                    for neighbor in self.graph[current]:
                        component_edges += 1
                        if neighbor not in visited:
                            stack.append(neighbor)
            return component_nodes, component_edges // 2

        for node in self.graph:
            if node not in visited:
                component_nodes, component_edges = dfs(node)
                components.append((component_nodes, component_edges))

        return (components.count((1, 0)) == 1 or components.count((2, 1)) == 1) and components.count((3, 3)) == 1

    def check_tree(self, verbose: bool):
        def cycles_info(cycles, verbose):
            if cycles:
                if verbose:
                    cycles_info = ':' + ', '.join([' -> '.join(map(str, cycle)) for cycle in cycles])
                else:
                    cycles_info = "."
                print(f"Граф содержит {len(cycles)} простых циклов{cycles_info}")
            else:
                print("Граф не содержит цикл")

        print("Проверка ацикличности : ")
        cycles = self.has_cycles()
        cycles_info(cycles, verbose)
        acyclic = (len(cycles) == 0)
        if acyclic:
            print("Граф ацикличен")
        else:
            print("Граф цикличен")

        num_nodes, num_edges = self.count_nodes_and_edges()
        print("Проверка древочисленности : ")
        print(f"Количество узлов : {num_nodes}, Количество рёбер : {num_edges}")
        tree_structure = (num_nodes == (num_edges + 1))
        if tree_structure:
            print("Граф древочисленный")
        else:
            print("Граф не древочисленный")

        print("Проверка субцикличности : ")
        subcyclic = True
        has_edges_added = False
        nodes = list(self.graph.keys())
        for i in range(len(nodes) - 1):
            for j in range(i + 1, len(nodes)):
                if nodes[j] not in self.graph[nodes[i]]:
                    self.add_edge(nodes[i], nodes[j])
                    print(f"Добавлено ребро : {nodes[i]} {nodes[j]}.")
                    cycles = self.has_cycles()
                    cycles_info(cycles, verbose)
                    if len(cycles) != 1:
                        subcyclic = False
                    has_edges_added = True
                    self.remove_edge(nodes[i], nodes[j])

        if not has_edges_added:
            print("Нет несмежных вершин")

        subcyclic = subcyclic and (
            has_edges_added or len(self.graph) == 1 or len(self.graph) == 2)
        if subcyclic:
            print("Граф субциклический")
        else:
            print("Граф не субциклический")

        print("Проверка 5 G: ациклический и древочисленный")
        if acyclic and tree_structure:
            print("Граф является ациклическим и древочисленным, то есть граф — это дерево.")
        elif acyclic:
            print("Граф является ациклическим, но не древочисленным.")
        elif tree_structure:
            print("Граф является древочисленным, но не ациклическим.")
        else:
            print("Граф не является ни ациклическим, ни древочисленным.")

        print("Проверка 6 G: древочисленный и субциклический за( двумя исключениями)")
        if subcyclic and tree_structure:
            if self.validate_graph_conditions():
                print("Граф является исключением.")
            else:
                print("Граф является древочисленным и субциклическим за( двумя исключениями), то есть граф — это дерево.")
        elif tree_structure:
            print("Граф является древочисленным, но не субциклическим.")
        elif subcyclic:
            print("Граф является субциклическим, но не древочисленным.")
        else:
            print("Граф не является ни древочисленным, ни субциклическим.")

        print("Проверка 7 G: ациклический и субциклический")
        if acyclic and subcyclic:
            print("Граф является ациклическим и субциклическим, то есть граф — это дерево.")
        elif acyclic:
            print("Граф является ациклическим, но не субциклическим.")
        elif subcyclic:
            print("Граф является субциклическим, но не ациклическим.")
        else:
            print("Граф не является ни ациклическим, ни субциклическим.")

    def load_tree_from_json(self, filename: str):
        with open(filename, 'r') as f:
            graph_data = json.load(f)

        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        for node in nodes:
            self.add_node(node)
        for u, v in edges:
            self.add_edge(u, v)

def main():
    graph = Graph()
    input_file = 'graph.json'

    try:
        graph.load_tree_from_json(input_file)
    except FileNotFoundError:
        print(f"Файл {input_file} не найден.")
        return

    verbose = True
    with RedirectPrint('out.log'):
        graph.check_tree(verbose)

if __name__ == '__main__':
    main()
