# NOTE: You can run this file locally to test if your program is working.

#===============================================================================

# INPUT FORMAT: ship, others

# ship: A list of length 4 consisting of [x, y, status, score], where

#   x, y is your current position

#   status = 1 if your goal is to travel counterclockwise
#   status = -1 if your goal is to travel clockwise
#   status = 0 if you have crashed

#   score = Number of times you have orbited the center in your target direction

# others: A list containing all other players' ships, in a fixed order. Each
#   ship is given in the same format as your ship, i.e. a list of length 4.

# Example input:

# ship: [3, 5, -1, 1.1]
# others: [[4, 4, 1, -1.3], [4, 6, 0, 0.1], [4, 6, 0, -0.3]]

#=============================================================================

# OUTPUT FORMAT: A list of two integers dx, dy satisfying dx^2 + dy^2 = 5.
# Your spaceship will move to the square x + dx, y + dy.

# Invalid outputs will result in the move you previously played being played
# again, with the exception of the first move, where a random move will be
# played instead.

### WARNING: COMMENT OUT YOUR DEBUG/PRINT STATEMENTS BEFORE SUBMITTING !!!
### (this file uses standard IO to communicate with the grader!)

#===============================================================================

# Write your bot in the spaceship_bot class. Helper functions and standard
# library modules are allowed, and can be written before before/inside these
# classes.

# You can define as many different strategies as you like, but only the class
# currently named "spaceship_bot" will be run officially.


# Example bot that moves in a random direction every round:

def dot(tup1, tup2):
    return tup1[0] * tup2[0] + tup1[1] * tup2[1]

def add(a,b):
    return (a[0]+b[0], a[1]+b[1])

def subtract(a,b):
    return (a[0]-b[0], a[1]-b[1])

def sun_dist(x,y):
    return math.sqrt(x**2 + y**2)

def opt_dir_circ(x,y,direction):
    if direction == 1: return (-y,x)
    else: return (y,-x)

def opt_dir(x,y,direction):
    if x < 2 and x > -2:
        return (-y*direction,0)
    elif y < 2 and y > -2:
        return (0,direction*x)
    elif direction == 1:
        if x > 0 and y > 0:
            return (-y,0)
        elif x > 0 and y < 0:
            return (0,x)
        elif x < 0 and y < 0:
            return (-y,0)
        elif x < 0 and y > 0:
            return (0,x)
    elif direction == -1:
        if x > 0 and y > 0:
            return (0,-x)
        elif x > 0 and y < 0:
            return (y,0)
        elif x < 0 and y < 0:
            return (0,-x)
        elif x < 0 and y > 0:
            return (y,0)
    else:
        return opt_dir_circ(x,y,direction)

def minecraft_survival_games_safe(pos,zone):
    zone = 3 if zone < 3 else zone
    x_safe = pos.x >= zone or pos.x <= -zone
    y_safe = pos.y >= zone or pos.y <= -zone 
    return x_safe or y_safe

def opt_dir_range(x,y,direction,distance):
    if x < distance-1 and x > -distance+1:
        return (-y*direction,0)
    elif y < distance-1 and y > -distance+1:
        return (0,direction*x)
    elif direction == 1:
        if x > 0 and y > 0:
            return (-y,0)
        elif x > 0 and y < 0:
            return (0,x)
        elif x < 0 and y < 0:
            return (-y,0)
        elif x < 0 and y > 0:
            return (0,x)
    elif direction == -1:
        if x > 0 and y > 0:
            return (0,-x)
        elif x > 0 and y < 0:
            return (y,0)
        elif x < 0 and y < 0:
            return (0,-x)
        elif x < 0 and y > 0:
            return (y,0)
    else:
        return opt_dir_circ(x,y,direction)

def predict_optimal_move(ship): # DEPRECATED, uses alignment and gravity
    x,y,direction,_=ship
    val = -math.inf
    best = []
    intended = opt_dir(x,y,direction)
    for move in [(1,2), (2,1), (2,-1), (1,-2), (-1,-2), (-2,-1), (-2,1), (-1,2)]:
        if safe(add((x,y), move)):
            d = dot(move,intended)
            sun = sun_dist2(x+move[0],y+move[1])
            evaluation =  d - 0.1 * sun
            if evaluation > val:
                val = evaluation
                best = []
                best.append(move)
            if evaluation == val:
                best.append(move)
    return best
