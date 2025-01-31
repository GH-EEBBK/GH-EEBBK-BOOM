# coding:utf-8
from qfluentwidgets import (
    SwitchSettingCard,
    PrimaryPushSettingCard,
    PushSettingCard,
    ScrollArea,
    ComboBoxSettingCard,
    ExpandLayout,
    setTheme,
    setFont,
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup as CardGroup
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog

from ..common.config import cfg, isWin11, qconfig
from ..common.setting import AUTHOR, VERSION, YEAR
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet


class SettingCardGroup(CardGroup):

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        setFont(self.titleLabel, 14, QFont.Weight.DemiBold)


class SettingInterface(ScrollArea):
    """设置界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 设置标签
        self.settingLabel = QLabel("设置", self)

        # 个性化
        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            "亚克力效果",
            "将半透明效果应用于窗口和表面",
            cfg.micaEnabled,
            self.personalGroup,
        )
        self.themeCard = ComboBoxSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "应用程序主题",
            "更改应用程序的外观",
            texts=["亮色", "暗色", "使用系统设置"],
            parent=self.personalGroup,
        )
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            "界面缩放",
            "更改控件和字体的大小",
            texts=["100%", "125%", "150%", "175%", "200%", "使用系统设置"],
            parent=self.personalGroup,
        )

        # 软件更新
        self.updateSoftwareGroup = SettingCardGroup("软件更新", self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            "启动时检查更新",
            "新版本将更加稳定并提供更多功能",
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup,
        )

        # 应用程序
        self.softwareGroup = SettingCardGroup("文件路径", self.scrollWidget)
        self.imgFolderCard = PushSettingCard(
            "IMG刷机文件",
            FIF.FOLDER,
            "IMG刷机文件",
            qconfig.get(cfg.imgFolderPath),
            self.softwareGroup,
        )

        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.aboutCard = PrimaryPushSettingCard(
            "检查更新",
            ":app/images/logo.jpg",
            "关于",
            "© 版权 " + str(YEAR) + ", " + AUTHOR + ". " + "版本 " + VERSION,
            self.aboutGroup,
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingInterface")

        # 初始化样式表
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")

        self.micaCard.setEnabled(isWin11())

        # 初始化布局
        self.__initLayout()
        self._connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 50)

        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.softwareGroup.addSettingCard(self.imgFolderCard)

        self.aboutGroup.addSettingCard(self.aboutCard)

        # 将设置卡片组添加到布局中
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.softwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        """显示重启提示"""
        InfoBar.success("更新成功", "配置将在重启后生效", duration=1500, parent=self)

    def _connectSignalToSlot(self):
        """连接信号到槽"""
        cfg.appRestartSig.connect(self._showRestartTooltip)

        # 个性化
        cfg.themeChanged.connect(setTheme)
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # 更新文件夹
        self.imgFolderCard.clicked.connect(self.__onImgFolderCardClicked)

        # 检查更新
        self.aboutCard.clicked.connect(signalBus.checkUpdateSig)

    def __onImgFolderCardClicked(self):
        """download folder card clicked slot"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if not folder or cfg.get(cfg.imgFolderPath) == folder:
            return

        qconfig.set(cfg.imgFolderPath, folder)
        self.imgFolderCard.setContent(folder)
