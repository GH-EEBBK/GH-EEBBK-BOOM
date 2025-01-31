# coding:utf-8
import sys
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, Theme, FolderValidator)

from .setting import CONFIG_FILE



def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # TODO: ADD YOUR CONFIG GROUP HERE

    # register
    rememberMe = ConfigItem("Register", "RememberMe", True)
    email = ConfigItem("Register", "Email", "")
    activationCode = ConfigItem("Register", "ActivationCode", "")

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())
    
    # img分区文件存储
    imgFolderPath = ConfigItem("Software", "ImgFolder", "C:/", FolderValidator())


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load(str(CONFIG_FILE.absolute()), cfg)