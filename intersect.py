__author__ = 'rast'

from math import *

eps = 10**-6

class Pt(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __lt__(self, other):
        return self.x < other.x - eps or abs(self.x-other.x) < eps and self.y < other.y - eps
    def __gt__(self, other):
        return other < self
    def __eq__(self, other):
        return (self.x - other.x) < eps and (self.y - other.y) < eps
    def __ne__(self, other):
        return not self == other


class Line(object):
    def __init__(self, p, q):
        self.a = p.y - q.y
        self.b = q.x - p.x
        self.c = -1*self.a * p.x - self.b * p.y
        self.__normalize()

    def __normalize(self):
        z = sqrt(self.a**2 + self.b**2)
        if abs(z) > eps:
            self.a /= z
            self.b /= z
            self.c /= z

    def dist(self, p):
        return self.a * p.x + self.b * p.y + self.c

def det(a, b, c, d):
    return a*d-b*c

def between(l, r, x):  # DOUBLES
    print("{} <= {} <= {}".format(l,x,r))
    return min(l, r)-eps <= x <= max(l, r)+eps

def intersect_projection(a, b, c, d):  # DOUBLES
    if a > b:
        (a, b) = (b, a)
    if c > d:
        (c, d) = (d, c)
    return max(a, c) <= min(b, d)+eps

def __intersect(a, b, c, d):  # PTs
    if not intersect_projection(a.x, b.x, c.x, d.x) or \
            not intersect_projection(a.y, b.y, c.y, d.y):
        #print("No mutual Xs or Ys")
        return False

    m = Line(a, b)
    n = Line(c, d)

    zn = det(m.a, m.b, n.a, n.b)

    if abs(zn) < eps:
        if abs(m.dist(c)) > eps or abs(n.dist(a)) > eps:
            #print("One line, no intersection")
            return False
        if b < a:
            (a, b) = (b, a)
        if d < c:
            (c, d) = (d, c)
        #print("One line, intersection!")
        return max(a, c), min(b, d)
    else:
        X = -1*det(m.c, m.b, n.c, n.b) / zn
        Y = -1*det(m.a, m.c, n.a, n.c) / zn
        if between(a.x, b.x, X) and \
                between(a.y, b.y, Y) and \
                between(c.x, d.x, X) and \
                between(c.y, d.y, Y):
            #print("Point intersection!")
            return Pt(X, Y)
        #print("Point does not belong to segments")
        return False

def segmentIntersection(((x1, y1), (x2, y2)), ((x3, y3), (x4, y4))):
    a = Pt(x1, y1)
    b = Pt(x2, y2)
    c = Pt(x3, y3)
    d = Pt(x4, y4)
    result = __intersect(a, b, c, d)
    #print("__intersect: {0}".format(result))
    if not result:
        return False
    elif type(result) is Pt:  # one point touch
        return int(round(result.x)), int(round(result.y))
    elif type(result) is tuple and len(result) == 2:  # intersection by segment
        return None
