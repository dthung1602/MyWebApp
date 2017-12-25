# -*- coding: UTF-8 -*-

from copy import copy
from string import uppercase

from Handler import Handler as Hl


class EnigmaRequestHandler(Hl):
    """Handle requests for enigma simulator"""

    page_title = "Enigma Simulator"

    def render(self, *args, **kwargs):
        """
            Override supper method
            Add default settings for enigma simulator if no setting is provided
        """
        if "w" in kwargs:
            super(EnigmaRequestHandler, self).render(*args, **kwargs)
        else:
            super(EnigmaRequestHandler, self).render(*args,
                                                     w=[None, 'I', 'II', 'III', 'IV'],
                                                     p=[None, 'A', 'A', 'A', 'A'],
                                                     rw='B', pb={}, rs=True, tf=True, **kwargs)

    def get(self):
        self.render("enigma.html")

    def post(self):
        # get data
        w1 = self.request.get("w1")
        w2 = self.request.get("w2")
        w3 = self.request.get("w3")
        w4 = self.request.get("w4")

        p1 = self.request.get("p1")
        p2 = self.request.get("p2")
        p3 = self.request.get("p3")
        p4 = self.request.get("p4")

        rw = self.request.get("rw")
        pb = [self.request.get(c) for c in uppercase]

        rs = self.request.get("reset")
        tf = self.request.get("textformat")

        # check if data is incomplete
        attr_len = [len(w1), len(w2), len(w3), len(w4), len(p1), len(p2), len(p3), len(p4), len(pb), len(rw)]
        if 0 in attr_len and sum(attr_len) > 0:
            self.render("enigma.html", error="Fehlende Einstellung!")
            return

        # process string and render html
        try:
            enigma = Enigma(w1, w2, w3, w4, p1, p2, p3, p4, rw, pb, rs, tf)
            text = enigma.process_string(self.request.get("text"))
            self.render("enigma.html", text=text,
                        w=[None, w1, w2, w3, w4], p=enigma.pos, rw=rw, pb=enigma.pb, rs=rs, tf=tf)
        except (ValueError, KeyError, IndexError, TypeError):
            self.render("enigma.html", error="Ungültige Einstellung!")
        except:
            self.error(500)


###################################################
#                 Enigma engine                   #
###################################################

wheels = {
    'I': ['Q', 'T', 'P', 'G', 'S', 'K', 'M', 'Y', 'N', 'U', 'O', 'H', 'I',
          'B', 'E', 'R', 'Z', 'C', 'D', 'F', 'V', 'A', 'W', 'X', 'L', 'J'],
    'II': ['H', 'A', 'D', 'W', 'X', 'S', 'V', 'J', 'Z', 'Q', 'O', 'C', 'I',
           'F', 'R', 'G', 'M', 'E', 'P', 'N', 'L', 'K', 'T', 'U', 'Y', 'B'],
    'III': ['H', 'E', 'Y', 'K', 'R', 'S', 'X', 'G', 'B', 'T', 'L', 'Z', 'U',
            'C', 'A', 'W', 'J', 'O', 'I', 'Q', 'D', 'M', 'P', 'F', 'V', 'N'],
    'IV': ['E', 'M', 'A', 'U', 'N', 'K', 'D', 'S', 'W', 'O', 'X', 'I', 'V',
           'Q', 'R', 'B', 'L', 'T', 'J', 'P', 'Y', 'H', 'F', 'Z', 'C', 'G'],
    'V': ['C', 'V', 'D', 'J', 'K', 'X', 'S', 'P', 'F', 'N', 'G', 'Z', 'T',
          'H', 'Y', 'L', 'Q', 'O', 'M', 'U', 'A', 'B', 'W', 'E', 'R', 'I'],
    'VI': ['L', 'C', 'D', 'B', 'V', 'F', 'I', 'E', 'P', 'G', 'M', 'A', 'K',
           'R', 'Y', 'O', 'S', 'X', 'T', 'U', 'N', 'J', 'Q', 'H', 'Z', 'W'],
    'VII': ['B', 'Y', 'C', 'P', 'S', 'D', 'H', 'T', 'L', 'Q', 'N', 'V', 'X',
            'F', 'M', 'U', 'E', 'J', 'I', 'G', 'W', 'K', 'O', 'A', 'R', 'Z'],
    'VIII': ['M', 'P', 'X', 'F', 'L', 'T', 'K', 'C', 'U', 'B', 'Q', 'G', 'D',
             'V', 'E', 'N', 'Z', 'W', 'A', 'H', 'O', 'R', 'S', 'I', 'Y', 'J']
}

