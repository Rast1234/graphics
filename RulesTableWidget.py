# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtGui import *

from QTableWidgetDragRow import *
from delegators import SpeedDelegate


class RulesTableWidget(QTableWidgetDragRow):
    """Table widget class with methods to input / output
    rules in list format and validate input fields
    """

    def __init__(self, parent=None):
        """Initial rules table. Set 2 columns, headers and delegates
        """
        super(RulesTableWidget, self).__init__(parent)

        self.setColumnCount(2)
        self.setItemDelegateForColumn(0, SpeedDelegate(self))
        self.setItemDelegateForColumn(1, SpeedDelegate(self))

        self.setHorizontalHeaderLabels((u"x", u"y"))
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    def addRule(self, x, y):
        """Add row to rules table
        """
        row = self.rowCount()
        self.insertRow(row)

        timeItem = QTableWidgetItem()
        speedItem = QTableWidgetItem()

        timeItem.setText(x)
        speedItem.setText(y)

        self.setItem(row, 0, timeItem)
        self.setItem(row, 1, speedItem)

        ranges = self.selectedRanges()
        if len(ranges):
            self.setRangeSelected(ranges[0], False)

        # correct set selection
        ran = QTableWidgetSelectionRange(row, 0, row, 1)
        self.setRangeSelected(ran, True)

    def removeRule(self):
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

    def fromRulesList(self, rules_list):
        """Generate rows from rule list
        rule in list it's tuple with time(int seconds) and speed(float)
        """
        self.setRowCount(0)
        # not needed because headers are not removed:
        #self.setHorizontalHeaderLabels((u"Время", u"Скорость"))

        for x, y in rules_list:
            a = "{d}".format(x)
            b = "{d}".format(y)

            self.addRule(a, b)

    def toRulesList(self):
        """Generate rule list from rules in table rows
        rule in list it's tuple with time(int seconds) and speed(float)
        """
        rules = []
        for row_number in xrange( self.rowCount() ):
            #print row_number

            time_item = self.item(row_number, 0)
            time = time_item.text()

            speed_item = self.item(row_number, 1)
            speed = speed_item.text()

            time = int(time[:-1])
            speed = int(speed[:-1])


            rules.append((time, speed))

        return rules
