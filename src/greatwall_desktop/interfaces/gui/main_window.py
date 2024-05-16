from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .greatwall_window import GreatWallWindow
from .memorization_window import MemorizationAssistantWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.error_occurred = Exception

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.welcome_view = self.init_welcome_view()
        self.stacked.addWidget(self.welcome_view)

        self.deriving_view = self.init_derive_view()
        self.stacked.addWidget(self.deriving_view)

        self.memorization_view = self.init_memorization_view()
        self.stacked.addWidget(self.memorization_view)

        self.stacked.setCurrentWidget(self.welcome_view)

    def init_welcome_view(self):
        # Set intro widgets layout
        intro_image_path = "greatwall_desktop/interfaces/gui/resources/gesture.png"
        intro_pixmap_image = QPixmap(intro_image_path)
        intro_image = QLabel(self)
        intro_image.setPixmap(intro_pixmap_image.scaled(QSize(100, 100)))
        intro_label = QLabel("Welcome to GreatWall!", self)

        intro_widgets_layout = QVBoxLayout()
        intro_widgets_layout.addStretch(1)
        intro_widgets_layout.addWidget(intro_image, alignment=Qt.AlignCenter)
        intro_widgets_layout.addWidget(intro_label, alignment=Qt.AlignCenter)
        intro_widgets_layout.addStretch(1)
        intro_widgets_group = QGroupBox()
        intro_widgets_group.setLayout(intro_widgets_layout)

        # Set practice widgets layout
        practice_image_path = "greatwall_desktop/interfaces/gui/resources/practice.png"
        practice_pixmap_image = QPixmap(practice_image_path)
        practice_image = QLabel(self)
        practice_image.setPixmap(practice_pixmap_image.scaled(QSize(100, 100)))
        practice_label = QLabel("Practice on your derivation!", self)
        practice_button = QPushButton("Practice", self)
        practice_button.clicked.connect(self.on_practice_button_click)

        practice_widgets_layout = QVBoxLayout()
        practice_widgets_layout.addWidget(practice_image, alignment=Qt.AlignCenter)
        practice_widgets_layout.addWidget(practice_label, alignment=Qt.AlignCenter)
        practice_widgets_layout.addWidget(practice_button)
        practice_widgets_group = QGroupBox()
        practice_widgets_group.setLayout(practice_widgets_layout)
        practice_widgets_group.setMinimumWidth(200)

        # Set deriving widgets layout
        deriving_image_path = "greatwall_desktop/interfaces/gui/resources/deriving.png"
        deriving_pixmap_image = QPixmap(deriving_image_path)
        deriving_image = QLabel(self)
        deriving_image.setPixmap(deriving_pixmap_image.scaled(QSize(100, 100)))
        deriving_label = QLabel("Deriving your hash!", self)
        deriving_button = QPushButton("Derive", self)
        deriving_button.clicked.connect(self.on_deriving_button_click)

        deriving_widgets_layout = QVBoxLayout()
        deriving_widgets_layout.addWidget(deriving_image, alignment=Qt.AlignCenter)
        deriving_widgets_layout.addWidget(deriving_label, alignment=Qt.AlignCenter)
        deriving_widgets_layout.addWidget(deriving_button)
        deriving_widgets_group = QGroupBox()
        deriving_widgets_group.setLayout(deriving_widgets_layout)
        deriving_widgets_group.setMinimumWidth(200)

        # Set navigation widgets layout
        navigation_widgets_layout = QHBoxLayout()
        navigation_widgets_layout.addWidget(practice_widgets_group)
        navigation_widgets_layout.addWidget(deriving_widgets_group)

        # Set welcome view layout
        welcome_layout = QVBoxLayout()
        welcome_layout.addWidget(intro_widgets_group)
        welcome_layout.addLayout(navigation_widgets_layout)
        welcome_view = QWidget()
        welcome_view.setLayout(welcome_layout)

        return welcome_view

    def init_derive_view(self):
        deriving_view = GreatWallWindow(self)
        return deriving_view

    def init_memorization_view(self):
        memorization_view = MemorizationAssistantWindow(self)
        return memorization_view

    def on_practice_button_click(self):
        self.memorization_view = self.init_memorization_view()
        self.stacked.addWidget(self.memorization_view)
        self.stacked.setCurrentWidget(self.memorization_view)

    def on_deriving_button_click(self):
        self.deriving_view = self.init_derive_view()
        self.stacked.addWidget(self.deriving_view)
        self.stacked.setCurrentWidget(self.deriving_view)


def main_gui():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
