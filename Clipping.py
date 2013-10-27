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

class Kind(object):
    neutral = 'neutral'
    incoming = 'incoming'
    outgoing = 'outgoing'

class Poly(object):
    """
    Polygone with operations
    """

    def __init__(self, points=[], kinds=[], color=None):
        kinds = kinds if len(kinds) == len(points) else [Kind.neutral]*len(points)
        self.points = zip(points, kinds)

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
            yield self.points[i][0], self.points[i+1][0]

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
        kinds = []
        first = True
        for seg in self.iterSegments():
            if first:
                result.append(seg[0])
                kinds.append(Kind.neutral)
                first = False
            for otherSeg in otherPoly.iterSegments():
                intersection, info = segmentIntersection(seg, otherSeg)
                if intersection:
                    result.append(intersection)
                    kind = Kind.incoming if info['sign'] < 0 else Kind.outgoing
                    kinds.append(kind)
                    #print("{} : {}  x  {}".format(info['sign'], seg, otherSeg))
                #this is for debugging
                debugResult.append((intersection, seg, otherSeg))
                #print("{0} :: {1} :: {2}".format(intersection, seg, otherSeg))
            result.append(seg[1])
            kinds.append(Kind.neutral)
        #GlobalQueue.queue = GlobalQueue.Queue(debugResult)
        return result, kinds

    def drawPoints(self, drawingFunc):
        """
        Draw points using callback
        """
        for p, _ in self.points:
            drawingFunc(p, color=self.color)
