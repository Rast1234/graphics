# -*- coding=utf-8 -*-
__author__ = 'rast'

from LinkedList import LinkedList
from intersect import segmentIntersection
from main import randomColor
from pprint import pprint
import GlobalQueue


testPoly_ = [(11, 132),
             (390, 134),
             (387, 174),
             (44, 178),
             (49, 195),
             (299, 204),
             (299, 230),
             (51, 225),
             (54, 248),
             (420, 246),
             (420, 282),
             (14, 274)
        ]

testPoly = [(108, 190),
            (161, 120),
            (355, 128),
            (394, 227),
            (304, 470),
            (111, 419),
            (156, 300),
            (262, 284),
            (250, 338),
            (320, 340),
            (349, 178)
        ]




testRect = [142, 100, 278, 300]  # x1, y1, x2, y2

class Kind(object):
    neutral = 'neutral'
    incoming = 'incoming'
    outgoing = 'outgoing'

class BravePoint(object):
    def __init__(self, p, k):
        self.point = p
        self.kind = k
        self.visited = False
    def __str__(self):
        return("{}-{}-{}".format(self.point, self.kind[0].upper(), str(self.visited)[0]))

    def __repr__(self):
        return self.__str__()

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
            candidates = []
            while otherNode.hasNext():
                nextOtherNode = otherNode.next
                otherSeg = (otherNode.data, nextOtherNode.data)

                intersection, info = segmentIntersection(seg, otherSeg)
                kind = None
                if intersection:
                    kind = Kind.incoming if info['sign'] < 0 else Kind.outgoing
                    tpl = (intersection, kind)
                    #print(seg, otherSeg, tpl)

                    #node.insertAfter((intersection, kind))
                    #otherNode.insertAfter((intersection, kind))
                    candidates.append(tpl)
                    #print("{} : {}  x  {}".format(info['sign'], seg, otherSeg))
                #this is for debugging
                debugResult.append((intersection, seg, otherSeg, kind))
                print("{0} :: {1} :: {2}".format(intersection, seg, otherSeg))
                otherNode = otherNode.next  # !!!!

            #print("----1>> ", candidates)
            candidates = sortByDist(node.data[0][0], node.data[0][1], candidates)
            result += candidates
            #print("----2>> ", candidates)

            node = node.next  # !!!
            result.append(node.data)

        GlobalQueue.queue = GlobalQueue.Queue(debugResult)
        return result
        #return linkedPoints.toList(), linkedOtherPoints.toList()

    def __sub__(self, other):
        """
        Subtraction of polygons
        """
        sequence = []

        # get raw points lists without duplication first-last
        tmp = [BravePoint(p,k) for p, k in self.points[:-1]]
        tmp2 = [BravePoint(p,k) for p, k in other.points[:-1]]
        tmp2.reverse()  # useful
        points = LinkedList()
        points.load(tmp)
        points.setEndless(True)

        otherPoints = LinkedList()
        otherPoints.load(tmp2)
        otherPoints.setEndless(True)

        pprint(tmp)
        pprint(tmp2)
        p = points.first
        while p.next is not points.first:
            d = p.data
            if d.kind != Kind.outgoing or d.visited:
                p = p.next
                continue
            # brave new polygon!
            newbies = getPointsUntilExit(points, otherPoints, p.data)
            print(newbies)
            sequence.append(newbies)
        print sequence

        result = []
        for lol in sequence:
            tmp = [bp.point for bp in lol]
            kinds = [Kind.neutral]*len(tmp)
            poly = Poly(points=zip(tmp, kinds))
            result.append(poly)
        return result

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

def getPointsUntilExit(primary, secondary, bravePoint):
    result = [bravePoint]
    if bravePoint.visited:
        # my hero!
        return result #find bravePoint in primary
    bravePoint.visited = True
    ptr = findPoint(primary, bravePoint)
    next = ptr.next
    while(next.data.kind == Kind.neutral):
        result.append(next.data)
        next.data.visited = True
        next = next.next
        #stop!
    #result.append(next)
    lastPoint = next.data
    print("tmp={}, switching on {}".format(result, lastPoint))
    return result + getPointsUntilExit(secondary, primary, lastPoint)

def findPoint(points, bravePoint):
    """
    Probably infinite
    """
    current = points.first
    while(current.hasNext()):
        #print current.data, bravePoint
        if current.data.point == bravePoint.point:
            return current
        current = current.next

def sortByDist(x,y, points):
    f = lambda (a, _): (x-a[0])**2 + (y-a[1])**2
    points.sort(key=lambda x: f(x))  # sorted inplace by distance from point, ascending
    return points



"""
вт 16:00 на кафедре
чт 14:20
"""