reflector_wheels = {
    'B': {'A': 'T', 'C': 'O', 'B': 'K', 'E': 'Q', 'D': 'G', 'G': 'D', 'F': 'X', 'I': 'R', 'H': 'Y',
          'K': 'B', 'J': 'S', 'M': 'P', 'L': 'V', 'O': 'C', 'N': 'U', 'Q': 'E', 'P': 'M', 'S': 'J',
          'R': 'I', 'U': 'N', 'T': 'A', 'W': 'Z', 'V': 'L', 'Y': 'H', 'X': 'F', 'Z': 'W'},
    'C': {'A': 'J', 'C': 'S', 'B': 'Q', 'E': 'F', 'D': 'H', 'G': 'U', 'F': 'E', 'I': 'N', 'H': 'D',
          'K': 'L', 'J': 'A', 'M': 'R', 'L': 'K', 'O': 'W', 'N': 'I', 'Q': 'B', 'P': 'T', 'S': 'C',
          'R': 'M', 'U': 'G', 'T': 'P', 'W': 'O', 'V': 'Y', 'Y': 'V', 'X': 'Z', 'Z': 'X'}
}


class Enigma:
    def __init__(self, w1, w2, w3, w4, p1, p2, p3, p4, rw, pb, rs, tf):
        """
            @:param w[i]: wheel settings, range: I, II, ... VIII
            @:param p[i]: first letter settings, range: ABC...Z
            @:param rw: reflect wheel, range BC
            @:param pb: plug board setting, range: permutation of ABC...Z
            @:param rs: whether to reset machine to init state
            @:param tf: whether to keep text format
        """

        # wheels
        self.wheel = [
            copy(wheels[w1]),
            copy(wheels[w2]),
            copy(wheels[w3]),
            copy(wheels[w4]),
        ]
        s = set()
        s.update([w1, w2, w3, w4])
        if len(s) < 4:  # all wheels must be different
            raise ValueError

        # init letters
        self.pos = [None, p1, p2, p3, p4]
        for i in xrange(4):
            p = self.wheel[i].index(self.pos[i + 1])
            self.wheel[i] = self.wheel[i][p:] + self.wheel[i][:p]

        # reflect wheel and plug board
        self.rw = reflector_wheels[rw]
        self.pb = self.create_plug_board(pb)

        # reset & text format
        self.rs = rs
        self.tf = tf

    def process_string(self, text):
        """encrypt/decrypt a string"""
        new_text = ""

        if not self.tf:
            # remove text format
            for char in [c for c in text.upper() if c.isalpha()]:
                new_text += self.process_char(char)
                if len(new_text) % 5 == 4:
                    new_text += " "
        else:
            # keep text format
            for char in text:
                if char.isalpha():
                    capital = char.isupper()
                    new_char = self.process_char(char.upper())
                    new_text += new_char if capital else new_char.lower()
                else:
                    new_text += char

        # keep wheel position
        if not self.rs:
            self.pos = [None] + [self.wheel[i][0] for i in xrange(4)]

        return new_text

    def process_char(self, char):
        """encrypt/decrypt a single char"""
        # plug board
        char = self.pb.get(char, char)

        # wheels
        A = ord('A')
        for i in xrange(4):
            char = self.wheel[i][ord(char) - A]

        # reflect
        char = self.rw[char]

        # wheels
        for i in xrange(3, -1, -1):
            char = chr(self.wheel[i].index(char) + A)

        # plug board
        char = self.pb.get(char, char)

        self.rotate(0)
        return char

    def rotate(self, w):
        """change state of enigma machine"""
        self.wheel[w] = self.wheel[w][1:] + self.wheel[w][0:1]
        if self.wheel[w][0] == 'A' and w < 3:
            self.rotate(w + 1)

    @staticmethod
    def create_plug_board(pb):
        """create a dictionary base on the given permutation of ABC...Z"""
        plug_board = {uppercase[i]: pb[i] for i in xrange(26) if pb[i]}
        for c in uppercase:
            if c in plug_board and plug_board[plug_board[c]] != c:
                raise ValueError
        return plug_board
