# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtGui import *

from QTableWidgetDragRow import *
from delegators import CellDelegate


class TupleTableWidget(QTableWidgetDragRow):
    """Table widget class with methods to input / output
    rules in list format and validate input fields
    """

    def __init__(self, parent=None, minValue=0, maxValue=1000, defaultValue=0):
        """Initial rules table. Set 2 columns, headers and delegates
        """
        super(TupleTableWidget, self).__init__(parent)

        self.setColumnCount(2)
        self.setItemDelegateForColumn(0, CellDelegate(self, minValue, maxValue, defaultValue))
        self.setItemDelegateForColumn(1, CellDelegate(self, minValue, maxValue, defaultValue))

        self.setHorizontalHeaderLabels((u"x", u"y"))
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    def addRow(self, xName, yName):
        """Add row to rules table
        """
        row = self.rowCount()
        self.insertRow(row)

        x = QTableWidgetItem()
        y = QTableWidgetItem()

        x.setText(xName)
        y.setText(yName)

        self.setItem(row, 0, x)
        self.setItem(row, 1, y)

        ranges = self.selectedRanges()
        if len(ranges):
            self.setRangeSelected(ranges[0], False)

        # correct set selection
        ran = QTableWidgetSelectionRange(row, 0, row, 1)
        self.setRangeSelected(ran, True)

    def delRow(self):
        """Remove selected row from rules table, then move
        focus to next row (or last row if last was removed)
        """
        ranges = self.selectedRanges()
        if not len(ranges):
            return

        removed_row = ranges[0].topRow()
        self.removeRow(removed_row)

        # correct set selection

        if removed_row == self.rowCount():
            removed_row -= 1
        else:
            pass
        ran = QTableWidgetSelectionRange(removed_row, 0, removed_row, 1)
        self.setRangeSelected(ran, True)

    def fromList(self, rules_list):
        """Generate rows from list of rows as tuples
        """
        self.setRowCount(0)
        # not needed because headers are not removed:

        for x, y in rules_list:
            a = "{d}".format(x)
            b = "{d}".format(y)

            self.addRow(a, b)

    def toList(self):
        """Save rows as tuples
        Return list of tuples
        """
        rules = []
        for row_number in xrange( self.rowCount() ):
            #print row_number

            xItem = self.item(row_number, 0)
            x = xItem.text()

            yItem = self.item(row_number, 1)
            y = yItem.text()

            x = int(x[:-1])
            y = int(y[:-1])


            rules.append((x, y))

        return rules
