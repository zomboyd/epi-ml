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
        self.q_table = np.zeros((7, 10))
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
        self.load()

    def get_nb_suspects(self):
        tuiles = list(self.env.get_all_tuiles().values())
        nb_suspects = 0
        for t in tuiles:
            if hasattr(t, 'status'):
                if t.status and t.status.suspect:
                    nb_suspects += 1
        return nb_suspects

    def get_action(self, choices, question):
        import pdb; pdb.set_trace()
        state = np.random.randint(0, 4, (1, 4))
        score = np.random.randint(0, 24, 1)
        q_type = question.type.value
        np.append(state, q_type)
        np.append(state, len(choices))
        np.append(state, score)
        nb_suspects = self.get_nb_suspects()
        print(f'nb_ suspects : {nb_suspects}')
        if len(self.states) == 0 or np.random.randn() < 0.1:
            action = self.pick_a_random_action(choices)
        else:
            print('q_table ', self.q_table[state, :])
            action_index = np.argmax(self.q_table[state, :])
            if action_index in list(range(0, len(choices))):
                action = action_index
            else:
                print(f'not good {action_index}')
                action = self.pick_a_random_action(choices)
            print(f'action -> {action} || choices : {choices}')
            print(f'action -> {action} || choices : {choices}')
        self.states.append(state)
        reward = self.compute_reward(nb_suspects, score, self.epochs)
        next_state = np.random.randint(0, 4, (1, 7))
        self.history[q_type].append((state, action, choices, reward))
        self.update_table(state, next_state, action, reward, q_type)
        self.epochs += 1
        return action

    def update_table(self, state, next_state, action, reward, question):
        # Q[s,a] = Q[s,a] + lr*(r + y*np.max(Q[s1,:]) - Q[s,a])
        self.q_table[state, action] = self.q_table[state, action] + self.lr * \
            (reward + self.y * np.max(self.q_table[next_state, :]) - self.q_table[state, action])

    def compute_reward(self, state, action, question):
        return -1

    def pick_a_random_action(self, actions):
        action = actions[np.random.randint(0, len(actions))]
        if getattr(action, 'value', None):
            return action.value
        return action

    def read_train_file(self):
        try:
            data = json.loads(open(self.train_file, 'r'))
            return data.get('data')
        except:
            return self.q_table

    def load(self):
        if os.path.exists(self.train_file):
            b_new = json.load(open(self.train_file))
            self.q_table = np.array(b_new.get('data'))
            return self.q_table
        return self.q_table

    def save(self):
        data = {'data': self.q_table.tolist()}
        json.dump(data, open(self.train_file, 'w'))
        return True


class Inspector(Agent):

    def compute_reward(self, nb_suspects, score, nb_tour):
        return score + (8 - (nb_suspects * (1 / (nb_tour + 1))))

class Fantome(Agent):

    def compute_reward(self, score, nb_suspects, nb_tour):
        return score - (8 - (nb_suspects * (1 / (nb_tour + 1))))

