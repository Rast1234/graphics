#!/usr/bin/python2
# -*- coding: utf-8 -*-

__author__ = 'rast'

from PySide.QtCore import *
from PySide.QtGui import *
import signal
import sys
import random
import time
from math import *
from TupleTableWidget import TupleTableWidget
from window import *

global hx
global hy
hx = None
hy = None

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
colors = None

def iterColor():
    colorSet = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
        (0, 0, 0),
    ]
    for x in colorSet:
        yield qRgb(*x)

def randomColor():
    [r,g,b] = [random.randint(0,255/3)*3 for _ in range(3)]
    return qRgb(r, g, b)

def sign(x):
    if x == 0:
        return 0
    return copysign(1,x)

def hyperbole(x, y, a, b):
    """x^2/a^2 - y^2/b^2 = 1
    """
    return abs((x * x) / (a * a) - (y * y) / (b * b) - 1)

def f(x, a, b):
    #return  a*x + b*x**2
    tmp = (b*x)**2 - (a*b)**2
    if tmp <= 0:
        return None
    return int(sqrt(tmp)/a)

def segmentIntersection(seg1, seg2):
    """
    seg1 = ( (x1, y1), (x2, y2) )
    seg2 = ( (x3, y3), (x4, y5) )
    returns False or (x, y) - intersection point
    """
    (p1, p2) = seg1
    (p3, p4) = seg2
    [p1, p2 ,p3, p4] = [Point(float(x), float(y)) for (x,y) in [p1, p2, p3, p4]]

    if max(p1.x, p2.x) < min(p3.x, p4.x):
        return False  # no mutual X intervals

    try:
        [a1, a2] = [(A.y-B.y)/(A.x-B.x) for (A,B) in [(p1, p2), (p3, p4)]]
    except ZeroDivisionError:
        #print("Zero division with segments {0} :: {1}".format(seg1, seg2))
        # this means that some Xs are equals
        return None
    [b1, b2] = [A.y-a*A.x for (A,a) in [(p1,a1), (p3,a2)]]

    if a1 == a2:
        return False  # parallel segments

    x = (b2 - b1)/(a1 - a2)
    y = a1*x + b1

    if x < max(min(p1.x, p2.x), min(p3.x, p4.x)) or \
            x > min(max(p1.x, p2.x), max(p3.x, p4.x)):
        return False

    return x,y

class Queue(object):
    """
    Drawing queue
    """

    def __init__(self, data):
        """
        Initialize queue with segments
        """
        self.data = data
        self.pos = 0
        self.force = False
        self.baseColor = qRgb(0, 0, 0)
        self.updateColor = qRgb(255, 0, 0)

    def draw(self, canvas):
        for i, (p,(p1,p2),(p3,p4)) in enumerate(self.data[:self.pos]):
            last = i == self.pos-1
            #print("i={}, pos={}, last={}".format(i,self.pos, last))
            color = self.updateColor if last else self.baseColor
            if last:
                print("{0} for {1}, {2} :: {3}, {4}".format(p,p1,p2,p3,p4))

            self.__do_draw(canvas, p, p1, p2, p3, p4, color)

    def __do_draw(self, canvas, p, p1, p2, p3, p4, color):
        #print(">    ",p,p1,p2,p3,p4)
        canvas.drawLine(p1,p2, color)
        canvas.drawLine(p3,p4, color)
        if p:
            canvas.drawCircle(p)
            pass

    def next(self):
        self.pos += 1

    def isDone(self):
        return self.pos >= len(self.data)


queue = Queue([])

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%d, %d)" %(self.x, self.y)


