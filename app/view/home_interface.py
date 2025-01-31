# coding: utf-8

import os
import base64
import zipfile
import io
import subprocess
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt
from loguru import logger
from qfluentwidgets import SmoothScrollArea, FlowLayout

from ..components.disclaimer_card import DisclaimerCard
from ..components.information_card import ConnectionInformationCard
from ..components.flash_card import FlashCard

# zip文件转换工具在file_to_base64.py里


# 瀑布流布局,用于加载功能板块
class HomeScrollArea(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = QWidget(self)

        self.__initWidget()

    def __initWidget(self):
        self.setObjectName("HomeScrollArea")
        self.setWidgetResizable(True)
        self.setWidget(self.widgets)
        self.setStyleSheet(
            "#HomeScrollArea{" "background:transparent;" "border:none;" "}"
        )

        self.widgets.setObjectName("HomeScrollAreaWidget")
        self.widgets.setStyleSheet(
            "#HomeScrollAreaWidget{"
            "background:transparent;"
            "background-color:#F7F9FC;"
            "}"
        )

        self.__initLayout()

    def __initLayout(self):
        self.layouts = FlowLayout(self.widgets)
        self.layouts.setContentsMargins(0, 5, 0, 5)
        self.widgets.setLayout(self.layouts)

    def addSubWidget(self, widget) -> None:
        """
        addSubWidget 添加子控件到流式布局中
        Args:
            widget (QWidget): 添加到流式布局的字控件
        """
        self.layouts.addWidget(widget)


class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.vBoxLayout = QVBoxLayout(self)

        self.connectionInformationCard = ConnectionInformationCard(self)
        self.disclaimerCard = DisclaimerCard(self)

        self.flashCard = FlashCard(self)

        self.scrollArea = HomeScrollArea(self)
        self.progressBar = QProgressBar(self)  # 创建进度条
        self.progressBar.setRange(0, 100)  # 设置进度条范围
        self.progressBar.setValue(0)

        self.__initWidget()

        # 启动自解压任务
        # self.unzip_and_run()

    def __initWidget(self):
        self.setObjectName("HomeInterface")

        self.scrollArea.addSubWidget(self.flashCard)

        self.__initLayout()

    def __initLayout(self):
        self.vBoxLayout.addWidget(
            self.connectionInformationCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.vBoxLayout.addWidget(self.disclaimerCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.scrollArea)
        self.vBoxLayout.addWidget(self.progressBar)  # 将进度条添加到布局中

    def unzip_and_run(self):
        """
        解压存储在 data_unzip.py 中的 ZIP 文件字符串，并启动 Flash.exe
        """
        try:
            from data_unzip import zip_data  # 导入打包的 ZIP 文件数据

            zip_bytes = base64.b64decode(zip_data)
            zip_file = io.BytesIO(zip_bytes)

            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                total_files = len(zip_ref.namelist())  # 获取 ZIP 文件中的文件总数
                extracted_count = 0

                # 创建一个临时目录来存储解压后的文件
                if not os.path.exists("unzipped_data"):
                    os.makedirs("unzipped_data")

                for file in zip_ref.namelist():
                    zip_ref.extract(file, "unzipped_data")  # 解压文件
                    extracted_count += 1
                    progress = int((extracted_count / total_files) * 100)  # 计算进度
                    self.progressBar.setValue(progress)  # 更新进度条
                    QtCore.QCoreApplication.processEvents()  # 确保界面更新

                logger.info("解压完成")
                self.progressBar.setValue(100)  # 设置进度条为100%

                # 查找并启动 Flash.exe
                flash_exe_path = self.find_flash_exe("unzipped_data")
                if flash_exe_path:
                    self.run_flash_exe(flash_exe_path)
                else:
                    QMessageBox.warning(self, "警告", "未找到 Flash.exe 文件")
        except Exception as e:
            logger.error(f"解压失败: {e}")
            QMessageBox.critical(self, "错误", f"解压失败: {e}")

    def find_flash_exe(self, directory):
        """
        在指定目录中查找 Flash.exe 文件
        """
        for root, dirs, files in os.walk(directory):
            if "Flash.exe" in files:
                return os.path.join(root, "Flash.exe")
        return None

    def run_flash_exe(self, path):
        """
        启动 Flash.exe 文件
        """
        try:
            subprocess.Popen(path, shell=True)
            QMessageBox.information(self, "成功", "Flash.exe 已启动")
        except Exception as e:
            logger.error(f"启动 Flash.exe 失败: {e}")
            QMessageBox.critical(self, "错误", f"启动 Flash.exe 失败: {e}")
