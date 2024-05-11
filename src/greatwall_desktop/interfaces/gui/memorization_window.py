import numpy as np
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
from ...greatwall.helpers import constants
from ...greatwall.helpers.colormaps import color_palettes
from ...greatwall.helpers.utils import FractalTacitKnowledgeParam
from ...greatwall.protocol import GreatWall


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


class MemorizationAssistantWindow(QMainWindow):
    gui_error_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.greatwall_finish_result: bytes = bytes(0000)
        self.error_occurred = Exception
        self.transitions_list: list[QSignalTransition] = []

        self.greatwall = GreatWall()

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.input_view = self.init_input_view()
        self.stacked.addWidget(self.input_view)

        self.input_confirmation_view = self.init_input_confirmation_view()
        self.stacked.addWidget(self.input_confirmation_view)

        self.waiting_derivation_view = self.init_waiting_derivation_view()
        self.stacked.addWidget(self.waiting_derivation_view)

        self.selecting_derivation_view = self.init_selecting_derivation_view()
        self.stacked.addWidget(self.selecting_derivation_view)

        self.result_confirmation_view = self.init_result_confirmation_view()
        self.stacked.addWidget(self.result_confirmation_view)

        self.result_view = self.init_result_view()
        self.stacked.addWidget(self.result_view)

        self.error_view = self.init_error_view()
        self.stacked.addWidget(self.error_view)

        # Launch UI
        self.main_states_list: list[QState] = []
        self.error_states_list: list[QState] = []
        self.main_gui_state = QStateMachine()
        self.main_derivation_state = QStateMachine()
        self.selecting_derivation_states_list: list[QState] = []
        self.init_main_app_state()
