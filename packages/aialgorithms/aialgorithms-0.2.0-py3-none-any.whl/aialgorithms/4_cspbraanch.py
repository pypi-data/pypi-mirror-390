def print_solution(board):
    for row in board:
        print(" ".join("Q" if x == 1 else "." for x in row))
    print()

def solve_n_queens_branch_bound(n):
    board = [[0]*n for _ in range(n)]
    cols = [False]*n
    d1 = [False]*(2*n-1)
    d2 = [False]*(2*n-1)
    
    def solve(row):
        if row == n:
            print_solution(board)
            return True
        for col in range(n):
            if not cols[col] and not d1[row - col + n - 1] and not d2[row + col]:
                board[row][col] = 1
                cols[col] = d1[row - col + n - 1] = d2[row + col] = True
                if solve(row + 1):
                    return True
                # Backtrack
                board[row][col] = 0
                cols[col] = d1[row - col + n - 1] = d2[row + col] = False
        return False

    solve(0)

n = int(input("Enter number of queens: "))
solve_n_queens_branch_bound(n)
