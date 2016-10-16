# -*- coding: utf-8 -*-
"""The UI for proto files."""
from PyQt4 import QtCore, QtGui
import os
import subprocess
import argparse
import json
import sub_dialog

from pbtool.pbtool_bin import script as it

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

DICTIONARY = {}
TEMP_LIST = []
TEMP_LIST1 = []
TEMP_LIST2 = []
TEMP_LIST3 = []


class Sbutton(QtGui.QPushButton):
    """Class for buttons."""

    global DICTIONARY, TEMP_LIST, TEMP_LIST1, TEMP_LIST2, TEMP_LIST3

    def for_textfields(self, i, dialg, field_desc, mname=None):
        """For text fields."""
        i = i + 1
        dialg.horizontalLayout = QtGui.QHBoxLayout()
        self.setObjectName(_fromUtf8("pushButton"))
        self.setText(_translate("Dialog", "Save", None))
        self.setFixedWidth(110)
        self.ptextEdit = QtGui.QLineEdit(dialg.scrollAreaWidgetContents)
        self.label = QtGui.QLabel(dialg.scrollAreaWidgetContents)
        self.ptextEdit.setObjectName(_fromUtf8("ptextEdit"))
        self.label.setObjectName(_fromUtf8("label"))
        label_text = field_desc.name.title() + ":"
        if field_desc.label == field_desc.LABEL_REQUIRED:
            self.label.setStyleSheet('color: red')
        self.label.setText(_translate("Dialog", label_text, None))
        self.clicked.connect(lambda: self.text_button_clicked(field_desc, mname))
        dialg.horizontalLayout.addWidget(self.label)
        dialg.horizontalLayout.addWidget(self.ptextEdit)
        dialg.horizontalLayout.addWidget(self)
        dialg.verticalLayout.addLayout(dialg.horizontalLayout)
        return i

    def text_button_clicked(self, field_desc, mname=None):
        """Push button event for text fields."""
        if field_desc.type in (1, 2):
            data_text = float(self.ptextEdit.text())
        elif field_desc.type in (3, 4, 5, 13):
            data_text = int(self.ptextEdit.text())
        else:
            data_text = str(self.ptextEdit.text())
        words = field_desc.name
        if mname is not None:
            TEMP_LIST1.append(str(words))
            TEMP_LIST2.append(data_text)
            TEMP_LIST3.append(mname)
        else:
            DICTIONARY[str(words)] = data_text

    def for_checkbox(self, i, dialg, field_desc, mname=None):
        """For check boxes."""
        i = i + 1
        dialg.horizontalLayout = QtGui.QHBoxLayout()
        self.setObjectName(_fromUtf8("pushButton"))
        self.setText(_translate("Dialog", "Save", None))
        self.setFixedWidth(110)
        self.checkBox = QtGui.QCheckBox(dialg.scrollAreaWidgetContents)
        self.checkBox.move(150, 150)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.checkBox.setEnabled(True)
        self.label = QtGui.QLabel(dialg.scrollAreaWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        label_text = field_desc.name.title() + ":"
        if field_desc.label == field_desc.LABEL_REQUIRED:
            self.label.setStyleSheet('color: red')
        self.label.setText(_translate("Dialog", label_text, None))
        self.clicked.connect(lambda: self.check_button_clicked(field_desc, mname))
        dialg.horizontalLayout.addWidget(self.label)
        dialg.horizontalLayout.addWidget(self.checkBox)
        dialg.horizontalLayout.addWidget(self)
        dialg.verticalLayout.addLayout(dialg.horizontalLayout)
        return i

    def check_button_clicked(self, field_desc, mname=None):
        """Push button event for check boxes."""
        words = field_desc.name
        if self.checkBox.checkState() == 2:
            data_text = True
        else:
            data_text = False
        if mname is not None:
            TEMP_LIST1.append(str(words))
            TEMP_LIST2.append(data_text)
            TEMP_LIST3.append(mname)
        else:
            DICTIONARY[str(words)] = data_text

    def for_combo_box(self, i, dialg, field_desc, mname=None):
        """For combo boxes."""
        i = i + 1
        dialg.horizontalLayout = QtGui.QHBoxLayout()
        self.setObjectName(_fromUtf8("pushButton"))
        self.setText(_translate("Dialog", "Save", None))
        self.label = QtGui.QLabel(dialg.scrollAreaWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.setFixedWidth(110)
        label_text = field_desc.name.title() + ":"
        if field_desc.label == field_desc.LABEL_REQUIRED:
            self.label.setStyleSheet('color: red')
        self.label.setText(_translate("Dialog", label_text, None))
        self.comboBox = QtGui.QComboBox(dialg.scrollAreaWidgetContents)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        for x in range(len(field_desc.enum_type.values_by_name)):
            self.comboBox.addItem(_fromUtf8(""))
            self.comboBox.setCurrentIndex(field_desc.default_value)
            self.comboBox.setItemText(x, _translate("Dialog", field_desc.enum_type.values_by_number[x].name, None))
        self.clicked.connect(lambda: self.combo_button_clicked(field_desc,
                                                               mname))
        dialg.horizontalLayout.addWidget(self.label)
        dialg.horizontalLayout.addWidget(self.comboBox)
        dialg.horizontalLayout.addWidget(self)
        dialg.verticalLayout.addLayout(dialg.horizontalLayout)
        return i

    def combo_button_clicked(self, field_desc, mname=None):
        """Push button event for combo boxes."""
        data_text = self.comboBox.currentText()
        words = field_desc.name
        if mname is not None:
            TEMP_LIST1.append(str(words))
            TEMP_LIST2.append(str(data_text))
            TEMP_LIST3.append(mname)
        else:
            DICTIONARY[str(words)] = str(data_text)

    def json_conversion(self, proto_file, message, dialg):
        """Method to convert the user data into JSON."""
        global TEMP_LIST1, TEMP_LIST2, TEMP_LIST3, TEMP_LIST

        def inner(temp_list1, temp_list2, temp_list3):
            """Second Inner Method."""
            global TEMP_LIST

            def into_inner(temp_list1, temp_list2, temp_list3):
                """Third Inner Method.

                This is to arrange all the repeated or non-repeated
                subfields in a
                dictionary pattern for a particular field.
                """
                if any(x for x in temp_list1 if temp_list1.count(x) > 1):
                    for y in range(1, len(temp_list1)):
                        if y < len(temp_list1):
                            if temp_list1[0] == temp_list1[y]:
                                diction = temp_list1[:y]     # first half
                                dictio = dict(zip(diction, temp_list2[:y]))
                                temp_list1 = temp_list1[y:]     # second half
                                temp_list2 = temp_list2[y:]     # second half
                                TEMP_LIST.append(dictio)
                                break
                    into_inner(temp_list1, temp_list2, temp_list3)
                else:
                    dictio = dict(zip(temp_list1, temp_list2))
                    TEMP_LIST.append(dictio)
            into_inner(temp_list1, temp_list2, temp_list3)
            DICTIONARY[temp_list3[0]] = TEMP_LIST
            TEMP_LIST = []

        def begin(temp_list1, temp_list2, temp_list3):
            """First Inner Method.

            This is to sort the list for repeated fields
            and then to send their subfields to the Second
            Inner Method.
            """
            if any(x for x in temp_list3 if temp_list3.count(x) > 1):
                for x in range(0, len(temp_list3)):
                    for y in range(x + 1, len(temp_list3)):
                        if temp_list3[x] != temp_list3[y]:
                            x = y - 1
                            for z in range(y, len(temp_list3)):
                                if temp_list3[x] == temp_list3[z]:
                                    temp = temp_list3[z]
                                    temp_list3[z] = temp_list3[x + 1]
                                    temp_list3[x + 1] = temp
                                    temp1 = temp_list1[z]
                                    temp_list1[z] = temp_list1[x + 1]
                                    temp_list1[x + 1] = temp1
                                    temp2 = temp_list2[z]
                                    temp_list2[z] = temp_list2[x + 1]
                                    temp_list2[x + 1] = temp2
                                    break
                for x in range(0, len(set(temp_list3))):
                    for y in range(1, len(temp_list3)):
                        if y < len(temp_list3):
                            if temp_list3[0] != temp_list3[y]:
                                temp = temp_list3[:y]     # first half
                                temp1 = temp_list1[:y]     # first half
                                temp2 = temp_list2[:y]     # first half
                                temp_list1 = temp_list1[y:]     # second half
                                temp_list2 = temp_list2[y:]     # second half
                                temp_list3 = temp_list3[y:]     # second half
                                inner(temp1, temp2, temp)     # Call to second inner method
                                break
                else:
                    inner(temp_list1, temp_list2, temp_list3)     # Call to second inner method
                    pass
            else:
                dictio = {}
                for x in range(len(temp_list3)):
                    if temp_list3.count(x) <= 1:
                        dictio[temp_list1[x]] = temp_list2[x]
                        listw = []
                        listw.append(dictio)
                        DICTIONARY[temp_list3[x]] = listw

        begin(TEMP_LIST1, TEMP_LIST2, TEMP_LIST3)
        with open('data.json', 'w') as outfile:
            outfile.write(json.dumps(DICTIONARY))
        bin_file = 'data.bin'
        if not os.path.exists(bin_file):
            open(bin_file, 'w')
        command = ['pbtool_bin', proto_file, message, os.path.abspath('data.json'),
                   '-o', os.path.abspath(bin_file)]
        try:
            subprocess.check_call(command)
        except Exception as e:
            print("Hey, You can't do that!! \nEnter the required fields please.")
        print("json: ", json.dumps(DICTIONARY))
        self.dialogTextBrowser = sub_dialog.SubDialog(dialg)
        self.dialogTextBrowser.exec_()


class MyDialog(QtGui.QDialog):
    """UI Widget is being made here."""

    global DICTIONARY, TEMP_LIST, TEMP_LIST1, TEMP_LIST2, TEMP_LIST3

    def setup_ui(self, mod, field_desc, i, mname=None):
        """Method to separate the field types."""
        d = 0
        # Is this field a string, int, float, double?
        if field_desc.type in (9, 3, 4, 5, 13, 1, 2):
            self.push_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
            a = Sbutton(self.push_button)
            i = a.for_textfields(i, self, field_desc, mname)
            self.push_button.hide()

        # Is this field actually a message definition?
        elif field_desc.type == field_desc.TYPE_MESSAGE:
            d = d + 1
            self.vertical = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
            self.line = QtGui.QFrame(self.scrollAreaWidgetContents)
            self.line.setFrameShape(QtGui.QFrame.HLine)
            self.line.setFrameShadow(QtGui.QFrame.Sunken)
            self.line.setObjectName(_fromUtf8("line"))

            label_text = field_desc.name.upper()
            self.label = QtGui.QLabel(self.scrollAreaWidgetContents)
            self.label.setObjectName(_fromUtf8("label"))
            self.label.setText(_translate("Dialog", label_text, None))
            self.label.setFont(self.bold_font)
            self.vertical.addWidget(self.line)
            self.vertical.addWidget(self.label)
            self.verticalLayout.addLayout(self.vertical)
            self.label.setStyleSheet('font-size: 10pt; font-family: Times;')

            def xyz(if_clicked=None):
                label_text = field_desc.name.upper()
                if if_clicked:
                    self.vertical1 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
                    self.line1 = QtGui.QFrame(self.scrollAreaWidgetContents)
                    self.line1.setFrameShape(QtGui.QFrame.HLine)
                    self.line1.setFrameShadow(QtGui.QFrame.Sunken)
                    self.line1.setObjectName(_fromUtf8("line1"))

                    self.label1 = QtGui.QLabel(self.scrollAreaWidgetContents)
                    self.label1.setObjectName(_fromUtf8("label1"))
                    self.label1.setText(_translate("Dialog", label_text, None))
                    self.label1.setFont(self.bold_font)
                    self.label1.setStyleSheet('font-size: 10pt; font-family: Times;')
                    self.vertical1.addWidget(self.line1)
                    self.vertical1.addWidget(self.label1)
                    self.verticalLayout.addLayout(self.vertical1)
                    self.vertical1.setSpacing(0)
                    self.vertical1.setContentsMargins(0, 0, 0, 0)
                print("message: {} is added".format(label_text))
                cls = getattr(mod,
                              field_desc.message_type.containing_type.name)
                self.app(cls, field_desc.message_type.name, i, field_desc.name)

            # Is this a repeated field?
            if field_desc.label == field_desc.LABEL_REPEATED:
                self.push_button = QtGui.QPushButton(
                    self.scrollAreaWidgetContents)
                self.push_button.setObjectName(_fromUtf8("pushButton"))
                self.push_button.setText(_translate("Dialog", "ADD " +
                                                    label_text, None))
                self.button_widget = QtGui.QWidget(self.scrollAreaWidgetContents)

                self.hButtonsLayout.addWidget(self.push_button)
                self.push_button.clicked.connect(lambda: xyz(True))
            xyz()

        # Is this field a bool?
        elif field_desc.type == field_desc.TYPE_BOOL:
            self.push_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
            a = Sbutton(self.push_button)
            i = a.for_checkbox(i, self, field_desc, mname)
            self.push_button.hide()

        # Is this field an enum?
        elif field_desc.type == field_desc.TYPE_ENUM:
            self.push_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
            a = Sbutton(self.push_button)
            i = a.for_combo_box(i, self, field_desc, mname)
            self.push_button.hide()
        return i

    def __init__(self, parent=None):
        """The start point."""
        super(MyDialog, self).__init__(parent)
        parser = argparse.ArgumentParser(
            description='Cross-sell Event Application.')
        parser.add_argument('proto', help='The .proto file to be compiled.')
        parser.add_argument('cls', help='The case-sensitive name of a class within the .proto file that will be instantiated and populated.')
        args = parser.parse_args()
        protobuf_filename = args.proto
        messagename = args.cls
        mod = it.compile(protobuf_filename)

        self.setObjectName(_fromUtf8("Dialog"))

        self.bold_font = QtGui.QFont()
        self.bold_font.setBold(True)
        self.italics_font = QtGui.QFont()
        self.italics_font.setItalic(True)

        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.headLabel = QtGui.QLabel(self)
        self.headLabel.setStyleSheet('font-size: 16pt; font-family: Times;')
        self.headLabel.setFont(self.bold_font)
        self.headLabel.setText(_translate("Dialog", messagename.upper(), None))

        self.gridLayout.addWidget(self.headLabel, 0, 0)
        self.headLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 500, 500))

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))

        self.hButtonsLayout = QtGui.QHBoxLayout(self.scrollAreaWidgetContents)

        self.tailLabel = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.tailLabel.setStyleSheet('color: red')
        self.tailLabel.setFont(self.italics_font)
        self.tailLabel.setText(_translate("Dialog", "Fields in red are required/mandatory.", None))

        self.app(mod, messagename, i=0)
        self.resize(600, 350)
        self.gridLayout.addLayout(self.hButtonsLayout, 2, 0)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
                                          QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.hButtonboxLayout = QtGui.QHBoxLayout(self)
        self.hButtonboxLayout.addWidget(self.tailLabel)
        self.hButtonboxLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.hButtonboxLayout, 3, 0)
        self.gridLayout.addWidget(self.scrollArea, 1, 0)

        self.setWindowTitle(_translate("Dialog", "Protobuf Tool", None))
        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowSystemMenuHint |
                            QtCore.Qt.WindowMinMaxButtonsHint)

        self.pushButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
        a = Sbutton(self.pushButton)
        self.pushButton.hide()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), lambda: a.json_conversion(protobuf_filename, messagename, self))
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)

    def app(self, mod, messagename, i, mname=None):
        """Reach in and get the class defined in messagename."""
        cls = getattr(mod, messagename)
        instance = cls()
        for field_desc in instance.DESCRIPTOR.fields:
            if field_desc.label in (field_desc.LABEL_REPEATED,
               field_desc.LABEL_REQUIRED, field_desc.LABEL_OPTIONAL):
                i = self.setup_ui(mod, field_desc, i, mname)


def main():
    """Main entry point."""
    import sys
    app = QtGui.QApplication(sys.argv)
    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
