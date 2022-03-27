

class MHTBot():
    

    def __init__(self):
        
    
    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        
        
       
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        
        
        

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        
        
        
        
    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        
        

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        
    


    


def MovementSOISMCTS(board_set, color):
    root = MovementMonteCarloTreeSearchNode(board_set = board_set, root_node = True, color = color)
    selected_node = root.best_action()
    return selected_node
        
    """
    make a tree
    (v,d) = select a node from starting state
    
    if there are still actions at this node:
        (v,d) = new node made by expanding current (v,d)
        
    get reward by simulating board
    backpropogate that reward
    
    return an action
        
    """       

    

class BSMCTSNode():
    def __init__(self, beliefs = None, parent=None, parent_action=None, root_node = False, color = None):
        self.beliefs  = []
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self.reward = 0
        self.root_node = root_node
        self.color = color

        self._untried_actions = []
        self._untried_actions = self.untried_actions()
        self._actions = []
        self._actions = self.actions()
        
    
    
    def untried_actions(self):
        self._untried_actions = self.get_legal_actions(self.state)
        return self._untried_actions
    
    def actions(self):
        self._actions = self.get_legal_actions(self.state)
        return self._actions
    
    def get_visits(self):
        return self._number_of_visits
    
    def get_reward(self):
        return self.reward
  

def nodeTakeAction(node, action):
    new_color = not node.color
    new_beliefs = []
    
    for belief in node.beliefs:
        new_state = belief.state.copy()
        
        if action in new_state.legal_moves:
            new_state.push(action)
            new_beliefs.append(Belief(new_state, belief.probability))

    return BSMCTSNode(new_beliefs, node, action, False, new_color)
            


        """
Broot , maximal samplings T, maximal iterations S
1: function BS-MCTS Broot
2: t ← 1
3: repeat
4: γ ← Sampling(Broot)
5: s ← 1
6: repeat
7: R ← Search(γ,Broot)
8: N(γ) ← N(γ) + 1
9: s ← s + 1
10: until s > S
11: t ← t + 1
12: until t > T
13: return a ← argmaxa∈A(Br o o t )U(Broot, a)
14: end function

"""
def BSMCTS(root_node, max_samples, max_iterations):
    t = 1
    while (t < max_samples):
        belief = sampling(root_node)
        s = 1
        
        while (s < max_iterations):
            reward = search(belief, root_node)
            belief.visits += 1
            s += 1
        
        t += 1
    
    
    action = maxRewardAction(root_node)
    
    return action
    

"""

15: function Expansion γ, B
16: N(γ) ← 0
17: for all a ∈ A(γ) do
18: if B · a not in the tree then
19: add B · a to the tree
20: end if
21: if γ · a not in B · a then
22: add γ · a to B · a
23: N(γ, a) ← 0
24: U(γ, a) ← 0
25: end if
26: end for
27: end function
"""

def expansion(belief, node):
    
    belief.visits = 0
    
    for action in belief.actions:
        new_node = nodeTakeAction(node, action)
        if new_node not in node.children:
            node.children.append(new_node)
         
        new_belief = beliefTakeAction(belief, action)
        if new_belief not in new_node.beliefs:
            new_node.addBelief(new_belief)
            new_belief.reward = 0
            new_belief.visits = 0
            

"""

28: function SamplingBroot
29: generate new γ
30: add γ to Broot
31: end function
"""            

def sampling(root_node):
    belief = generateBelief()
    root_node.addBelief(belief)
    
"""

32: function Search γ,B
33: if N(B) = 0 then
34: R ← Simulation(γ)
35: return R
36: end if
37: if γ has no children then
38: Expansion(γ,B)
39: end if
40: N(γ) ← N(γ) + 1
41: action a← Selection(γ,B)
42: R←−Search(γ · a,B · a)
43: N(γ, a) ← N(γ, a) + 1
44: U(γ, a) ← U(γ, a) + 1
N (γ ,a) [R − U(γ, a)]
45: return R
46: end function

"""

def search(belief, node):
    if (node.visits == 0):
        reward = simulation(belief)
        return reward
    
    if (node.children == []):
        expansion(belief, node)
        
    belief.visits += 1
    action = selection(belief, node)
    reward = search(beliefTakeAction(belief, action), nodeTakeAction(node, action))
    
    belief.actionVisits[action] += 1
    
    belief.actionRewards[action] += (1/belief.actionVisits[action]) * (reward - belief.actionRewards[action])
    
    return reward

"""
47: function Selectionγ, B
48: if B is Player node then
49: a ← argmaxa∈A(γ )VplayerNode (B, a)
50: else
51: a ← RouletteWheelSelection(Pro(ai))
52: end if
53: return a
54: end function
"""

def selection(belief, node):
    
    if node.isPlayerNode():
        action = nodeRewardEstimation(node, belief, action)
        
    else:
        action = rouleteWheelSelection(actionProbabilities(node))


    
class Belief(state, probability):
    
    def __init__(self, state, probability):
       self.visits = 0
       self.reward = 0
       self.state = state
       self.actionVisits = {}
       self.actionRewards = {}
      
    
    def simulate(self):

        simulation_number = 1


        board = self.state
        new_board = board.copy()
        new_board.clear_stack()
        enemy_king_square = new_board.king(not new_board.turn)
        my_king_square = new_board.king(new_board.turn)
        try:
            enemy_king_attackers = new_board.attackers(new_board.turn, enemy_king_square)
        except TypeError:
            #print("Type Error Trapped")
            enemy_king_attackers = False
            
        try:
            my_king_attackers = new_board.attackers(not new_board.turn, my_king_square)
        except TypeError:
            #print("Type Error Trapped")
            my_king_attackers = False
            
        if enemy_king_attackers:
            #print("I can win")
            return 1
        elif my_king_attackers:
            #print("I can lose")
            return -1
        else:
            
            x = self.singleRandomSim(new_board)
            #print(x)
            return x
            
            
    def singleRandomSim(self, board):
        #print("random sim")
        new_board = board.copy()
        while (not self.is_game_over(new_board)):
            enemy_king_square = new_board.king(not new_board.turn)

            try:
                enemy_king_attackers = new_board.attackers(new_board.turn, enemy_king_square)
            except TypeError:
                #print("Type Error Trapped")
                enemy_king_attackers = False

            if enemy_king_attackers:
                #print("Opponent king open!")
                attacker_square = enemy_king_attackers.pop()
                best_move = chess.Move(attacker_square, enemy_king_square)

            else:
                best_move = random.choice(self.get_legal_actions(new_board))

            new_board.push(best_move)

        return self.game_result(new_board, self.color)

    
    
    def get_legal_actions(self, board): 
        return list(board.pseudo_legal_moves)
        
    def is_game_over(self, board):
        return board.king(True) == None or board.king(False) == None
        
    def game_result(self, board, color):
        
        if board.king(color) == None:
            x = 1
            return x
        if board.king(not color) == None:
            x = -1
            return x
        
    def move(self, board, action):
        new_board = board.copy()
        new_board.push(action)
        return new_board
    


def beliefTakeAction(belief, action):
    new_state = belief.state.copy()
    new_state.push(action)
    
    return Belief(new_state, belief.probability)




