from PyQt5.QtCore import (
    QEvent,
    QMargins,
    QPoint,
    QRect,
    QRectF,
    QSignalTransition,
    QSize,
    QState,
    QStateMachine,
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt5.QtGui import QBrush, QColor, QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)
from greatwall_desktop.interfaces.gui.greatwall_window import GreatWallWindow


class MainWindow(QMainWindow):
    gui_error_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.error_occurred = Exception

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.welcome_view = self.init_welcome_view()
        self.stacked.addWidget(self.welcome_view)

        self.deriving_view = self.init_derive_view()
        self.stacked.addWidget(self.deriving_view)

        # self.memorization_view = self.init_memorization_view()
        # self.stacked.addWidget(self.memorization_view)

        self.stacked.setCurrentWidget(self.welcome_view)

    def init_welcome_view(self):
        practice_image_path = "/usr/home/MuhammadMouradFbsd/Projects/T3InfoSecurity/Great_Wall/src/greatwall_desktop/interfaces/gui/icons/practice.png"
        image = QPixmap(practice_image_path)
        self.practice_image = QLabel(self)
        self.practice_image.setPixmap(image.scaled(QSize(100, 100)))
        self.practice_label = QLabel("Practice on your derivation!", self)
        self.practice_button = QPushButton("Practice", self)
        self.practice_button.clicked.connect(self.on_practice_button_click)

        practice_widgets_layout = QVBoxLayout()
        practice_widgets_layout.addStretch(1)
        practice_widgets_layout.addWidget(self.practice_image, alignment=Qt.AlignCenter)
        practice_widgets_layout.addWidget(self.practice_label, alignment=Qt.AlignCenter)
        practice_widgets_layout.addWidget(self.practice_button)
        practice_widgets_layout.addStretch(1)

        practice_widgets_group = QGroupBox()
        practice_widgets_group.setLayout(practice_widgets_layout)
        practice_widgets_group.setMinimumWidth(200)

        practice_image_path = "/usr/home/MuhammadMouradFbsd/Projects/T3InfoSecurity/Great_Wall/src/greatwall_desktop/interfaces/gui/icons/derivative.png"
        image = QPixmap(practice_image_path)
        self.deriving_image = QLabel(self)
        self.deriving_image.setPixmap(image.scaled(QSize(100, 100)))
        self.deriving_label = QLabel("Deriving your hash!", self)
        self.deriving_button = QPushButton("Derive", self)
        self.deriving_button.clicked.connect(self.on_deriving_button_click)

        deriving_widgets_layout = QVBoxLayout()
        deriving_widgets_layout.addStretch(1)
        deriving_widgets_layout.addWidget(self.deriving_image, alignment=Qt.AlignCenter)
        deriving_widgets_layout.addWidget(self.deriving_label, alignment=Qt.AlignCenter)
        deriving_widgets_layout.addWidget(self.deriving_button)
        deriving_widgets_layout.addStretch(1)

        deriving_widgets_group = QGroupBox()
        deriving_widgets_group.setLayout(deriving_widgets_layout)
        deriving_widgets_group.setMinimumWidth(200)

        # Set welcome view layout
        welcome_layout = QHBoxLayout()
        welcome_layout.addWidget(practice_widgets_group)
        welcome_layout.addWidget(deriving_widgets_group)
        welcome_view = QWidget()
        welcome_view.setLayout(welcome_layout)

        return welcome_view

    def init_derive_view(self):
        deriving_view = GreatWallWindow(self)
        return deriving_view

    def init_memorization_view(self):
        pass

    def on_practice_button_click(self):
        pass

    def on_deriving_button_click(self):
        self.deriving_view = self.init_derive_view()
        self.stacked.addWidget(self.deriving_view)
        self.stacked.setCurrentWidget(self.deriving_view)


def main_gui():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
