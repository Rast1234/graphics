__author__ = 'rast'

from PySide.QtGui import qRgb

class Queue(object):
    """
    Drawing queue
    """

    def __init__(self):
        """
        Initialize queue with segments
        """
        self.data = []
        self.pos = 0
        self.force = False
        self.baseColor = qRgb(0, 0, 0)
        self.updateColor = qRgb(255, 0, 0)

    def finalize(self):
        """
        add last step
        """
        p = (0, 0)
        self.data.append( ((False, ((p, None), (p, None)), ((p, None), (p, None)), 'neutral'), self.baseColor) )

    def insert(self, data, color=qRgb(0, 0, 0)):
        """
        Append
        """
        self.data += zip(data, [color]*len(data))

    def draw(self, canvas):
        for i, ((p,((p1,qq),(p2,qqq)),((p3,qqq),(p4,qqqq)), k), color) in enumerate(self.data[:self.pos]):
            last = i == self.pos-1
            #print("i={}, pos={}, last={}".format(i,self.pos, last))
            realColor = self.updateColor if last else color
            if last:
                #print("{0} for {1}, {2} :: {3}, {4}".format(p,p1,p2,p3,p4))
                #print(info)
                pass
            self.__do_draw(canvas, p, p1, p2, p3, p4, k, realColor)

    def __do_draw(self, canvas, p, p1, p2, p3, p4, k, color):
        #print(">    ",p,p1,p2,p3,p4)
        canvas.drawLine(p1,p2, color)
        canvas.drawLine(p3,p4, color)
        if p:
            canvas.drawCross(p, kind=k, color=qRgb(0, 0, 255))
            pass

    def next(self):
        self.pos += 1

    def isDone(self):
        return self.pos >= len(self.data)

queue = Queue()
