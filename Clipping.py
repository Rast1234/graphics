__author__ = 'rast'

from intersect import segmentIntersection
from main import randomColor
import GlobalQueue

testPoly = [
    (168, 190),
    (221, 120),
    (415, 128),
    (454, 227),
    (364, 470),
    (171, 419),
    (216, 300),
    (322, 284),
    (310, 338),
    (380, 340),
    (409, 178),
]
testRect = [202, 113, 338, 291]  # x1, y1, x2, y2

class Poly(object):
    """
    Polygone with operations
    """

    def __init__(self, points, color=None):
        self.points = points

        if color is None:
            self.color = randomColor()
        else:
            self.color = color

        #normalize
        if self.points[0] != self.points[-1]:
            self.points.append(self.points[0])

    def iterSegments(self):
        """
        Iterate over self segments
        Segment is ((x1, y1), (x2, y2))
        """
        for i, _ in enumerate(self.points[:-1]):
            yield self.points[i], self.points[i+1]

    def draw(self, drawingFunc):
        """
        Draw self on canvas, given in constructor
        """
        for a, b in self.iterSegments():
            drawingFunc(a, b, color=self.color)

    def extendWithIntersectionPoints(self, otherPoly):
        """
        Update current points list,
        extended with intersection points
        """
        debugResult = []
        result = []
        for seg in self.iterSegments():
            for otherSeg in otherPoly.iterSegments():
                intersection, info = segmentIntersection(seg, otherSeg)
                result.append(seg[0])
                if intersection:
                    result.append(intersection)
                    print("{} : {}  x  {}".format(info['sign'], seg, otherSeg))
                result.append(seg[1])
                #this is for debugging
                debugResult.append((intersection, seg, otherSeg))
                #print("{0} :: {1} :: {2}".format(intersection, seg, otherSeg))
        GlobalQueue.queue = GlobalQueue.Queue(debugResult)
        return result

    def drawPoints(self, drawingFunc):
        """
        Draw points using callback
        """
        for p in self.points:
            drawingFunc(p, color=self.color)
