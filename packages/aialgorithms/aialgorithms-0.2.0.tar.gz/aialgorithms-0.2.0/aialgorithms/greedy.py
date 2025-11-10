INF = 9999999

def take_input():
    n = int(input("Vertices: "))
    print("Enter matrix (0 = no edge):")
    G = []
    for i in range(n):
        row = list(map(int, input().split()))
        G.append(row)
    return G, n

def prims(G, n):
    sel = [0]*n
    sel[0] = 1
    print("\nEdge : Weight")
    for _ in range(n-1):
        m, x, y = INF, 0, 0
        for i in range(n):
            if sel[i]:
                for j in range(n):
                    if not sel[j] and 0 < G[i][j] < m:
                        m, x, y = G[i][j], i, j
        print(f"{x}-{y} : {m}")
        sel[y] = 1

G, n = take_input()
prims(G, n)
