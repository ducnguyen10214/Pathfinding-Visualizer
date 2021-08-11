import pygame, sys
from queue import PriorityQueue
import numpy as np

pygame.init()

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH + 700, WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")
gui_font = pygame.font.SysFont('Arial', 35)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (133, 2, 1)
VISIT1 = (0, 255, 230)
VISIT2 = (0, 80, 230)
VISIT3 = (1, 106, 106)
LOOK = (0, 255, 164)
START = (217, 1, 183)
END = RED
GREY = (63, 63, 63)
OPEN = (0, 255, 149)
OPEN1 = (0, 106, 0)
PATH1 = (255, 200, 0)
PATH2 = (255, 254, 0)
PATH3 = (0, 200, 0)
VISITED = []

#####################################################
# THIS IS WHERE WE BUILD NODE OBJECTS               #
#####################################################
class Node:
    def __init__(self, row, col, width, total_rows):
        self.last = pygame.time.get_ticks()
        self.cooldown = 300 
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.dec_animation = False
        self.weight = False
        
    def get_pos(self):
        return self.row, self.col
    
    def is_visited(self):
        return self.color == VISIT1
    
    def is_open(self):
        return self.color == OPEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_weight(self):
        return self.weight
    
    def is_start(self):
        return self.color == START
    
    def is_end(self):
        return self.color == END
    
    def is_neutral(self):
        return self.color == WHITE
    
    def is_looked(self):
        return self.color == LOOK
    
    def reset(self):
        self.color = WHITE
        self.weight = False
    
    def make_visited(self):
        if not self.is_weight():
            self.color = VISIT2
        else:
            self.color = VISIT3
        
    def make_open(self):
        if not self.is_weight():
            self.color = OPEN
        else:
            self.color = OPEN1

    def make_barrier(self):
        if not self.is_start() and not self.is_end():
            self.color = BLACK
            self.weight = False
            
    def make_weight(self):
        if not self.is_start() and not self.is_end():
            self.color = BROWN
            self.weight = True
    
    def make_end(self):
        self.color = END
        self.weight = False
    
    def make_start(self):
        self.color = START
        self.weight = False
        
    def make_path(self):
        if not self.is_weight():
            self.color = PATH1
        else:
            self.color = PATH3
    
    def looking_at(self):
        self.color = LOOK

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # MOVING DOWN?
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # MOVING UP?
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # MOVING RIGHT?
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # MOVING LEFT?
            self.neighbors.append(grid[self.row][self.col - 1])        

    def __lt__(self, other): # handle what happens if we compare two objects together?
        return False

######################################################
# THIS IS WHERE WE BUILD THE BUTTON OBJECTS          #
######################################################
class Button:
    def __init__(self, x, y, width, height, text, elevation):
        # Core attributes
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = y

        # Top rectangle
        self.top_rect = pygame.Rect((x, y), (width, height))
        self.top_color = '#475F77'

        # Bottom rectangle
        self.bottom_rect = pygame.Rect((x, y), (width, elevation))
        self.bottom_color = '#354B5E'

        # Text
        self.text_surf = gui_font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw(self, win):
        # Elevation Logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        pygame.draw.rect(win, self.bottom_color, self.bottom_rect, border_radius = 12)
        pygame.draw.rect(win, self.top_color, self.top_rect, border_radius = 12)
        win.blit(self.text_surf, self.text_rect)
        self.check_click()
    
    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elevation = 0
                self.pressed = True
            else:
                self.dynamic_elevation = self.elevation
                if self.pressed == True:
                    self.pressed = False
        else:
            self.dynamic_elevation = self.elevation
            self.top_color = '#475F77'
    def is_hover(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x-self.height//2 and pos[0] < self.x + self.width + self.height // 2:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

###################################################
# THIS IS WHERE WE BUILD THE INFO SCREEN          #
###################################################
class InfoScreen:
    def __init__(self, x, y, width, height, text=''):
        self.color = '#475F77'
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label1 = ""
        self.text1 = text
        self.text2 = ""
        self.text3 = ""
        
    def set_label1(self, label):
        self.label1 = label
    
    def set_text1(self, text):
        self.text1 = text
    def set_text2(self, text):
        self.text2 = text
    def set_text3(self, text):
        self.text3 = text
        
    def get_text1(self):
        return self.text1

    def draw(self, win):
        pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.height), 0)
        
        if self.label1 != '':
            label = gui_font.render(self.label1, 1, WHITE)
            win.blit(label, (self.x + 230, self.y + 10))
        
        if self.text1 != '':
            text = gui_font.render(self.text1, 1, WHITE)
            win.blit(text, (self.x + 170, self.y + 100))
        if self.text2 != '':
            text = gui_font.render(self.text2, 1, WHITE)
            win.blit(text, (self.x + 170, self.y + 150))
        if self.text3 != '':
            text = gui_font.render(self.text3, 1, WHITE)
            win.blit(text, (self.x + 170, self.y + 200))

