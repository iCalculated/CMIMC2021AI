import random
import math
from collections import namedtuple
import operator

Point = namedtuple('Point','x y')
Point.__add__ = lambda a, b: Point(a[0] + b[0], a[1] + b[1])
Point.__sub__ = lambda a, b: Point(a[0] - b[0], a[1] - b[1])

MOVES = {
        Point(1,2),
        Point(1,-2),
        Point(-1,2),
        Point(-1,-2),
        Point(2,1),
        Point(2,-1),
        Point(-2,1),
        Point(-2,-1),
        }

def safe(pos):
    return max(abs(pos.y),abs(pos.x)) >= 3

def sun_dist2(pos):
    return pos.x**2 + pos.y**2

def dist2(ship1, ship2):
    return (ship1[0] - ship2[0])**2 + (ship1[1] - ship2[1])**2

def evaluate_move(move, pos, direction):
    delta = math.atan2(pos.x+move[0],pos.y+move[1]) - math.atan2(pos.x,pos.y)
    if delta<-math.pi:
        delta += 2*math.pi
    elif delta>math.pi:
        delta -= 2*math.pi
    delta *= -direction
    sun = sun_dist2(pos+move)
    return 100 * delta - sun

def predict_optimal_move(ship):
    x,y,direction,_=ship
    pos = Point(x,y)

    val = -math.inf
    best = []
    for move in MOVES:
        if safe(pos + move):
            evaluation = evaluate_move(move, pos, direction)
            if evaluation > val:
                val = evaluation
                best = []
                best.append(move)
            elif evaluation == val:
                best.append(move)
    return best

def predict_all_moves(ship):
    return MOVES

def predict_directional_moves(ship):
    x,y,direction,_=ship
    pos = Point(x,y)
    viable =  filter(lambda x: evaluate_move(x, pos, direction) > 0, MOVES)
    return viable

def danger_zone(ship, moves):
    pos = Point(ship[0],ship[1])
    return map(lambda x: pos + x, moves)

class spaceship_bot:
    def __init__(self):
        self.moves = MOVES
        self.round = 0
        self.others_archive = []
        self.wreckage = set()
        self.verbose, self.error = (True, True)
        self.priors = []
     
    def move(self, ship, others):
        self.others_archive.append(others)
        self.update_wreckage()

        x, y, self.direction, score = ship
        self.pos = Point(x, y)
        self.others = others

        self.round += 1
        for strat in [predict_all_moves, predict_directional_moves, predict_optimal_move]:
            self.avoidance_strategy = strat
            self.check_moves()

            choice = self.choose_move()
            if choice:
                self.priors.append(choice)
                return choice
        return random.sample(self.moves.difference(self.illegal_moves), 1)[0]

    def avoidance_lookup(self, ship):
        tracking_index = None
        for i, (*pos, _, _) in enumerate(self.others_archive[-1]):
            if tuple(pos) == (ship[0], ship[1]):
                tracking_index = i
        frames = []
        for idx, frame in enumerate(self.others_archive[:-1]):
            *pos, _, _ = frame[tracking_index]
            if tuple(pos) == (ship[0], ship[1]):
                self.debug("Found match!")
                frames.append(idx)
        moves = {}
        self.debug(f"{frames=}")
        for frame in frames:
            x, y, _, _ = self.others_archive[frame][tracking_index]
            init_pos = Point(x,y)
            x, y, _, _ = self.others_archive[frame+1][tracking_index]
            final_pos = Point(x,y)

            move = final_pos - init_pos 
            if move in moves:
                moves[move] += 1
            else:
                moves[move] = 1

        if len(moves) != 0: 
            return [max(moves, key=moves.get)]

        return self.avoidance_strategy(ship)

    def update_wreckage(self):
        locations = set()
        for x, y, _, _ in self.others_archive[-1]:
            location = Point(x,y)
            if location in locations:
                self.wreckage.add(location)
            else:
                locations.add(location)

    def choose_move(self):
        val = -math.inf
        best = None
        for move in self.moves.difference(self.illegal_moves):
            if not move in self.unsafe_moves:
                evaluation = evaluate_move(move, self.pos, self.direction)
                if evaluation > val:
                    val = evaluation
                    best = move
        return best

    def check_moves(self):
        danger_nodes = copy.deepcopy(self.wreckage)
        def is_threat(ship, other):
            return dist2(ship, other) < 25 and not (other[0], other[1]) in self.wreckage

        for s in filter(lambda l: is_threat(self.pos,l), self.others):
            danger_nodes.update(danger_zone(s,self.avoidance_strategy(s)))

        self.unsafe_moves = self.find_unsafe_moves(danger_nodes)
        self.illegal_moves = self.find_illegal_moves()
        if len(self.priors) >= 4 \
                and self.priors[-2] not in self.illegal_moves \
                and self.priors[-1] - self.priors[-3] == (0,0) \
                and self.priors[-2] - self.priors[-4] == (0,0) \
                and self.priors[-1] + self.priors[-2] == (0,0):
            self.illegal_moves.append(self.priors[-2])

    def sun_scan(self):
        count = 0
        for s in self.others:
            if -6 <= s[0] <= 6 and -6 <= s[1] <= 6 and (s[0],s[1]) not in self.wreckage:
                count += 1
        return count

    def debug(self, s):
        if self.verbose: print(s)

    def error(self, s):
        if self.errors: print(s)

    def find_unsafe_moves(self, dangers):
        return list(filter(lambda x: self.pos + x in dangers, self.moves))

    def find_illegal_moves(self):
        return list(filter(lambda x: self.pos + x in self.wreckage \
                                    or not safe(self.pos + x), \
                                    self.moves))

