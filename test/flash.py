import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QTextEdit,
    QMessageBox,
    QCheckBox,
)
from PyQt5.QtCore import QProcess


class EDLFlashTool(QWidget):
    def __init__(self):
        super().__init__()
        self.img_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # 获取程序所在目录
        self.img_files = {}  # 存储分区名与img文件路径的映射（例如 {"boot": "boot.img"}）
        self.initUI()
        self.scan_img_files()  # 启动时自动扫描img文件

    def initUI(self):
        self.setWindowTitle("高通EDL刷机工具 (固定路径模式)")
        self.setGeometry(100, 100, 800, 600)

        # 主布局
        layout = QVBoxLayout()

        # 分区列表
        self.partition_list_label = QLabel("可刷写的分区 (自动加载程序目录中的.img文件):")
        self.partition_list = QListWidget()
        self.refresh_button = QPushButton("刷新列表")
        self.refresh_button.clicked.connect(self.scan_img_files)

        # 操作按钮
        self.flash_button = QPushButton("刷写选中分区")
        self.flash_button.clicked.connect(self.flash_selected_partitions)

        # 高级选项
        self.format_data_checkbox = QCheckBox("刷写完成后格式化DATA分区")

        # 日志输出
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # 布局
        layout.addWidget(self.partition_list_label)
        layout.addWidget(self.partition_list)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.format_data_checkbox)
        layout.addWidget(self.flash_button)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        # QProcess对象
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)

    def scan_img_files(self):
        """扫描程序目录中的.img文件，自动填充分区列表"""
        self.img_files.clear()
        self.partition_list.clear()

        for file in os.listdir(self.img_dir):
            if file.endswith(".img"):
                partition = file[:-4]  # 去除".img"后缀作为分区名
                self.img_files[partition] = os.path.join(self.img_dir, file)
                self.partition_list.addItem(partition)

        self.log_output.append(f"找到 {len(self.img_files)} 个可刷写的分区镜像")

    def flash_selected_partitions(self):
        """刷写用户选中的分区"""
        selected_items = self.partition_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "错误", "请先选择要刷写的分区！")
            return

        # 获取选中的分区名
        partitions = [item.text() for item in selected_items]

        # 逐个刷写分区
        for partition in partitions:
            img_path = self.img_files.get(partition)
            if not img_path or not os.path.exists(img_path):
                self.log_output.append(f"错误: 分区 {partition} 的镜像文件不存在！")
                continue

            self.log_output.append(f"正在刷写 {partition}...")
            self.process.start(f"fastboot flash {partition} {img_path}")
            if not self.process.waitForFinished(30000):  # 30秒超时
                self.log_output.append(f"刷写 {partition} 超时！")

        # 格式化DATA分区（如果勾选）
        if self.format_data_checkbox.isChecked():
            self.log_output.append("正在格式化DATA分区...")
            self.process.start("fastboot format data")
            self.process.waitForFinished()

        self.log_output.append("操作完成！")

    def handle_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.log_output.append(output)

    def handle_error(self):
        error = self.process.readAllStandardError().data().decode()
        self.log_output.append(f"错误: {error}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = EDLFlashTool()
    tool.show()
    sys.exit(app.exec_())