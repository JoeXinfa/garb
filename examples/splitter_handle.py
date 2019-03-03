# -*- coding: utf-8 -*-
"""
https://www.tutorialspoint.com/pyqt/pyqt_qsplitter_widget.htm
"""

import sys
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()
		
        self.initUI()
	
    def initUI(self):
	
        hbox = QHBoxLayout(self)
		
        topleft = QFrame()
        topleft.setFrameShape(QFrame.StyledPanel)
        bottom = QFrame()
        bottom.setFrameShape(QFrame.StyledPanel)
		
        splitter1 = QSplitter(Qt.Horizontal, frameShape=QFrame.StyledPanel, frameShadow=QFrame.Sunken)
        textedit = QTextEdit()
        splitter1.addWidget(topleft)
        splitter1.addWidget(textedit)
        splitter1.setSizes([100,200])
		
        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(bottom)
		
        hbox.addWidget(splitter2)
		
        self.setLayout(hbox)
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
        
#        splitter1.setStyleSheet("QSplitter::handle { image: none; }")
#        splitter1.setStyleSheet("QSplitter::handle { image: url(images/splitter.png); }")
        splitter1.setStyleSheet("QSplitter::handle { background-color: rgb(255, 0, 0); }")

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('QSplitter demo')
        self.show()
		
def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
	
if __name__ == '__main__':
    main()