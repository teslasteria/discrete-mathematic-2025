#include <iostream>
#include <vector>
#include <stack>
#include <cstdlib>
#include <ctime>
#include <fstream>
using namespace std;

struct State {
    int depth;
    vector<int> mapping;
    vector<int> candidates;
    int current_candidate;
};

vector<vector<int>> generate_random_graph(int n) {
    vector<vector<int>> graph(n, vector<int>(n, 0));
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (rand() % 2) {
                graph[i][j] = 1;
                graph[j][i] = 1;
            }
        }
    }
    return graph;
}

void write_graph_to_file(const vector<vector<int>>& graph, ofstream& file) {
    int n = graph.size();
    int m = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (graph[i][j]) {
                m++;
            }
        }
    }
    file << m << endl;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (graph[i][j]) {
                file << i << " " << j << endl;
            }
        }
    }
}

vector<vector<int>> read_graph_from_file(ifstream& file, int n) {
    vector<vector<int>> graph(n, vector<int>(n, 0));
    int m;
    file >> m;
    for (int i = 0; i < m; i++) {
        int u, v;
        file >> u >> v;
        graph[u][v] = 1;
        graph[v][u] = 1;
    }
    return graph;
}

vector<int> generate_candidates(int depth, const vector<int>& mapping, const vector<vector<int>>& G1, const vector<vector<int>>& G2) {
    vector<int> candidates;
    int v = depth;
    int n = G2.size();
    vector<bool> used(n, false);
    for (int i = 0; i < depth; i++) {
        if (mapping[i] != -1) used[mapping[i]] = true;
    }
    for (int w = 0; w < n; w++) {
        if (used[w]) continue;
        bool compatible = true;
        for (int u = 0; u < depth; u++) {
            if (G1[u][v] != G2[mapping[u]][w]) {
                compatible = false;
                break;
            }
        }
        if (compatible) {
            candidates.push_back(w);
        }
    }
    return candidates;
}

vector<int> vf2_iterative(const vector<vector<int>>& G1, const vector<vector<int>>& G2) {
    int n = G1.size();
    if (n != G2.size()) {
        return vector<int>();
    }
    stack<State> stk;
    State initial;
    initial.depth = 0;
    initial.mapping = vector<int>(n, -1);
    initial.candidates = generate_candidates(initial.depth, initial.mapping, G1, G2);
    initial.current_candidate = 0;
    stk.push(initial);

    while (!stk.empty()) {
        State current = stk.top();
        stk.pop();

        if (current.depth == n) {
            return current.mapping;
        }

        if (current.current_candidate < current.candidates.size()) {
            int w = current.candidates[current.current_candidate];
            State next = current;
            next.depth = current.depth + 1;
            next.mapping[current.depth] = w;
            next.candidates = generate_candidates(next.depth, next.mapping, G1, G2);
            next.current_candidate = 0;
            
            current.current_candidate++;
            stk.push(current);
            stk.push(next);
        }
    }
    return vector<int>();
}

int main() {
    srand(time(0));
    int n;
    cout << "Enter number of vertices (n): ";
    cin >> n;

    vector<vector<int>> graph1 = generate_random_graph(n);
    vector<vector<int>> graph2 = generate_random_graph(n);

    ofstream outfile("graphs.txt");
    outfile << n << endl;
    write_graph_to_file(graph1, outfile);
    write_graph_to_file(graph2, outfile);
    outfile.close();

    ifstream infile("graphs.txt");
    infile >> n;
    vector<vector<int>> G1 = read_graph_from_file(infile, n);
    vector<vector<int>> G2 = read_graph_from_file(infile, n);
    infile.close();

    vector<int> isomorphism = vf2_iterative(G1, G2);

    if (isomorphism.empty()) {
        cout << "Graphs are not isomorphic." << endl;
    } else {
        cout << "Graphs are isomorphic. Isomorphism:" << endl;
        for (int i = 0; i < n; i++) {
            cout << i << " -> " << isomorphism[i] << endl;
        }
    }

    return 0;
}