class old_faithful:
    def __init__(self):
        self.moves = {(1,2), (2,1), (2,-1), (1,-2),
                      (-1,-2), (-2,-1), (-2,1), (-1,2)}

        self.round = 0
        self.others_archive = []
        self.wreckage = set()
        self.verbose = False
        self.errors = True
        self.priors = []

     
    def move(self, ship, others):
        self.others_archive.append(others)
        self.update_wreckage()

        self.x, self.y, self.direction, score = ship
        self.pos = Point(self.x, self.y)
        self.others = others


        self.intended = opt_dir(self.x, self.y, self.direction) 

        self.round += 1
        for strat in [predict_all_moves, predict_directional_moves, predict_optimal_move]:
            if strat != predict_all_moves:
                self.debug(f"Fallback: now using {strat}")
            self.set_avoidance_strategy(strategy=strat)
            self.check_moves()

            choice = self.choose_move()
            if choice:
                self.priors.append(choice)
                return choice
        #self.error(f"Error: no move")
        return random.sample(self.moves.difference(self.illegal_moves), 1)[0]


    def set_avoidance_strategy(self, strategy = predict_all_moves):
        self.avoidance_strategy = strategy
        #self.avoidance_lookup

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
            *init_pos, _, _ = self.others_archive[frame][tracking_index]
            *final_pos, _, _ = self.others_archive[frame+1][tracking_index]
            move = subtract(init_pos, final_pos)
            if move in moves:
                moves[move] += 1
            else:
                moves[move] = 1

        if len(moves) != 0: 
            return [max(moves, key=moves.get)]

        return self.avoidance_strategy(ship)

    def predict_optimal_move(self, ship):
        x,y,direction,_=ship
        intended = opt_dir(x,y,direction)

        def evaluate_move(move):
            delta = math.atan2(x+move[0],y+move[1]) - math.atan2(x,y)
            if delta<-math.pi:
                delta += 2*math.pi
            elif delta>math.pi:
                delta -= 2*math.pi
            delta *= -direction
            sun = sun_dist2(x+move[0],y+move[1])
            return 100 * delta - sun

        val = -math.inf
        best = []
        for move in [(1,2), (2,1), (2,-1), (1,-2), (-1,-2), (-2,-1), (-2,1), (-1,2)]:
            if safe(add((x,y), move)):
                evaluation = evaluate_move(move)
                if evaluation > val:
                    val = evaluation
                    best = []
                    best.append(move)
                elif evaluation == val:
                    best.append(move)
        return best


    def update_wreckage(self):
        locations = set()
        for *location, _, _ in self.others_archive[-1]:
            location = tuple(location)
            if location in locations:
                self.wreckage.add(location)
            else:
                locations.add(location)

    def choose_move(self):
        val = -math.inf
        best = None
        for move in self.moves.difference(self.illegal_moves):
            if not move in self.unsafe_moves:
                evaluation = self.evaluate_move(move)
                if evaluation > val:
                    val = evaluation
                    best = move

        #if best == None: 
        #    self.error(f"Error: no move")
        #    best = random.sample(self.moves.difference(self.illegal_moves), 1)[0]
        return best

    def evaluate_move(self, move):
        #alignment = dot(move,self.intended)
        delta = math.atan2(self.x+move[0],self.y+move[1]) - math.atan2(self.x,self.y)
        if delta<-math.pi:
            delta += 2*math.pi
        elif delta>math.pi:
            delta -= 2*math.pi
        delta *= -self.direction
        sun = sun_dist2(self.x+move[0],self.y+move[1])
        #print(f"{move[0]:2} {move[1]:2}: {1000*delta:3} {sun:3}")
        return 100 * delta - sun #100 * alignment - sun


    def check_moves(self):
        danger_nodes = copy.deepcopy(self.wreckage)
        def is_threat(ship, other):
            return dist2(ship, other) < 25 and not (other[0], other[1]) in self.wreckage

        for s in filter(lambda l: is_threat(self.pos,l), self.others):
            danger_nodes.update(danger_zone(s,self.avoidance_strategy(s)))

        self.unsafe_moves = self.find_unsafe_moves(danger_nodes)
        self.illegal_moves = self.find_illegal_moves()
        if len(self.priors) >= 4 \
                and self.priors[-1] == self.priors[-3] \
                and self.priors[-2] == self.priors[-4] \
                and self.priors[-1][0] == -self.priors[-2][0] \
                and self.priors[-1][1] == -self.priors[-2][1]:
            self.illegal_moves.add(self.priors[-2])

    def sun_scan(self):
        count = 0
        for s in self.others:
            if -6 <= s[0] <= 6 and -6 <= s[1] <= 6 and (s[0],s[1]) not in self.wreckage:
                count += 1
        return count

    def debug(self, s):
        if self.verbose:
            print(s)

    def error(self, s):
        if self.errors:
            print(s)


    def find_unsafe_moves(self, dangers):
        unsafe_moves = set()
        for move in self.moves:
            if add(self.pos, move) in dangers: 
                unsafe_moves.add(move)
        return unsafe_moves

    def find_illegal_moves(self):
        illegal_moves = set() 
        for move in self.moves:
            if add(self.pos, move) in self.wreckage or not safe(add(self.pos,move)):
                illegal_moves.add(move)
        return illegal_moves
