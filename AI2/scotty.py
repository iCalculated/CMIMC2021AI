import sys
import copy
import json
import random
import math

from collections import namedtuple, defaultdict
import operator

Point = namedtuple('Point','x y')
Point.__add__ = lambda a, b: Point(a[0] + b[0], a[1] + b[1])
Point.__sub__ = lambda a, b: Point(a[0] - b[0], a[1] - b[1])

class scotty_bot:
  def __init__(self):
    self.pathing = dijkstra()

  def find_scotty(self, board):
      # Helper function that finds Scotty's location on the board
      for y in range(15):
          for x in range(15):
              if board[y][x] == 1:
                  return (x, y)
  
  def move(self, board):
    x,y = self.find_scotty(board)
    self.pos = Point(x,y)
    self.pathing.board = board
    self.pathing.heatmap = self.pathing.generate_backmap()
    if x == 0:
      return [-1,0]
    elif x == 14: 
      return [1,0]
    elif y == 0:
      return [0,-1]
    elif y == 14:
      return [0,1]
    self.pathing.generate_node_rank()
    self.pathing.pretty_node_rank()
    steps = self.pathing.find_ultimate_path(self.pos)
    if len(steps) == 0:
      obj = Point(*random.choice(self.pathing.neighbors((x,y))))
      return (obj-self.pos)
    #print(steps)
    return steps[0]


class trapper_bot:
    def __init__(self):
        self.pathing = dijkstra()
        self.escape = None


    def find_scotty(self, board):
        # Helper function that finds Scotty's location on the board
        for y in range(15):
            for x in range(15):
                if board[y][x] == 1:
                    return Point(x, y)

    def move(self, board):
        self.pos = self.find_scotty(board)
        self.pathing.board = copy.deepcopy(board)
        self.pathing.heatmap = self.pathing.generate_backmap()
        self.pathing.generate_node_rank()
        #self.pathing.generate_tree(self.pos)
        steps = self.pathing.find_path(self.pos)
        if len(steps) == 0:
          return self.pathing.neighbors(self.pos)[0]
        end_delta = sum(steps,Point(0,0))
        #print(f"target: {self.pos + end_delta}")
        
        s = len(steps)
        next_n = self.pos + steps[0]

        self.pathing.board[next_n.y][next_n.x] = 2
        self.pathing.heatmap = self.pathing.generate_backmap()

        one_block = self.pathing.find_path(self.pos)
        newt = len(one_block)
        if newt - s > 1 or newt == 0:
            return next_n

        self.pathing.board[next_n.y][next_n.x] = 0

        self.escape = self.pos + end_delta

        if len(steps) == 1:
            return self.escape
        else:
            self.pathing.board[self.escape.y][self.escape.x] = 2
            self.pathing.heatmap = self.pathing.generate_backmap()
            steps = self.pathing.find_path(self.pos)
            if len(steps) == 0:
                return self.escape
            end_delta = sum(steps,Point(0,0))
            self.pathing.board[self.escape.y][self.escape.x] = 2
            #print(f"current: {self.pos + end_delta}")
            return self.pos + end_delta

