# Scotty Dog Starter File

# NOTE: You can run this file locally to test if your program is working.

# =============================================================================

# INPUT FORMAT: board

# board: A 15 x 15 2D array, where each element is:
#   0 - an empty square
#   1 - the current position of Scotty
#   2 - a naturally generated barrier
#   3 - a player placed barrier

# Example Input:

# board: See "SAMPLE_BOARD" below.

# =============================================================================

# OUTPUT FORMAT when scotty_bot is called:

# A list of two integers [dx, dy], designating in which
# direction you would like to move. Your output must satisfy

# -1 <= dx, dy <= 1

# and one of the following, where board[y][x] is Scotty's current position:

# 15(x + dx, y + dy) >= 15 OR min(x + dx, y + dy) < 0 (move off the board)
# OR
# board[y + dy][x + dx] < 2 (move to an empty square or stay still)

# Invalid outputs will result in Scotty not moving.

# =============================================================================

# OUTPUT FORMAT when trapper_bot is called:

# A list of two integers [x, y], designating where you would
# like to place a barrier. The square must be currently empty, i.e.
# board[y][x] = 0

# Invalid outputs will result in no barrier being placed.

# WARNING: COMMENT OUT YOUR DEBUG/PRINT STATEMENTS BEFORE SUBMITTING !!!
# (this file uses standard IO to communicate with the grader!)

# =============================================================================

# Write your bots in the scotty_bot and trapper_bot classes. Helper functions
# and standard library modules are allowed, and can be written before/inside
# these classes.

# You can define as many different strategies as you like, but only the classes
# currently named "scotty_bot" and "trapper_bot" will be run officially.


# Example Scotty bot that makes a random move:


class choke_trapper_bot:
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
        self.pathing.board = board
        self.pathing.heatmap = self.pathing.generate_backmap()
        steps = self.pathing.find_path((x,y))
        if len(steps) == 0:
          return self.pathing.neighbors((x,y))[0]
        end_delta= [sum(step) for step in zip(*steps)]
        candidates = [(x+end_delta[0], y+end_delta[1]), (x+steps[0][0],y+steps[0][1])]

        shortest = len(steps)
        choice = candidates[0]
        for candidate in candidates:
            future_board = copy.deepcopy(board)
            future_board[candidate[1]][candidate[0]] = 2
            self.pathing.board = future_board
            self.pathing.heatmap = self.pathing.generate_backmap()
            path_len = len(self.pathing.find_path((x,y)))
            if path_len >= shortest:
                choice = candidate
                shortest = path_len
        return choice

def count_roots(root):
    if len(root.children) == 0:
        return 0
    roots = 1
    for child in root.children:
        roots += count_roots(child)
    return roots

class tree:
  def __init__(self, pos, parent, children=[]):
        self.pos = pos
        self.children = children
        self.parent = parent

  def add_child(self, child):
      self.children.append(child)

