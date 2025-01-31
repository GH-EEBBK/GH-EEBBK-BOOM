# coding: utf-8

import mysql.connector
from PyQt5.QtCore import QThread, pyqtSignal


class LicenseServiceThread(QThread):
    resultSignal = pyqtSignal(bool)

    def __init__(self, qqNubmer, license):
        super().__init__()
        self.qqNubmer = qqNubmer
        self.license = license

    def run(self):
        # 创建数据库连接
        db = mysql.connector.connect(
            host="mysql2.sqlpub.com",
            user="	hungry630",
            password="tq0EutRGnmMdzMls",
            database="database666",
            port=3307,
        )

        cursor = db.cursor()
        cursor.execute("SELECT * FROM qqnumber;")
        results = cursor.fetchall()

        results = [str(item[0]).strip() for item in results]

        if self.qqNubmer in results:
            cursor.execute("SELECT * FROM license")
            results = cursor.fetchall()

            results = [item[0] for item in results][0]
            if self.license == results:
                self.resultSignal.emit(True)

            else:
                self.resultSignal.emit(False)

        else:

            self.resultSignal.emit(False)

        cursor.close()
        db.close()
        self.finished.emit()
