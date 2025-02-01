# coding: utf-8

import os

from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt, QProcess

from qfluentwidgets import (
    HeaderCardWidget,
    BodyLabel,
    ToolButton,
    CheckBox,
    ListWidget,
    PrimaryPushButton,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    StateToolTip,
)

from ..common.config import qconfig, cfg
from ..common.has_installed import has_install


class FlashCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("高通EDL刷机(固定路径模式)")
        self.setFixedWidth(350)
        self.setFixedHeight(250)

        self.imgListLabel = BodyLabel(self)
        self.imgListWidget = ListWidget(self)

        self.updateListButton = ToolButton(self)

        self.formatCheckBox = CheckBox(self)

        self.startButton = PrimaryPushButton(self)

        self.stateToolTip = None
        self.process = QProcess()

        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)

        self.__initWidget()
        self._chechInstall()

    def __initWidget(self):
        self.imgListLabel.setText("可刷写的分区")
        _, fileList = self._loadImgList(qconfig.get(cfg.imgFolderPath))
        print(fileList)
        self.imgListWidget.addItems(fileList)

        self.updateListButton.setIcon(FluentIcon.SYNC)
        self.updateListButton.clicked.connect(self._updateList)

        self.formatCheckBox.setText("完成后\n格式化DATA")

        self.startButton.setText("刷写选中分区")
        self.startButton.clicked.connect(self.flash_selected_partitions)

        self.__initLayout()

    def __initLayout(self):
        self.viewLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.listLayout = QVBoxLayout()
        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.listLayout.addWidget(self.imgListLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.listLayout.addWidget(self.imgListWidget)

        self.buttonLayout.addWidget(
            self.formatCheckBox, 0, Qt.AlignmentFlag.AlignBottom
        )
        self.buttonLayout.addWidget(self.startButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.viewLayout.addLayout(self.listLayout)
        self.viewLayout.addLayout(self.buttonLayout)

        self.headerLayout.addWidget(
            self.updateListButton, 0, Qt.AlignmentFlag.AlignRight
        )

    def _loadImgList(self, directory):
        file_dict = {}
        file_list = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".img"):
                    file_path = os.path.join(root, file)
                    file_dict[file] = file_path

                    file_list.append(file)

        return file_dict, file_list

    def _updateList(self):
        _, fileList = self._loadImgList(qconfig.get(cfg.imgFolderPath))
        self.imgListWidget.clear()
        self.imgListWidget.addItems(fileList)
        self._chechInstall()

    def flash_selected_partitions(self):
        files, fileList = self._loadImgList(qconfig.get(cfg.imgFolderPath))
        """刷写用户选中的分区"""
        selected_items = self.imgListWidget.selectedItems()
        if not selected_items:
            InfoBar.warning(
                title="提示",
                content="请先选择要刷写的分区！",
                orient=Qt.Horizontal,
                isClosable=False,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.parent().parent().parent().parent(),
            )
            return

        # 获取选中的分区名
        partitions = [item.text() for item in selected_items]

        # 逐个刷写分区
        # 只做了美化,没改功能
        for partition in partitions:
            img_path = files.get(partition)
            if not img_path or not os.path.exists(img_path):
                InfoBar.error(
                    title="错误",
                    content=f"分区 {partition} 的镜像文件不存在！",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    duration=3000,
                    position=InfoBarPosition.TOP_RIGHT,
                    parent=self.parent().parent().parent().parent(),
                )
                continue

            if not self.stateToolTip:
                self.stateToolTip = StateToolTip(
                    "正在刷写分区...",
                    "请耐心等待哦~",
                    self.parent().parent().parent().parent(),
                )
                self.stateToolTip.move(self.stateToolTip.getSuitablePos())
                self.stateToolTip.show()

            self.process.start(f"fastboot flash {partition} {img_path}")

            if not self.process.waitForFinished(30000):  # 30秒超时
                InfoBar.warning(
                    title="超时",
                    content=f"刷写 {partition} 超时！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=3000,
                    position=InfoBarPosition.TOP_RIGHT,
                    parent=self.parent().parent().parent().parent(),
                )
                continue

        # 格式化DATA分区（如果勾选）
        if self.formatCheckBox.isChecked():
            if self.stateToolTip:
                self.stateToolTip.setTitle("正在格式化DATA分区...")
            self.process.start("fastboot format data")
            self.process.waitForFinished()

        InfoBar.success(
            title="成功",
            content="刷写完成！",
            orient=Qt.Horizontal,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.parent().parent().parent().parent(),
        )
        if self.stateToolTip:
            self.stateToolTip.setTitle("完成")
            self.stateToolTip.setContent("刷写完成！")
            self.stateToolTip.setState(True)
            self.stateToolTip = None

    def handle_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        InfoBar.info(
            title="提示",
            content=output,
            orient=Qt.Horizontal,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.parent().parent().parent().parent(),
        )

    def handle_error(self):
        error = self.process.readAllStandardError().data().decode()
        InfoBar.error(
            title="错误",
            content=error,
            orient=Qt.Horizontal,
            isClosable=False,
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT,
            parent=self.parent().parent().parent().parent(),
        )

    # 检测QFIL是否安装
    def _chechInstall(self):
        exeName = "QFIL.exe"
        softName = "QPST"
        if not has_install(softName, m_strCurExecFileName=exeName):
            self.startButton.setEnabled(False)
            self.startButton.setToolTip("请先安装QPST")
        else:
            self.startButton.setEnabled(True)
            self.startButton.setToolTip("刷写选中分区")
