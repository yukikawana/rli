#!/usr/bin/python
from collections import defaultdict
import re
import random
import numpy as np
import sys
import math


print_move = True

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
q = lambda: -4.
q = lambda: -float('INF')
c = lambda: 0.
Q = defaultdict(q)
C = defaultdict(c)
# ff = lambda: (0, 0)
eps = 1e-9
eps = 0.5
max_speed = 5
gamma = 1.
S = 'S'
X = 'X'
G = 'G'
W = 1.
actions = []
for x in [-1, 0, 1]:
    for y in [-1, 0,1]:
        actions.append((y, x))
ff = lambda: [1./len(actions)]*(len(actions))
pi = defaultdict(ff)
random.seed(0)


def is_intersect(pos1, pos2):
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

def generate_episode():
    episode = []
    start_poss = char_poss(S)
    start_pos = (0, start_poss[random.randint(0, len(start_poss)-1)])
    speed = (0, 0)
    state = (start_pos, speed)
    while True:
    #for i in xrange(0, 100):
        mult = np.random.multinomial(1, pi[state], size=1)
        action = actions[mult.argmax()]
        #action = actions[random.randint(0, len(actions)-1)]
        current_pos = state[0]
        current_speed = state[1]
        new_speed = (max(0, min(5, action[0] + current_speed[0])), max(0, min(5, action[1] + current_speed[1])))
        if new_speed == (0, 0):
            if random.randint(0,1) == 1:
                new_speed = (0, 1)
            else:
                new_speed = (1, 0)
        new_pos = (current_pos[0]+new_speed[0], current_pos[1]+new_speed[1])
        reward = -1.

        line = is_intersect(current_pos, new_pos)
        for ele in line:
            if ele[0] > hight - 1 or ele[1] > width -1 or lines[ele[0]][ele[1]] == ' ':
                #print new_pos, hight, width, start_poss, current_pos
                start_pos = (0, start_poss[random.randint(0, len(start_poss)-1)])
                new_pos = start_pos
                new_speed = (0, 0)
                break
            if lines[ele[0]][ele[1]] == 'G':
                reward = 0.
                episode.append((state, action, reward))
                return episode
        episode.append((state, action, reward))
        state = (new_pos, new_speed)
    return episode


def draw_trajectory():
    global pi
    trajectory = lines[:]
    start_poss = char_poss(S)
    goal_poss = char_poss(G)
    current_pos = (0, start_poss[random.randint(0, len(start_poss)-1)])
    current_speed = (0, 0)
    if print_move:
        line = trajectory[current_pos[0]]
        line = list(line)
        line[current_pos[1]] = '#'
        trajectory[current_pos[0]]= ''.join(line)
        for line in trajectory:
            print line
        # trajectory = lines[:]
    while True:
        accel = actions[np.asarray(pi[(current_pos, current_speed)]).argmax()]
        new_speed_y = max(0, min(5, accel[0] + current_speed[0]))
        new_speed_x = max(0, min(5, accel[1] + current_speed[1]))
        if new_speed_y == 0 and new_speed_x == 0:
            if random.randint(0,1) == 1:
                new_speed_y = 1
            else:
                new_speed_x = 1
        new_speed = (new_speed_y, new_speed_x)
        # new_speed = (max(1, abs(min(5, accel[0] + current_speed[0]))), max(1, abs(min(5, accel[1] + current_speed[1]))))
        new_pos = (current_pos[0]+new_speed[0], current_pos[1]+new_speed[1])
        line = is_intersect(current_pos, new_pos)
        print line, new_pos, current_pos
        for ele in line:
            if ele[0] > hight - 1 or ele[1] > width -1 or lines[ele[0]][ele[1]] == ' ':
                print 'course out'
                return 0
            elif lines[ele[0]][ele[1]] == 'G':
                line1 = trajectory[ele[0]]
                line1 = list(line1)
                line1[ele[1]] = '#'
                trajectory[ele[0]]= ''.join(line1)
                line2 = trajectory[current_pos[0]]
                trajectory[current_pos[0]]= ''.join(line2)
                for line3 in trajectory:
                    print line3
                print 'made it!'
                return 1
            else:
                line1 = trajectory[ele[0]]
                line1 = list(line1)
                line1[ele[1]] = '.'
                trajectory[ele[0]]= ''.join(line1)
        line2 = trajectory[new_pos[0]]
        line2 = list(line2)
        line2[new_pos[1]] = '*'
        trajectory[new_pos[0]]= ''.join(line2)
        line2 = trajectory[current_pos[0]]
        line2 = list(line2)
        line2[current_pos[1]] = '*'
        trajectory[current_pos[0]]= ''.join(line2)
        for line3 in trajectory:
            print line3
        current_pos = new_pos
        current_speed = new_speed
    return 0


# while True:
for count in xrange(0, 10000):
    print 'count ', count
    W = 1.
    returns = 0.
    episode = generate_episode()
    for state, action, reward in episode[::-1]:
        print reward
        #state = t[0]
        #action = t[1]
        #reward = t[2]
        returns = returns * gamma + reward
        C[(state, action)] += W
        '''
        print ''
        print 'W ', W
        print 'R ', returns
        print 'Q ', Q[(states[t], actions[t])]
        print W / C[(states[t], actions[t])]
        print  (returns - Q[(states[t], actions[t])])
        '''
        Q[(state, action)] += W / C[(state, action)] * (returns - Q[(state, action)])
        '''
        print 'Q ', Q[(states[t], actions[t])]
        print 'C ', C[(states[t], actions[t])]
        '''
        # printn actions
        #print count, 't ', t
        #'''
        '''
        for a in actions:
            print 'Q#', Q[(state, a)]
        '''
        selected_action = 0
        for i in xrange(0, len(actions)):
            pi[state][i] = eps / float(len(actions))
        selected_action = np.asarray([Q[(state, a)] for a in actions]).argmax()
        pi[state][selected_action] = 1. - eps + eps / float(len(actions))
        if not actions[selected_action] == action:
        #if False:
            break
        else:
            #W = W * 1. / pi[states[t]][np.array(states[t]).argmax()]
            # W = 1.
            # W = W * 1. / (1. / len(actions))
            W = W * 1. / pi[state][selected_action]
            # W = W * pi[states[t]][actions.index(actions[t])] / len(actions)
        #W = W * pi[states[t]][np.array(states[t]).argmax()] / (1. / len(actions))
    if draw_trajectory()  == 1:
        print 'done', count
        #sys.exit(0)
