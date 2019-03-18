import sys
import logging
import game as _
from random import randrange

jid = '0'
role = "l'inspecteur" if jid == '0' else 'le fantome'
space_begin = '      '
formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs)03d - %(levelname)-8s:{role:12} - %(message)s'.format(
        role=role),
    datefmt='%H:%M:%S'
)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

log = logging.getLogger(__name__)
log.setLevel(logging.NOTSET)
log.addHandler(handler)

# passage
#
# 8--------9
# |        |
# |        |
# 4--5--6--7
# |        |
# 0--1--2--3
#

# passage secret
#
#   ________
#  /        \
# | 8--------9
# | |\      /|
#  \| \    / |
#   4--5--6--7
#   |  |  |  |\
#   0--1--2--3 |
#       \______/
#


class Process():

    passages = [{1, 4},
                {0, 2},
                {1, 3},
                {2, 7},
                {0, 5, 8},
                {4, 6},
                {5, 7},
                {3, 6, 9},
                {4, 9},
                {7, 8}]
    passages_rose = [{1, 4},
                     {0, 2, 5, 7},
                     {1, 3, 6},
                     {2, 7},
                     {0, 5, 8, 9},
                     {4, 6, 1, 8},
                     {5, 7, 2, 9},
                     {3, 6, 9, 1},
                     {4, 9, 5},
                     {7, 8, 4, 6}]

    def __init__(self, world: _.World):
        self.world = world
        self.func_map = {
            _.Question.Type.unknown: lambda x: log.info(x),
            _.Question.Type.available_tile: self.tuile_dispo,
            _.Question.Type.available_pos: self.position_dispo,
            _.Question.Type.use_power: self.activer_pouvoir,
            _.Question.Type.pouvoir.gris: self.pouvoir_gris,
            _.Question.Type.pouvoir.bleu.un: self.pouvoir_bleu_un,
            _.Question.Type.pouvoir.bleu.deux: self.pouvoir_bleu_deux,
            _.Question.Type.pouvoir.violet: self.pouvoir_violet,
            _.Question.Type.pouvoir.blanc: self.pouvoir_blanc,
        }

    def tuile_dispo(self, q, state):
        """
        question: Tuiles disponibles : [rose-3-clean, gris-4-clean] choisir entre 0 et 2
        response: id of the element in the list
        """
        lst = list(q)
        ret = randrange(len(lst))

        # for keeping track of the current played 'tuile'
        self.world.current_tile = self.world.get_tuile(lst[ret])
        return lst[ret]

    def position_dispo(self, q, state):
        """
        question: positions disponibles : {1, 3}, choisir la valeur
        response: an element of the list
        """

        lst = list(q)
        dct = {}
        tuiles = self.world.get_all_tuiles().values()
        a_tuiles = []
        for v in tuiles:
            if  v.position is not None and v.position in lst:
                a_tuiles.append(v)

        for k, v in dct.items():
            log.info(space_begin + '{!s}: {!s}'.format(k, v))
        suspects = list(filter(lambda t: t.status.value, a_tuiles))
        if len(suspects) > 0:
            ret = suspects[0].position
            print('ret suspect : ', ret)
            return ret
        ret = a_tuiles[0].position
        print('ret : ', ret)
        return ret

    def activer_pouvoir(self, q, state):
        """
        question: Voulez-vous activer le pouvoir (0/1) ?
        response: 0 or 1
        """
        use = [_.Tile.Color.noir, _.Tile.Color.gris]
        not_use = [_.Tile.Color.blanc]

        if self.world.current_tile is None:
            return 0
        if self.world.current_tile.Color in use:
            return 1
        elif self.world.current_tile.Color in not_use:
            return 0
        return 1

    def pouvoir_gris(self, q, state):
        """
        question: Quelle salle obscurcir ? (0-9)
        response: number between 0 and 9
        """
        lst = list(q)
        dct = {}
        for v in self.world.get_all_tuiles().values():
            if v.position is None:
                continue
            if v.position not in dct:
                dct[v.position] = {}
            if v.status not in dct[v.position]:
                dct[v.position][v.status] = []
            dct[v.position][v.status].append(v)

        for k, v in dct.items():
            log.info(space_begin + '{!s}: {!s}'.format(k, v))

        dct = {k: len(v) for k, v in dct.items()}
        dct = sorted(dct, key=dct.get)

        if len(dct) is not 0:
            ret = dct[0]
        else:
            ret = lst[randrange(len(lst))]

        return ret

    def pouvoir_bleu_un(self, q, state):
        """
        question: Quelle salle bloquer ? (0-9)
        response: number between 0 and 9
        """
        lst = list(q)
        res = randrange(len(lst))
        return res

    def pouvoir_bleu_deux(self, q, state):
        """
        question: Quelle sortie ? Chosir parmi : {0, 2}
        response: an element of the list
        """
        lst = list(q)
        res = randrange(len(lst))
        return lst[res]

    def pouvoir_violet(self, q, state):
        """
        question: Avec quelle couleur échanger (pas violet!) ?
        response: color of an element in the list
        """
        lst = list(q)
        res = randrange(len(lst))
        return lst[res].color

    def pouvoir_blanc(self, q, state):
        """
        question: rose-6-suspect, positions disponibles : {5, 7}, choisir la valeur
        response: an element of the list
        """
        lst = list(q)
        res = randrange(len(lst))
        return lst[res]

    def process_question(self, q: _.Question, game_state: {}):
        if q is None:
            return -1
        self.q = q
        res = self.take_action(q, game_state)
        log.info('{} {}'.format(space_begin, str(q)))
        return res

    def take_action(self, q: _.Question, game_state):
        ret = self.func_map[self.q.type](q, game_state)
        return ret


def lancer():
    old_question = None
    world = _.World(jid)
    process = Process(world)
    world.init_file()
    while not world.is_end():
        question = world.pull_question()
        if question != old_question and question != '':
            log.info('QUESTION: {}'.format(question[0]))
            game_state = world.get_game_state()
            question = world.parse_question(question[0])
            res = process.process_question(question, game_state)
            log.info('REPONSE: {}'.format(res))
            world.push_response(res)
            log.info('')
            old_question = question
    log.info('=== END')