def h(p1, p2): 
    # The heuristic Function using Manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def visit_animation1(node):
    # Visit animation for nodes in general
    if node.color == VISIT1:
        return True
    else:
        r, g, b = node.color
        b += 1
        node.color = (r, g, b)
        return False

def visit_animation(visited):
    # Visit animation for visited nodes
    for node in visited:
        if node.color == VISIT1 or node.color == VISIT3:
            visited.remove(node)
            continue
        r, g, b = node.color
        if g < 255:
            g += 1
        node.color = (r, g, b)

def path_animation(path):
    # Path animation for RGB effect when reconstructing the final path
    for node in path:
        if not node.is_start():
            r, g, b = node.color
            if node.dec_animation:
                g -= 1
                if g <= PATH1[1]:
                    node.dec_animation = False
            else:
                g += 1
                if g >= PATH2[1]:
                    node.dec_animation = True
        node.color = (r, g, b)

def reconstruct_path(came_from, start, current, draw, visited,  win, width, grid, is_draw = True):
    # When we've finished finding a path
    path = []
    c = 0  #for weight nodes 
    while current in came_from:
        visit_animation(visited)
        current = came_from[current]
        if current.is_weight():
            c+= 5
        else:
            c+=1
        if current in visited:
            visited.remove(current)
        if current != start:
            path.insert(0, current)
        current.make_path()
        if is_draw:
            for rows in grid:
                for node in rows:
                    node.draw(win)
            draw_grid(win, len(grid), width)
            pygame.display.update()
    return path, c-1

def astar(draw, grid, start, end, output, win, width):
    # Using A* Search Algorithm
    count = 0
    vis = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} #Keep track of what node came from where
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    visited = []
    nebrs = []

    open_set_hash = {start} #Check if a certain item is in the priority queue
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path, inc = reconstruct_path(came_from, start, end, draw, visited, win, width, grid)
            output.set_text1(f"Path Length: {inc}")
            output.set_text2(f"Number Of Visited Nodes: {vis}")
            if vis != 0:
                output.set_text3(f"Efficiency: {np.round(inc / vis, decimals = 3)}")

            start.make_start()
            return visited, path
        c = 1
        for neighbor in current.neighbors:
            if not neighbor.is_barrier():
                if neighbor.is_weight():
                    c = 5
            temp_g_score = g_score[current] + c
            temp_f_score = temp_g_score + h(neighbor.get_pos(), end.get_pos())
            if temp_g_score < g_score[neighbor]: #There is a shorter path --> Update
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_f_score
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                if neighbor != end:
                    nebrs.append(neighbor)
                    neighbor.make_open()
        if current != start:
            vis += c
            visited.append(current)
            current.make_visited()
        visit_animation(visited)
        for rows in grid:
            for node in rows:
                node.draw(win)
        draw_grid(win, len(grid), width)
        pygame.display.update()
    return visited, False

def dijkstra(draw, grid, start, end, output, win, width):
    # Using A* Search Algorithm
    count = 0
    vis = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} #Keep track of what node came from where
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    visited = []
    nebrs = []
    open_set_hash = {start} #Check if a certain item is in the priority queue
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path, inc = reconstruct_path(came_from, start, end, draw, visited, win, width, grid)
            output.set_text1(f"Path Length: {inc}")
            output.set_text2(f"Number Of Visited Nodes: {vis}")
            if vis != 0:
                output.set_text3(f"Efficiency: {np.round(inc / vis, decimals = 3)}")

            start.make_start()
            return visited, path
        c = 1
        for neighbor in current.neighbors:
            if not neighbor.is_barrier():
                if neighbor.is_weight():
                    c = 5
            temp_g_score = g_score[current] + c
            temp_f_score = temp_g_score
            if temp_g_score < g_score[neighbor]: #There is a shorter path --> Update
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_f_score
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                if neighbor != end:
                    nebrs.append(neighbor)
                    neighbor.make_open()
        if current != start:
            vis += c
            visited.append(current)
            current.make_visited()
        visit_animation(visited)
        for rows in grid:
            for node in rows:
                node.draw(win)
        draw_grid(win, len(grid), width)
        pygame.display.update()
    return visited, False

