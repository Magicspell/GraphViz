from typing import Tuple, List
import math

POLARITY = 1                # 1: Magnets have same polarity and repell, -1: magnets have opposite and attract
PERMEABILITY = 0.03         # Less permeability means less magnetic force.
MOMENT_MUL = 0.2              # Strength of moments.

# F = (u/4pi) * (m1*m2/r^2)
# Returns the displacment the object should receive, in x-y tuple
def apply_mag(object : List[int], other : List[int], m1 : int, m2 : int) -> List[int]:
    if m1 == 0: m1 = 1
    if m2 == 0: m2 = 1
    m1 = m1*MOMENT_MUL
    m2 = m2*MOMENT_MUL
    x_dist = abs(object[0] - other[0])
    y_dist = abs(object[1] - other[1])
    dist = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))

    # Magnitude (hypotenuse) of magnetic force
    d = (4 * math.pi * math.pow(dist, 3))
    if round(d, 6) == 0: d = PERMEABILITY*5
    F = PERMEABILITY * m1 * m2 / d

    # Find the x-y components of F
    x_mul = (object[0] - other[0])/dist if dist != 0 else (object[0] - other[0])/0.001
    y_mul = (object[1] - other[1])/dist if dist != 0 else (object[0] - other[0])/0.001
    return [POLARITY*F*x_mul, POLARITY*F*y_mul]

# Returns list of objects after applying magnetic forces onece
def update_objects(objects : List[List[int]], degrees) -> List[List[int]]:
    new_objs = []

    o_i = 0
    for o in objects:
        to_move = [0, 0]

        other_i = 0
        for other in objects:
            if o_i != other_i:
                new_move = apply_mag(o, other, degrees[o_i], degrees[other_i])
                to_move[0] += new_move[0]
                to_move[1] += new_move[1]
            other_i += 1
        new_objs.append([o[0] + to_move[0], o[1] + to_move[1]])
        o_i += 1
    return new_objs

def update_object(object : Tuple[int], others : List[List[int]]) -> Tuple[int]:
    to_move = [0, 0]

    for other in others:
        new_move = apply_mag(object, other)
        to_move[0] += new_move[0]
        to_move[1] += new_move[1]
    return ([object[0] + to_move[0], object[1] + to_move[1]])