import chess
import chess.engine
import chess.syzygy
import random
import math
import numpy as np
from collections import defaultdict
from reconchess import *
import os


import operator
from collections import Counter
from itertools import groupby
import chess.svg


STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'
os.environ['STOCKFISH_EXECUTABLE'] = r"C:\Users\kimbe\Documents\Brady Stuff\NRL Stuff\Chess Tools\lc0-v0.28.2-windows-cpu-dnnl\lc0.exe"

def normalize(belief_state):
    
    raw_list = []
    for belief in belief_state:
        raw_list.append(belief.probability)
        
    norm_list = [float(i)/max(raw_list) for i in raw_list]
    
    for x in range(len(belief_state)):
        belief_state[x].probability = norm_list[x]
        
    
        


class BeliefBot():
    

    def __init__(self):
        #print("HELLO WORLD")
        self.board = None
        self.color = None
        self.opponent_color = None
        self.belief_state = []
        self.board_set = []
        self.my_piece_captured_square = None
        self.need_new_boards = True
        self.sense_dict = {0:9,1:9,2:10,3:11,4:12,5:13,6:14,7:14,8:9,15:14,16:17,23:22,24:25,31:30,32:33,39:38,40:41,47:46,48:49,55:54,56:49,57:49,58:50,59:51,60:52,61:53,62:54,63:54}
        self.piece_scores = {'P':1, 'N':3, 'B':3, 'R':5, 'Q':9, 'K':9}
        
        
        self.tablebase = chess.syzygy.open_tablebase(r"C:\Users\kimbe\Documents\Brady Stuff\NRL Stuff\Chess Tools\syzygy")
        #self.tablebase.add_directory(r"E:\SEAP 2021\Syzygy-6")
        # make sure stockfish environment variable exists
        if STOCKFISH_ENV_VAR not in os.environ:
            raise KeyError(
                'TroutBot requires an environment variable called "{}" pointing to the Stockfish executable'.format(
                    STOCKFISH_ENV_VAR))

        # make sure there is actually a file
        stockfish_path = os.environ[STOCKFISH_ENV_VAR]
        if not os.path.exists(stockfish_path):
            raise ValueError('No stockfish executable found at "{}"'.format(stockfish_path))

        # initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.engine.configure({"SyzygyPath":r"C:\Users\kimbe\Documents\Brady Stuff\NRL Stuff\Chess Tools\syzygy"})
        

    def possibleMoves(self, board, color):
        board.turn = color
        return list(board.pseudo_legal_moves)
    
    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.belief_state.append(Belief(board,1))
        self.board_set.append(board)
        self.color = color
        self.opponent_color = not color
        self.first_turn = True
        
       
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            new_belief_state = self.belief_state.copy()
            for belief in belief_state:
                board = belief.board
                new_belief_state.remove(board)
                square_attackers = board.attackers(self.opponent_color, self.my_piece_captured_square)

                while square_attackers:
                    new_board = board.copy()
                    attacker_square = square_attackers.pop()
                    new_board.push(chess.Move(attacker_square, self.my_piece_captured_square))
                    new_belief_state.append(new_board)
               
            print("new boards: " + str(len(new_belief_state)))
            
            normalize(new_belief_state)
            self.belief_state = new_belief_state
            self.need_new_boards = False
            print("opponent move predict off")
        

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
                
        
        """
        x = self.belief_state.copy()
        try:
            z = BSMCTS()
        except IndexError:
            
            print("Index Error - Random Sense")
            return random.choice(sense_actions + [None])
        
        if sense_choice in sense_actions:
            print("Sensing MCTS successful")
            return sense_choice

        else:
            print("Random Sense")
            return random.choice(sense_actions + [None])
        """
        return self.MHT_choose_sense(sense_actions, move_actions, seconds_left)
        
        

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        
        
        self.MHT_handle_sense_result(sense_result)
        
        print("BSMCTS handle sense result")
        new_belief_state = self.belief_state.copy()
        if self.need_new_boards:
            #print("predicting opponent moves")
            for belief in self.belief_state:
                board = belief.board
                opponent_moves = self.possibleMoves(board, self.opponent_color)
                for move in opponent_moves:
                    newbelief = beliefTakeAction(belief, move)
                    new_belief_state.append(newbelief)
                
            self.belief_state = new_belief_state.copy()
            
        else:
            self.need_new_boards = True
            #print("opponent move predict back on")
            
        #print("now narrowing down")
        for belief in self.belief_state:
            board = belief.board
            possible = True
            for square, piece in sense_result:
                if board.piece_at(square) != piece:
                    possible = False
            if not possible:
                new_belief_state.remove(belief)
                
        
        #print("narrow down boards: " + str(len(new_belief_state)))
        
        normalize(self.belief_state)
        
        
        
    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        print("BS-MCTS choose move")
        x = self.belief_state.copy()
        root_node = BSMCTSNode(root_node = True, color = self.color, beliefState = x)
        try:
            z = BSMCTS(root_node, 100, 5)
            print(z)
            return z
        except IndexError:
            
            print("Index Error - Random Move")
            return random.choice(move_actions + [None])
        
        if move_choice in move_actions:
            print("Movement MCTS successful")
            return move_choice

        else:
            print("Random move")
            return random.choice(move_actions + [None])
        

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        
        self.MHT_handle_move_result(requested_move, taken_move, captured_opponent_piece, capture_square)
        
        
        print("BS-MCTS handle move result")
        if taken_move != None:
            
            #print("updating boards with my move")
            new_belief_state = self.belief_state.copy()
            for belief in self.belief_state:
                new_belief_state.remove(belief)
                board = belief.board
                if taken_move in board.pseudo_legal_moves:
                    newbelief = beliefTakeAction(belief, taken_move)
                    new_belief_state.append(newbelief)
            
            self.belief_state = new_belief_state
            normalize(self.belief_state)
        
        

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        pass
        
    
    
    def MHT_handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        print("MHT move handled")
        
        
        if taken_move != None:
            
            #print("updating boards with my move")
            new_board_set = self.board_set.copy()
            for board in self.board_set:
                new_board_set.remove(board)
                if taken_move in board.pseudo_legal_moves:
                    newboard = board.copy()
                    newboard.push(taken_move)
                    new_board_set.append(newboard)
            
            self.board_set = new_board_set
        
        #else:
            #print("No change, so no move update")
            
        #print("")
    

    def MHT_choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        
        print("MHT CHOOSE SENSE")  
        #print("CHOOSING SENSE")
        board_locations = {}
        for square in chess.SQUARES:
            board_locations[square] = [[],0]
    
        for board in self.board_set:
            opponent_moves = self.possibleMoves(board, self.opponent_color)
            for move in opponent_moves:
                location = move.to_square
                piece_symbol = str(board.piece_at(move.from_square)).upper()
                piece_score = self.piece_scores[piece_symbol]
                newboard = board.copy()
                newboard.push(move)
                board_locations[location][0].append(newboard)
                board_locations[location][1] += piece_score
    
        sense_weights = {}
        for location in board_locations:
            sense_weights[location] = len(board_locations[location][0]) * board_locations[location][1]
        
        best_val = max(sense_weights.values())
        keys = sense_weights.keys()
        pot_senses = []
        for key in keys:
            if sense_weights[key] == best_val:
                pot_senses.append(key)
        sense_choice = random.choice(pot_senses)
        #print("sense chosen: " + str(sense_choice))
        
        if sense_choice in self.sense_dict.keys():
            new_sense = self.sense_dict[sense_choice]
            sense_choice = new_sense
            #print("sense corrected: " + str(sense_choice))
        
        return sense_choice
        

    def MHT_handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        
        print("MHT SENSE RESULT")  
        new_board_set = self.board_set.copy()
        if self.need_new_boards:
            #print("predicting opponent moves")
            for board in self.board_set:
                opponent_moves = self.possibleMoves(board, self.opponent_color)
                for move in opponent_moves:
                    newboard = board.copy()
                    newboard.push(move)
                    new_board_set.append(newboard)
                
            self.board_set = new_board_set.copy()
            
        else:
            self.need_new_boards = True
            #print("opponent move predict back on")
            
        #print("now narrowing down")
        for board in self.board_set:
            possible = True
            for square, piece in sense_result:
                if board.piece_at(square) != piece:
                    possible = False
            if not possible:
                new_board_set.remove(board)
                
        
        #print("narrow down boards: " + str(len(new_board_set)))
        
        
        if len(new_board_set) <= 200:
            self.board_set = new_board_set

        else:
            syzygy_check = True
            for board in new_board_set:
                if len(board.piece_map()) > 5:
                    syzygy_check = False
                    break
            
            if syzygy_check:
                #print("syzygy")
                wdl_set = []
                for board in new_board_set:
                    wdl_set.append(self.tablebase.probe_wdl(board))
                    
                mode_wdl = random.choice(mode(wdl_set))
                
                dtz_set = []
                if mode_wdl > 0:
                    for board in new_board_set:
                        evaluation = self.tablebase.probe_dtz(board)
                        if evaluation <= 0:
                            evaluation = 200
                        dtz_set.append([board, evaluation])
                    sorted_dtz_set = sorted(dtz_set, key=operator.itemgetter(1))
                    final_dtz_set = sorted_dtz_set[0:50]
                    
                    final_board_set = []
                    for item in final_dtz_set:
                        final_board_set.append(item[0])
                    
                    self.board_set = final_board_set
                    
                else:
                    for board in new_board_set:
                        evaluation = self.tablebase.probe_dtz(board)
                        if evaluation == 0:
                             evaluation = 178
                        dtz_set.append([board, evaluation])
                    sorted_dtz_set = sorted(dtz_set, key=operator.itemgetter(1), reverse = True)
                    final_dtz_set = sorted_dtz_set[0:50]
                    
                    final_board_set = []
                    for item in final_dtz_set:
                        final_board_set.append(item[0])
                        
                    self.board_set = final_board_set
                
            else:
                #print("narrowed down")
                self.board_set = random.sample(new_board_set,200)

            
        print("possible boards: " + str(len(self.board_set)))

    

