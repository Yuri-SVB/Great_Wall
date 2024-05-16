import numpy as np
from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QImage, QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...greatwall.helpers import constants
from ...greatwall.helpers.colormaps import color_palettes
from ...memo_assistant import MemoCard


class ImageViewer(QGraphicsView):
    """Custom image viewer widget with zoom and pan capability."""

    def __init__(self, parent):
        super(ImageViewer, self).__init__(parent)
        self.empty = True
        self.image = QGraphicsPixmapItem()
        self.scene = QGraphicsScene(self)
        self.scene.addItem(self.image)

        # The following attributes are for internal implementation only.
        self._zoom = 0

        # The main purpose of the following attributes are to keep
        # the underline data preserved and not noisy and distorted
        # by python garbage collection when manipulating the underline data.
        self._normalized_array = None
        self._rgb_img = None
        self._qimage = None

        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

    def numpy_2darray_to_Qimage(self, numpy_2darray, colormap):
        """
        Convert the 2D numpy array into a 3-chanels 8-bit QImage depending on
            passed `colormap` argument. The first dimension represents the
            vertical image axis.
        """
        numpy_2darray = numpy_2darray * 255
        numpy_2darray = np.require(numpy_2darray, np.uint8, "C")

        if len(numpy_2darray.shape) != 2:
            raise ValueError(
                "Sorry, but we can only convert 2D arrays! Check your input please!"
            )
        width, height = numpy_2darray.shape

        self._qimage = QImage(numpy_2darray.data, width, height, QImage.Format_Indexed8)
        self._qimage.setColorTable(colormap)

        return self._qimage

    def hasPhoto(self):
        return not self.empty

    def fitInView(self, scale=True):
        if self.hasPhoto():
            rect = QRectF(self.image.pixmap().rect())
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())

            viewrect = self.rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(
                viewrect.width() / scenerect.width(),
                viewrect.height() / scenerect.height(),
            )
            self.scale(factor, factor)
        self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self.empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.image.setPixmap(pixmap)
        else:
            self.empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self.image.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0


class MemorizationAssistantWindow(QWidget):
    gui_error_signal = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Set header widgets group
        pallette_types_label = QLabel("Tacit Knowledge Types:", self)
        pallette_types_combobox = QComboBox(self)
        pallette_types_combobox.addItems(constants.AVAILABLE_TACIT_KNOWLEDGE_TYPES)
        pallette_types_combobox.setCurrentText(
            constants.AVAILABLE_TACIT_KNOWLEDGE_TYPES[0]
        )
        pallette_types_combobox.currentTextChanged.connect(
            self._on_pallette_type_change
        )
        guide_message_label = QLabel(
            "Please, choose at which level you remember the following Card:", self
        )
        header_layout = QVBoxLayout()
        header_layout.addWidget(pallette_types_label)
        header_layout.addWidget(pallette_types_combobox)
        header_layout.addWidget(guide_message_label)

        header_group = QGroupBox()
        header_group.setLayout(header_layout)

        # Set assistant widgets group
        memorization_pallette = QLabel(self)
        again_button = QPushButton("Again", self)
        hard_button = QPushButton("Hard", self)
        good_button = QPushButton("Good", self)
        easy_button = QPushButton("easy", self)

        grade_layout = QHBoxLayout()
        grade_layout.addWidget(again_button)
        grade_layout.addWidget(hard_button)
        grade_layout.addWidget(good_button)
        grade_layout.addWidget(easy_button)

        pallette_layout = QVBoxLayout()
        pallette_layout.addStretch(1)
        pallette_layout.addWidget(memorization_pallette)
        pallette_layout.addStretch(1)
        pallette_layout.addLayout(grade_layout)

        pallette_group = QGroupBox()
        pallette_group.setLayout(pallette_layout)

        # Set navigation widgets group
        leave_button = QPushButton("Leave", self)
        leave_button.clicked.connect(self._on_leave_button_click)
        navigation_layout = QHBoxLayout()
        navigation_layout.addWidget(leave_button)

        # Set memorization group
        memorization_layout = QVBoxLayout()
        memorization_layout.addWidget(header_group)
        memorization_layout.addWidget(pallette_group)
        memorization_layout.addLayout(navigation_layout)
        self.setLayout(memorization_layout)

    def _on_pallette_type_change(self):
        pass

    def _on_again_button_click(self):
        pass

    def _on_hard_button_click(self):
        pass

    def _on_good_button_click(self):
        pass

    def _on_easy_button_click(self):
        pass

    def _on_leave_button_click(self):
        self.close()
        self.main_window.stacked.setCurrentWidget(self.main_window.welcome_view)
