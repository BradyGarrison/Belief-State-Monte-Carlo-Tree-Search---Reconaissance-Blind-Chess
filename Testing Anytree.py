
"""
Created on Tue Jun 28 13:52:21 2022

@author: kimbe
"""

from BeliefBotTest import *

from graphviz import Digraph
from anytree import NodeMixin, RenderTree
from anytree.exporter import DotExporter


class TreeNode(NodeMixin):
    def __init__(self, BSMCTSNode, parent=None, name = None):
        self.children = [TreeNode(node, self, str(node.parent_action)) for node in BSMCTSNode.children]
        self.parent = parent
        self.name = name


def possibleMoves(board, color):
    new_board = board.copy()
    new_board.turn = color
    return list(new_board.pseudo_legal_moves)


def normalize(belief_state):
    
    raw_list = []
    for belief in belief_state:
        raw_list.append(belief.probability)
        
    norm_list = [float(i)/sum(raw_list) for i in raw_list]
    
    for x in range(len(belief_state)):
        belief_state[x].probability = norm_list[x]



x = [Belief(chess.Board(),1)]


new_belief_state = x.copy()


 
for belief in new_belief_state:
    belief.board.turn = False
for belief in x:
    board = belief.board
    opponent_moves = possibleMoves(board, False)
    for move in opponent_moves:
        newbelief = beliefTakeAction(belief, move)
        new_belief_state.append(newbelief)
        #print(newbelief.board)
        #print(newbelief.board.turn)
        
for belief in new_belief_state:
    belief.board.turn = True


normalize(new_belief_state)



    #White to move
#Queen Capture - chess.Board("rnbqkbnr/ppp2ppp/8/3pp3/Q1P5/8/PP1PPPPP/RNB1KBNR w")
#Knight Capture - chess.Board("rnbqkbnr/pp3ppp/2pN4/3pp3/8/8/PPPPPPPP/RNBQKB1R w")
#Rook Capture - chess.Board("R5k1/5ppp/8/8/8/8/5PPP/6K1 w")
#Rook 2-Step - chess.Board("6k1/5ppp/8/R7/8/8/5PPP/6K1 w")

    #Black to move
#Queen Capture - chess.Board("rnb1kbnr/pp1ppppp/8/q1p5/3PP3/8/PPP2PPP/RNBQKBNR b")
#Knight Capture - chess.Board("r1bqkbnr/pppppppp/8/8/3PP3/3n1P2/PPP3PP/RNBQKBNR b")
#Rook Capture - chess.Board("6k1/5ppp/8/8/8/8/5PPP/1r4K1 b")
#Rook 2-Step - chess.Board("6k1/5ppp/8/8/1r6/8/5PPP/6K1 b")


QW = chess.Board("rnbqkbnr/ppp2ppp/8/3pp3/Q1P5/8/PP1PPPPP/RNB1KBNR w")
KW = chess.Board("rnbqkbnr/pp3ppp/2pN4/3pp3/8/8/PPPPPPPP/RNBQKB1R w")
RW = chess.Board("R5k1/5ppp/8/8/8/8/5PPP/6K1 w")
R2W = chess.Board("6k1/5ppp/8/R7/8/8/5PPP/6K1 w")

QB = chess.Board("rnb1kbnr/pp1ppppp/8/q1p5/3PP3/8/PPP2PPP/RNBQKBNR b")
KB = chess.Board("r1bqkbnr/pppppppp/8/8/3PP3/3n1P2/PPP3PP/RNBQKBNR b")
RB = chess.Board("6k1/5ppp/8/8/8/8/5PPP/1r4K1 b")
R2B = chess.Board("6k1/5ppp/8/8/1r6/8/5PPP/6K1 b")


board = R2B
color = board.turn

root_node = BSMCTSNode(root_node = True, color = color, beliefState = [Belief(board,1)])
#root_node = BSMCTSNode(root_node = True, color = False, beliefState = new_belief_state)

z = BSMCTS(root_node, 10, 50)

actions, weights = z

if color:
    move_choice = actions[np.argmin(weights)]
    
else:
    move_choice = actions[np.argmax(weights)]

print(list(zip([str(action) for action in actions], weights)))

print(move_choice)

test = TreeNode(root_node)

for row in RenderTree(test):
    print("%s%s" % (row.pre, row.node.name))

DotExporter(test).to_dotfile("test2.dot")