#######################################################
# TO GENERATE A DEPTH-FIRST SEARCH MAZE               #
#######################################################
def is_free(grid, x, y):
    count = 0
    if y+1 < len(grid) and grid[x][y+1].is_barrier() :
        count +=1
    if y-1>=0 and grid[x][y-1].is_barrier():
        count +=1
    if x+1 < len(grid) and grid[x+1][y].is_barrier():
        count+=1
    if x-1>=0 and grid[x-1][y].is_barrier():
        count+=1
    if count >= 3:
        return True
    return False

def unvisited_n(grid, x, y):
    n = []
    if y+1 < len(grid) and grid[x][y+1].is_barrier() and is_free(grid, x, y+1):
        n.append((x, y+1))
    if y-1>=0 and grid[x][y-1].is_barrier() and is_free(grid, x, y-1):
        n.append((x, y-1))
    if x+1 < len(grid) and grid[x+1][y].is_barrier() and is_free(grid, x+1, y):
        n.append((x+1, y))
    if x-1>=0 and grid[x-1][y].is_barrier() and is_free(grid, x-1, y):
        n.append((x-1, y))
    return n

def make_black(grid, win):
    for row in grid:
        for node in row:
            node.make_barrier()
            node.draw(win)
    pygame.display.update()

def dfs_maze(draw, width, grid, start, end, left, right, top, bottom, win, vertical=True):
    make_black(grid, win)
    x, y = 1, 1
    head = grid[x][y]
    head.looking_at()
    stack = [(x, y)]
    while True:
        neighbors = unvisited_n(grid, x, y)
        if len(neighbors) > 0:
            random_index = np.random.randint(len(neighbors))
            x, y = neighbors[random_index]
            head = grid[x][y]
            head.looking_at()
            stack.append((x, y))
            head.draw(win)
            draw_grid(win, len(grid), width)
            pygame.display.update()
        else:
            if len(stack) > 0:
                x, y = stack.pop()
                grid[x][y].reset()
                grid[x][y].draw(win)
                draw_grid(win, len(grid), width)
                pygame.display.update()
            if len(stack) > 0:
                x, y = stack[-1]
            else:
                break

######################################################
# TO DRAW GRID, GRIDLINES AND EVERYTHING ELSE        #
######################################################
def make_grid(rows, width):
    # Make the overall grid
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return np.array(grid)

def draw_grid(win, rows, width):
    # Draw grid
    gap = width // rows
    for i in range(rows+1):
        pygame.draw.line(win, GREY, (0, i * gap), (rows * gap, i * gap))
    for i in range(rows+1):
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, rows * gap))