class survivor_bot:
    def __init__(self):
        self.moves = [(1,2), (2,1), (2,-1), (1,-2),
                      (-1,-2), (-2,-1), (-2,1), (-1,2)]
        self.data = []
        self.ship = []
     
    def move(self, ship, others):
        self.data.append(others)
        self.ship.append(ship)
        x, y, direction, _ = ship
        self.pos = Point(x,y)
        intended = opt_dir(x,y,direction)

        val = -math.inf
        best = None
        banned_moves = []
        for s in others:
            ship_dist = dist2(ship, s) 
            if ship_dist <=20:
                s_move = self.predict(s)
                s_pos = (s[0] + s_move[0], s[1] + s_move[1])
                for move in self.moves:
                    if (ship[0] + move[0], ship[1] + move[1]) == s_pos:
                        banned_moves.append(move)
        for move in self.moves:
            if safe(add(self.pos,move)) and not move in banned_moves:
                d = dot(move,intended)
                sun = sun_dist2(x+move[0],y+move[1])
                evaluation =  d - 0.1 * sun
                if evaluation > val:
                    val = evaluation
                    best = move
        if best == None: 
            best = random.choice(self.moves)
        return best

    def predict(self, ship):
        x,y,direction,_=ship
        val = -math.inf
        best = None
        intended = opt_dir(x,y,direction)
        for move in self.moves:
            if safe(add(self.pos,move)): 
                d = dot(move,intended)
                sun = sun_dist2(x+move[0],y+move[1])
                evaluation =  d - 0.5 * sun
                if evaluation > val:
                    val = evaluation
                    best = move
        return best
class dist_square_bot:
    def __init__(self):
        self.moves = [(1,2), (2,1), (2,-1), (1,-2),
                      (-1,-2), (-2,-1), (-2,1), (-1,2)]
    
    def move(self, ship, others):
        x, y, direction, score = ship
        intended = opt_dir(x,y,direction)
        # You should write your code that moves every turn here

        val = -math.inf
        best = None
        for move in self.moves:
            if safe((x+move[0],y+move[1])):
                d = dot(move,intended)
                sun = sun_dist2(x+move[0],y+move[1])
                evaluation =  d - 0.5 * sun
                if evaluation > val:
                    val = evaluation
                    best = move
        if best == None: 
            best = random.choice(self.moves)
        return best
class dist_circle_bot: 
    def __init__(self):
        # You can define global states (that last between moves) here
        self.moves = [(1,2), (2,1), (2,-1), (1,-2),
                      (-1,-2), (-2,-1), (-2,1), (-1,2)]
    
    def move(self, ship, others):
        x, y, direction, score = ship
        intended = opt_dir_circ(x,y,direction)
        if sun_dist2(x,y) > 40:
            intended = (intended[0] - 2*x, intended[1] - 2*y)

        # You should write your code that moves every turn here

        val = 0
        best = None
        for move in self.moves:
            if safe((x+move[0],y+move[1])):
                if dot(move, intended) > val:
                    val = dot(move,intended)
                    best = move
        if best == None: 
            move = random.choice(self.moves)
        return best
class naive_circle_bot:
    def __init__(self):
        # You can define global states (that last between moves) here
        self.moves = [(1,2), (2,1), (2,-1), (1,-2), (-1,-2), (-2,-1), (-2,1), (-1,2)]
    
    def move(self, ship, others):
        x, y, direction, score = ship
        intended = opt_dir_circ(x,y,direction)
        # You should write your code that moves every turn here

        val = 0
        best = None
        for move in self.moves:
            if safe(add((x,y),move)):
                evaluation = dot(move, intended)
                if evaluation > val:
                    val = evaluation
                    best = move
        if best == None: 
            best = random.choice(self.moves)
        return best

class safe_random_bot:
    def __init__(self):
        # You can define global states (that last between moves) here
        self.moves = [(1,2), (2,1), (2,-1), (1,-2),
                      (-1,-2), (-2,-1), (-2,1), (-1,2)]
    
    def move(self, ship, others):
        x, y, direction, score = ship
        # You should write your code that moves every turn here
        is_safe = False
        while not is_safe:
            move = random.choice(self.moves)
            if safe((x+move[0],y+move[1])):
                is_safe=True
        return move
class random_bot:
    def __init__(self):
        # You can define global states (that last between moves) here
        self.moves = [(1,2), (2,1), (2,-1), (1,-2),
                      (-1,-2), (-2,-1), (-2,1), (-1,2)]
    
    def move(self, ship, others):
        # You should write your code that moves every turn here
        return random.choice(self.moves)
class flee_bot:
    def __init__(self):
        self.moves = [(1,2), (2,1), (2,-1), (1,-2),
                      (-1,-2), (-2,-1), (-2,1), (-1,2)]
    
    def move(self, ship, others):
        x, y, direction, score = ship
        intended = opt_dir(x,y,direction)
        # You should write your code that moves every turn here

        val = -math.inf
        best = None
        for move in self.moves:
            if safe(x+move[0],y+move[1]):
                d = dot(move,intended)
                sun = sun_dist2(x+move[0],y+move[1])
                evaluation =  d + sun
                if evaluation > val:
                    val = evaluation
                    best = move
        if best == None: 
            best = random.choice(self.moves)
        return best
