#!/usr/bin/python
from collections import defaultdict
import re
import random
import numpy as np
import math
import os
import pickle
import dill


print_move = True
episode_num = 120000

course = \
'''\
                               
            XXXXXXXXXXXXXXXXXXG
           XXXXXXXXXXXXXXXXXXXG
           XXXXXXXXXXXXXXXXXXXG
      XXXXXXXXXXXXXXXXXXXXXXXXG
     XXXXXXXXXXXXXXXXXXXXXX    
     XXXXXXXXXXXXXXXXX         
    XXXXXXXXXXX                
    XXXXXXXXXXXX               
    XXXXXXXXXXXX               
       XXXXXXXXXX              
        XXXXXXXXXX             
      XXXXXXXXXXXX             
     XXXXXXXXXXXXX             
    XXXXXXXXXXXXX              
    XXXXXXXXXXX                
    XXXXXXXXXX                 
    XXXXXXXXXX                 
   XXXXXXXXXXX                 
   XXXXXXXXXXX                 
  XXXXXXXXXXX                  
  SSSSSSSSSSS                  '''
acourse = \
'''\
               
   XXXXXXXXXXXG
   XXXXXXXXXXXG
   XXXXXXXXXX  
   XXXX        
   XXXX        
    SSS        '''

print course
lines = course.split('\n')
lines.reverse()
width = len(lines[0])
hight = len(lines)
q = lambda: -6.
q = lambda: -float('INF')
q = lambda: -20.
c = lambda: 0.
Q = defaultdict(q)
C = defaultdict(c)
eps = 1e-9
eps = 0.5
max_speed = 5
gamma = 1.
start_char = 'S'
goal_char = 'G'
max_speed = 5
min_speed = 0
actions = []
for x in [-1, 0, 1]:
    for y in [-1, 0,1]:
        actions.append((y, x))
ff = lambda: [1./len(actions)]*(len(actions))
pi = defaultdict(ff)
random.seed(0)


def interpolation(pos1, pos2):
    if pos2[1] - pos1[1] <= 0:
        return [(y, pos1[1]) for y in xrange(pos1[0], pos2[0]+1)]
    elif pos2[0] - pos1[0] <= 0:
        return [(pos1[0], x) for x in xrange(pos1[1], pos2[1]+1)]
    else:
        
        a = float((pos2[0] - pos1[0] + 1)) / float((pos2[1] - pos1[1] + 1))
        b = pos1[0] - a * pos1[1]
        if pos2[1] - pos1[1] > pos2[0] - pos1[0]:
            return [(int(math.floor(a * x + b)), x) for x in xrange(pos1[1], pos2[1] + 1)]
        else:
            return [(y, int(math.floor((y - b) / a))) for y in xrange(pos1[0], pos2[0] + 1)]

def char_poss(char):
    return [m.start(0) for m in re.finditer(char, lines[0])]


def next_state(state, action):
    current_position = state[0]
    current_speed = state[1]
    new_speed = (max(min_speed, min(max_speed, action[0] + current_speed[0])), max(min_speed, min(max_speed, action[1] + current_speed[1])))
    if new_speed == (0, 0):
        if random.randint(0,1) == 1:
            new_speed = (0, 1)
        else:
            new_speed = (1, 0)
    new_position = (current_position[0]+new_speed[0], current_position[1]+new_speed[1])
    interpolated_line = interpolation(current_position, new_position)
    reward = -1.
    for interpolated_position in interpolated_line:
        if interpolated_position[0] > hight - 1 or interpolated_position[1] > width -1 or lines[interpolated_position[0]][interpolated_position[1]] == ' ':
            start_position_candidates = char_poss(start_char)
            start_position = (0, start_position_candidates[random.randint(0, len(start_position_candidates) - 1)])
            new_position = start_position
            new_speed = (0, 0)
            new_state = (new_position, new_speed)
            return new_state, reward
        if lines[interpolated_position[0]][interpolated_position[1]] == goal_char:
            reward = 0.
            new_state = (new_position, new_speed)
            return new_state, reward
    new_state = (new_position, new_speed)
    return new_state, reward


def generate_episode():
    episode = []
    start_position_candidates = char_poss(start_char)
    start_position = (0, start_position_candidates[random.randint(0, len(start_position_candidates) - 1)])
    initial_speed = (0, 0)
    state = (start_position, initial_speed)
    while True:
        action = actions[np.random.multinomial(1, pi[state], size=1).argmax()]
        new_state, reward = next_state(state, action)
        episode.append((state, action, reward))
        state = new_state
        if reward == 0.:
            break
    return episode


def draw_on_course(position, trajectory, char):
    line = list(trajectory[position[0]])
    line[position[1]] = char
    trajectory[position[0]]= ''.join(line)
    return trajectory


def draw_trajectory(start_position_x):
    trajectory = lines[:]
    start_position = (0, start_position_x)
    initial_speed = (0, 0)
    state = (start_position, initial_speed)
    trajectory[:] = draw_on_course(start_position, trajectory, '*')
    is_start = True
    G = 0
    goal_or_course_out = True
    while True:
        action = actions[np.asarray(pi[state]).argmax()]
        new_state, reward = next_state(state, action)
        G += reward
        interpolated_line = interpolation(state[0], new_state[0])
        for interpolated_position in interpolated_line:
            if interpolated_position[0] > hight - 1 or interpolated_position[1] > width -1 or lines[interpolated_position[0]][interpolated_position[1]] == ' ' or (lines[state[0][0]][state[0][1]] == start_char and not is_start):
                goal_or_course_out = False
                return goal_or_course_out, G, trajectory
            elif lines[interpolated_position[0]][interpolated_position[1]] == 'G':
                trajectory[:] = draw_on_course(interpolated_position, trajectory, '#')
                return goal_or_course_out, G, trajectory
            else:
                trajectory[:] = draw_on_course(interpolated_position, trajectory, '.')
        if not lines[new_state[0][0]][new_state[0][1]] == start_char:
            trajectory[:] = draw_on_course(new_state[0], trajectory, '*')
        trajectory[:] = draw_on_course(state[0], trajectory, '*')
        state = new_state
        is_start = False

if __name__ == "__main__":
    filename = 'racetrack_'+str(episode_num)+'.pickle'
    print filename
    if not os.path.exists(filename):
        for count in xrange(0, episode_num):
            print count,'th episode'
            W = 1.
            returns = 0.
            episode = generate_episode()
            for state, action, reward in episode[::-1]:
                returns = returns * gamma + reward
                C[(state, action)] += W
                Q[(state, action)] += W / C[(state, action)] * (returns - Q[(state, action)])
                selected_action = 0
                for i in xrange(0, len(actions)):
                    pi[state][i] = eps / float(len(actions))
                selected_action = np.asarray([Q[(state, a)] for a in actions]).argmax()
                pi[state][selected_action] = 1. - eps + eps / float(len(actions))
                if not actions[selected_action] == action:
                    break
                else:
                    W = W * 1. / pi[state][selected_action]

        obj = [pi, Q, C]
        with open(filename, 'wb') as f:
            pickle.dump(obj, f)
    else:
        with open(filename, 'rb') as f:
            obj = pickle.load(f)
            pi = obj[0]
            Q = obj[1]
            C = obj[2]

    start_positions = char_poss(start_char)
    for start_position_x in start_positions :
        print start_positions.index(start_position_x), 'th start position'
        goal_or_course_out, G, trajectory  = draw_trajectory(start_position_x)
        for line in trajectory[::-1]:
            print line
        if goal_or_course_out:
            print int(-G), 'steps to reach goal'
        else:
            print 'course out'
        print ''
        print ''
