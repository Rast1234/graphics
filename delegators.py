# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtCore import *
from PySide.QtGui import *


class CellDelegate(QItemDelegate):
    """Delegate in table
    """

    __displayFormat = u"{0}"
    __min = 0
    __max = 100
    __default = 0

    def __init__(self, parent, minValue, maxValue, defaultValue):
        super(CellDelegate, self).__init__(parent)
        self.__min = minValue
        self.__max = maxValue
        self.__default = defaultValue

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setMaximum(self.__max)
        editor.setMinimum(self.__min)
        editor.setValue(self.__default)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        value = value[:-1]
        try:
            editor.setValue(int(value))
        except ValueError:  # empty value arrives
            pass

    def setModelData(self, editor, model, index):
        data = self.__displayFormat.format(editor.value())
        model.setData(index, data, Qt.EditRole)