class BSMCTSNode():
    def __init__(self, beliefs = [], parent=None, parent_action=None, root_node = False, color = None, beliefState = [], playerColor = None):
        self.beliefs  = beliefs
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.visits = 0
        self.reward = 0
        self.root_node = root_node
        self.color = color
        
        self.beliefState = beliefState
        
        self.playerColor = playerColor
        
        self.actions = []
        
        if self.root_node:
            self.playerColor = self.color
        
    
    
    def get_visits(self):
        return self.visits
    
    def get_reward(self):
        return self.reward
    
    def generateBelief(self):
        belief = random.sample(self.beliefState, 1)[0]
        
        if belief not in self.children:
            for action in belief.get_legal_actions(belief.board):
                if action not in self.actions:
                    self.actions.append(action) 
        #print(belief)
        return belief
    
    def isPlayerNode(self):
        return self.color == self.playerColor
  

def nodeTakeAction(node, action):
    new_color = not node.color
    new_beliefs = []
    
    for belief in node.beliefs:
        new_state = belief.board.copy()
        
        if action in new_state.legal_moves:
            new_state.push(action)
            new_beliefs.append(Belief(new_state, belief.probability))

    return BSMCTSNode(new_beliefs, node, action, False, new_color, node.playerColor)


def maxRewardAction(node):
    choices_weights = []
    for action in node.actions:
        reward = actionReward(node, action)

        choices_weights.append(reward)
    print(node.actions)
    print(choices_weights)
    return node.actions[np.argmax(choices_weights)]

