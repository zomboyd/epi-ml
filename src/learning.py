import numpy as np
import json
import os
import codecs
from game import Question

class Logger:
    def __init__(self, path, data):
        self.data = data
        self.filename = ''

    def save(self):
        pass

    def load(self):
        pass


class Agent:

    def __init__(self, player_id, env):
        self.player_id = player_id
        self.q_table = {
            Question.Type.activer_pouvoir.value: np.zeros((4, 2)),
            Question.Type.position_dispo.value: np.zeros((4, 8)),
            Question.Type.tuile_dispo.value: np.zeros((4, 8)),
        }
        self.states = []
        self.history = {
            Question.Type.activer_pouvoir.value: [],
            Question.Type.position_dispo.value: [],
            Question.Type.tuile_dispo.value: [],
            5.1: [],
            5.2: [],
            6: [],
            4: []
        }
        self.env = env
        self.epochs = 0
        self.train_file = f'./{player_id}/train.json'
        self.lr = .8
        self.y = .95
        # self.load()

    def get_nb_suspects(self):
        tuiles = list(self.env.get_all_tuiles().values())
        nb_suspects = 0
        for t in tuiles:
            if hasattr(t, 'status'):
                if t.status and t.status.suspect:
                    nb_suspects += 1
        return nb_suspects

    def get_action(self, choices, question):
        state = np.random.randint(0, 5, (1, 4))
        # state = np.array([1, 2, 2, 4]).reshape((1, 4))
        action = self.pick_a_random_action(choices)
        nb_suspects = self.get_nb_suspects()
        print(f'nb_ suspects : {nb_suspects}')
        q_type = question.type.value
        if getattr(action, 'value', None):
            action = action.value
        # if len(self.states) == 0 or np.random.randn() < 0.1:
        #     action = self.pick_a_random_action(choices)
        #     if getattr(action, 'value', None):
        #         action = action.value
        # else:
        #     action = int(self.q_table[q_type][state][np.argmax(self.q_table[q_type][state])])
            print(f'action -> {action} || choices : {choices}')
        self.states.append(state)
        reward = self.compute_reward(state, action, q_type)
        self.history[q_type].append((state, action, choices, reward))
        # self.update_table(state, state, action, reward, q_type)
        self.epochs += 1
        return action

    def update_table(self, state, next_state, action, reward, question):
        # Q[s,a] = Q[s,a] + lr*(r + y*np.max(Q[s1,:]) - Q[s,a])
        print(f'question : {question}')
        # try:
        self.q_table[question][state, action] = self.q_table[question][state, action] + self.lr * \
            (reward + self.y * np.max(self.q_table[question][next_state, :]) - self.q_table[question][state, action])
        # except IndexError:
        #     import pdb; pdb.set_trace()

    def compute_reward(self, state, action, question):
        return -1

    def pick_a_random_action(self, actions):
        return actions[np.random.randint(0, len(actions))]

    def read_train_file(self):
        try:
            data = json.loads(open(self.train_file, 'r'))
            return data.get('data')
        except:
            return self.q_table

    def load(self):
        if os.path.exists(self.train_file):
            obj_text = codecs.open(self.train_file, 'r',
                                   encoding='utf-8').read()
            b_new = json.loads(obj_text)
            self.q_table = np.array(b_new)
            return self.q_table
        return self.q_table

    def save(self):
        json.dump(self.q_table, codecs.open(self.train_file, 'w',
                                            encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)
        return True


class Inspector(Agent):

    def compute_reward(self, state, action, question):
        return -1


class Fantome(Agent):

    def compute_reward(self, state, action, question):
        return -1

