__author__ = 'rast'


class Node(object):
    def __init__(self, data=None, prev=None, next=None):
        if (prev and not isinstance(prev, Node)) or \
                (next and not isinstance(next, Node)):
            raise ValueError("Invalid parameters")
        self.data = data
        self.prev = prev
        self.next = next

    def hasNext(self):
        return False if self.next is None else True

    def hasPrev(self):
        return False if self.prev is None else True

    def insertAfter(self, data):
        newNode = Node(data=data, prev=self, next=self.next)
        if self.next is not None:
            self.next.prev = newNode
        self.next = newNode
        return newNode

    def insertBefore(self, data):
        newNode = Node(data=data, next=self, prev=self.prev)
        if self.prev is not None:
            self.prev.next = newNode
        self.prev = newNode
        return newNode

    def __str__(self):
        return "Node({}, next={}, prev={})".format(self.data, self.next.__repr__(), self.prev.__repr__())

class LinkedList(object):
    def __init__(self):
        self.first = None

    def load(self, dataList):
        for x in dataList:
            self.append(x)

    def append(self, data):
        if self.first is None:
            self.first = Node(data=data)
        else:
            current = self.first
            while current.hasNext():
                current = current.next
            current.next = Node(data=data, prev=current)  # !!

    def __getitem__(self, index):
        if index < 0:
            index = len(self) + index
        if index == 0:
            if self.first is None:
                raise IndexError("Index out of range: {}".format(index))
            return self.first

        count = 0
        current = self.first
        while count < index and current.hasNext() and current.next is not self.first:  # fix for endless mode
            current = current.next
            count += 1
        if count == index:
            return current
        raise IndexError("Index out of range: {}".format(index))

    def toList(self):
        return map(lambda x: x.data, list(self))

    def setEndless(self, infinite):
        if infinite:
            last = self[-1]
            self.first.prev = last
            last.next = self.first
        else:
            self.first.prev = None
            self[-1].next = None
    def isEndless(self):
        return self.first.prev!=None and self[-1].next!=None

    def __len__(self):
        count = 0
        if self.first == None:
            return count
        current = self.first
        count += 1
        while current.hasNext() and current.next is not self.first:
            current = current.next
            count += 1
        return count

    def __str__(self):
        if self.isEndless():
            return "Infinite loop"
        return ", ".join(map(lambda x: str(x), list(self)))

    def __iter__(self):
        current = self.first
        yield current
        while current is not None and current.hasNext():
            current = current.next
            yield current

'''
l = LinkedList()
l.load(range(10))
l.setEndless(True)
'''