class dijkstra:
    def __init__(self):
        self.board = None
        self.width = 15
        self.height = 15
        self.obstacles = [2,3]
        self.x = 7
        self.y = 7
        self.MAX = math.inf
        self.heatmap = None
        self.t = None
        self.node_rank = defaultdict(int)

    def valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and self.board[y][x] not in self.obstacles

    def neighbors(self, point):
        x,y = point

        list_neighbors = [(i, y + 1) for i in [x - 1, x, x + 1] if self.valid(i, y + 1)] \
        + [(j, y) for j in [x - 1, x + 1] if self.valid(j, y)] \
        + [(k, y - 1) for k in [x - 1, x, x + 1] if self.valid(k, y-1)]

        return list_neighbors

    def pretty_heatmap(self):
      for row in self.heatmap[::-1]:
        for el in row:
          if not el == math.inf: 
            print(f"{el:3}",end="")
          else:
            print(f"  X",end="")
        print()

    def pretty_node_rank(self):
        for i in range(14,-1,-1):
            for j in range(0,15):
                if self.valid(j,i):
                    print(f"{self.node_rank[(j,i)]:3}", end="")
                else:
                    print(f"  X",end="")
            print()

    def barriers(self):
      for row in self.board:
        for el in row:
          if not el == 2:
            print(f"   ",end="")
          else:
            print(f"  X",end="")
        print()
    
    def generate_heatmap(self, start):
      heatmap = [[self.MAX] * 15 for _ in range(15)] 
      #q = [(i, j) for i in range(15) for j in range(15) if ((self.board[i][j] != 2) and ((i == 0 or i == 14) or (j == 0 or j == 14)))]
      q =  [start]
      step = 0 
      while q: 
        new_q = [] 
        for point in q: 
          new_q += [p for p in self.neighbors(point) if heatmap[p[1]][p[0]] == math.inf] 
          if heatmap[point[1]][point[0]] > step:
              heatmap[point[1]][point[0]] = step 
        step += 1 
        q = list(set(new_q))
      return heatmap

    def generate_backmap(self):
      heatmap = [[self.MAX] * 15 for _ in range(15)] 
      q = [(i, j) for i in range(15) for j in range(15) if ((self.board[j][i] not in self.obstacles) and ((i == 0 or i == 14) or (j == 0 or j == 14)))]
      step = 0 
      while q: 
        new_q = [] 
        for point in q: 
          if heatmap[point[1]][point[0]] > step:
              heatmap[point[1]][point[0]] = step 
          for p in self.neighbors(point):
            if heatmap[p[1]][p[0]] > step:
              new_q += [p]  
        step += 1 
        q = list(set(new_q))
      return heatmap

    def generate_tree(self, start):
      def dist(point): return self.heatmap[point[1]][point[0]]

      current_node = start
      self.t = tree(start, None)
      q = [self.t]
      while q:
        new_q = []
        for tree_node in q:
          #print(tree_node)
          for node in self.neighbors(tree_node.pos):
            if dist(node) < dist(self.t.pos):
              new_tree = tree(node, tree_node)
              tree_node.add_child(new_tree)
              new_q.append(new_tree)
        q = list(set(new_q))
    

    def generate_node_rank(self):
        def dist(point): return self.heatmap[point[1]][point[0]]
        for i in range(0,15):
            for j in range(0,15):
                if self.valid(i,j):
                    d = dist((i,j))
                    self.node_rank[Point(i,j)]= len(list(filter(lambda x: dist(x) < d, self.neighbors((i,j)))))

    def find_path(self, start):
      def find_dir(start,end): return [end[0] - start[0], end[1] - start[1]]
      def dist(point): return self.heatmap[point[1]][point[0]]

      steps = []
      current_node = start
      while True:
        inst = None
        dist_traveled = dist(current_node)
        next_nodes = self.neighbors(current_node)
        next_node = None
        good_choices = list(filter(lambda x: dist(x) < dist_traveled, next_nodes))
        for node in good_choices:
            max_rank = -1
            if self.node_rank[node] > max_rank:
                max_rank = self.node_rank[node]
                next_node = node
            inst = find_dir(current_node, next_node)
        if next_node == None:
          break
        steps.append(Point(*inst))
        current_node = next_node
      return steps
      
    def find_ultimate_path(self, start):
      def dist(point): return self.heatmap[point[1]][point[0]]
      def find_dir(start,end): return [end[0] - start[0], end[1] - start[1]]
      dist_traveled = dist(start)
      good_choices = list(filter(lambda x: dist(x) < dist_traveled, self.neighbors(start)))
      super_set = []
      for node in good_choices:
        steps = []
        steps.append(Point(*find_dir(start,node)))
        steps += self.find_path(node)

        evaluation = 0
        curr = start
        scalar = 1
        for step in steps:
          curr += step
          evaluation += scalar * self.node_rank[curr]
          scalar *= 1.2
        super_set.append((steps, evaluation))
      if super_set == []:
        return []
      return max(super_set, key=lambda x: x[1])[0]

# =============================================================================

# Local testing parameters

