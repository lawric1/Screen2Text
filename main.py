import pytesseract
from io import BytesIO
from PIL import Image, ImageGrab
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QAction, QSystemTrayIcon, QMenu
import sys

pytesseract.pytesseract.tesseract_cmd = r'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.setWindowOpacity(0.1)

        self.exit = QAction("Exit Application", shortcut = QtGui.QKeySequence("ESC"), triggered=lambda:self.close())
        self.addAction(self.exit)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(0, 0, 255, 160))  
        qp.setBrush(br)   
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.getText(self.begin, self.end)

        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def getText(self, p1, p2):
        x1, y1, x2, y2 = self.getRectCoords(p1, p2)

        img = ImageGrab.grab()
        img = img.crop((x1, y1, x2, y2)).convert('L')

        width, height = img.size
        ratio = width/height

        new_height = 500
        new_width = int(new_height * ratio)

        img = img.resize((new_width, new_height))
        img = img.point(lambda x: 0 if x<100 else 255, '1')
        # img.show()

        result = pytesseract.image_to_string(img, config="--psm 6")
        print(result)

        self.copyToClipboard(result)
        self.close()

    def getRectCoords(self, p1, p2):
        p1 = (int(p1.x()), int(p1.y()))
        p2 = (int(p2.x()), int(p2.y()))
        p3 = (p1[0], p2[1])
        p4 = (p2[0], p1[1])

        startPoint = min(p1,p2,p3,p4)
        endPoint = max(p1,p2,p3,p4)

        return startPoint[0], startPoint[1], endPoint[0], endPoint[1]

    def copyToClipboard(self, result):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(result, mode=cb.Clipboard)

class Tray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()

        icon = QtGui.QIcon("icon.png")
        self.setIcon(icon)
        self.setVisible(True)

if __name__ == "__main__":
    App = QApplication(sys.argv)
    App.setQuitOnLastWindowClosed(False)

    canvas = Canvas()
    tray = Tray()
    
    menu = QMenu()
    menu.addAction("Run", canvas.showFullScreen)
    menu.addAction("Quit", App.quit)
    tray.setContextMenu(menu)

    tray.activated.connect(canvas.showFullScreen)

    sys.exit(App.exec())


# To-do

    # After canvas is closed, send notification with the extracted text, and send text to clipboard
    # Better OCR text detection