def actionVisits(node, action):
    visits = 0
    for belief in node.beliefs:
        if action in belief.actionVisits.keys():
            visits += belief.actionVisits[action]
        
    return visits


def actionReward(node, action):
    reward = 0
    for belief in node.beliefs:
        if action in belief.actionRewards.keys():
            reward += belief.actionRewards[action]
        
    return reward
         

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
    
    for action in belief.actions():
        new_node = nodeTakeAction(node, action)
        if new_node not in node.children:
            node.children.append(new_node)
         
        new_belief = beliefTakeAction(belief, action)
        if new_belief not in new_node.beliefs:
            new_node.beliefs.append(new_belief)
            

"""

28: function SamplingBroot
29: generate new γ
30: add γ to Broot
31: end function
"""            

def sampling(root_node):
    belief = root_node.generateBelief()
    #print(belief)
    root_node.beliefs.append(belief)
    return belief
    
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
    print(str(belief))
    if (node.visits == 0):
        node.visits += 1
        reward = belief.simulate()
        return reward
    
    if (node.children == []):
        expansion(belief, node)
    node.visits += 1    
    belief.visits += 1
    action = selection(belief, node)
    reward = -1 * search(beliefTakeAction(belief, action), nodeTakeAction(node, action))
    
    if action in belief.actionVisits.keys():
        belief.actionVisits[action] += 1
    else:
        belief.actionVisits[action] = 1
    
    #Iterative Backpropogation
    if action in belief.actionRewards.keys():
        belief.actionRewards[action] += (1/belief.actionVisits[action]) * (reward - belief.actionRewards[action])
    else:
        belief.actionRewards[action] = reward
    #print(belief.actionRewards[action])
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
        action = maxNodeRewardEstimation(node,belief)
        
    else:
        action = rouleteWheelSelection(node.beliefs)
        
    return action

def maxNodeRewardEstimation(node, belief):
    choices_weights = []
    actions = belief.actions()
    for action in actions:
        if action in belief.actionVisits.keys():
            reward = nodeRewardEstimation(node, action)
        else:
            reward = 0

        choices_weights.append(reward)
   
    return actions[np.argmax(choices_weights)]

def nodeRewardEstimation(node,action):
    exploration = 0.7
    U = actionReward(node,action) 
    lnN = math.log(node.visits)
    NBa = actionVisits(node, action)
    return U + exploration * math.sqrt(lnN / NBa)

def roulette_wheel_selection(beliefs):
    maximum = sum(belief.probability for belief in beliefs)
    pick = random.uniform(0, maximum)
    current = 0
    for belief in beliefs:
        current += belief.probability
        if current > pick:
            return belief
    
class Belief():
    
    def __init__(self, board, probability):
       self.visits = 0
       self.reward = 0
       self.board = board
       self.probability = probability
       self.actionVisits = {}
       self.actionRewards = {}
       
      
    def __repr__(self):
        info = " Belief - Board: " + self.board.fen() + " probability: " + str(self.probability) + " visits: " + str(self.visits) + " reward: " + str(self.reward)
        return info

    def simulate(self):

        simulation_number = 1


        #board = self.board
        new_board = self.board.copy()
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
        color = new_board.turn
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

        return self.game_result(new_board, color)

    
    
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
    
    def actions(self):
        return self.get_legal_actions(self.board)
    


def beliefTakeAction(belief, action):
    new_state = belief.board.copy()
    new_state.push(action)
    
    return Belief(new_state, belief.probability)




