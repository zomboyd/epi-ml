import re
import copy
from collections import deque
from enum import Enum


class Tile:
    class Status(Enum):
        clean = 0
        suspect = 1

        def __repr__(self):
            return '<{c!s}.{str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return self.name

    class Color(Enum):
        rose = 1
        gris = 2
        rouge = 3
        marron = 4
        bleu = 5
        violet = 6
        blanc = 7
        noir = 8

        def __repr__(self):
            return '<{c!s}.{str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return self.name

    def __init__(self, color: Color, status: Status = None, position: int = None):
        self._color = color
        self._position = position
        self._status = status

    def __repr__(self):
        return '<{c!s}: {str!s}>'.format(c=self.__class__.__name__, str=self)

    def __str__(self):
        return '{_color!s}-{_position!s}-{_status!s}'.format(**self.__dict__)

    @property
    def color(self):
        return self._color

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status


class World():
    file_question = 'questions.txt'
    file_response = 'reponses.txt'
    file_info = 'infos.txt'

    class Score():
        def __init__(self, value=None, max=None):
            self.value = value
            self.max = max

        def __repr__(self):
            return '<{c!s}: {str!s}>'.format(c=self.__class__.__name__, str=self)

        def __str__(self):
            return '{value!s}/{max!s}'.format(**self.__dict__)

    class _Parse():

        @staticmethod
        def available_tiles(line: str):
            """ ex: Tuiles disponibles : [rose-3-clean, gris-4-clean] choisir entre 0 et 2 """
            q = line
            tiles = {
                Tile.Color[x[0]]: Tile(
                    Tile.Color[x[0]],
                    Tile.Status[x[2].strip()],
                    int(x[1].strip())
                ) for x in [x.strip().split('-') for x in q[q.index('[') + 1: q.index(']')].split(',')]
            }
            return tiles

        @staticmethod
        def available_pos(line: str):
            """ positions disponibles : {1, 3}, choisir la valeur """
            q = line
            return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

        @staticmethod
        def use_power():
            """ Voulez-vous activer le pouvoir (0/1) ?  """
            return [0, 1]

        @staticmethod
        def pouvoir_gris():
            """ Quelle salle obscurcir ? (0-9) """
            return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        @staticmethod
        def pouvoir_bleu_un():
            """ Quelle salle bloquer ? (0-9) """
            return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        def pouvoir_bleu_deux(line=''):
            """ Quelle sortie ? Chosir parmi : {0, 2} """
            return [int(x) for x in line[line.index('{') + 1:line.index('}')].split(',')]

        @staticmethod
        def pouvoir_violet(lst: list):
            """ Avec quelle couleur échanger (pas violet!) ?  """
            return [x for x in lst if x.color is not Tile.Color.violet]

        @staticmethod
        def pouvoir_blanc(line: str):
            """ rose-6-suspect, positions disponibles : {5, 7}, choisir la valeur """
            q = line
            return [int(x) for x in q[q.index('{') + 1:q.index('}')].split(',')]

    def __init__(self, jid: int):
        self._player_id = jid
        self._turn = None
        self._score = None
        self._shadow = None
        self._blocked = None
        self._current_tile = None
        self._list_question = deque([])
        self._game_tiles = {
            Tile.Color.rose: deque([Tile(Tile.Color.rose)]),
            Tile.Color.gris: deque([Tile(Tile.Color.gris)]),
            Tile.Color.rouge: deque([Tile(Tile.Color.rouge)]),
            Tile.Color.marron: deque([Tile(Tile.Color.marron)]),
            Tile.Color.bleu: deque([Tile(Tile.Color.bleu)]),
            Tile.Color.violet: deque([Tile(Tile.Color.violet)]),
            Tile.Color.blanc: deque([Tile(Tile.Color.blanc)]),
            Tile.Color.noir: deque([Tile(Tile.Color.noir)]),
        }

    def __repr__(self):
        return '<{c!s}: {str!s}>'.format(c=self.__class__.__name__, str=self)

    def __str__(self):
        return 'Tour={_tour!s}, {_score!s}, Ombre={_ombre!s}, Bloque={_bloque!s}'.format(**self.__dict__)

    def get_all_tuiles(self):
        return {k: self._game_tiles[k][0] for k in self._game_tiles}

    def get_tuile(self, color):
        if isinstance(color, str):
            return self._game_tiles[Tile.Color[color]][0]
        return self._game_tiles[color][0]

    def init_file(self):
        for file in [self.file_info, self.file_response, self.file_question]:
            path = './{jid}/{file}'.format(jid=self._player_id, file=file)
            with open(path, 'w+') as f:
                f.write("")

    def pull_question(self, file: str = file_question):
        path = './{jid}/{file}'.format(jid=self._player_id, file=file)
        with open(path, 'r') as f:
            return f.read().strip(), self._score, self._turn, self._shadow, self._blocked

    def push_response(self, text, file: str = file_response):
        path = './{jid}/{file}'.format(jid=self._player_id, file=file)
        with open(path, 'w') as f:
            return f.write(str(text))

    def is_end(self, file: str = file_info):
        path = './{jid}/{file}'.format(jid=self._player_id, file=file)
        with open(path, 'r') as f:
            x = list(f)
            if len(x) > 0:
                return "Score final" in (x[-1])
            return False

    def parse_word_state(self, line: str):
        """
        Tour:3, Score:10/22, Ombre:7, Bloque:{8, 9}
        """

        self._line = line
        r = re.search(r'^Tour:(?P<tour>[0-9]*),'
                      '.*Score:(?P<score-v>[0-9]*)/(?P<score-m>[0-9]*),'
                      '.*Ombre:(?P<ombre>[0-9]*),'
                      '.*Bloque:{(?P<bloque>.*)}$', line)
        self._turn = int(r.group('tour'))
        self._score = self.Score(value=r.group('score-v'),
                                 max=r.group('score-m'))
        self._shadow = int(r.group('ombre'))
        self._blocked = [int(x) for x in r.group('bloque').split(',')]

    def parse_question(self, line: str):
        q = None
        if 'Tuiles disponibles :' in line:
            self._current_tile = None
            t = self._Parse.available_tiles(line)
            self._append_to_hist(t)
            q = Question(self._current_tile, line, Question.Type.available_tile, t)

        elif 'positions disponibles :' in line:
            q = Question(self._current_tile, line, Question.Type.available_pos,
                         self._Parse.available_pos(line))

        elif 'Voulez-vous activer le pouvoir' in line:
            q = Question(self._current_tile, line, Question.Type.use_power,
                         self._Parse.use_power(line))

        # pouvoir gris
        elif 'Quelle salle obscurcir ? (0-9)' in line:
            q = Question(self._current_tile, line, Question.Type.pouvoir.gris,
                         self._Parse.pouvoir_gris(line))

        # pouvoir bleu 1
        elif 'Quelle salle bloquer ? (0-9)' in line:
            q = Question(self._current_tile, line, Question.Type.pouvoir.bleu,
                         self._Parse.pouvoir_bleu(line))

        # pouvoir bleu 2
        elif 'Quelle sortie ? Chosir parmi :' in line:
            q = Question(self._current_tile, line, Question.Type.pouvoir.bleu.deux,
                         self._Parse.pouvoir_bleu_deux(line))

        # pouvoir violet
        elif 'Avec quelle couleur échanger (pas violet!) ?' in line:
            q = Question(self._current_tile, line, Question.Type.pouvoir.violet,
                         self._Parse.pouvoir_violet(line, copy.deepcopy(self.get_all_tuiles()).values()))

        # pouvoir blanc
        elif ', positions disponibles :' in line:
            q = Question(self._current_tile, line, Question.Type.pouvoir.blanc,
                         self._Parse.pouvoir_blanc(line))

        if q is not None:
            self._list_question.appendleft(q)
        return q

    def _append_to_hist(self, lst: list):
        for k, v in self._game_tiles.items():
            if k in lst and k != lst[k]:
                self._game_tiles[k].appendleft(lst[k])

    @property
    def jid(self):
        return self._player_id

    @property
    def tour(self):
        return self._turn

    @property
    def score(self):
        return self._score

    @property
    def shadow(self):
        return self._shadow

    @shadow.setter
    def shadow(self, shadow):
        self._shadow = shadow

    @property
    def blocked(self):
        return self._blocked

    @blocked.setter
    def blocked(self, blocked):
        self._blocked = blocked

    @property
    def current_tile(self):
        return self._current_tile

    @current_tile.setter
    def current_tile(self, current_tile: Tile):
        self._current_tile = current_tile

    @property
    def list_question(self):
        return self._list_question

    @property
    def hist_tiles(self):
        return self._game_tiles


