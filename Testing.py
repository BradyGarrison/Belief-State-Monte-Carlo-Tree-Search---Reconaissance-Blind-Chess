# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 13:52:21 2022

@author: kimbe
"""

from BeliefBotTest import *

x = [Belief(chess.Board(),1)]


root_node = BSMCTSNode(root_node = True, color = True, beliefState = x)

z = BSMCTS(root_node, 100, 5)

print(z)