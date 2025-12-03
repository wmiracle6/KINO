import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty

class MenuButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.setStyleSheet("")
        self._rotation = 0
        self.is_open = False
        self.menu = None  # ссылка на выпадающее меню
        self.size_anim = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg = QColor(27, 38, 79, 77)  # #1B264F @ 30%
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 30, 30)

        bar_color = QColor("#302B27")
        painter.setBrush(bar_color)
        painter.setPen(Qt.PenStyle.NoPen)

        bar_w, bar_h = 30, 3
        spacing = 4
        total_h = 4 * bar_h + 3 * spacing
        y0 = (60 - total_h) // 2
        x0 = (60 - bar_w) // 2

        if self._rotation != 0:
            painter.save()
            painter.translate(30, 30)
            painter.rotate(self._rotation)
            painter.translate(-30, -30)

        for i in range(4):
            y = y0 + i * (bar_h + spacing)
            painter.drawRect(QRect(x0, y, bar_w, bar_h))

        if self._rotation != 0:
            painter.restore()

    def getRotation(self):
        return self._rotation
    def setRotation(self, angle):
        self._rotation = angle
        self.update()
    rotation = pyqtProperty(int, getRotation, setRotation)

    def getHeight(self):
        return self.height()
    def setHeight(self, h):
        self.setFixedSize(60, h)
    anim_height = pyqtProperty(int, getHeight, setHeight)

    def toggle(self):
        self.anim = QPropertyAnimation(self, b"rotation")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        if self.is_open:
            self.anim.setStartValue(90)
            self.anim.setEndValue(0)
        else:
            self.anim.setStartValue(0)
            self.anim.setEndValue(90)

        def on_finished():
            self.is_open = not self.is_open
            if self.is_open:
                self.show_menu()
            else:
                self.hide_menu()
        self.anim.finished.connect(on_finished)
        self.anim.start()

    def show_menu(self):
        if not self.menu:
            self.menu = DropdownMenu(self)
            self.menu.setParent(self)
            self.menu.move(0, 60)  # сразу под полосками
            self.menu.hide()  # скрываем, чтобы потом показать с анимацией

        self.menu.show()
        self.menu.raise_()

        # Анимация увеличения высоты кнопки
        self.size_anim = QPropertyAnimation(self, b"anim_height")
        self.size_anim.setDuration(300)
        self.size_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.size_anim.setStartValue(60)
        self.size_anim.setEndValue(210)  # 60 + 150
        self.size_anim.start()

    def hide_menu(self):
        if self.menu:
            self.menu.hide()
        self.size_anim = QPropertyAnimation(self, b"anim_height")
        self.size_anim.setDuration(250)
        self.size_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.size_anim.setStartValue(self.height())
        self.size_anim.setEndValue(60)
        self.size_anim.start()


class DropdownMenu(QFrame):
    """Выпадающее меню, привязанное к кнопке"""
    def __init__(self, parent_button):
        super().__init__(parent_button)
        self.parent_button = parent_button
        self.setFixedWidth(60)
        self.setFixedHeight(150)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
            QPushButton {
                background-color: #274690;
                color: #F5F3F5;
                border-radius: 6px;
                font-family: 'Inter';
                font-size: 14px;
                padding: 8px;
                margin: 4px;
                min-height: 36px;
            }
            QPushButton#active { background-color: #FF5353; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(4)
        for name in ["Афиша", "Акции", "Профиль"]:
            btn = QPushButton(name)
            if name == "Афиша":
                btn.setObjectName("active")
            layout.addWidget(btn)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Онлайн-сервис покупки билетов в кинотеатр")
        self.resize(1280, 720)
        self.setStyleSheet("QMainWindow { background-color: #567CA8; }")

        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(15, 15, 0, 0)
        self.btn = MenuButton()
        self.btn.clicked.connect(self.btn.toggle)
        top_layout.addWidget(self.btn)
        top_layout.addStretch()
        main.addWidget(top_bar)

        # Контент
        label = QLabel("Афиша\n\n🔹 Горизонтальные полоски → закрыто\n🔹 Вертикальные → открыто")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #F5F3F5; font: 18px 'Inter';")
        main.addWidget(label)
        main.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())