graph = {}
n = int(input("Vertices: "))

for i in range(n):
    v = input(f"V{i+1}: ")
    graph[v] = input(f"Nbrs of {v}: ").split()

def dfs(node, visited):
    print(node, end=" ")
    visited.add(node)
    for n in graph[node]:
        if n not in visited:
            dfs(n, visited)

def bfs(queue, visited):
    if not queue:
        return
    node = queue.pop(0)
    if node not in visited:
        print(node, end=" ")
        visited.append(node)
        queue.extend(graph[node])
    bfs(queue, visited)

start = input("Start: ")

print("\nDFS:")
dfs(start, set())

print("\nBFS:")
bfs([start], [])
