class screen():
    def __init__(self, x,y,width,height, text=''):
        self.color = WHITE
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

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.label1 != '':
            font = pygame.font.SysFont('comicsans', 20)
            label = font.render(self.label1, 1, (0,0,0))
            win.blit(label, (self.x + 10, self.y + 10))
        
        if self.text1 != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text1, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2) - 50))
        if self.text2 != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text2, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))
        if self.text3 != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text3, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), 50 + self.y + (self.height/2 - text.get_height()/2)))

    def is_hover(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False
    
def h(p1, p2): # The heuristic Function using Manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def visit_animation2(node):
    if node.color == VISIT1:
        return True
    else:
        r, g, b = node.color
        b += 1
        node.color = (r, g, b)
        return False

def visit_animation(visited):
    for node in visited:
        if node.color == VISIT1 or node.color == VISIT3:
            visited.remove(node)
            continue
        r, g, b = node.color
        if g < 255:
            g += 1
        node.color = (r, g, b)

def path_animation(path):
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
    path = []
    c = 0
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
        
def algorithm(draw, grid, start, end, output, win, width):
    count = 0
    vis = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} # Keep track of what node came from where
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    visited = []
    nebrs = []

    open_set_hash = {start} # Check if a certain item is in the priority queue
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path, inc = reconstruct_path(came_from, start, end, draw, visited, win, width, grid)
            start.make_start()
            output.set_text1(f"Path Length: {inc}")
            output.set_text2(f"#Visited nodes: {vis}")
            if vis != 0:
                output.set_text3(f"Efficiency: {np.round(inc/vis, decimals=3)}")
            return visited, path

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]: # There is a shorter path --> Update
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                if neighbor != end:
                    nebrs.append(neighbor)
                    neighbor.make_open()
        if current != start:
            visited.append(current)
            current.make_visited()
        visit_animation(visited)
        for rows in grid:
            for node in rows:
                node.draw(win)
        draw_grid(win, len(grid), width)
        pygame.display.update()
    return visited, False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return np.array(grid)

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows+1):
        pygame.draw.line(win, GREY, (0, i * gap), (rows * gap, i * gap))
    for i in range(rows+1):
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, rows * gap))
        
def draw(win, grid, rows, width, algorithms, mazes, options, output, menu = True):
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
        font = pygame.font.SysFont('comicsans', 35)
        text = font.render("Algorithms", 1, WHITE)
        top = 0
        end = ht//13
        win.blit(text, (width+delta//6, (end-top)/2.5))
        for algorithm in algorithms:
            algorithm.draw(win, BLACK)
        
        text = font.render("Mazes", 1, WHITE)
        but_height = ht//15
        top += (4*but_height)
        end += (1.9*(3*but_height//2)) + but_height + ht//12
        win.blit(text, (width+delta//6, ((end-top)/2) + top))
        for maze in mazes:
            maze.draw(win, BLACK)
            
        end += (1.3*(3*but_height//2)) + ht//6
        top += (5*but_height//2)
        
        text = font.render("Options", 1, WHITE)
        win.blit(text, (width+delta//6, ((end-top)/2) + top))
        for option in options:
            option.draw(win, BLACK)
        output.draw(win, BLACK)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
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

    top_start = ht/13
    but_height = ht//15
    but_width = delta//4
    algorithms = [
        Button(width+delta//5, top_start, but_width-but_height, but_height, "A*"),
        Button(width+delta//5+(5*but_width//4), top_start, but_width-but_height, but_height, 'IDA*'),
        Button(width+delta//5, top_start+(3*but_height//2), but_width-but_height, but_height, 'Modified A*'),
        Button(width+delta//5+(5*but_width//4), top_start+(3*but_height//2), but_width-but_height, but_height, 'DFA*'),
        Button(width+delta//5+((5*(but_width-80)//4)//2)-20, top_start+(3*but_height), but_width+delta//8-but_height+60, but_height, 'Modified Bidirectional A*'),
    ]
    top_start = top_start + (1.9*(3*but_height//2)) + but_height + ht//12
    but_height = ht//15
    but_width = delta//4+ delta//10
    mazes = [
        Button(width+delta//5, top_start, but_width-delta//8-but_height, but_height, "DFS"),
        Button(width+delta//5+(5*(but_width-80)//4), top_start, but_width-but_height, but_height, 'Recursive Division'),
        Button(width+delta//5+(5*(but_width-150)//4)//2, top_start+(3*but_height//2), but_width+delta//8-but_height, but_height, 'Modified Sidewinder'),
    ]
    top_start = top_start + (1.3*(3*but_height//2)) + ht//10
    but_height = ht//15
    but_width =  delta//10
    options = [
        Button(width+delta//5, top_start, but_width-but_height+20, but_height, "Clear"),
        Button(width+delta//5-20 + delta//5 + (4*(but_width+50)//3), top_start, 0, but_height, "-"),
        Button(width+delta//5 + delta//5 + (4*(but_width+50)//3)+(4*(but_width-30)//3), top_start,0, but_height, "+"),
    ]
    sc_start = ht-240
    sc_height = 230
    sc_width = delta-delta//4
    output = screen(width+delta//8, sc_start, sc_width, sc_height, "Choose an Algorithm")
    output.set_label1(f"Number of rows: {ROWS}")
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

        draw(win, grid, ROWS, width, algorithms, mazes, options, output)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]: # LEFT MOUSE 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if row>= 0 and row<ROWS and col < ROWS and col >= 0:
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
                    output.draw(win, (0, 0, 0))
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
                        output.set_text1("......")
                        output.set_text2("")
                        output.set_text3("")
                        output.draw(win, BLACK)
                        pygame.display.update()
                        visited, path = algorithm(lambda: draw(win, grid, ROWS, width, algorithms, mazes, options, output), grid, start, end, output, win, width)
                        if not path:
                            output.set_text1("Path not available")    
                elif options[0].is_hover(pos):
                    output.set_text1("1. Pick starting node")
                    output.set_text2("2. Pick ending node")
                    output.set_text3("3. Choose an algorithm")
                    output.draw(win, BLACK)
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
                    if ROWS>5:
                        ROWS-=1
                        grid = make_grid(ROWS, width)
                    output.set_label1(f"Number of rows: {ROWS}")
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
                    if ROWS<100:
                        ROWS+=1
                        grid = make_grid(ROWS, width)
                    output.set_label1(f"Number of rows: {ROWS}")
   
            
    pygame.quit()
main(WIN, WIDTH)