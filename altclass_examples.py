from altclass import *


def Pair(a, b):
    # Getters and setters will be generated locally
    return gendispatch(Pair, locals())  # MUST be present for /all/ function-classes


"""
This is roughly equivalent to the following:

    class Pair:
        def __init__(self, a, b):
            self.a = a
            self.b = b
"""


print(Pair(1, 2)("_a")())  # call the getter for a
print(Pair(1, 2)("_b")())

##########


def Coord_ext(_base, c, hoho):
    def gen_unique_id():
        return 2 ** _base("_a")() * 3 ** _base("_b")() * 5 ** c  # ;)

    def _hoho():
        return f"THIS THING IS {hoho}"

    return gendispatch(Coord_ext, locals())  # must still be present, even for
    # classes meant to extend others


Coord = lambda a, b, c, d: fcmerge(Coord, Pair(a, b), Coord_ext, (c, d))  # extend

"""
This is roughly equivalent to the following:

    class Coord(Pair):
        def __init__(self, a, b, c):
            super().__init__(a, b)
            self.c = c
    def gen_unique_id(self):
        return 2**self.a * 3**self.b * 5**self.c  # ;)
"""

print("-------")
print(Coord(1, 2, 3, 4)("_a")())  # call the getter for a
"""Above is equivalent to print(Coord(1, 2, 3).a)"""
print(Coord(1, 2, 3, 4)("_b")())
print(Coord(1, 2, 3, 4)("_c")())
print(Coord(1, 2, 3, 4)("gen_unique_id")())
print(Coord(1, 2, 3, 4)("_hoho")())
"""Above is equivalent to print(Coord(1, 2, 3).gen_unique_id())"""
