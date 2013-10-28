
__author__ = 'rast'

from LinkedList import LinkedList
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

    def __init__(self, points=[], color=None):
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
            yield self.points[i][0], self.points[i+1][0]

    def extendWithIntersectionPoints(self, other):
        """
        Update current points list,
        extended with intersection points
        """
        debugResult = []
        first = True
        result = []

        linkedPoints = LinkedList()
        linkedPoints.load(self.points)
        linkedOtherPoints = LinkedList()
        linkedOtherPoints.load((other.points))

        node = linkedPoints[0]
        while node.hasNext():
            if first:
                result.append(node.data)
                first = False
            nextNode = node.next
            seg = (node.data, nextNode.data)

            otherNode = linkedOtherPoints[0]
            while otherNode.hasNext():
                nextOtherNode = otherNode.next
                otherSeg = (otherNode.data, nextOtherNode.data)

                intersection, info = segmentIntersection(seg, otherSeg)
                kind = None
                if intersection:
                    kind = Kind.incoming if info['sign'] < 0 else Kind.outgoing
                    tpl = (intersection, kind)
                    print(seg, otherSeg, tpl)

                    #node.insertAfter((intersection, kind))
                    #otherNode.insertAfter((intersection, kind))
                    result.append(tpl)
                    #print("{} : {}  x  {}".format(info['sign'], seg, otherSeg))
                #this is for debugging
                debugResult.append((intersection, seg, otherSeg, kind))
                #print("{0} :: {1} :: {2}".format(intersection, seg, otherSeg))
                otherNode = otherNode.next  # !!!!
            node = node.next  # !!!
            result.append(node.data)

        return result
        return linkedPoints.toList(), linkedOtherPoints.toList()

    def __sub__(self, other):
        """
        Subtraction of polygons
        """
        sequence = []

        # get raw points lists without duplication first-last
        points = [dict([["point",p], ["kind",k], ["visited", False]]) for p, k in self.points[:-1]]
        otherPoints = [dict([["point",p], ["kind",k], ["visited", False]]) for p, k in other.points[:-1]]




    def drawPoints(self, drawingFunc):
        """
        Draw points using callback
        """
        for point, kind in self.points:
            drawingFunc(point, kind=kind, color=self.color)

    def draw(self, drawingFunc):
        """
        Draw self on canvas, given in constructor
        """
        for a, b in self.iterSegments():
            drawingFunc(a, b, color=self.color)

    def __findFirstOutgoing(self):
        """
        Return position of first "outgoing" point
        """
        for i, (_, kind) in self.points:
            if kind == Kind.outgoing:
                return i
        return None

