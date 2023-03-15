import sys
from gym_maze.envs.maze_generator import get_maze
import numpy as np
import math
import random
import json
import requests
import time

import gym_maze
from gym_maze.envs.maze_manager import MazeManager
from riddle_solvers import *



def npos(row, col, ncols):
    return row * ncols + col
def get_pos(pos):
    return [int(pos[0]), int(pos[1])]


def is_good_pos(pos):
    if(pos[0] < 0): return False
    if(pos[0] > 9): return False
    if(pos[1] < 0): return False
    if(pos[1] > 9): return False
    return True


def addPosToStack(pos, stack):
    if(pos[0] < 0): return
    if(pos[0] > 9): return
    if(pos[1] < 0): return
    if(pos[1] > 9): return
    stack.append(pos)
pos_set = set()
moves = []
moves_trace = []

def invert(move):
    if(move == 'N'): return 'S'
    if(move == 'S'): return 'N'
    if(move == 'E'): return 'W'
    if(move == 'W'): return 'E'

all_actions = []
all_pos = []

parent_pos = []
for i in range(100):
    parent_pos.append('')
    all_pos.append(['S','E', 'N', 'W'])
for i in range(1, 10):
    all_pos[npos(0, i, 10)] = ['S', 'E',  'W']
    all_pos[npos(9, i, 10)] = ['E', 'N', 'W']
    all_pos[npos(i, 0, 10)] = [ 'S', 'E','N']
    all_pos[npos(i, 9, 10)] = [ 'S','N', 'W']

all_pos[npos(0, 0, 10)] = ['S', 'E']
all_pos[npos(0, 9, 10)] = ['S', 'W']
all_pos[npos(9, 9, 10)] = ['N', 'W']
all_pos[npos(9, 0, 10)] = ['E', 'N']


    

parent_map = dict()
explored = set()
pos_moves = set()                   
pos_moves.add("-1")
pending = []
parent_map['00'] = None
last_pos = [0, 0]
last_action = ''
all_actions = ['N', 'S', 'E', 'W']
last_parent =''


dir_map = {
    "0, -1": 'N',
    "0, 1": 'S',
    "1, -1": 'N',
    "1, 1": 'S',
    "-1, 0": 'W',
    "1, 0": 'E',
    "-1, -1": 'W',
    "-1, 1": 'W',
    "0, 0": 'N'
}
def get_move(arr):
    manhattan_distances = []
    for i in range(len(arr[1])):
        if arr[1][i] == -1:
            manhattan_distances.append(1000)
        else:
            manhattan_distances.append(arr[1][i])
    mini = min(manhattan_distances)
    idx = manhattan_distances.index(mini)
    dir = arr[2][idx]
    return dir_map["{}, {}".format(dir[0], dir[1])]



