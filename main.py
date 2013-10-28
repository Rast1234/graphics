#!/usr/bin/python2
# -*- coding: utf-8 -*-

__author__ = 'rast'

from PySide.QtCore import *
from PySide.QtGui import *
import signal
import sys
import random
from pprint import pprint
from math import *
from TupleTableWidget import TupleTableWidget
from Clipping import *
import GlobalQueue
from window import *

global hx
global hy
hx = None
hy = None

def randomColor():
    #[r,g,b] = [random.randint(0,255/3)*3 for _ in range(3)]
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
    (r,g,b)= random.choice(colorSet)
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
        #print GlobalQueue.queue.data, GlobalQueue.queue.isDone()
        if not GlobalQueue.queue.isDone() or GlobalQueue.queue.force:
            GlobalQueue.queue.draw(self)
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

    def drawCross(self, centerPoint, kind=None, length=3, color=None):
        """
        Draws (bad) circle
        """
        if color is None:
            color = randomColor()
        x = centerPoint[0]
        y = centerPoint[1]
        segments = [
            ( (x+length,y+length), (x-length,y-length) ),
            ( (x-length,y+length), (x+length,y-length) )
        ]
        for (p1, p2) in segments:
            self.drawLine(p1, p2, color)

        if kind is not None:
            self.__drawKind(x+3, y-5, kind, color)

    def drawSquare(self, centerPoint, kind=None, size=3, color=None):
        """
        Draws square from center
        """
        if color is None:
            color = randomColor()
        x = centerPoint[0]
        y = centerPoint[1]
        segments = [
            ( (x-size,y-size), (x+size,y-size) ),
            ( (x+size,y-size), (x+size,y+size) ),
            ( (x+size,y+size), (x-size,y+size) ),
            ( (x-size,y+size), (x-size,y-size) ),
        ]
        for (p1, p2) in segments:
            self.drawLine(p1, p2, color)

        self.__drawKind(x+3, y+5, kind, color)

    def __drawKind(self, x, y, kind, color):
            """
            Draws symbolic kkind representation
            """
            segments = []
            if kind == Kind.neutral:  # N
                segments = [
                    ( (x-2,y+3), (x-2,y-3) ),
                    ( (x-2,y-3), (x+2,y+3) ),
                    ( (x+2,y+3), (x+2,y-3) ),
                        ]
            elif kind == Kind.incoming:  # I
                segments = [
                    ( (x-2,y+3), (x+2,y+3) ),
                    ( (x-2,y-3), (x+2,y-3) ),
                    ( (x,y-3), (x,y+3) ),
                        ]
            elif kind == Kind.outgoing:  # O
                segments = [
                    ( (x-1,y+3), (x+1,y+3) ),
                    ( (x+1,y+3), (x+2,y+1) ),
                    ( (x+2,y+1), (x+2,y-1) ),
                    ( (x+2,y-1), (x+1,y-3) ),
                    ( (x+1,y-3), (x-1,y-3) ),
                    ( (x-1,y-3), (x-2,y-1) ),
                    ( (x-2,y-1), (x-2,y+1) ),
                    ( (x-2,y+1), (x-1,y-3) ),
                        ]
            for (p1, p2) in segments:
                self.drawLine(p1, p2, color)

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
        data = map(lambda x: int(x.value()), self.data[1])
        polyData = self.data[0]
        poly = Poly(points=polyData)
        poly.draw(self.drawLine)

        rectData = [(data[0], data[1]),(data[2], data[1]),(data[2], data[3]),(data[0], data[3])]
        rect = Poly(points=rectData)
        rect.draw(self.drawLine)

        print("="*60)
        newPolyData, polyKinds = poly.extendWithIntersectionPoints(rect)
        newPoly = Poly(points=newPolyData, kinds=polyKinds, color=poly.color)
        newRectData, rectKinds = rect.extendWithIntersectionPoints(poly)
        newRect = Poly(points=newRectData, kinds=rectKinds, color=rect.color)

        newPoly.drawPoints(self.drawCross)
        pprint(newPoly.points)
        newRect.drawPoints(self.drawSquare)
        pprint(newRect.points)
        endPoly = newPoly - newRect


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
        GlobalQueue.queue.force = False
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
            if GlobalQueue.queue is not None and not GlobalQueue.queue.isDone():
                GlobalQueue.queue.next()
                GlobalQueue.queue.force = True
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

