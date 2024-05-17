import numpy as np
from PyQt5.QtCore import (
    QMargins,
    QPoint,
    QRect,
    QRectF,
    QSize,
    Qt,
)
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
    QLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)

from ...greatwall.helpers import constants
from ...greatwall.helpers.colormaps import color_palettes


class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def insertWidget(self, idx, widget):
        """Insert widget `widget` at specific index `idx` in the widgets list.

        If the index `idx` equals to -1 this method will add the widget at the
        end of widgets list.

        If the widget is already exist this method will remove the widget from
        current position and insert it at the index `idx`.
        """
        self._item_list = [i for i in self._item_list if i.widget() != widget]
        if idx == -1:
            self._item_list.insert(len(self._item_list), QWidgetItem(widget))
        else:
            self._item_list.insert(idx, QWidgetItem(widget))

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(
            2 * self.contentsMargins().top(), 2 * self.contentsMargins().top()
        )
        return size

    def _do_layout(self, rect, test_only):
        # Center the item group vertically, taking into
        # account the width in the row.
        row_widths = [0]
        row = 0
        for item in self._item_list:
            wid = item.widget()
            space_x = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
            )
            item_width = item.sizeHint().width() + space_x
            if row_widths[row] + item_width < rect.right():
                row_widths[row] += item_width
            else:
                row += 1
                row_widths.append(item_width)

        x = int((rect.width() - row_widths[0]) / 2)
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        row = 0
        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                row += 1
                x = int((rect.width() - row_widths[row]) / 2)
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


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
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Set header widgets group
        palette_types_label = QLabel("Tacit Knowledge Types:", self)
        self.palette_types_combobox = QComboBox(self)
        self.palette_types_combobox.currentTextChanged.connect(
            self._on_palette_type_change
        )
        guide_message_label = QLabel(
            f"The following is a palettes used to derive your hash.\n"
            f"Please, choose at which level you remember these palettes:",
            self,
        )
        header_layout = QVBoxLayout()
        header_layout.addWidget(palette_types_label)
        header_layout.addWidget(self.palette_types_combobox)
        header_layout.addWidget(guide_message_label)

        header_group = QGroupBox()
        header_group.setLayout(header_layout)

        # Set assistant widgets group
        self.memorization_palette = QStackedWidget(self)
        again_button = QPushButton("Again", self)
        again_button.clicked.connect(self._on_again_button_click)
        again_button.clicked.connect(self._on_palette_type_change)
        again_button.setStyleSheet("background-color: gray")
        hard_button = QPushButton("Hard", self)
        hard_button.clicked.connect(self._on_hard_button_click)
        hard_button.clicked.connect(self._on_palette_type_change)
        hard_button.setStyleSheet("background-color: red")
        good_button = QPushButton("Good", self)
        good_button.clicked.connect(self._on_good_button_click)
        good_button.clicked.connect(self._on_palette_type_change)
        good_button.setStyleSheet("background-color: green")
        easy_button = QPushButton("easy", self)
        easy_button.clicked.connect(self._on_easy_button_click)
        easy_button.clicked.connect(self._on_palette_type_change)
        easy_button.setStyleSheet("background-color: lime")

        grade_layout = QHBoxLayout()
        grade_layout.addWidget(again_button)
        grade_layout.addWidget(hard_button)
        grade_layout.addWidget(good_button)
        grade_layout.addWidget(easy_button)

        palette_layout = QVBoxLayout()
        palette_layout.addWidget(self.memorization_palette)
        palette_layout.addLayout(grade_layout)

        self.palette_types_combobox.addItems(constants.AVAILABLE_TACIT_KNOWLEDGE_TYPES)

        palette_group = QGroupBox()
        palette_group.setLayout(palette_layout)

        # Set navigation widgets group
        leave_button = QPushButton("Leave", self)
        leave_button.clicked.connect(self._on_leave_button_click)
        navigation_layout = QHBoxLayout()
        navigation_layout.addWidget(leave_button)

        # Set memorization group
        memorization_layout = QVBoxLayout()
        memorization_layout.addWidget(header_group)
        memorization_layout.addWidget(palette_group)
        memorization_layout.addLayout(navigation_layout)
        self.setLayout(memorization_layout)

    def _on_palette_type_change(self):
        def memo_cards_sort_fun(e):
            return e.due

        if not hasattr(self.main_window, "greatwall"):
            palette_group = QLabel("Sorry! But you don't have cards to review.", self)
            self.memorization_palette.addWidget(palette_group)
            self.memorization_palette.setCurrentWidget(palette_group)
            return

        if not self.main_window.greatwall.get_memorization_cards:
            palette_group = QLabel("Sorry! But you don't have cards to review.", self)
            self.memorization_palette.addWidget(palette_group)
            self.memorization_palette.setCurrentWidget(palette_group)
            return

        user_choice = self.palette_types_combobox.currentText()
        self.main_window.greatwall.get_memorization_cards.sort(
            reverse=True, key=memo_cards_sort_fun
        )
        if user_choice == constants.FRACTAL:
            for idx, card in enumerate(
                self.main_window.greatwall.get_memorization_cards
            ):
                if card.knowledge_type == constants.FRACTAL:
                    scroll_area = QScrollArea()
                    flow_widget = QWidget()
                    flow_layout = FlowLayout()

                    for palette in self.main_window.greatwall.get_memorization_cards[
                        idx
                    ].knowledge:
                        fractal_viewer = ImageViewer(self)
                        colormap = color_palettes["Viridis Colormap"]

                        fractal_raw = QPixmap.fromImage(
                            fractal_viewer.numpy_2darray_to_Qimage(palette, colormap)
                        )
                        fractal_viewer.setFixedSize(QSize(205, 205))
                        fractal_viewer.setPhoto(fractal_raw)
                        fractal_viewer.setVisible(True)

                        flow_layout.addWidget(fractal_viewer)

                    # WARNING: We are adding the `FlowLayout` to `QWidget`
                    # to be able to remove it later.
                    flow_widget.setLayout(flow_layout)

                    scroll_area.setWidgetResizable(True)
                    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
                    scroll_area.viewport().installEventFilter(self)
                    scroll_area.setWidget(flow_widget)

                    palette_group = scroll_area
                    self.memorization_palette.addWidget(palette_group)
                    break
            else:
                palette_group = QLabel(
                    "Sorry! But you don't have cards to review in this knowledge type.",
                    self,
                )
                self.memorization_palette.addWidget(palette_group)
                self.memorization_palette.setCurrentWidget(palette_group)
                return
        elif user_choice == constants.FORMOSA:
            user_sentences = []

            fractal_viewer = ImageViewer(self)

            palette_group = scroll_area
            self.memorization_palette.addWidget(palette_group)
            pass
        elif user_choice == constants.SHAPE:
            user_shapes = []

            fractal_viewer = ImageViewer(self)

            palette_group = scroll_area
            self.memorization_palette.addWidget(palette_group)
            pass
        else:
            ## TODO: Add error handling. <17-05-2024, MuhammadMuradG>
            palette_group = QLabel("Sorry! But you don't have cards to review", self)
            self.memorization_palette.addWidget(palette_group)

        self.memorization_palette.setCurrentWidget(palette_group)

    def _on_again_button_click(self):
        self.main_window.greatwall.get_memorization_cards[0].rate_card("again")

    def _on_hard_button_click(self):
        self.main_window.greatwall.get_memorization_cards[0].rate_card("hard")

    def _on_good_button_click(self):
        self.main_window.greatwall.get_memorization_cards[0].rate_card("good")

    def _on_easy_button_click(self):
        self.main_window.greatwall.get_memorization_cards[0].rate_card("easy")

    def _on_leave_button_click(self):
        self.close()
        self.main_window.stacked.setCurrentWidget(self.main_window.welcome_view)