class Canvas(QWidget):
    """A canvas with support of simple
    graphics operations
    """
    def __init__(self, bcolor, lcolor):
        super(Canvas, self).__init__()
        self.baseColor = bcolor
        self.lineColor = lcolor
        self.image = QImage(self.size(), QImage.Format_RGB888)
        self.drawClear()
        self.task = None  # function to do stuff
        self.data = []

    def paintEvent(self, e):  # all painting here
        qp = QtGui.QPainter()
        qp.begin(self)

        # reinitialize image (size may change during work)
        self.image = QImage(self.size(), QImage.Format_RGB888)
        self.drawClear()

        #dirty
        global queue
        #print queue.data, queue.isDone()
        if not queue.isDone() or queue.force:
            queue.draw(self)
            #=queue.next()
        elif self.task is not None:
            self.task()  # do useful stuff

        qp.drawImage(0, 0, self.image)
        qp.end()

    def drawClear(self):
        """Empty the canvas
        """
        self.image.fill(self.baseColor)

    def task2(self):
        """Task 2 wrapper
        """
        data = map(lambda x: int(x.value()), self.data)
        point1 = (data[0], data[1])
        point2 = (data[2], data[3])
        color = qRgb(0, 0, 255)
        self.drawLine(point1, point2, self.lineColor)

    def setPixel(self, x, y, color):
        size = self.size()
        (width, height) = (size.width(), size.height())
        if 0< x< width-1 and 0< y < height-1:
            self.image.setPixel(x, y, color)

    def drawLine(self, point1, point2, color=None):
        """Bresenham algorithm for drawing lines
        """
        if color is None:
            color = randomColor()
        size = self.size()
        (width, height) = (size.width(), size.height())
        p1 = Point(point1[0], point1[1])
        p2 = Point(point2[0], point2[1])

        if p1.x == p2.x:
            for y in xrange(min(p1.y, p2.y), max(p1.y, p2.y)):
                self.setPixel(p1.x, y, color)
            return

        if p1.y == p2.y:
            for x in xrange(min(p1.x, p2.x), max(p1.x, p2.x)):
                self.setPixel(x, p1.y, color)
            return

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        ix = sign(dx)
        iy = sign(dy)
        dx = abs(dx)
        dy = abs(dy)


        if dx > dy:  # line through X
            pdx = ix
            pdy = 0
            es = dy
            el = dx
        else:  # line through Y
            pdx = 0
            pdy = iy
            es = dx
            el = dy
        x = p1.x
        y = p1.y
        error = el/2
        self.setPixel(x, y, color)  # first dot

        for t in xrange(el):
            error -= es
            if error < 0:
                error += el
                x += ix
                y += iy
            else:
                x += pdx
                y += pdy
            self.setPixel(x, y, color)

    def drawCircle(self, centerPoint, color=None):
        """
        Draws (bad) circle
        """
        if color is None:
            color = randomColor()
        x = centerPoint[0]
        y = centerPoint[1]
        points = [
            (x,y),
            (x+1,y+1),
            (x+1,y-1),
            (x-1,y+1),
            (x-1,y-1),
        ]
        for x,y in points:
            self.setPixel(x, y, color)

    def task3(self):
        """Task 3 wrapper
        """
        data = map(lambda x: float(x.value()), self.data)
        color = qRgb(0, 0, 255)
        a = data[0]
        b = data[1]
        self.drawHyperbole(a, b, self.lineColor)

    def drawHyperbole(self, a, b, color):
        """Hyperbole using Bresenham algorithm
        """

        size = self.size()
        xsize = size.width()
        ysize = size.height()
        dy = ysize/2
        dx = xsize/2
        # Axis
        self.drawLine((0,dy),(xsize,dy), color)
        self.drawLine((dx,0),(dx,ysize), color)
        # Asymptotes
        offset = 10
        x1 = int(dx + offset * a)
        x2 = int(dx - offset * a)
        y1 = int(dy + offset * b)
        y2 = int(dy - offset * b)
        self.drawLine((x2, y2), (x1, y1), color)
        self.drawLine((x2, y1), (x1, y2), color)
        x1 = a
        y1 = 0.0
        # Function
        self.setPixel(int(dx+a), dy, color)
        self.setPixel(int(dx-a), dy, color)
        while x1 < xsize:
            x2 = x1+1
            y2 = y1+1
            hg = hyperbole(x2, y1, a, b)
            hv = hyperbole(x1, y2, a, b)
            hd = hyperbole(x2, y2, a, b)
            if hg<hd:
                xhd2 = int(x2)
                yhd2 = int(y1)
                x1 = x2
            else:
                if hv < hd:
                    xhd2 = int(x1)
                    yhd2 = int(y2)
                    y1 = y2
                else:
                    xhd2 = int(x2)
                    yhd2 = int(y2)
                    y1 = y2
                    x1 = x2
            self.setPixel(dx + xhd2, dy - yhd2, color)
            self.setPixel(dx - xhd2, dy + yhd2, color)
            self.setPixel(dx - xhd2, dy - yhd2, color)
            self.setPixel(dx + xhd2, dy + yhd2, color)

    def task4(self):
        """Task 4 wrapper
        """
        global colors
        colors = iterColor()  # re-seed colors for repainting

        data = map(lambda x: int(x.value()), self.data[1])
        polyData = self.data[0]
        poly = Poly(polyData, self)
        poly.draw()

        rectData = [(data[0], data[1]),(data[2], data[1]),(data[2], data[3]),(data[0], data[3])]
        rect = Poly(rectData, self)
        rect.draw()

        print("="*60)
        poly.extendWithIntersectionPoints(rect)