def select_action(state):
    # This is a random agent 
    # This function should get actions from your trained agent when inferencing.
    global last_action
    global last_pos
    global all_actions
    global parent_map
    global parent_pos
    global last_parent

    pos = [state[0][1], state[0][0]]

    if(last_pos[0] != pos[0] or last_pos[1] != pos[1]):

        if is_good_pos([pos[0] - 1, pos[1]]) and (invert(last_action) in all_pos[npos(pos[0] - 1, pos[1], 10)] and last_action == 'N'):
            all_pos[npos(pos[0] - 1, pos[1], 10)].remove(invert(last_action))

        elif is_good_pos([pos[0] + 1, pos[1]]) and (invert(last_action) in all_pos[npos(pos[0] + 1, pos[1], 10)]  and last_action == 'S'):
            all_pos[npos(pos[0] + 1, pos[1], 10)].remove(invert(last_action))

        elif is_good_pos([pos[0], pos[1] + 1]) and (invert(last_action) in all_pos[npos(pos[0], pos[1] + 1, 10)] and last_action == 'E'):
            all_pos[npos(pos[0], pos[1] + 1, 10)].remove(invert(last_action))

        elif is_good_pos([pos[0], pos[1] - 1]) and (invert(last_action) in all_pos[npos(pos[0], pos[1] - 1, 10)] and last_action == 'W'):
            all_pos[npos(pos[0], pos[1] - 1, 10)].remove(invert(last_action))


        if(len(parent_pos[npos(last_pos[0], last_pos[1], 10)])==1):
            parent_pos[npos(last_pos[0], last_pos[1], 10)] = ''
        else:
            parent_pos[npos(last_pos[0], last_pos[1], 10)]=parent_pos[npos(last_pos[0], last_pos[1], 10)][:-1]
        if(str(last_pos[0]) + str(last_pos[1]) in parent_map):
            parent_map[str(last_pos[0]) + str(last_pos[1])] = parent_map[str(last_pos[0]) + str(last_pos[1])][:-2]
    actions = all_pos[npos(pos[0], pos[1], 10)]

    random_action = ''
    move_to_parent=False
    if(len(actions) == 0):
        move_to_parent=True
        random_action = parent_pos[npos(pos[0], pos[1], 10)]
        print(npos(pos[0], pos[1], 10))
    else:
        manhattan_move=get_move(state)
        if (len(manhattan_move)>0 and manhattan_move in actions):
            random_action = manhattan_move
        else:
            random_action = actions[0]
    
    random_action = random_action[0]
    last_action = random_action
    action_index = all_actions.index(random_action)
    
    new_pos = []
    if(random_action == 'N'):
        new_pos = [pos[0] - 1, pos[1]]
    if(random_action == 'S'):
        new_pos = [pos[0] + 1, pos[1]]
    if(random_action == 'E'):
        new_pos = [pos[0], pos[1] + 1]
    if(random_action == 'W'):
        new_pos = [pos[0], pos[1] - 1]
    if(len(pending) > 0):
        if(not(pos[0] == new_pos[0] and pos[1] == new_pos[1])):
            pending.append(pos)
        else:
            pending.append(pos)
    if(not(move_to_parent)):
        if str(new_pos[0]) + str(new_pos[1]) in parent_map:
            parent_map[str(new_pos[0]) + str(new_pos[1])] =parent_map[str(new_pos[0]) + str(new_pos[1])] + str(pos[0]) + str(pos[1])
        parent_map[str(new_pos[0]) + str(new_pos[1])] = str(pos[0]) + str(pos[1])

    last_pos[0] = new_pos[0]
    last_pos[1] = new_pos[1]
    if(len(all_pos[npos(pos[0], pos[1], 10)]) > 0):        
        all_pos[npos(pos[0], pos[1], 10)].remove(random_action)
    if(not(move_to_parent) and invert(random_action) in (all_pos[npos(new_pos[0], new_pos[1], 10)]) ):
        all_pos[npos(new_pos[0], new_pos[1], 10)].remove(invert(random_action))
    if(not(move_to_parent)):
        parent_pos[npos(new_pos[0], new_pos[1], 10)] += invert(random_action)
    return random_action, action_index

ctr = 0
solved = 0
def local_inference(riddle_solvers):
    global ctr,solved
    r = []
    obv = manager.reset(agent_id)
    ctr = 0
    for t in range(MAX_T):
        ctr += 1
        # Select an action
        state_0 = obv
        action, action_index = select_action(state_0)
        obv, reward, terminated, truncated, info = manager.step(agent_id, action)
        if not info['riddle_type'] == None:
            if(info['riddle_type'] not in r):
                r.append(info['riddle_type'])
                solved+=1
            solution = riddle_solvers[info['riddle_type']](info['riddle_question'])
            obv, reward, terminated, truncated, info = manager.solve_riddle(info['riddle_type'], agent_id, solution)

        print(ctr)
        # if((solved>=2 and ctr>50)):
        #     break;
        # THIS IS A SAMPLE TERMINATING CONDITION WHEN THE AGENT REACHES THE EXIT
        # IMPLEMENT YOUR OWN TERMINATING CONDITION
        if np.array_equal(obv[0], (9,9)):
            manager.set_done(agent_id)
            break # Stop Agent

        if RENDER_MAZE:
            manager.render(agent_id)

        states[t] = [obv[0].tolist(), action_index, str(manager.get_rescue_items_status(agent_id))]


