import numpy as np
from game import Question


class Env:

    def __init__(self):
        pass

    def reset(self):
        pass

    @property
    def action_space(self):
        return


output = np.zeros((1, 3))


def get_random_choice(size): return np.random.randint(0, size)


def get_questions():
    nb_q = 2
    questions = [Question.Type.position_dispo.value,
                 Question.Type.tuile_dispo.value, Question.Type.activer_pouvoir.value]
    if np.random.rand() > 0.4:
        return questions[:nb_q]
    return questions


ACTION_SPACE = 3
OBS_SPACE = 10
NB_GAMES = 100
NB_TURNS = 20

def get_next_step(a):
    # return: state, r, d, _
    return np.random.randint(0, 10, size=(1, 10)), np.random.randn() * 10, int(np.random.randint(0, 2)), -1


q_table = {
    Question.Type.activer_pouvoir.value: np.zeros((OBS_SPACE, 2)),
    Question.Type.position_dispo.value: np.zeros((OBS_SPACE, 10)),
    Question.Type.tuile_dispo.value: np.zeros((OBS_SPACE, 10)),
}

lr = .8
y = .95
jList = []
rList = []
for i in range(NB_GAMES):
    # Reset environment and get first new observation
    rAll = 0
    d = False
    for j in range(0, NB_TURNS):
        questions = get_questions()
        for question in questions:
            if question == Question.Type.activer_pouvoir.value:
                action = np.random.randint(0, 2)
            else:
                action = np.random.randint(0, 10)
            state = np.random.randint(0, 10, size=(1, 10))
            # Get new state and reward from environment
            s1, reward, d, _ = get_next_step(question)
            # Update Q-Table with new knowledge
            try:
                q_table[question][state, action] = q_table[question][state, action] + lr * \
                    (reward + y*np.max(q_table[question][s1, :]) -
                     q_table[question][state, action])
            except IndexError:
                import pdb
                pdb.set_trace()
            rAll += reward
            state = s1
        if d == True:
            break
    # jList.append(j)
    rList.append(rAll)
