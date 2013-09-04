# -*- coding: utf-8 -*-

import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui

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
    
from ui_Lottery import Ui_MainWindow
from Lottery_Filter import *

import random

class Lottery(QtGui.QMainWindow):
    redBall = [0,0,0,0,0,0]
    blueBall = [0]
    def __init__(self, parent=None):
        super(Lottery, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.hopeButton, QtCore.SIGNAL("clicked()"), self.hopeButton_click)
        self.setFilter()
    def hopeButton_click(self):
        self.ui.hopeButton.setProperty("enabled", False)
        count = 0
        while(True):
            redBall = [0,0,0,0,0,0]
            self.randomBall()
            count += 1
            if self.ui.fliterBox_1.checkState():
                if not filter_1(self.redBall,self.blueBall) :
                    continue
            if self.ui.fliterBox_2.checkState():
                if not filter_2(self.redBall,self.blueBall) :
                    continue
            if self.ui.fliterBox_3.checkState():
                if not filter_3(self.redBall,self.blueBall) :
                    continue
            if self.ui.fliterBox_4.checkState():
                if not filter_4(self.redBall,self.blueBall) :
                    continue
            if self.ui.fliterBox_5.checkState():
                if not filter_5(self.redBall,self.blueBall) :
                    continue
            if self.ui.fliterBox_6.checkState():
                if not filter_6(self.redBall,self.blueBall) :
                    continue
            if self.ui.fliterBox_7.checkState():
                if not filter_7(self.redBall,self.blueBall) :
                    continue
            break
        print count
                
        self.setLcdNumber()
        self.ui.hopeButton.setProperty("enabled", True)

    def randomBall(self):
        a = 0
        for i in range(6):
            while(a in self.redBall or a==0):
                a = random.randint(1,33)
            self.redBall[i] = a
        self.redBall.sort()
        self.blueBall[0] = random.randint(1,16)
        
    def setLcdNumber(self):
        self.ui.redNumber_1.setProperty("intValue", self.redBall[0])
        self.ui.redNumber_2.setProperty("intValue", self.redBall[1])
        self.ui.redNumber_3.setProperty("intValue", self.redBall[2])
        self.ui.redNumber_4.setProperty("intValue", self.redBall[3])
        self.ui.redNumber_5.setProperty("intValue", self.redBall[4])
        self.ui.redNumber_6.setProperty("intValue", self.redBall[5])

        self.ui.blueNumber.setProperty("intValue", self.blueBall[0])
    def setFilter(self):
        self.ui.fliterBox_1.setChecked(True)
        self.ui.fliterBox_2.setChecked(True)
        self.ui.fliterBox_3.setChecked(True)
        self.ui.fliterBox_4.setChecked(True)
        self.ui.fliterBox_5.setChecked(True)
        self.ui.fliterBox_6.setChecked(True)
        self.ui.fliterBox_7.setChecked(True)
        self.ui.fliterBox_8.setChecked(True)
        self.ui.fliterBox_9.setChecked(True)
        self.ui.fliterBox_10.setChecked(True)
        
        self.ui.fliterBox_1.setText(_translate("MainWindow", filter_1.__doc__, None))
        self.ui.fliterBox_2.setText(_translate("MainWindow", filter_2.__doc__, None))
        self.ui.fliterBox_3.setText(_translate("MainWindow", filter_3.__doc__, None))
        self.ui.fliterBox_4.setText(_translate("MainWindow", filter_4.__doc__, None))
        self.ui.fliterBox_5.setText(_translate("MainWindow", filter_5.__doc__, None))
        self.ui.fliterBox_6.setText(_translate("MainWindow", filter_6.__doc__, None))
        self.ui.fliterBox_7.setText(_translate("MainWindow", filter_7.__doc__, None))
        self.ui.fliterBox_8.setText(_translate("MainWindow", filter_8.__doc__, None))
        self.ui.fliterBox_9.setText(_translate("MainWindow", filter_9.__doc__, None))
        self.ui.fliterBox_10.setText(_translate("MainWindow",filter_10.__doc__, None))
        
        
    
        
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    application = Lottery()
    application.show()
    sys.exit(app.exec_())