#=============================================================================

# Local testing parameters

# If you would like to view a turn by turn game display while testing locally,
# set this parameter to True

LOCAL_VIEW = False

# Set the size of the area (around the origin) you would like to display, as a
# square of side length 2 * SIDE + 1
# The first ship will be displayed as "1", other ships will be displayed as "0",
# crashed ships will be displayed as "X", and the sun will be displayed as "S".

SIDE = 10

# Set a list of (arbitrarily many) strategies you would like to test locally

LOCAL_STRATS = [
    spaceship_bot(),
    spaceship_bot(),
    spaceship_bot(),
    spaceship_bot(),
    spaceship_bot(),
    spaceship_bot(),
    spaceship_bot(),
    spaceship_bot(),
    ]
#LOCAL_STRATS = [ spaceship_bot() ]

# Set how many rounds you would like the game to run for (official is 500)

ROUNDS = 500

#=============================================================================












































# You don't need to change any code below this point

import json
import sys
import random
import math
import copy

def WAIT():
    return json.loads(input())

def SEND(data):
    print(json.dumps(data), flush=True)

def dispboard_for_tester(board):
    print('\n'.join(' '.join(i) for i in board))

MASK = lambda a,i:a[:i]+a[i+1:]
LEGAL = [(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)]
SIDES = 2*SIDE+1

def PLAY(playerlist):
    n = len(playerlist)
    players = [(playerlist[i],i) for i in range(n)]
    #random.shuffle(players)
    r = max(8,n)
    ships = [[0]*4 for i in range(n)]
    moves = [random.choice(LEGAL) for i in range(n)]
    history = []
    off = 2*math.pi*random.random()/n
    for i in range(n):
        theta = i*2*math.pi/n+off
        x,y = int(r*math.sin(theta)),int(r*math.cos(theta))
        if (x+y)%2:
            if random.choice((0,1)):
                x += random.choice((-1,1))
            else:
                y += random.choice((-1,1))
        ships[i][0] = x
        ships[i][1] = y
        ships[i][2] = 2*(i%2)-1
    board = [[' ']*SIDES for i in range(SIDES)]
    for i in range(SIDE-2, SIDE+3):
        for j in range(SIDE-2, SIDE+3):
            board[i][j] = 'S'
    for _ in range(ROUNDS):
        chips=copy.deepcopy(ships)
        history.append(chips)
        for i in range(SIDES):
            for j in range(SIDES):
                if board[i][j] in '01':
                    board[i][j]=' '
        for i in range(n):
            if ships[i][2]:
                player = players[i][0]
                try:
                    move = player.move(chips[i], MASK(chips,i))
                    if move not in LEGAL:
                        raise Exception("invalid move")
                    moves[i] = move
                except Exception as e:
                    print(f"Player {players[i][1]} has an error: {e}! Defaulting to previous move.")
                    print(e)
                oldx, oldy = ships[i][0],ships[i][1]
                ships[i][0] += moves[i][0]
                ships[i][1] += moves[i][1]
                newx, newy = ships[i][0],ships[i][1]
                if -2 <= newx <= 2 and -2 <= newy <= 2:
                    ships[i][2] = 0
                else:
                    delta = math.atan2(newy,newx)-math.atan2(oldy,oldx)
                    if delta<-math.pi:
                        delta += 2*math.pi
                    elif delta>math.pi:
                        delta -= 2*math.pi
                    delta *= ships[i][2]
                    ships[i][3] += delta/(2*math.pi)
                    if abs(ships[i][0]) <= SIDE and abs(ships[i][1]) <= SIDE:
                        board[SIDE-ships[i][1]][SIDE+ships[i][0]]='1' if players[i][1]==0 else '0'
            else:
                if abs(ships[i][0]) <= SIDE and abs(ships[i][1]) <= SIDE:
                    if not (-2 <= ships[i][0] <= 2 and -2 <= ships[i][1] <= 2):
                        board[SIDE-ships[i][1]][SIDE+ships[i][0]]='X'
        if LOCAL_VIEW:
            dispboard_for_tester(board)
            input("Enter to continue (change LOCAL_VIEW to toggle this)")
        for i in range(n):
            for j in range(i):
                if ships[i][0]==ships[j][0] and ships[i][1]==ships[j][1]:
                    ships[i][2] = 0
                    ships[j][2] = 0
    scores = sorted((players[i][1],ships[i][3]) for i in range(n))
    final = [x[1] for x in scores]
    print("Final scores:")
    print('\n'.join(map(str,final)))
    #print(sum(final[0:4]))
    #print(sum(final[4:8]))
    if not LOCAL_VIEW:
        print("Change LOCAL_VIEW to True to see a turn by turn replay")

if len(sys.argv) < 2 or sys.argv[1] != 'REAL':
    PLAY(LOCAL_STRATS)
    input()

else:
    player = spaceship_bot()
    while True:
        data = WAIT()
        play = player.move(data["ship"], data["others"])
        SEND(play)
