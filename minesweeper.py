from tkinter.constants import RIGHT, LEFT
import clips
from queue import Queue
from itertools import combinations
from tkinter import Tk, Canvas, Frame, BOTH, Button, ttk, Label, LabelFrame
import copy

# Baca input
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

# Generate matriks angka (-1 bom, 0-4 jumlah bom di sekeliling kotak yang dimaksud)
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

# Generate board untuk agent
agent_board = [[-100 for i in range(n)] for j in range(n)] # -100: unopened

# Mencatat semua move - inisialisasi
clicked = [("-", copy.deepcopy(agent_board))]

# Print board solusi (yang sudah terbuka semua)
print("Solution: ")
for i in range(n):
    for j in range(n):
        print(board[i][j], end="\t")
    print()

# Fungsi untuk execute
def execute(x, y):
    global board, agent_board, clicked
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

    clicked.append(((x,y), copy.deepcopy(agent_board)))
    opened = 0
    for i in range(n):
        for j in range(n):
            if agent_board[i][j] != -100:
                opened += 1
            print(agent_board[i][j], end="\t")
        print()
    return opened

# Fungsi untuk melakukan generate solusi
def find_solution(cells, rules, env):
    # Menginisialisasi rule dengan menggunakan defrule dengan salience 10
    defrule_string = '(defrule find-solution (declare (salience 10)) '
    
    for cell in cells:
        defrule_string += '(combination ' + cell + ' ?n' + cell + ')'
    
    for rule in rules:
        if len(rule[1]) == 1:
            defrule_string += '(test (= ?n' + str(rule[1][0]) + ' ' + str(rule[0]) + '))'
        elif len(rule[1]) > 1:
            defrule_string += '(test (= (+ '
            for cell in rule[1]:
                defrule_string += '?n' + str(cell) + ' '
            defrule_string += ')' + str(rule[0]) + '))'

    defrule_string += ' => (bind ?*solution_count* (+ ?*solution_count* 1))'
    for cell in cells:
        defrule_string += '(bind ?*' + cell + '_count* (+ ?*' + cell + '_count* ?n' + cell + '))'
    defrule_string += ')'
    env.build(defrule_string)

# Melakukan print probability
def print_probability(cells, env):
    defrule_string = '(defrule print_probability (declare (salience -10)) => '
    defrule_string += '(printout t "Found Probabilities" crlf)'
    for cell in cells:
        defrule_string += '(printout t "' + cell + ' = " (/ ?*' + cell + '_count* ?*solution_count*) crlf)'
    defrule_string += ')'
    env.build(defrule_string)

# Fungsi untuk mengembalikan cell yang ingin dibuka
def get_move(cells, env):
    for cell in cells:
        defrule_string = '?*' + cell + '_count*'
        if int(env.eval(defrule_string)) == 0:
            return cell
    return None

# Fungsi untuk deklarasi fakta
def startup(cells, env):
    # Deklarasi facts dengan menggunakan assert
    defrule_string = '(assert (number 0) (number 1) '
    for cell in cells:
        defrule_string += '(cell ' + cell + ') '
    defrule_string += ')'
    env.eval(defrule_string)

    defrule_string = '(defglobal ?*solution_count* = 0)'
    env.build(defrule_string)

    for cell in cells:
        defrule_string = '(defglobal ?*' + cell + '_count* = 0)'
        env.build(defrule_string)

# Inisialisasi board dengan buka di (0,0) saat turn awal
opened = execute(0,0)

# Run
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

    for fact in environment.facts():
        print('FACT: ', fact)

    for rule in environment.rules():
        print('RULE: ', rule)

