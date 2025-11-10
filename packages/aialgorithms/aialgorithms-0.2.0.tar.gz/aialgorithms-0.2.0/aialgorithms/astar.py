from heapq import heappush, heappop

grid = [
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [1, 0, 0, 0],
    [0, 0, 1, 0]
]

start = (0, 0)
goal = (3, 3)

def h(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])  # Manhattan distance

def astar(start, goal):
    pq = [(0, start, [start])]
    visited = set()
    while pq:
        cost, (x, y), path = heappop(pq)
        if (x, y) == goal:
            return path
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < 4 and 0 <= ny < 4 and grid[nx][ny] == 0:
                heappush(pq, (cost+1+h((nx,ny),goal), (nx,ny), path+[(nx,ny)]))

print("Shortest Path:", astar(start, goal))