if __name__ == "__main__":

    sample_maze = get_maze()
    # sample_maze = np.array([[4 ,4, 4, 4, 4, 2, 4, 4, 2, 2],[8, 4, 4, 4, 2, 2, 8, 4, 4, 2],[8, 8, 1, 4, 2, 4, 4, 8, 4, 2],[8, 4, 8, 2, 4, 8, 8, 1, 1, 2],[2, 8, 2, 1, 2, 4, 8, 2, 1, 1],[4, 8, 2, 8, 1, 8, 2, 1, 2, 8],[8, 4, 2, 8, 4, 2, 1, 8, 4, 8],[8, 8, 1, 8, 8, 2, 1, 1, 8, 2],[8, 4, 8, 8, 1, 1, 4, 8, 8, 2],[8, 1, 1, 8, 1, 1, 8, 1, 1, 1]])
    # sample_maze = np.array([[4, 4, 2, 1, 1, 1, 2, 1, 1, 1],[2 ,1 ,2 ,4 ,8 ,1 ,1 ,8 ,4 ,8],[2 ,1 ,1 ,4 ,2 ,4 ,4 ,8 ,1 ,1],[4 ,2 ,8 ,8 ,2 ,2 ,8 ,1 ,2 ,8],[8 ,4 ,2 ,8 ,2 ,1 ,8 ,1 ,4 ,8],[8 ,2 ,1 ,1 ,1 ,4 ,2 ,8 ,1 ,1],[8 ,2 ,8 ,8 ,8 ,1 ,1 ,2 ,1 ,1],[4 ,4 ,4 ,8 ,2 ,4 ,8 ,1 ,2 ,8],[4 ,4 ,8 ,2 ,2 ,8 ,4 ,4 ,4 ,2],[4 ,8 ,1 ,1 ,4 ,8 ,1 ,1 ,1 ,1]])
#     [[4 2 1 1 1 4 4 2 2 1]
#  [2 1 4 8 8 1 2 1 2 8]
#  [4 4 8 4 8 8 1 8 1 8]
#  [8 1 4 8 1 8 2 2 1 1]
#  [8 8 8 1 4 8 4 2 8 8]
#  [8 1 1 8 8 4 2 1 2 8]
#  [8 1 4 2 1 8 2 2 2 8]
#  [4 8 4 4 4 8 2 1 2 8]
#  [4 8 8 2 1 1 4 2 2 8]
#  [4 8 1 1 4 8 1 1 1 8]]

# [[4 2 1 2 1 1 1 1 1 1]
#  [8 2 8 1 4 4 4 4 8 1]
#  [2 1 8 4 4 4 4 4 2 1]
#  [2 8 4 2 1 1 1 1 1 8]
#  [4 4 8 1 1 2 1 1 4 8]
#  [8 2 1 1 8 1 4 4 8 8]
#  [8 2 4 4 4 4 8 8 2 8]
#  [8 2 8 2 2 1 8 1 1 8]
#  [8 1 1 2 2 8 2 4 8 1]
#  [8 1 8 1 1 8 4 4 4 8]]
    print(sample_maze)

    agent_id = "9" # add your agent id here
    
    manager = MazeManager()
    manager.init_maze(agent_id, maze_cells=sample_maze)
    env = manager.maze_map[agent_id]

    riddle_solvers = {'cipher': cipher_solver, 'captcha': captcha_solver, 'pcap': pcap_solver, 'server': server_solver}
    maze = {}
    states = {}

    
    maze['maze'] = env.maze_view.maze.maze_cells.tolist()
    maze['rescue_items'] = list(manager.rescue_items_dict.keys())

    MAX_T = 5000
    RENDER_MAZE = True
    

    local_inference(riddle_solvers)

    with open("./states.json", "w") as file:
        json.dump(states, file)

    
    with open("./maze.json", "w") as file:
        json.dump(maze, file)
    