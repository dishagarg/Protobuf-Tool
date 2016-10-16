# -*- coding: utf-8 -*-
"""New window to Copy bin."""
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class SubDialog(QtGui.QDialog):
    """Creates a new window to copy bin contents."""

    def __init__(self, parent=None):
        super(SubDialog, self).__init__(parent)
        self.pushButtonWindow = QtGui.QPushButton(self)
        self.pushButtonWindow.setText("Copy the contents of bin file?")
        self.pushButtonWindow.clicked.connect(self.on_pushbutton_clicked)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.addWidget(self.pushButtonWindow)
        self.setWindowTitle(_translate("Dialog", "Copy Bin", None))

    @QtCore.pyqtSlot()
    def on_pushbutton_clicked(self):
        """Action event for copy button."""
        with open('data.bin', 'rb') as fbin:
            text = fbin.read()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            print("bin's content: ", text)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialog = SubDialog()
    dialog.show()
    sys.exit(app.exec_())
