import clips
from queue import Queue
from itertools import combinations
from tkinter import Tk, Canvas, Frame, BOTH, Button, ttk

# baca input
FileName = input("Masukkan file testcase: ")
with open(FileName, 'r') as f:
    n = int(f.readline())
    bombs = [[0 for i in range(n)] for j in range(n)]
    m = int(f.readline())
    for i in range(m):
        line = f.readline().split(', ')
        x = int(line[0])
        y = int(line[1])
        bombs[x][y] = 1
clicked = []
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

# generate board u/ agent
agent_board = [[-100 for i in range(n)] for j in range(n)] # -100: unopened

# print board solusi
for i in range(n):
    for j in range(n):
        print(board[i][j], end="\t")
    print()

def execute(x, y):
    global board, agent_board, clicked
    # simulate opening
    clicked.append((x,y))
    queue = Queue()
    print('Opening cell', x, y)
    agent_board[x][y] = board[x][y]
    if board[x][y] == 0:
        queue.put((x, y))
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

    opened = 0
    for i in range(n):
        for j in range(n):
            if agent_board[i][j] != -100:
                opened += 1
            print(agent_board[i][j], end="\t")
        print()
    return opened

def find_solution(cells, rules, env):
    defrule_string = '(defrule find-solution (declare (salience 10)) '
    
    for cell in cells:
        defrule_string += '(combination ' + cell + ' ?n' + cell + ')'
        # defrule_string += '(' + cell + '_count ?x' + cell + ')'
    
    for rule in rules:
        # print(rule)
        if len(rule[1]) == 1:
            defrule_string += '(test (= ?n' + str(rule[1][0]) + ' ' + str(rule[0]) + '))'
        elif len(rule[1]) > 1:
            defrule_string += '(test (= (+ '
            for cell in rule[1]:
                defrule_string += '?n' + str(cell) + ' '
            defrule_string += ')' + str(rule[0]) + '))'

    # defrule_string += ' => (printout t "Found Solution" crlf) '
    defrule_string += ' => (bind ?*solution_count* (+ ?*solution_count* 1))'
    for cell in cells:
        # defrule_string += '(printout t "' + cell + ' = " ?n' + cell + ' crlf)'
        # defrule_string += '(retract (' + cell + '_count ?x' + cell + ')) '
        # defrule_string += '(assert (' + cell + '_count ?x' + cell + ' + ?n' + cell + ')) '
        defrule_string += '(bind ?*' + cell + '_count* (+ ?*' + cell + '_count* ?n' + cell + '))'
    defrule_string += ')'
    # print(defrule_string)
    # for fact in environment.facts():
    #     print('FACT: ', fact)
    env.build(defrule_string)

def print_probability(cells, env):
    defrule_string = '(defrule print_probability (declare (salience -10)) => '
    defrule_string += '(printout t "Found Probabilities" crlf)'
    for cell in cells:
        defrule_string += '(printout t "' + cell + ' = " (/ ?*' + cell + '_count* ?*solution_count*) crlf)'
    defrule_string += ')'
    env.build(defrule_string)

def get_move(cells, env):
    for cell in cells:
        defrule_string = '?*' + cell + '_count*'
        if int(env.eval(defrule_string)) == 0:
            return cell
    return None

def startup(cells, env):
    defrule_string = '(assert (number 0) (number 1) '
    for cell in cells:
        defrule_string += '(cell ' + cell + ') '
    defrule_string += ')'
    # print(defrule_string)
    env.eval(defrule_string)

    defrule_string = '(defglobal ?*solution_count* = 0)'
    # print(defrule_string)
    env.build(defrule_string)

    for cell in cells:
        defrule_string = '(defglobal ?*' + cell + '_count* = 0)'
        # print(defrule_string)
        env.build(defrule_string)

# inisialisasi board dengan buka di 0,0 saat turn awal
opened = execute(0,0)

# run
while opened < n * n - m:
    environment = clips.Environment()
    
    environment.load('minesweeper.clp')

    cells = []
    rules = []
    for i in range(n):
        for j in range(n):
            if agent_board[i][j] > 0:
                unopened = []
                for k in range(8):
                    nx = i + dx[k]
                    ny = j + dy[k]
                    if nx >= 0 and nx < n and ny >= 0 and ny < n:
                        if agent_board[nx][ny] == -100: # not opened
                            cell_name = 'c' + str(nx) + str(ny)
                            unopened.append(cell_name)
                            if cell_name not in cells:
                                cells.append(cell_name)
                rules.append((agent_board[i][j], unopened))

    startup(cells, environment)
    find_solution(cells, rules, environment)
    print_probability(cells, environment)

    for rule in environment.rules():
        rule.watch_firings = True
        rule.watch_activations = True

    environment.run()
    move = get_move(cells, environment)
        
    
    if not move == None:
        opened = execute(int(move[1]), int(move[2]))
    # for a in environment.activations():
    #     print('ACT: ', a)
    # for fact in environment.facts():
    #     print('FACT: ', fact)
    # for rule in environment.rules():
    #     print('RULE: ', rule)

class Board:

    def __init__(self, agent_board, tk):
        super().__init__()
        # self.master.title("MineSweeper")
        # self.pack(fill=BOTH, expand=1)
        self.board = agent_board
        self.tk = tk
        self.frame = Frame(self.tk)
        self.setup()
    
    def setup(self):
        n = True
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):

                if(self.board[i][j] == -100):
                    if n:
                        tile = Button(self.tk, text = "", width = 4, height = 2, bg = "#34495E", state="disabled", borderwidth=0, font=("CourierNew 16 bold"), disabledforeground="#7F8C8D")
                    else:
                        tile = Button(self.tk, text = "", width = 4, height = 2, bg = "#2C3E50", state="disabled", borderwidth=0, font=("CourierNew 16 bold"), disabledforeground="#7F8C8D")
                else:
                    if n:
                        tile = Button(self.tk, text = self.board[i][j], width = 4, height = 2, bg = "#ECF0F1", state="disabled", borderwidth=0, font=("CourierNew 16 bold"), disabledforeground="#7F8C8D")
                    else:
                        tile = Button(self.tk, text = self.board[i][j], width = 4, height = 2, bg = "#DFE4E6", state="disabled", borderwidth=0, font=("CourierNew 16 bold"), disabledforeground="#7F8C8D")
                        
                    if (self.board[i][j] == 1):
                        tile.config(disabledforeground="#3498DB")
                    elif (self.board[i][j] == 2):
                        tile.config(disabledforeground="#2ECC71")
                    elif (self.board[i][j] == 3):
                        tile.config(disabledforeground="#E74C3C")

                tile.grid(row = i + 1, column = j)
                n = not n
            n = not n
                
print(clicked)
        
window = Tk()
window.title("Mineshaft")
board = Board(agent_board, window)
window.mainloop()
