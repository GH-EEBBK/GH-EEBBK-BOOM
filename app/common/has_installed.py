import winreg


def has_install(soft_name, m_strCurExecFileName=""):
    # 定义注册表路径
    base_key = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"

    try:
        # 打开注册表键
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_key) as reg_key:
            # 遍历所有子键
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                sub_key_name = winreg.EnumKey(reg_key, i)
                sub_key_path = f"{base_key}\\{sub_key_name}"

                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key_path) as sub_key:
                    try:
                        # 获取 DisplayName
                        display_name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                        # 获取 InstallLocation
                        install_location, _ = winreg.QueryValueEx(
                            sub_key, "InstallLocation"
                        )

                        if soft_name.lower() in display_name.lower():
                            # 替换路径分隔符，并拼接 bin 文件夹和当前执行文件名
                            file_path = (
                                install_location.replace("\\", "/")
                                + "/bin/"
                                + m_strCurExecFileName
                            )
                            return file_path
                    except OSError:
                        # 如果某些键没有 DisplayName 或 InstallLocation，忽略错误
                        continue
    except OSError:
        # 如果注册表路径不存在，返回空字符串
        pass

    return ""
m_strCurExecFileName = "QFIL.exe"  # 假设当前执行文件名为 example.exe
result = has_install("QPST")
if result:
    print("软件已安装，路径为：", result)
else:
    print("软件未安装")
