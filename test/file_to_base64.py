# coding: utf-8

import os
import base64
import zipfile
import io
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QLabel,
    QMessageBox
)
from PyQt5.QtCore import Qt
from loguru import logger


class FilePacker(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("文件夹打包为base64")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        self.label = QLabel("请选择要打包的文件夹")
        self.layout.addWidget(self.label)

        self.selectFolderButton = QPushButton("选择文件夹")
        self.selectFolderButton.clicked.connect(self.selectFolder)
        self.layout.addWidget(self.selectFolderButton)

        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.layout.addWidget(self.progressBar)

        self.packButton = QPushButton("生成打包文件")
        self.packButton.clicked.connect(self.packFiles)
        self.layout.addWidget(self.packButton)

        self.setLayout(self.layout)

    def selectFolder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.folder_path = folder_path
            self.label.setText(f"已选择文件夹: {folder_path}")
        else:
            self.label.setText("未选择文件夹")

    def packFiles(self):
        if not hasattr(self, 'folder_path'):
            QMessageBox.warning(self, "警告", "请先选择一个文件夹")
            return

        try:
            zip_data = self.create_zip(self.folder_path)
            self.write_to_python_file(zip_data)
            QMessageBox.information(self, "成功", "打包文件已生成")
        except Exception as e:
            logger.error(f"打包失败: {e}")
            QMessageBox.critical(self, "错误", f"打包失败: {e}")

    def create_zip(self, folder_path):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            total_files = sum([len(files) for r, d, files in os.walk(folder_path)])
            processed_files = 0

            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, rel_path)
                    processed_files += 1
                    self.update_progress(processed_files, total_files)

        zip_buffer.seek(0)
        return base64.b64encode(zip_buffer.getvalue()).decode('utf-8')

    def update_progress(self, processed_files, total_files):
        progress = int((processed_files / total_files) * 100)
        self.progressBar.setValue(progress)
        QtCore.QCoreApplication.processEvents()

    def write_to_python_file(self, zip_data):
        with open('data_unzip.py', 'w') as f:
            f.write('zip_data = """\n')
            f.write(zip_data)
            f.write('\n"""\n')
        logger.info("打包文件已成功写入 data_unzip.py")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ex = FilePacker()
    ex.show()
    sys.exit(app.exec_())