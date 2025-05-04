import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from test_ui import Ui_MainWindow  # 假設你的 UI 檔叫 test.ui → pyuic5 轉成 test.py

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.label_combo.setStyleSheet("color: white; font-size: 36px; background-color: rgba(0,0,0,0);")

        self.movie = QtGui.QMovie(r"C:\Users\user\Desktop\Merry\音樂健康\gif素材\blue_fire.gif")
        self.ui.fire.setMovie(self.movie)
        self.movie.start()

        self.ui.label_combo.setText("Combo\nx5")
        self.ui.label_combo.raise_()

        # ⏲️ 5 秒後關閉火焰動畫
        QtCore.QTimer.singleShot(5000, self.clear_fire)

    def clear_fire(self):
        self.movie.stop()
        self.ui.fire.setMovie(None)
        self.ui.fire.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