def draw(win, grid, rows, width, algorithms, options, output, menu = True):
    # Draw everything (interface + buttons)
    win.fill(BLACK)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    if menu:
        n = 17
        delta = 700
        ht = 900
        width = ht
        w = 1600
        text = gui_font.render("Algorithms", 1, WHITE)
        top = 0
        end = ht // 10
        win.blit(text, (width+delta // 5 + 25, (end-top) / 2))
        for algorithm in algorithms:
            algorithm.draw(win)
        end += 200
        top += 200
        text = gui_font.render("Options", 1, WHITE)
        win.blit(text, (width+delta // 6 + 70, ((end-top) / 2) + top))
        for option in options:
            option.draw(win)
        output.draw(WIN)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    # User interactions with the grid
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def main(win, width):
    ROWS = 50
    w, ht = pygame.display.get_surface().get_size()
    width = ht
    grid = make_grid(ROWS, width)
    delta = w - width - 10

    top_start = ht / 2 - 300
    button_height = ht // 15
    button_width = delta // 4
    algorithms = [
        Button(width + delta / 4 + 10, top_start, button_width - button_height + 210, button_height, "A*", 6),
        Button(width + delta / 4 + 10, top_start + 80, button_width - button_height + 210, button_height, "Dijkstra", 6)
    ]
    top_start = top_start + 500
    options = [
        Button(width + delta / 4 + 10, top_start - 300, button_width - button_height + 50, button_height, "Clear", 6),
        Button(width + delta // 5 + 300, top_start - 300, 70, button_height, "-", 6),
        Button(width + delta // 5 + 230, top_start - 300, 70, button_height, "+", 6),
        Button(width + delta / 4 + 10, top_start - 220, 330, button_height, "Generate DFS Maze", 6)
    ] #Options
    output = InfoScreen(width + delta // 8 - 70, ht - 320, 660, 300, "Choose an Algorithm")
    output.set_label1(f"Grid: {ROWS} x {ROWS}")
    output.set_text1("1. Pick starting node")
    output.set_text2("2. Pick ending node")
    output.set_text3("3. Choose an algorithm")
    start = None
    end = None

    run = True
    started = False
    visited = []
    weighted = []
    path = False

    while run:
        if len(visited):
            visit_animation(visited)
        if path:
            path_animation(path)

        draw(win, grid, ROWS, width, algorithms, options, output)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]: # LEFT MOUSE 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row >= 0 and row < ROWS and col < ROWS and col >= 0:
                    node = grid[row][col]
                    if node in visited:
                        visited.remove(node)
                    if node in weighted:
                        weighted.remove(node)
                    if path:
                        if node in path:
                            path.remove(node)
                    if not start and node != end:
                        if node in visited:
                            visited.remove(node)
                        start = node
                        start.make_start()
                    elif not end and node != start:
                        end = node
                        end.make_end()
                    elif node != end and node != start:
                        node.make_barrier()
                elif algorithms[0].is_hover(pos):
                    output.draw(win)
                    if len(weighted):
                        for node in weighted:
                            node.make_weight()
                    if start and end:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                                if not node.is_neutral() and node != start and node != end and not node.is_barrier() and not node.is_weight():
                                    node.reset()
                        visited = []
                        path = []
                        output.set_text1("Finding...")
                        output.set_text2("")
                        output.set_text3("")
                        output.draw(win)
                        pygame.display.update()
                        visited, path = astar(lambda: draw(win, grid, ROWS, width, algorithms, options, output), grid, start, end, output, win, width)
                        if not path:
                            output.set_text1("Path not available") 
                elif algorithms[1].is_hover(pos):
                    output.draw(win)
                    if len(weighted):
                        for node in weighted:
                            node.make_weight()
                    if start and end:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                                if not node.is_neutral() and node != start and node != end and not node.is_barrier() and not node.is_weight():
                                    node.reset()
                        visited = []
                        path = []
                        output.set_text1("Finding...")
                        output.set_text2("")
                        output.set_text3("")
                        output.draw(win)
                        pygame.display.update()
                        visited, path = dijkstra(lambda: draw(win, grid, ROWS, width, algorithms, options, output), grid, start, end, output, win, width)
                        if not path:
                            output.set_text1("Path not available") 
                elif options[0].is_hover(pos):
                    output.set_text1("1. Pick starting node")
                    output.set_text2("2. Pick ending node")
                    output.set_text3("3. Choose an algorithm")
                    output.draw(win)
                    pygame.display.update()
                    weighted = []
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
                            node.reset()
                elif options[1].is_hover(pos):
                    weighted = []
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
                            node.reset()
                    if ROWS > 5:
                        ROWS -= 1
                        grid = make_grid(ROWS, width)
                    output.set_label1(f"Grid: {ROWS} x {ROWS}")
                elif options[2].is_hover(pos):
                    weighted = []
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
                            node.reset()
                    if ROWS < 100:
                        ROWS += 1
                        grid = make_grid(ROWS, width)
                    output.set_label1(f"Grid: {ROWS} x {ROWS}")
                elif options[3].is_hover(pos):
                    output.set_text1("Generating...")
                    output.set_text2("")
                    output.set_text3("")
                    output.draw(win)
                    pygame.display.update()
                    start = None
                    end = None
                    visited = []
                    path = []
                    weighted = []
                    for row in grid:
                        for node in row:
                            if node.is_barrier() or node.is_start() or node.is_end():
                                node.reset()
                    dfs_maze(lambda: draw(win, grid, ROWS, width, algorithms, options, output), width, grid, start, end, 0, ROWS, 0, ROWS, win)
                    output.set_text1("1. Pick starting node")
                    output.set_text2("2. Pick ending node")
                    output.set_text3("3. Choose an algorithm")
    pygame.quit()
    sys.exit()

main(WIN, WIDTH)