# If you would like to view a turn by turn game display while testing locally,
# set this parameter to True


LOCAL_VIEW = True

# Sample board your game will be run on (flipped vertically)
# This file will display 0 as ' ', 1 as '*', 2 as 'X', and 3 as 'O'
      
SAMPLE_BOARD = [[0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0],
            [0, 2, 0, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0], [0, 2, 0, 0, 0, 2, 2, 0, 0, 2, 0, 0, 2, 0, 0], [0, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 0, 2, 2, 0], [2, 2, 0, 2, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 0],
                [0, 0, 0, 0, 0, 2, 2, 1, 2, 0, 0, 0, 0, 2, 2], [2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 0, 2], [0, 0, 0, 0, 0, 0, 2, 2, 0, 2, 2, 0, 2, 0, 0], [2, 0, 0, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0],
                    [0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2], [2, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0], [2, 0, 2, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 2], [0, 0, 0, 2, 0, 0, 2, 0, 2, 2, 0, 0, 0, 0, 2]] 
# =============================================================================


# You don't need to change any code below this point


def WAIT():
    return json.loads(input())


def SEND(data):
    print(json.dumps(data), flush=True)


def dispboard_for_tester(board):
    print()
    print('\n'.join(''.join(map(lambda x: ' *XO'[x], i))for i in reversed(board)))
    print()


def find_scotty_for_tester(board):
    for y in range(15):
        for x in range(15):
            if board[y][x] == 1:
                return (x, y)


def trapped_for_tester(board):
    pos = find_scotty_for_tester(board)
    moves = [*zip([0, 1, 1,1,0,-1,-1,-1],[1,1,0,-1,-1,-1,0,1])]
    trap = True
    for i in moves:
        if 0 <= pos[0] + i[0] < 15 and 0 <= pos[1] + i[1] < 15:
            if board[pos[1] + i[1]][pos[0] + i[0]] == 0:
                trap = False
                break
        else:
            trap = False
            break
    return trap


def PLAY(scotty, trapper, board):
    result = -1
    while True:
        try:
            val = trapper.move(board)
            if not (val[0] == int(val[0]) and 0 <= val[0] < 15
                    and val[1] == int(val[1]) and 0 <= val[1] < 15
                    and board[val[1]][val[0]] == 0):
                raise Exception('invalid move')
            board[val[1]][val[0]] = 3
        except Exception as e:
            print(f'Your trapper has an error: {e}! Doing nothing instead.')
            val = -1
        if trapped_for_tester(board):
            result = 1
            break
        if LOCAL_VIEW:
            dispboard_for_tester(board)
            input("Enter to continue (change LOCAL_VIEW to toggle this)")
        try:
            val = scotty.move(board)
            if not (val[0] == int(val[0]) and -1 <= val[0] <= 1
                    and val[1] == int(val[1]) and -1 <= val[1] <= 1):
                raise Exception('invalid move')
        except Exception as e:
            print(f'Your Scotty has an error: {e}! Doing nothing instead.')
            val = (0, 0)
        pos = find_scotty_for_tester(board)
        if 0 <= pos[0] + val[0] < 15 and 0 <= pos[1] + val[1] < 15:
            if board[pos[1] + val[1]][pos[0] + val[0]] == 0:
                board[pos[1] + val[1]][pos[0] + val[0]] = 1
                board[pos[1]][pos[0]] = 0
        else:
            board[pos[1]][pos[0]] = 0
            result = 0
            break
        if LOCAL_VIEW:
            dispboard_for_tester(board)
            input("Enter to continue (change LOCAL_VIEW to toggle this)")
    print(["Scotty", "Trapper"][result], "won!")
    if not LOCAL_VIEW:
        print("Change LOCAL_VIEW to True to see a turn by turn replay")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != 'REAL':
        PLAY(scotty_bot(), trapper_bot(), SAMPLE_BOARD)
        input()

    else:
        scotty = scotty_bot()
        trapper = trapper_bot()
        while True:
            data = WAIT()
            board = data["board"]
            role = data["role"]
            if role == "trapper":
                SEND(trapper.move(board))
            else:
                SEND(scotty.move(board))