# Inisialisasi kelas Board
class Board:
    # Konstruktor
    def __init__(self, clicked, tk):
        super().__init__()
        # self.master.title("MineSweeper")
        # self.pack(fill=BOTH, expand=1)
        self.board = clicked[0][1]
        self.move = clicked[0][0]
        self.tk = tk
        self.frame = Frame(self.tk)
        self.clicked = clicked
        self.turn = 0
        self.setup()
    
    def next(self):
        if (self.turn < len(clicked) - 1):
            self.turn += 1
            self.board = clicked[self.turn][1]
            self.move = clicked[self.turn][0]
            self.update()
    
        
    def prev(self):
        if (self.turn > 0):
            self.turn -= 1
            self.board = clicked[self.turn][1]
            self.move = clicked[self.turn][0]
            self.update()

    # Method setup
    def setup(self):
        for child in self.tk.winfo_children():
            child.destroy()
        n = True
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):

                if(self.board[i][j] == -100):
                    if n:
                        tile = Frame(self.tk, width = 60, height = 60, bg = "#34495E", borderwidth=0)
                    else:
                        tile = Frame(self.tk, width = 60, height = 60, bg = "#2C3E50", borderwidth=0)
                else:
                    if n:
                        tile = Frame(self.tk, width = 60, height = 60, bg = "#ECF0F1", borderwidth=0)
                    else:
                        tile = Frame(self.tk, width = 60, height = 60, bg = "#DFE4E6", borderwidth=0)
                        
                    if (self.board[i][j] == 1):
                        Label(tile, text=self.board[i][j], bg = tile.cget("bg"), font=("CourierNew 24 bold"), foreground="#3498DB").place(x = 30, y = 30, anchor="center")
                    elif (self.board[i][j] == 2):
                        Label(tile, text=self.board[i][j], bg = tile.cget("bg"), font=("CourierNew 24 bold"), foreground="#2ECC71").place(x = 30, y = 30, anchor="center")
                    elif (self.board[i][j] == 3):
                        Label(tile, text=self.board[i][j], bg = tile.cget("bg"), font=("CourierNew 24 bold"), foreground="#E67E22").place(x = 30, y = 30, anchor="center")
                    elif (self.board[i][j] == 4):
                        Label(tile, text=self.board[i][j], bg = tile.cget("bg") , font=("CourierNew 24 bold"), foreground="#9B59B6").place(x = 30, y = 30, anchor="center")
                    # elif (self.board[i][j] == 5):
                        # Label(tile, text=self.board[i][j], bg = tile.cget("bg"), font=("CourierNew 24 bold"), foreground="#E74C3C").place(x = 30, y = 30, anchor="center")
                    # elif (self.board[i][j] == 6):
                        # Label(tile, text=self.board[i][j], bg = tile.cget("bg"), font=("CourierNew 24 bold"), foreground="#1ABC9C").place(x = 30, y = 30, anchor="center")
                    # elif (self.board[i][j] == 7):
                        # Label(tile, text=self.board[i][j], bg = tile.cget("bg"), font=("CourierNew 24 bold"), foreground="#2C3E50").place(x = 30, y = 30, anchor="center")
                    # elif (self.board[i][j] == 8):
                        # Label(tile, text=self.board[i][j], bg = tile.cget("bg"), font=("CourierNew 24 bold"), foreground="#7F8C8D").place(x = 30, y = 30, anchor="center")

                tile.grid(row = i, column = j)
                n = not n
            n = not n
        tile = Frame(self.tk, width = 60 * (j+1), height = 60, bg = "#95A5A6", borderwidth=0)
        tile.grid(row = i+1, column = 0, columnspan = j+1)
        Button(tile, text = "◀", bg = "#2ECC71", borderwidth=0, font=("CourierNew 24 bold"), foreground="#ECF0F1", command = self.prev).pack(side=LEFT, expand=False, fill='both', anchor="w")
        Button(tile, text = "▶", bg = "#2ECC71", borderwidth=0, font=("CourierNew 24 bold"), foreground="#ECF0F1", command = self.next).pack(side=RIGHT, expand=False, fill='both', anchor="e")
        b = Frame(tile, width = 60 * (j-0.4), height = 60, bg = "#3498DB", borderwidth=0)
        Label(b, text="Move: " + str(self.move), bg = "#3498DB", font=("CourierNew 18 bold"), foreground="#ECF0F1").place(x = (60 * (j-0.4))/2, y = 30, anchor="center")
        b.pack(expand=True, fill='both', side="left")

    def update(self):
        for child in self.tk.winfo_children():
            info = child.grid_info()
            n = (info["row"]+(info["column"] % 2)) % 2 == 0
            if (info["row"] < len(self.board) and info["column"] < len(self.board[info["row"]])):
                if (self.board[info["row"]][info["column"]] == -100):
                    if n:
                        child.config(bg = "#34495E")
                    else:
                        child.config(bg = "#2C3E50")
                    for labels in child.winfo_children():
                        labels.destroy()
                else:
                    if n:
                        child.config(bg = "#ECF0F1")
                    else:
                        child.config(bg = "#DFE4E6")
                    if (len(child.winfo_children()) == 0):
                        if (self.board[info["row"]][info["column"]] == 1):
                            Label(child, text=self.board[info["row"]][info["column"]], bg = child.cget("bg"), font=("CourierNew 24 bold"), foreground="#3498DB").place(x = 30, y = 30, anchor="center")
                        elif (self.board[info["row"]][info["column"]] == 2):
                            Label(child, text=self.board[info["row"]][info["column"]], bg = child.cget("bg"), font=("CourierNew 24 bold"), foreground="#2ECC71").place(x = 30, y = 30, anchor="center")
                        elif (self.board[info["row"]][info["column"]] == 3):
                            Label(child, text=self.board[info["row"]][info["column"]], bg = child.cget("bg"), font=("CourierNew 24 bold"), foreground="#E67E22").place(x = 30, y = 30, anchor="center")
                        elif (self.board[info["row"]][info["column"]] == 4):
                            Label(child, text=self.board[info["row"]][info["column"]], bg = child.cget("bg") , font=("CourierNew 24 bold"), foreground="#9B59B6").place(x = 30, y = 30, anchor="center")
            else:
                for subchild in child.winfo_children():
                    if subchild.winfo_class() == 'Frame':
                        subchild.winfo_children()[0].destroy()
                        Label(subchild, text="Move: " + str(self.move), bg = "#3498DB", font=("CourierNew 18 bold"), foreground="#ECF0F1").place(x = (60 * (j-0.4))/2, y = 30, anchor="center")
                        subchild.pack(expand=True, fill='both', side="left")
                
# Membuat GUI
window = Tk()
window.title("踩地雷 - Nyapu Ranjau - Mainswiper")
window.resizable(False, False)
board = Board(clicked, window)
window.mainloop()