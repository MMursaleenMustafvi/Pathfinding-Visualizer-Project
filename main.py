import pygame
import sys
import heapq
from collections import deque

GRID_SIZE = 10
CELL_SIZE = 50
WIDTH, HEIGHT = 1000, 950 

LIGHT_BG=(245,246,250)
LIGHT_GRID=(255,255,255)
LIGHT_TEXT=(40,40,40)

DARK_BG=(25,27,32)
DARK_GRID=(45,48,56)
DARK_TEXT=(240,240,240)

CLR_START=(46,204,113)     
CLR_GOAL=(155,89,182)      
CLR_WALL=(231,76,60)       
CLR_PATH=(255,214,0)       
CLR_EXPLORE=(52,152,219)   
CLR_BTN=(52,73,94)
CLR_BTN_ALT=(44, 62, 80)   
CLR_EXIT=(192, 57, 43)     # Distinct red for exit

class PathfinderApp:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE)
        pygame.display.set_caption("SEARCHING ALGORITHM SHORT ROUTE FINDER POWERED BY M.Mursaleen Mustafvi")
        self.font=pygame.font.SysFont("Arial",16,bold=True)
        self.font_title=pygame.font.SysFont("Arial",30,bold=True)
        self.font_name=pygame.font.SysFont("Arial",14,italic=True)
        self.clock=pygame.time.Clock()

        self.dark=False
        self.speed=40
        self.fullscreen=False
        self.reset_all()

    def reset_all(self):
        self.start=None
        self.target=None
        self.walls=set()
        self.path=[]
        self.explored=set()
        self.frontier=set()
        self.mode="START"
        self.visit_order={}
        self.counter=1

    def colors(self):
        if self.dark:
            return DARK_BG,DARK_GRID,DARK_TEXT
        return LIGHT_BG,LIGHT_GRID,LIGHT_TEXT

    def get_neighbors(self,r,c):
        directions=[(-1,0),(0,1),(1,0),(1,1),(0,-1),(-1,-1)]
        res=[]
        for dr,dc in directions:
            nr,nc=r+dr,c+dc
            if 0<=nr<GRID_SIZE and 0<=nc<GRID_SIZE and (nr,nc) not in self.walls:
                res.append((nr,nc))
        return res

    def draw(self):
        BG,GRID,TEXT=self.colors()
        win_w, win_h = self.screen.get_size()
        ox=(win_w-(GRID_SIZE*CELL_SIZE))//2
        
        slider_y = 200
        oy = 280 

        self.screen.fill(BG)

        title=self.font_title.render("PATHFINDING VISUALIZER",True,TEXT)
        self.screen.blit(title,(win_w//2-title.get_width()//2,20))
        
        # Credit Name
        name_tag=self.font_name.render("Created by: M.Mursaleen Mustafvi",True,TEXT)
        self.screen.blit(name_tag,(win_w//2-name_tag.get_width()//2,60))

        self.btn_rects=[]
        
        # Row 1: Algorithm Buttons
        algo_names=["BFS","DFS","UCS","DLS","IDDFS","Bidirectional"]
        for i,name in enumerate(algo_names):
            rect=pygame.Rect(win_w//2-420+(i*140),90,130,40)
            pygame.draw.rect(self.screen,CLR_BTN,rect,border_radius=8)
            self.btn_rects.append((rect,name))
            label=self.font.render(name,True,(255,255,255))
            self.screen.blit(label,(rect.centerx-label.get_width()//2,rect.centery-label.get_height()//2))

        # Row 2: Utility Buttons (Added Exit)
        util_names = ["Reset (R)", "Dark Mode (D)", "Full Screen (F)", "Exit (X)"]
        for i, name in enumerate(util_names):
            color = CLR_EXIT if "Exit" in name else CLR_BTN_ALT
            rect = pygame.Rect(win_w//2-290+(i*150), 140, 140, 40)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            self.btn_rects.append((rect, name))
            label = self.font.render(name, True, (255,255,255))
            self.screen.blit(label, (rect.centerx-label.get_width()//2, rect.centery-label.get_height()//2))

        # Speed Slider
        pygame.draw.rect(self.screen,(180,180,180),(win_w//2-150,slider_y,300,6))
        knob_x=win_w//2-150+self.speed*3
        pygame.draw.circle(self.screen,(255,80,80),(knob_x,slider_y + 3),8)
        spd_txt=self.font.render(f"Speed: {self.speed}",True,TEXT)
        self.screen.blit(spd_txt,(win_w//2-40,slider_y + 20))

        # Grid Drawing
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect=pygame.Rect(ox+c*CELL_SIZE,oy+r*CELL_SIZE,CELL_SIZE,CELL_SIZE)
                color=GRID
                if (r,c)==self.start: color=CLR_START
                elif (r,c)==self.target: color=CLR_GOAL
                elif (r,c) in self.walls: color=CLR_WALL
                elif (r,c) in self.path: color=CLR_PATH
                elif (r,c) in self.explored: color=CLR_EXPLORE

                pygame.draw.rect(self.screen,color,rect,border_radius=6)
                pygame.draw.rect(self.screen,(120,120,120),rect,1,border_radius=6)

                if (r,c)==self.start:
                    t=self.font.render("S",True,(0,0,0))
                    self.screen.blit(t,(rect.centerx-6,rect.centery-8))
                elif (r,c)==self.target:
                    t=self.font.render("G",True,(0,0,0))
                    self.screen.blit(t,(rect.centerx-6,rect.centery-8))
                elif (r,c) in self.walls:
                    t=self.font.render("-1",True,(0,0,0))
                    self.screen.blit(t,(rect.centerx-12,rect.centery-8))
                if (r,c) in self.visit_order:
                    txt=self.font.render(str(self.visit_order[(r,c)]),True,(0,0,0))
                    self.screen.blit(txt,(rect.x+3,rect.y+3))

        pygame.display.flip()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    def animate(self,frontier,explored):
        self.frontier=set(frontier)
        for node in explored:
            if node not in self.visit_order:
                self.visit_order[node]=self.counter
                self.counter+=1
        self.explored=explored
        self.draw()
        pygame.time.delay(max(1,120-self.speed))

    def reconstruct(self,parent):
        curr=self.target
        self.path=[]
        while curr:
            self.path.append(curr)
            curr=parent.get(curr)
        self.path=self.path[::-1]

    def run_bfs(self):
        q=deque([self.start]); parent={self.start:None}; explored=set()
        while q:
            curr=q.popleft()
            if curr==self.target: self.reconstruct(parent); return
            for n in self.get_neighbors(*curr):
                if n not in parent: parent[n]=curr; q.append(n)
            explored.add(curr); self.animate(q,explored)

    def run_dfs(self):
        stack=[self.start]; parent={self.start:None}; explored=set()
        while stack:
            curr=stack.pop()
            if curr==self.target: self.reconstruct(parent); return
            if curr not in explored:
                explored.add(curr)
                for n in self.get_neighbors(*curr):
                    if n not in explored: parent[n]=curr; stack.append(n)
            self.animate(stack,explored)

    def run_ucs(self):
        pq=[(0,self.start)]; parent={self.start:None}; cost={self.start:0}; explored=set()
        while pq:
            c,curr=heapq.heappop(pq)
            if curr==self.target: self.reconstruct(parent); return
            explored.add(curr)
            for n in self.get_neighbors(*curr):
                new=c+1
                if n not in cost or new<cost[n]: cost[n]=new; parent[n]=curr; heapq.heappush(pq,(new,n))
            self.animate([i[1] for i in pq],explored)

    def run_dls(self,limit=40):
        parent={self.start:None}; explored=set(); found=False
        def rec(node,depth):
            nonlocal found
            explored.add(node); self.animate([],explored)
            if node==self.target: found=True; return True
            if depth==0: return False
            for n in self.get_neighbors(*node):
                if n not in explored:
                    parent[n]=node
                    if rec(n,depth-1): return True
            return False
        rec(self.start,limit)
        if found: self.reconstruct(parent)

    def run_iddfs(self):
        for depth in range(1,GRID_SIZE*GRID_SIZE):
            parent={self.start:None}; explored=set()
            def rec(node,d):
                explored.add(node); self.animate([],explored)
                if node==self.target: return True
                if d==0: return False
                for n in self.get_neighbors(*node):
                    if n not in explored:
                        parent[n]=node
                        if rec(n,d-1): return True
                return False
            if rec(self.start,depth): self.reconstruct(parent); return

    def run_bidirectional(self):
        f_q, b_q = deque([self.start]), deque([self.target])
        f_parent, b_parent = {self.start:None}, {self.target:None}
        f_vis, b_vis = {self.start}, {self.target}
        while f_q and b_q:
            curr=f_q.popleft()
            for n in self.get_neighbors(*curr):
                if n not in f_vis: f_parent[n]=curr; f_q.append(n); f_vis.add(n)
                if n in b_vis: self.build_path(f_parent,b_parent,n); return
            curr=b_q.popleft()
            for n in self.get_neighbors(*curr):
                if n not in b_vis: b_parent[n]=curr; b_q.append(n); b_vis.add(n)
                if n in f_vis: self.build_path(f_parent,b_parent,n); return
            self.animate(list(f_q)+list(b_q),f_vis.union(b_vis))
        
    def build_path(self,f_parent,b_parent,meet):
        path=[]
        curr=meet
        while curr: path.append(curr); curr=f_parent.get(curr)
        path=path[::-1]
        curr=b_parent.get(meet)
        while curr: path.append(curr); curr=b_parent.get(curr)
        self.path=path

    def main_loop(self):
        while True:
            self.draw()
            win_w, _ = self.screen.get_size()
            ox=(win_w-(GRID_SIZE*CELL_SIZE))//2
            oy=280 

            for event in pygame.event.get():
                if event.type==pygame.QUIT: pygame.quit(); sys.exit()
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_r: self.reset_all()
                    if event.key==pygame.K_d: self.dark=not self.dark
                    if event.key==pygame.K_f: self.toggle_fullscreen()
                    if event.key==pygame.K_x: pygame.quit(); sys.exit()

                if pygame.mouse.get_pressed()[0]:
                    mx,my=pygame.mouse.get_pos()
                    if 195<my<215 and win_w//2-150<mx<win_w//2+150:
                        self.speed=(mx-(win_w//2-150))//3

                    for rect,name in self.btn_rects:
                        if rect.collidepoint(mx,my):
                            if name=="Reset (R)": self.reset_all()
                            elif name=="Dark Mode (D)": self.dark = not self.dark
                            elif name=="Full Screen (F)": self.toggle_fullscreen()
                            elif name=="Exit (X)": pygame.quit(); sys.exit()
                            elif self.mode=="WALLS":
                                if name=="BFS": self.run_bfs()
                                elif name=="DFS": self.run_dfs()
                                elif name=="UCS": self.run_ucs()
                                elif name=="DLS": self.run_dls()
                                elif name=="IDDFS": self.run_iddfs()
                                elif name=="Bidirectional": self.run_bidirectional()

                    c,r=(mx-ox)//CELL_SIZE,(my-oy)//CELL_SIZE
                    if 0<=r<GRID_SIZE and 0<=c<GRID_SIZE:
                        if self.mode=="START": self.start=(r,c); self.mode="TARGET"
                        elif self.mode=="TARGET" and (r,c)!=self.start: self.target=(r,c); self.mode="WALLS"
                        elif self.mode=="WALLS" and (r,c) not in [self.start,self.target]: self.walls.add((r,c))
                    
if __name__=="__main__":
    PathfinderApp().main_loop()