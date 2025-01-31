# coding: utf-8

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt

from qfluentwidgets import CardWidget, BodyLabel

from ..common.setFont import setFont, FontWeight


class DisclaimerCard(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.vBoxLayout = QVBoxLayout(self)

        self.titleLabel = BodyLabel(self)
        self.contextLabel = BodyLabel(self)

        self.__initWidget()

    def __initWidget(self):
        self.titleLabel.setText("免责声明")
        setFont(self.titleLabel, 16, FontWeight.DemiBold)

        self.contextLabel.setWordWrap(True)
        self.contextLabel.setText(
            "本软件仅供学习和研究使用，未经授权不得用于商业用途。\n用户使用本软件时，应遵守相关法律法规。\n开发者不承担因使用本软件而产生的任何法律责任。"
        )
        setFont(self.contextLabel, 13, FontWeight.Normal)

        self.__initLayout()

    def __initLayout(self):
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(10, 5, 5, 5)

        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contextLabel)
