import sys
import numpy as np
import math
import random
import json
import requests

from riddle_solvers import *

### the api calls must be modified by you according to the server IP communicated with you
#### students track --> 16.170.85.45
#### working professionals track --> 13.49.133.141
server_ip = '16.170.85.45'

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
    "1, -1": 'E',
    "1, 1": 'E',
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


def move(agent_id, action):
    response = requests.post(f'http://{server_ip}:5000/move', json={"agentId": agent_id, "action": action})
    return response

def solve(agent_id,  riddle_type, solution):
    response = requests.post(f'http://{server_ip}:5000/solve', json={"agentId": agent_id, "riddleType": riddle_type, "solution": solution}) 
    print(response.json()) 
    return response

def get_obv_from_response(response):
    directions = response.json()['directions']
    distances = response.json()['distances']
    position = response.json()['position']
    obv = [position, distances, directions] 
    return obv

ctr = 0
solved = 0        
def submission_inference(riddle_solvers):
    response = requests.post(f'http://{server_ip}:5000/init', json={"agentId": agent_id})
    obv = get_obv_from_response(response)
    global ctr,solved

    while(True):
        ctr += 1
        # Select an action
        state_0 = obv
        action, action_index = select_action(state_0) # Random action
        response = move(agent_id, action)
        if not response.status_code == 200:
            print(response)
            break

        obv = get_obv_from_response(response)
        print(response.json())

        if not response.json()['riddleType'] == None:
            solution = riddle_solvers[response.json()['riddleType']](response.json()['riddleQuestion'])
            response = solve(agent_id, response.json()['riddleType'], solution)
            solved+=1
                


        if ctr>=50 and ctr<60 and solved >= 2:
            response = requests.post(f'http://{server_ip}:5000/leave', json={"agentId": agent_id})
            break

        # THIS IS A SAMPLE TERMINATING CONDITION WHEN THE AGENT REACHES THE EXIT
        # IMPLEMENT YOUR OWN TERMINATING CONDITION
        if np.array_equal(response.json()['position'], (9,9)):
            response = requests.post(f'http://{server_ip}:5000/leave', json={"agentId": agent_id})
            break


if __name__ == "__main__":
    agent_id = "U3VyPaWVF0"
    riddle_solvers = {'cipher': cipher_solver, 'captcha': captcha_solver, 'pcap': pcap_solver, 'server': server_solver}
    submission_inference(riddle_solvers)