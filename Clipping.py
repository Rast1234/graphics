
__author__ = 'rast'

from LinkedList import LinkedList
from intersect import segmentIntersection
from main import randomColor
import GlobalQueue
from pprint import pprint

testPoly = [  # G ->
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
testRect = [202, 113, 338, 291]  # x1, y1, x2, y2  # [] ->

testPoly = [(11, 132),  # E
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

testPoly_ = [(108, 190),  # G
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
testRect = [142, 100, 278, 300]  # x1, y1, x2, y2  # []


class BravePoint(object):
    def __init__(self, p, k):
        self.point = p
        self.kind = k
        self.visited = False
    def __str__(self):
        return("{}-{}-{}".format(self.point, self.kind[0].upper(), str(self.visited)[0]))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.point == other.point


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
            candidates = []
            if first:
                candidates.append(node.data)
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
                    #print("seg, otherseg, tpl: ",seg, otherSeg, tpl)

                    #node.insertAfter((intersection, kind))
                    #otherNode.insertAfter((intersection, kind))
                    candidates.append(tpl)
                    #print("{} : {}  x  {}".format(info['sign'], seg, otherSeg))
                #this is for debugging
                debugResult.append((intersection, seg, otherSeg, kind))
                #print("{0} :: {1} :: {2}".format(intersection, seg, otherSeg))
                otherNode = otherNode.next  # !!!!
            node = node.next  # !!!

            sorted = lolsort(candidates, node.data)
            result += sorted

            result.append(node.data)

        GlobalQueue.queue.insert(debugResult)

        return filterDuplicates(result)

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


        tmp = [BravePoint(p,k) for p, k in self.points[:-1]]
        tmp2 = [BravePoint(p,k) for p, k in other.points[:-1]]
        tmp2.reverse()  # useful
        points = LinkedList()
        points.load(tmp)
        points.setEndless(True)

        otherPoints = LinkedList()
        otherPoints.load(tmp2)
        otherPoints.setEndless(True)

        #pprint(tmp)
        #pprint(tmp2)
        p = points.first
        firstStep = True
        while p is not points.first or firstStep:
            firstStep = False
            d = p.data
            if d.kind != Kind.outgoing or d.visited:
                p = p.next
                continue
            # brave new polygon!
            newbies = getPointsUntilExit(points, otherPoints, p.data)
            #print("newbies= ", newbies)
            sequence.append(newbies)
        #print "sequence= ", sequence

        points.setEndless(False)
        otherPoints.setEndless(False)
        #pprint({'points': points.toList(), 'otherPoints': otherPoints.toList()})

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

    def draw(self):
        """
        Draw self on canvas, given in constructor
        """
        lol = []
        for a, b in self.iterSegments():
            #   data.append((None, a, b, Kind.neutral))
            #       (p,((p1,qq),(p2,qqq)),((p3,qqq),(p4,qqqq)), k)
            lol.append( (a, ((a,None),(b,None)), ((a,None),(b,None)), Kind.neutral) )
            #print "a,b = ",a,b
            #drawingFunc(a, b, color=self.color)
        GlobalQueue.queue.insert(lol, color=self.color)

    def __findFirstOutgoing(self):
        """
        Return position of first "outgoing" point
        """
        for i, (_, kind) in self.points:
            if kind == Kind.outgoing:
                return i
        return None

def lolsort(array, point):
    """
    sort by DESC to the next point
    """
    #print "lolsort:", array, point
    array.sort(key=lambda x: (x[0][0]-point[0][0])**2+(x[0][1]-point[0][1])**2, reverse=True)
    #print "sorted: ", array
    return array

def getPointsUntilExit(primary, secondary, bravePoint, tab=0):
    ptr = findPoint(primary, bravePoint)
    result = [ptr.data]
    if ptr.data.visited:
        # my hero!
        return result #find bravePoint in primary
    ptr.data.visited = True

    next = ptr.next
    while(next.data.kind == Kind.neutral):
        result.append(next.data)
        next.data.visited = True
        next = next.next
        #stop!
    #result.append(next)
    lastPoint = next.data

    print(" "*tab+"{}, {}".format(result, lastPoint))
    tab = tab+len(str(result))+1

    return result + getPointsUntilExit(secondary, primary, lastPoint, tab=tab)

def findPoint(points, bravePoint):
    current = points.first
    while(current.hasNext()):
        #print current.data, bravePoint
        if current.data.point == bravePoint.point:
            return current
        current = current.next

def filterDuplicates(array):
    result = [array[0]]
    for curr in array[1:]:
        if result[-1] != curr:
            result.append(curr)
        else:
            print("filtered duplicate:", curr, "and we already have", result[-1])
    return result