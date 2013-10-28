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

    def append(self, data):
        if self.first is None:
            self.first = Node(data=data)
        else:
            current = self.first
            while current.hasNext():
                current = current.next
            current.next = Node(data=data, prev=current)  # !!

    def __getitem__(self, index):
        if index == 0:
            return self.first
        if index < 0:
            index = len(self) + index

        count = 0
        current = self.first
        while count < index and current.hasNext():
            current = current.next
            count += 1
        if count == index:
            return current
        raise IndexError("Index out of range: {}".format(index))

    def toList(self):
        return map(lambda x: x.data, list(self))

    def __len__(self):
        count = 0
        if self.first == None:
            return count
        current = self.first
        count += 1
        while current.hasNext():
            current = current.next
            count += 1
        return count

    def __str__(self):
        return ", ".join(map(lambda x: str(x), list(self)))

    def __iter__(self):
        current = self.first
        yield current
        while current is not None and current.hasNext():
            current = current.next
            yield current

l = LinkedList()
[l.append(x) for x in range(10)]
print len(l)
print l[3].data, l[4].data, l[5].data
l[4].insertBefore('a')
print len(l)
print l[3].data, l[4].data, l[5].data