class skip(object):
    """
    Protects item from becoming an Enum member during class creation.
    """

    def __init__(self, value):
        self.value = value

    def __get__(self, instance, ownerclass=None):
        return self.value


class Question(list):
    class Type(Enum):
        unknown = 0
        available_tile = 1
        available_pos = 2
        use_power = 3

        @skip
        class pouvoir(Enum):
            gris = 4
            violet = 6
            blanc = 7

            @skip
            class bleu(Enum):
                un = 5.1
                deux = 5.2

                def __repr__(self):
                    return '<{!s}>'.format(self)

                def __str__(self):
                    return 'Type.pouvoir.{!s}.{!s}'.format(type(self).__name__, self.name)

            def __repr__(self):
                return '<{!s}>'.format(self)

            def __str__(self):
                return 'Type.{!s}.{!s}'.format(type(self).__name__, self.name)

        def __repr__(self):
            return '<{!s}>'.format(self)

        def __str__(self):
            return '{!s}.{!s}'.format(type(self).__name__, self.name)

    def __init__(self, tile: Tile, line: str, type: Type, *args):
        self._tile = tile
        self._line = line
        self._type = type
        list.__init__(self, *args)

    def __getitem__(self, key):
        return list.__getitem__(self, key)

    def __repr__(self):
        return '<{c!s}:{on!r} {t!r} {s!r}>'.format(c=self.__class__.__name__, on=self._tile,
                                                   t=self.type, s=list.__repr__(self))

    def __str__(self):
        return '{t!s} {s!s}'.format(t=self.type, s=list.__str__(self))

    @property
    def tile(self):
        return self._tile

    @property
    def line(self):
        return self._line

    @property
    def type(self):
        return self._type
