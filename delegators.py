# -*- coding: utf-8 -*-

__author__ = 'actics'

from PySide.QtCore import *
from PySide.QtGui import *


class SpeedDelegate(QItemDelegate):
    """Speed field delegate in rules table
    """

    __displayFormat = u"{0}"


    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setMaximum(9000)
        editor.setMinimum(0)
        editor.setValue(1)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        value = value[:-1]
        editor.setValue(int(value))

    def setModelData(self, editor, model, index):
        data = self.__displayFormat.format(editor.value())
        model.setData(index, data, Qt.EditRole)
