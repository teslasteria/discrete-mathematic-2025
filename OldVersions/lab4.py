from collections import defaultdict, deque
import argparse
import openpyxl
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
        sys.stdout = self.original_stdout
        self.file.close()
        with open(self.filename, 'r') as f:
            print(f.read())


class Graph:
    def __init__(self, nodes=None, edges=None) -> None:
        self.graph = defaultdict(set)
        if nodes is not None:
            for node in nodes:
                self.add_node(node)
        if edges is not None:
            for u, v in edges:
                self.add_edge(u, v)

    def add_edge(self, u, v) -> None:
        self.graph[u].add(v)
        self.graph[v].add(u)

    def add_node(self, node) -> None:
        if node not in self.graph:
            self.graph[node] = set()

    def remove_edge(self, u, v) -> None:
        self.graph[u].discard(v)
        self.graph[v].discard(u)

    def greedy_coloring(self) -> dict:
        color_map = {}
        for node in self.graph:
            neighbor_colors = {
                color_map[neighbor]
                for neighbor in self.graph[node]
                if neighbor in color_map
            }
            color = 0
            while color in neighbor_colors:
                color += 1
            color_map[node] = color
        return color_map

    def _is_safe(self, node, color, color_map):
        for neighbor in self.graph[node]:
            if neighbor in color_map and color_map[neighbor] == color:
                return False
        return True

    def _graph_coloring(self, max_colors):
        color_map = {}
        nodes = list(self.graph.keys())
        stack = deque([(0, 0)])
        while stack:
            node_index, color_processed = stack.pop()
            if node_index == 0 and color_processed == 1:
                return None
            if node_index == len(nodes):
                return color_map
            node_name = nodes[node_index]
            if nodes[node_index] in color_map:
                del color_map[node_name]
            for color in range(color_processed, max_colors):
                if self._is_safe(node_name, color, color_map):
                    color_map[node_name] = color
                    stack.append((node_index, color + 1))
                    stack.append((node_index + 1, 0))
                    break
        return None

    def graph_coloring(self):
        for num_colors in range(1, len(self.graph) + 1):
            color_map = self._graph_coloring(num_colors)
            if color_map:
                return color_map
        return None

    def load_tree_from_excel(self, filename: str):
        wb = openpyxl.load_workbook(filename)
        sheet = wb.active
        nodes = set()
        edges = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            u, v = row
            nodes.update([u, v])
            edges.append((u, v))
        for node in nodes:
            self.add_node(node)
        for u, v in edges:
            self.add_edge(u, v)


def main():
    parser = argparse.ArgumentParser(description="Хроматическое число графа")
    graph_group = parser.add_argument_group('Граф', 'Способы задания графа')
    graph_group.add_argument(
        '--edges',
        nargs='+',
        help='Список рёбер графа в формате: узел1 узел2, например: A B C D (для рёбер A-B и C-D)',
        required=False)
    graph_group.add_argument('--nodes', nargs='+', help='Список узлов графа, например: A B C D', required=False)
    graph_group.add_argument(
        '--excel-load',
        help='Загрузить граф из Excel файла, например: graph.xlsx',
        default='graph.xlsx',
        required=False)
    args = parser.parse_args()
    g = Graph()
    with RedirectPrint('output.txt'):
        if args.edges:
            print("Загрузка графа из рёбер.")
            for node in args.nodes:
                g.add_node(node)
            for i in range(0, len(args.edges), 2):
                g.add_edge(args.edges[i], args.edges[i + 1])
            print(
                f"Граф загружен с {len(args.nodes)} узлами и {len(args.edges) // 2} рёбрами.")
        elif args.excel_load:
            print(f"Загрузка графа из файла {args.excel_load}.")
            g.load_tree_from_excel(args.excel_load)
            print("Граф успешно загружен из Excel.")
        else:
            raise ValueError(
                "Неизвестный алгоритм. Укажите рёбра или файл Excel.")
        print("Выполнение жадной раскраски.")
        greedy_coloring = g.greedy_coloring()
        print(
            "Раскраска (жадная): ",
            greedy_coloring)
        print("Выполнение оптимальной раскраски.")
        best_coloring = g.graph_coloring()
        print(
            "Раскраска (оптимальная): ",
            best_coloring)
        print(
            f"Хроматическое число (жадная раскраска): {max(greedy_coloring.values()) + 1}")
        print(
            f"Хроматическое число (оптимальная раскраска): {max(best_coloring.values()) + 1}")


if __name__ == "__main__":
    main()
