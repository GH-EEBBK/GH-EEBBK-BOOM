# encoding: utf-8

from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import (QApplication, QLayout, QPushButton, QSizePolicy, QWidget,QLabel)
import random

class QL(QLabel):
    def __init__(self,parent=None,*args,**kwargs):
        super(QL,self).__init__(parent,*args,**kwargs)
        self.setMinimumWidth(100)
        self.setMinimumHeight(random.randint(20,150))
        self.setStyleSheet(r"background:green")
        self.setAlignment(Qt.AlignCenter)

    def hasHeightForWidth(self):
        return True
    def heightForWidth(self,width):
        ratio = self.width()/self.height()
        height = int(self.width()/ratio)
        return height

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly:bool):
        x = rect.x()
        y = rect.y()
        isAtFisrstRow = True
        item_rects = []

        for i,item in enumerate(self.itemList):
            wid = item.widget()
            style_layoutspacing_h = wid.style().layoutSpacing(QSizePolicy.Frame,QSizePolicy.Frame, Qt.Horizontal)
            spaceX = self.spacing() + style_layoutspacing_h
            style_layoutspacing_v = wid.style().layoutSpacing(QSizePolicy.Frame,QSizePolicy.Frame, Qt.Vertical)
            spaceY = self.spacing() + style_layoutspacing_v
            spaceSide = abs(rect.width() - (rect.width()//wid.width())*wid.width() - (rect.width()//wid.width()-1)*spaceX )//2
            
            if isAtFisrstRow:
                if len(item_rects)==0:
                    x+=spaceSide
                current_item_rect = QRect(QPoint(x, y), item.sizeHint())
                item_rects.append(current_item_rect)
                if not testOnly:
                    item.setGeometry(current_item_rect)
                next_x = current_item_rect.right() + spaceX
                x = next_x
                if next_x+current_item_rect.width() > rect.right():
                    isAtFisrstRow = False
            else:
                shortest_item_rect = min(item_rects,key = lambda item_rect:item_rect.height())
                x = shortest_item_rect.x()
                y = shortest_item_rect.bottom() + spaceY
                current_item_rect = QRect(QPoint(x, y), item.sizeHint())
                item_rects.remove(shortest_item_rect)
                item_rects.append(QRect(shortest_item_rect.topLeft(),current_item_rect.bottomRight()))
                if not testOnly:
                    item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
        if len(item_rects)> 0:
            return max(item_rects,key=lambda x:x.height()).height()
        else:
            return 0

