import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PyQt6.QtGui import QPainter, QColor, QPen, QIcon, QPixmap
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize

class MenuButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.setStyleSheet("border: none;")
        self._rotation = 0
        self.is_open = False
        self.menu = None  # ссылка на выпадающее меню

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

    def hide_menu(self):
        if self.menu:
            self.menu.hide()


class DropdownMenu(QFrame):
    """Выпадающее меню, привязанное к кнопке"""
    def __init__(self, parent_button):
        super().__init__(parent_button)
        self.parent_button = parent_button
        self.setFixedWidth(60)
        # Высота зависит от количества кнопок, примерно 3 кнопки * 60px
        self.setFixedHeight(190)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(5)

        self.buttons = {}
        self.current_active = "Афиша"

        # Настройка кнопок с изображениями
        # (Название, Обычная картинка, Картинка при выборе)
        items = [
            ("Афиша", "img/Афиша.png", "img/Афиша выбрана.png"),
            ("Акции", "img/Акции.png", "img/Акция выбрана.png"),
            ("Профиль", "img/Профиль.png", "img/Профиль выбран.png")
        ]

        for name, img_normal, img_active in items:
            btn = QPushButton()
            btn.setFixedSize(60, 50)
            btn.setIconSize(QSize(50, 50))
            
            # Сохраняем пути к картинкам в объекте кнопки
            btn.img_normal = img_normal
            btn.img_active = img_active
            btn.name = name
            
            btn.clicked.connect(lambda checked, n=name: self.set_active(n))
            
            layout.addWidget(btn)
            self.buttons[name] = btn

        # Устанавливаем начальное состояние
        self.update_icons()

    def set_active(self, name):
        self.current_active = name
        self.update_icons()

    def update_icons(self):
        for name, btn in self.buttons.items():
            if name == self.current_active:
                pixmap = QPixmap(btn.img_active)
            else:
                pixmap = QPixmap(btn.img_normal)
            
            if not pixmap.isNull():
                btn.setIcon(QIcon(pixmap))
            else:
                btn.setText(name) # Fallback если картинка не найдена


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