class Poly(object):
    """
    Polygone with operations
    """

    def __init__(self, points, canvas, color=None):
        self.points = points
        self.canvas = canvas

        self.color = color if color is not None else colors.next()

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

    def draw(self):
        """
        Draw self on canvas, given in constructor
        """
        for a, b in self.iterSegments():
            self.canvas.drawLine(a, b, self.color)

    def extendWithIntersectionPoints(self, otherPoly):
        """
        Return current points list,
        extended with intersection points
        """
        result = []
        for seg in self.iterSegments():
            for otherSeg in otherPoly.iterSegments():
                intersection = segmentIntersection(seg, otherSeg)

                #self.canvas.drawLine(seg[0], seg[1])
                #self.canvas.drawLine(otherSeg[0], otherSeg[1])
                # pause
                result.append((intersection, seg, otherSeg))
                #print("{0} :: {1} :: {2}".format(intersection, seg, otherSeg))
        global queue
        queue = Queue(result)




class ControlMainWindow(QMainWindow):
    """A main window class
    """

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()  # get layout from 'pyside-uic mainwindow.ui' command
        self.ui.setupUi(self)
        self.dragPosition = None

        bcolor = qRgb(200, 200, 200)
        lcolor = qRgb(0, 0, 0)
        self.canvas = Canvas(bcolor, lcolor)
        self.ui.centralwidget.layout().insertWidget(1, self.canvas)
        self.ui.paintButton.clicked.connect(self.paintClick)

        self.pointsTable = TupleTableWidget(self.ui.ghostWidget)

        #set up test data
        self.pointsTable.fromList(testPoly)
        self.ui.task4_x1.setValue(testRect[0])
        self.ui.task4_y1.setValue(testRect[1])
        self.ui.task4_x2.setValue(testRect[2])
        self.ui.task4_y2.setValue(testRect[3])

        add_rule_callback = lambda: self.pointsTable.addRow("0", "0")
        remove_rule_callback = lambda: self.pointsTable.delRow()
        self.ui.addRuleButton.clicked.connect(add_rule_callback)
        self.ui.removeRuleButton.clicked.connect(remove_rule_callback)


        self.radios = [self.ui.radio_task2,
                  self.ui.radio_task3,
                  self.ui.radio_task4]
        self.frames = [self.ui.frame_task2,
                       self.ui.frame_task3,
                       self.ui.frame_task4]
        self.tasks = [self.task2,
                      self.task3,
                      self.task4]
        self.allinputs = [self.ui.task2_x1,
                  self.ui.task2_y1,
                  self.ui.task2_x2,
                  self.ui.task2_y2,
                  self.ui.task3_a,
                  self.ui.task3_b,
                  # to be continued...
                  ]
        for x in self.allinputs:
            x.valueChanged.connect(self.canvas.repaint)
        for x in self.radios:
            x.toggled.connect(self.radioClick)
        self.radioClick()

    def paintClick(self):
        for x in xrange(3):
            if self.radios[x].isChecked():
                self.tasks[x]()
        global queue
        queue.force = False
        self.canvas.repaint()

    def radioClick(self):
        for x in xrange(3):
            if self.radios[x].isChecked():
                self.frames[x].setEnabled(True)
            else:
                self.frames[x].setEnabled(False)
        if self.canvas.task is not None:
            self.paintClick()

    def keyPressEvent(self, event):
        """Overrides default keypress
        """
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close()
        elif key == QtCore.Qt.Key_Equal:
            global queue
            if queue is not None and not queue.isDone():
                queue.next()
                queue.force = True
                self.canvas.repaint()

    def mousePressEvent(self, event):
        """Make window draggable
        part 1
        """
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        """Make window draggable
        part 2
        """
        if event.buttons() and Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
        event.accept()

    def task2(self):
        inputs = [self.ui.task2_x1,
                  self.ui.task2_y1,
                  self.ui.task2_x2,
                  self.ui.task2_y2]
        self.canvas.task = self.canvas.task2
        self.canvas.data = inputs

    def task3(self):
        inputs = [self.ui.task3_a,
                  self.ui.task3_b]
        self.canvas.task = self.canvas.task3
        self.canvas.data = inputs

    def task4(self):
        inputs = [self.ui.task4_x1,
                  self.ui.task4_y1,
                  self.ui.task4_x2,
                  self.ui.task4_y2]
        self.canvas.task = self.canvas.task4
        self.canvas.data = (self.pointsTable.toList(), inputs)


def main():
    """Program enter
    """

    # Ctrl+C in linux terminal
    if sys.platform == "linux2":
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    random.seed(42)

    app = QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

