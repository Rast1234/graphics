# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtCore import *
from PySide.QtGui  import *


class QTableWidgetDragRow(QTableWidget):
    """Special TableWiget class which allows selection
    and dragging of a single row
    """

    def __init__(self, parent=None):
        """Init method which sets flags
        """
        super(QTableWidgetDragRow, self).__init__(parent)

        self.viewport().setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def dropEvent(self, event):
        """Drop event callback
        """
        if event.source() == self and event.dropAction() == Qt.CopyAction:
            selRow = self.selectionModel().selection()[0].top()
            dropRow = self.indexAt(event.pos()).row()

            if dropRow == -1:
                dropRow = self.rowCount()
            elif selRow < dropRow:
                dropRow += 1

            self.insertRow(dropRow)

            selRow = self.selectionModel().selection()[0].top()

            # copy selected line to drop
            for col in xrange(self.columnCount()):
                source = QTableWidgetItem( self.item(selRow, col) )
                self.setItem(dropRow, col, source)

            self.removeRow(selRow)

            selRow = self.selectionModel().selection()[0].top()

            if dropRow == self.rowCount():
                dropRow -= 1
            elif selRow < dropRow:
                dropRow -= 1

            # correct set selected after drop
            ran = QTableWidgetSelectionRange(selRow, 0, selRow, self.columnCount()-1)
            self.setRangeSelected(ran, False)
            ran = QTableWidgetSelectionRange(dropRow, 0, dropRow, self.columnCount()-1)
            self.setRangeSelected(ran, True)

            event.accept()
