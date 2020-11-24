import clips
from queue import Queue

# baca input
with open('tc.txt', 'r') as f:
    n = int(f.readline())
    bombs = [[0 for i in range(n)] for j in range(n)]
    m = int(f.readline())
    for i in range(m):
        line = f.readline().split(', ')
        x = int(line[0])
        y = int(line[1])
        bombs[x][y] = 1

# generate matriks angka (-1 bom, 0-4 jumlah bom di sekeliling)
board = [[0 for i in range(n)] for j in range(n)]
dx = [1, 1, 0, -1, -1, -1, 0, 1]
dy = [0, -1, -1, -1, 0, 1, 1, 1]
for i in range(n):
    for j in range(n):
        count = 0
        if bombs[i][j]:
            board[i][j] = -1
        else:
            for k in range(8):
                nx = i + dx[k]
                ny = j + dy[k]
                if nx >= 0 and nx < n and ny >= 0 and ny < n:
                    if bombs[nx][ny] == 1:
                        count += 1
            board[i][j] = count

agent_board = [[-100 for i in range(n)] for j in range(n)]

for i in range(n):
    for j in range(n):
        print(board[i][j], end="\t")
    print()

def execute(x, y):
    global board, agent_board
    # simulate opening
    queue = Queue()
    print('Opening cell', x, y)
    if board[x][y] == 0:
        queue.put((x, y))
        agent_board[x][y] = board[x][y]
        while not queue.empty():
            curx, cury = queue.get()
            for k in range(8):
                nx = curx + dx[k]
                ny = cury + dy[k]
                if nx >= 0 and nx < n and ny >= 0 and ny < n:
                    if agent_board[nx][ny] == -100:
                        agent_board[nx][ny] = board[nx][ny]
                        if board[nx][ny] == 0:
                            queue.put((nx, ny))
    else:
        agent_board[x][y] = 1

    for i in range(n):
        for j in range(n):
            print(agent_board[i][j], end="\t")
        print()

# run
while m > 0:
    environment = clips.Environment()
    
    # masukin fact dan rule
    # fact 1
    # fact 2

    environment.run()
    for a in environment.activations():
        print('ACT: ', a)
    for fact in environment.facts():
        print('FACT: ', fact)
    
    execute(0, 0)
    m = 0
    
