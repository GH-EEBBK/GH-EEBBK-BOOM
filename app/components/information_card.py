# coding: utf-8

from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtCore import Qt

from ..common.setFont import setFont, FontWeight

from qfluentwidgets import CardWidget, BodyLabel


class ConnectionInformationCard(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.hBoxLayout = QHBoxLayout(self)

        self.connectDevices = BodyLabel(self)
        self.connectPort = BodyLabel(self)

        self.__initWidget()

    def __initWidget(self):
        self.connectDevices.setText("连接设备: 暂无连接")
        setFont(self.connectDevices, 14, FontWeight.DemiBold)

        self.connectPort.setText("连接端口: 暂无连接")
        setFont(self.connectPort, 14, FontWeight.DemiBold)

        self.__initLayout()

    def __initLayout(self):
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.connectDevices)
        self.hBoxLayout.addSpacing(30)
        self.hBoxLayout.addWidget(self.connectPort)

    def updateInformation(self, deviceName, port) -> None:
        """
        updateInformation - 更新连接信息
        Args:
            deviceName (str): 连接设备名称
            port (str): 连接端口号
        """

        self.connectDevices.setText(f"连接设备: {deviceName}")
        self.connectPort.setText(f"连接端口: {port}")
        self.update()

    def closeConnection(self) -> None:
        """
        closeConnection 设置状态为全部关闭
        """

        self.connectDevices.setText("连接设备: 暂无连接")
        self.connectPort.setText("连接端口: 暂无连接")
        self.update()

    @property
    def isConnected(self) -> bool:
        """
        isConnected 返回连接状态

        Returns:
            bool: 是否连接
        """

        if (
            self.connectDevices.text() == "连接设备: 暂无连接"
            or self.connectPort.text() == "连接端口: 暂无连接"
        ):
            return False
        else:
            return True
