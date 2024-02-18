import numpy as np
from PyQt5.QtCore import (
    QEvent,
    QRectF,
    QMargins,
    QPoint,
    QRect,
    QSignalTransition,
    QSize,
    QState,
    QStateMachine,
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt5.QtGui import QBrush, QColor, QImage, QPixmap
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
    QStackedWidget,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from resources import constants
from resources.greatwall import GreatWall


class GreatWallThread(QThread):
    """GreatWall thread class to perform the time-consuming great wall task."""

    finished = pyqtSignal()
    canceled = pyqtSignal()
    error_occurred = pyqtSignal(str)  # Signal for passing error messages

    def __init__(self, greatwall: GreatWall):
        super().__init__()
        self.greatwall: GreatWall = greatwall
        self._is_initializing: bool = True
        self._is_canceled: bool = False
        self.user_choice: int = 0

    def run(self):
        try:
            if self._is_initializing and self.greatwall.current_level:
                raise ValueError(
                    f"GreatWall initialization doesn't match the current level {self.greatwall.current_level}"
                )
            elif self._is_initializing and not self.greatwall.current_level:
                self.greatwall.init_state_hashes()
                self._is_initializing = False
            else:
                self.greatwall.derive_from_user_choice(self.user_choice)
            if not self._is_canceled:
                self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def cancel(self):
        self._is_canceled = True
        self.canceled.emit()


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
        self.photo = QGraphicsPixmapItem()
        self.scene = QGraphicsScene(self)
        self.scene.addItem(self.photo)

        self._zoom = 0

        # The main purpose of the following attributes are to keep
        # the underline data preserved and not noisy and distorted
        # when manipulating the underline data.
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

    def gray_array_to_Qimage(self, gray_array, width=100, height=100):
        """
        Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
        colormap. The first dimension represents the vertical image axis.
        """
        if len(gray_array.shape) != 2:
            raise ValueError("gray2QImage can only convert 2D arrays")

        width, height = gray_array.shape

        self._qimage = QImage(gray_array.data, width, height, QImage.Format_Indexed8)
        for i in range(max(width, height)):
            gray_array.setColor(i, QColor(i, i, i).rgb())
        return self._qimage

    def gray_array_to_rgb_array(self, gray_array):
        """
        Convert the 2D numpy array `gray` after normalizing it into a colored
        3D numpy array with `Viridis` scheme.

        See the following for more details: `https://waldyrious.net/viridis-palette-generator/`
            and `https://www.kennethmoreland.com/color-advice/`.
        """

        color_map = {
            0: [-1e100, 0.0, 68, 1, 84],
            1: [0.0, 0.05, 68, 1, 84],
            2: [0.05, 0.1, 72, 20, 103],
            3: [0.1, 0.15, 72, 37, 118],
            4: [0.15, 0.2, 69, 55, 129],
            5: [0.2, 0.25, 64, 70, 136],
            6: [0.25, 0.3, 57, 85, 140],
            7: [0.3, 0.35, 51, 99, 141],
            8: [0.35, 0.4, 45, 113, 142],
            9: [0.4, 0.45, 40, 125, 142],
            10: [0.45, 0.5, 35, 138, 141],
            11: [0.5, 0.55, 31, 150, 139],
            12: [0.55, 0.6, 32, 163, 134],
            13: [0.6, 0.65, 41, 175, 127],
            14: [0.65, 0.7, 61, 188, 116],
            15: [0.7, 0.75, 86, 198, 103],
            16: [0.75, 0.8, 117, 208, 84],
            17: [0.8, 0.85, 149, 216, 64],
            18: [0.85, 0.9, 186, 222, 40],
            19: [0.9, 0.95, 221, 227, 24],
            20: [0.95, 0.1, 253, 231, 37],
            21: [1.0, 1e100, 253, 231, 37],
        }

        self._normalized_array = (
            (gray_array - np.min(gray_array))
            / (np.max(gray_array) - np.min(gray_array))
            if np.max(gray_array) - np.min(gray_array)
            else gray_array - np.min(gray_array)
        )

        self._rgb_img = np.zeros((*gray_array.shape, 3), np.uint8, "C")
        for key in color_map.keys():
            start, end, *_rgb = color_map[key]
            boolean_array = np.logical_and(
                self._normalized_array >= start, self._normalized_array <= end
            )
            self._rgb_img[boolean_array] = _rgb

        return self._rgb_img

    def rgb_array_to_Qimage(self, array, width=100, height=100):
        """
        Convert the 3D numpy array `gray` into a 8-bit QImage with a RGB
        colormap. The first dimension represents the vertical image axis.
        """
        if np.ndim(array) == 3:
            height, width, d = array.shape

            nd = d
            if nd == 3:  # 3D RGB Image
                nd = 4
            if nd == 1:  # 3D Grayscaler Image
                nd = 3

            img = np.zeros([height, width, nd], np.uint8, "C")
            img[:, :, :3] = array[:, :, (2, 1, 0)]
            img[:, :, 3] = 255
        else:
            raise ValueError("can only convert 3D arrays")

        self._qimage = QImage(img.data, img.shape[0], img.shape[1], QImage.Format_RGB32)
        return self._qimage

    def hasPhoto(self):
        return not self.empty

    def fitInView(self, scale=True):
        if self.hasPhoto():
            rect = QRectF(self.photo.pixmap().rect())
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
            self.photo.setPixmap(pixmap)
        else:
            self.empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self.photo.setPixmap(QPixmap())
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


class GreatWallGui(QMainWindow):
    gui_error_signal = pyqtSignal()
    level_up_signal = pyqtSignal()
    level_down_signal = pyqtSignal()

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

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            if isinstance(obj, QWidget):
                return True
            else:
                return False
        else:
            return super().eventFilter(obj, event)

    def init_input_view(self):
        self.tacit_knowledge_label = QLabel(self)
        self.tacit_knowledge_label.setText("Tacit knowledge type")
        self.tacit_knowledge_combobox = QComboBox(self)
        self.tacit_knowledge_combobox.addItems(
            constants.AVAILABLE_TACIT_KNOWLEDGE_TYPES
        )
        self.tacit_knowledge_combobox.setCurrentText(
            constants.AVAILABLE_TACIT_KNOWLEDGE_TYPES[0]
        )
        self.tacit_knowledge_combobox.currentTextChanged.connect(
            self.on_change_tacit_knowledge_combobox
        )

        self.fractal_function_label = QLabel("Fractal function type", self)
        self.fractal_function_combobox = QComboBox(self)
        self.fractal_function_combobox.addItems(constants.FRACTAL_FUNCTIONS)
        self.fractal_function_combobox.setCurrentText(constants.FRACTAL_FUNCTIONS[0])

        self.theme_label = QLabel("Choose Theme", self)
        self.theme_combobox = QComboBox(self)
        self.theme_combobox.addItems(constants.FORMOSA_THEMES)
        self.theme_combobox.setCurrentText(constants.FORMOSA_THEMES[0])

        self.tlp_label = QLabel("Choose TLP parameter from 1 to 2016", self)
        self.tlp_spinbox = QSpinBox(self)
        self.config_spinbox(self.tlp_spinbox, 1, 24 * 7 * 4 * 3, 1, 1)

        self.depth_label = QLabel("Choose tree depth from 1 to 256", self)
        self.depth_spinbox = QSpinBox(self)
        self.config_spinbox(self.depth_spinbox, 1, 256, 1, 1)

        self.arity_label = QLabel("Choose tree arity from 2 to 256", self)
        self.arity_spinbox = QSpinBox(self)
        self.config_spinbox(self.arity_spinbox, 1, 256, 1, 2)

        self.password_label = QLabel("Enter Time-Lock Puzzle password:", self)
        self.password_text = QTextEdit(self)

        # Hardcode to fast tests
        # self.password_text.setText(
        #     "viboniboasmofiasbrchsprorirerugugucavehistmiinciwibowifltuor"
        # )

        # Lists of input widgets
        self.input_state_widgets_list = [
            self.tacit_knowledge_label,
            self.tacit_knowledge_combobox,
            self.fractal_function_label,
            self.fractal_function_combobox,
            self.theme_label,
            self.theme_combobox,
            self.tlp_label,
            self.tlp_spinbox,
            self.depth_label,
            self.depth_spinbox,
            self.arity_label,
            self.arity_spinbox,
            self.password_label,
            self.password_text,
        ]

        self.input_exit_navigation_button = QPushButton("Exit", self)
        self.input_next_navigation_button = QPushButton("Next", self)

        # Lists of input navigation widgets
        self.input_navigation_widgets_list = [
            self.input_exit_navigation_button,
            self.input_next_navigation_button,
        ]

        input_widgets_layout = QVBoxLayout()
        for widget in self.input_state_widgets_list:
            input_widgets_layout.addWidget(widget)
        input_widgets_layout.addStretch(1)
        input_group = QGroupBox()
        input_group.setLayout(input_widgets_layout)

        navigation_buttons_layout = QHBoxLayout()
        for widget in self.input_navigation_widgets_list:
            navigation_buttons_layout.addWidget(widget)

        input_layout = QVBoxLayout()
        input_layout.addWidget(input_group)
        input_layout.addLayout(navigation_buttons_layout)

        input_view = QWidget()
        input_view.setLayout(input_layout)

        return input_view

    def init_input_confirmation_view(self):
        self.input_confirmation_label = QLabel(self)
        self.input_confirmation_tacit_knowledge_type_label = QLabel(self)
        self.input_confirmation_theme_label = QLabel(self)
        self.input_confirmation_tlp_label = QLabel(self)
        self.input_confirmation_depth_label = QLabel(self)
        self.input_confirmation_arity_label = QLabel(self)
        self.input_confirmation_password_label = QLabel(self)

        # Lists of input confirmation widgets
        self.input_confirmation_widgets_list = [
            self.input_confirmation_label,
            self.input_confirmation_tacit_knowledge_type_label,
            self.input_confirmation_theme_label,
            self.input_confirmation_tlp_label,
            self.input_confirmation_depth_label,
            self.input_confirmation_arity_label,
            self.input_confirmation_password_label,
        ]

        self.input_confirmation_back_navigation_button = QPushButton(self)
        self.input_confirmation_next_navigation_button = QPushButton(self)

        # Lists of input confirmation navigation widgets
        self.input_confirmation_navigation_widgets_list = [
            self.input_confirmation_back_navigation_button,
            self.input_confirmation_next_navigation_button,
        ]

        confirmation_widgets_layout = QVBoxLayout()
        for widget in self.input_confirmation_widgets_list:
            confirmation_widgets_layout.addWidget(widget)
        confirmation_widgets_layout.addStretch(1)
        confirmation_group = QGroupBox()
        confirmation_group.setLayout(confirmation_widgets_layout)

        navigation_buttons_layout = QHBoxLayout()
        for widget in self.input_confirmation_navigation_widgets_list:
            navigation_buttons_layout.addWidget(widget)

        confirmation_layout = QVBoxLayout()
        confirmation_layout.addWidget(confirmation_group)
        confirmation_layout.addLayout(navigation_buttons_layout)

        confirmation_view = QWidget()
        confirmation_view.setLayout(confirmation_layout)

        return confirmation_view

    def init_waiting_derivation_view(self):
        self.waiting_derivation_label = QLabel(self)
        self.waiting_derivation_label.setText(
            "Please, wait until the derivation finish!\n"
            + "Be patient, this will take some time..."
        )
        # self.wait_derivation_bar = QProgressBar()

        # Lists of waiting derivation widgets
        self.waiting_derivation_widgets_list = [
            self.waiting_derivation_label,
            # self.wait_derivation_bar,
        ]

        self.waiting_reset_navigation_button = QPushButton("Reset", self)
        self.waiting_next_navigation_button = QPushButton("Next", self)
        self.waiting_next_navigation_button.setEnabled(False)

        # Lists of waiting derivation navigation widgets
        self.waiting_navigation_widgets_list = [
            self.waiting_reset_navigation_button,
            self.waiting_next_navigation_button,
        ]

        waiting_derivation_widgets_layout = QVBoxLayout()
        for widget in self.waiting_derivation_widgets_list:
            waiting_derivation_widgets_layout.addWidget(widget)
        waiting_derivation_widgets_layout.addStretch(1)
        waiting_derivation_group = QGroupBox()
        waiting_derivation_group.setLayout(waiting_derivation_widgets_layout)

        navigation_buttons_layout = QHBoxLayout()
        for widget in self.waiting_navigation_widgets_list:
            navigation_buttons_layout.addWidget(widget)

        waiting_derivation_layout = QVBoxLayout()
        waiting_derivation_layout.addWidget(waiting_derivation_group)
        waiting_derivation_layout.addLayout(navigation_buttons_layout)

        waiting_derivation_view = QWidget()
        waiting_derivation_view.setLayout(waiting_derivation_layout)

        return waiting_derivation_view

    def init_selecting_derivation_view(self):
        self.selecting_derivation_option_number_selected: int = 0
        self.selecting_derivation_current_level_label = QLabel(self)
        self.selecting_derivation_level_label = QLabel(self)
        self.selecting_derivation_level_spinbox = QSpinBox(self)

        # Lists of selecting derivation header widgets
        self.selecting_derivation_header_widgets_list = [
            self.selecting_derivation_current_level_label,
            self.selecting_derivation_level_label,
            self.selecting_derivation_level_spinbox,
        ]

        self.selecting_derivation_options_layout = QVBoxLayout()

        # Lists of selecting derivation options widgets
        self.selecting_derivation_options_widgets_list = []

        self.selecting_reset_navigation_button = QPushButton("Reset", self)
        self.selecting_next_navigation_button = QPushButton("Next", self)
        self.selecting_next_navigation_button.setEnabled(False)

        # Lists of selecting derivation navigation widgets
        self.selecting_navigation_widgets_list = [
            self.selecting_reset_navigation_button,
            self.selecting_next_navigation_button,
        ]

        selecting_derivation_header_widgets_layout = QVBoxLayout()
        for widget in self.selecting_derivation_header_widgets_list:
            selecting_derivation_header_widgets_layout.addWidget(widget)
        selecting_derivation_header_widgets_group = QGroupBox()
        selecting_derivation_header_widgets_group.setLayout(
            selecting_derivation_header_widgets_layout
        )

        selecting_derivation_widgets_group = QGroupBox()
        selecting_derivation_widgets_group.setLayout(
            self.selecting_derivation_options_layout
        )

        navigation_buttons_layout = QHBoxLayout()
        for widget in self.selecting_navigation_widgets_list:
            navigation_buttons_layout.addWidget(widget)
        selecting_derivation_layout = QVBoxLayout()
        selecting_derivation_layout.addWidget(selecting_derivation_header_widgets_group)
        selecting_derivation_layout.addWidget(selecting_derivation_widgets_group)
        selecting_derivation_layout.addLayout(navigation_buttons_layout)

        selecting_derivation_view = QWidget()
        selecting_derivation_view.setLayout(selecting_derivation_layout)

        return selecting_derivation_view

    def init_result_confirmation_view(self):
        self.result_confirmation_current_level_label = QLabel(self)

        # Lists of result confirmation header widgets
        self.result_confirmation_header_widgets_list = [
            self.result_confirmation_current_level_label,
        ]

        self.result_confirmation_confirm_question_label = QLabel(self)
        self.result_confirmation_result_hash_label = QLabel(self)
        self.result_confirmation_previous_step_button = QPushButton(self)

        # Lists of result confirmation header widgets
        self.result_confirmation_widgets_list = [
            self.result_confirmation_confirm_question_label,
            self.result_confirmation_result_hash_label,
            self.result_confirmation_previous_step_button,
        ]

        self.result_confirmation_reset_navigation_button = QPushButton("Reset", self)
        self.result_confirmation_next_navigation_button = QPushButton("Next", self)

        # Lists of result confirmation navigation widgets
        self.result_confirmation_navigation_widgets_list = [
            self.result_confirmation_reset_navigation_button,
            self.result_confirmation_next_navigation_button,
        ]

        result_confirmation_header_widgets_layout = QVBoxLayout()
        for widget in self.result_confirmation_header_widgets_list:
            result_confirmation_header_widgets_layout.addWidget(widget)
        result_confirmation_header_widgets_group = QGroupBox()
        result_confirmation_header_widgets_group.setLayout(
            result_confirmation_header_widgets_layout
        )

        result_confirmation_widgets_layout = QVBoxLayout()
        for widget in self.result_confirmation_widgets_list:
            if widget == self.result_confirmation_result_hash_label:
                result_confirmation_widgets_layout.addWidget(
                    widget, alignment=Qt.AlignCenter
                )
            else:
                result_confirmation_widgets_layout.addWidget(widget)
        result_confirmation_widgets_layout.addStretch(1)
        result_confirmation_widgets_group = QGroupBox()
        result_confirmation_widgets_group.setLayout(result_confirmation_widgets_layout)

        navigation_buttons_layout = QHBoxLayout()
        for widget in self.result_confirmation_navigation_widgets_list:
            navigation_buttons_layout.addWidget(widget)

        result_confirmation_layout = QVBoxLayout()
        result_confirmation_layout.addWidget(result_confirmation_header_widgets_group)
        result_confirmation_layout.addWidget(result_confirmation_widgets_group)
        result_confirmation_layout.addLayout(navigation_buttons_layout)

        result_confirmation_view = QWidget()
        result_confirmation_view.setLayout(result_confirmation_layout)

        return result_confirmation_view

    def init_result_view(self):
        self.result_finish_message_label = QLabel("This is the result output:", self)
        self.result_finish_output_text = QTextEdit(self)
        self.result_show_hide_output_button = QPushButton(self)
        self.result_copy_output_button = QPushButton("Copy output to clipboard", self)

        self.result_show_hide_output_button.clicked.connect(
            self.on_hide_show_button_click
        )
        self.result_copy_output_button.clicked.connect(self.on_copy_button_click)

        # Lists of result widgets
        self.result_widgets_list = [
            self.result_finish_message_label,
            self.result_finish_output_text,
            self.result_show_hide_output_button,
            self.result_copy_output_button,
        ]

        self.result_reset_navigation_button = QPushButton("Reset", self)

        # Lists of result navigation widgets
        self.result_navigation_widgets_list = [
            self.result_reset_navigation_button,
        ]

        result_widgets_layout = QVBoxLayout()
        for widget in self.result_widgets_list:
            result_widgets_layout.addWidget(widget)
        result_widgets_layout.addStretch(1)
        result_widgets_group = QGroupBox()
        result_widgets_group.setLayout(result_widgets_layout)

        navigation_buttons_layout = QHBoxLayout()
        for widget in self.result_navigation_widgets_list:
            navigation_buttons_layout.addWidget(widget)

        result_layout = QVBoxLayout()
        result_layout.addWidget(result_widgets_group)
        result_layout.addLayout(navigation_buttons_layout)

        result_view = QWidget()
        result_view.setLayout(result_layout)

        return result_view

    def init_error_view(self):
        self.error_message_label = QLabel("The following error has been raised:", self)
        self.error_message_text = QTextEdit(self)
        self.error_message_text.setReadOnly(True)

        # Lists of result widgets
        self.error_widgets_list = [
            self.error_message_label,
            self.error_message_text,
        ]

        self.error_reset_navigation_button = QPushButton("Reset", self)

        # Lists of result navigation widgets
        self.error_navigation_widgets_list = [
            self.error_reset_navigation_button,
        ]

        error_widgets_layout = QVBoxLayout()
        for widget in self.error_widgets_list:
            error_widgets_layout.addWidget(widget)
        error_widgets_layout.addStretch(1)
        error_widgets_group = QGroupBox()
        error_widgets_group.setLayout(error_widgets_layout)

        navigation_buttons_layout = QHBoxLayout()
        for widget in self.error_navigation_widgets_list:
            navigation_buttons_layout.addWidget(widget)

        error_layout = QVBoxLayout()
        error_layout.addWidget(error_widgets_group)
        error_layout.addLayout(navigation_buttons_layout)

        error_view = QWidget()
        error_view.setLayout(error_layout)

        return error_view

    def on_change_tacit_knowledge_combobox(self):
        self.fractal_function_combobox.setEnabled(
            self.tacit_knowledge_combobox.currentText() == constants.FRACTAL
        )

    def config_spinbox(
        self,
        spinbox: QSpinBox,
        min_value: int,
        max_value: int,
        step_value: int = 1,
        default_value: int = 0,
        set_wrapping: bool = True,
    ):
        """An easy configuration to any spinbox with one line call."""
        spinbox.setRange(min_value, max_value)
        spinbox.setSingleStep(step_value)
        spinbox.setValue(default_value)
        spinbox.setWrapping(set_wrapping)

    def init_main_app_state(self):
        exit_app_state = QState()
        exit_app_state.setObjectName("Exit Application")

        input_state = QState()
        input_state.setObjectName("User Inputs")

        input_confirmation_state = QState()
        input_confirmation_state.setObjectName("User Inputs Confirmation")

        derivation_state = QState()
        derivation_state.setObjectName("Derivation")

        result_confirmation_state = QState()
        result_confirmation_state.setObjectName("Result Confirmation")

        result_state = QState()
        result_state.setObjectName("Result")

        error_state = QState()
        error_state.setObjectName("GUI Error")

        # List of states
        self.error_states_list = [
            error_state,
        ]
        self.main_states_list = [
            exit_app_state,
            input_state,
            input_confirmation_state,
            derivation_state,
            result_confirmation_state,
            result_state,
            error_state,
        ]

        # Define transitions
        input_state.addTransition(
            self.input_next_navigation_button.clicked, input_confirmation_state
        )
        input_state.addTransition(
            self.input_exit_navigation_button.clicked, exit_app_state
        )
        input_confirmation_state.addTransition(
            self.input_confirmation_next_navigation_button.clicked, derivation_state
        )
        input_confirmation_state.addTransition(
            self.input_confirmation_back_navigation_button.clicked, input_state
        )
        # NOTE: The derivation state includes waiting,
        # selecting and confirming result views.
        derivation_state.addTransition(
            self.waiting_next_navigation_button.clicked, result_state
        )
        derivation_state.addTransition(
            self.waiting_reset_navigation_button.clicked, input_state
        )
        derivation_state.addTransition(
            self.selecting_reset_navigation_button.clicked, input_state
        )
        derivation_state.addTransition(
            self.result_confirmation_next_navigation_button.clicked, result_state
        )
        derivation_state.addTransition(
            self.result_confirmation_reset_navigation_button.clicked, input_state
        )
        result_state.addTransition(
            self.result_reset_navigation_button.clicked, input_state
        )
        error_state.addTransition(
            self.error_reset_navigation_button.clicked, input_state
        )

        # Error transitions, add to all states except the error states
        for state in set(self.main_states_list) - set(self.error_states_list):
            state.addTransition(self.gui_error_signal, error_state)

        # Add states to the state machine
        for state in self.main_states_list:
            self.main_gui_state.addState(state)

        # Set initial state
        self.main_gui_state.setInitialState(input_state)

        # Start the state machine
        self.main_gui_state.start()

        # Connect states to methods
        exit_app_state.entered.connect(self.on_exit_app)
        input_state.entered.connect(self.input_state1_entered)
        input_confirmation_state.entered.connect(self.confirmation_state2_entered)
        derivation_state.entered.connect(self.derivation_state3_entered)
        result_state.entered.connect(self.result_state4_entered)
        error_state.entered.connect(self.error_state0_entered)

    def config_input_confirmation_widgets(self):
        self.input_confirmation_label.setText("Confirm your values")
        self.input_confirmation_tacit_knowledge_type_label.setText(
            "Tacit knowledge type\n" + self.tacit_knowledge_combobox.currentText()
        )
        self.input_confirmation_theme_label.setText(
            "Theme\n" + str(self.theme_combobox.currentText())
        )
        self.input_confirmation_tlp_label.setText(
            "TLP parameter\n" + str(self.tlp_spinbox.value())
        )
        self.input_confirmation_depth_label.setText(
            "Tree depth\n" + str(self.depth_spinbox.value())
        )
        self.input_confirmation_arity_label.setText(
            "Tree arity\n" + str(self.arity_spinbox.value())
        )
        self.input_confirmation_password_label.setText(
            "Time-Lock Puzzle password\n" + self.password_text.toPlainText()
        )
        self.input_confirmation_back_navigation_button.setText("Back")
        self.input_confirmation_next_navigation_button.setText("Next")

    def config_selecting_derivation_widgets_layout(self):
        # Remove previously added selection options to selecting derivation layout
        for idx in reversed(range(self.selecting_derivation_options_layout.count())):
            widget = self.selecting_derivation_options_layout.takeAt(idx).widget()
            if widget is not None:
                widget.deleteLater()
        self.selecting_derivation_options_widgets_list.clear()

        if self.tacit_knowledge_combobox.currentText() == constants.FRACTAL:
            selection_button = QPushButton("Previous Step", self)
            self.selecting_derivation_options_layout.addWidget(selection_button)
            self.selecting_derivation_options_widgets_list.append(selection_button)

            scroll_area = QScrollArea()
            flow_widget = QWidget()
            flow_layout = FlowLayout()
            for idx in range(self.greatwall.tree_arity):
                view = ImageViewer(self)
                selection_button = QPushButton(str(idx), self)

                selection_box = QVBoxLayout()
                selection_box.addWidget(view)
                selection_box.addWidget(selection_button)

                selection_box_widget = QWidget()
                selection_box_widget.setLayout(selection_box)

                flow_layout.addWidget(selection_box_widget)

                self.selecting_derivation_options_widgets_list.append(
                    (view, selection_button)
                )

            # WARNING: We added the flow layout to QWidget to be able to remove it later
            flow_widget.setLayout(flow_layout)

            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            scroll_area.viewport().installEventFilter(self)
            scroll_area.setWidget(flow_widget)

            self.selecting_derivation_options_layout.addWidget(scroll_area)
        elif self.tacit_knowledge_combobox.currentText() == constants.SHAPE:
            selection_button = QPushButton("Previous Step", self)
            self.selecting_derivation_options_layout.addWidget(selection_button)
            self.selecting_derivation_options_widgets_list.append(selection_button)

            flow_widget = QWidget()
            flow_layout = FlowLayout()
            for idx in range(self.greatwall.tree_arity):
                selection_button = QPushButton(self)

                flow_layout.addWidget(selection_button)

                self.selecting_derivation_options_widgets_list.append(selection_button)

            # WARNING: We added the flow layout to QWidget to be able to remove it later
            flow_widget.setLayout(flow_layout)
            self.selecting_derivation_options_layout.addLayout(flow_widget)

            self.selecting_derivation_options_layout.addStretch(1)
        else:
            for _ in range(self.greatwall.tree_arity + 1):
                selection_button = QPushButton(self)
                self.selecting_derivation_options_layout.addWidget(selection_button)
                self.selecting_derivation_options_widgets_list.append(selection_button)

            self.selecting_derivation_options_layout.addStretch(1)

    def config_selecting_derivation_widgets(self):
        self.selecting_derivation_current_level_label.setText(
            f"Level {self.greatwall.current_level} of {self.greatwall.tree_depth}"
        )
        self.selecting_derivation_level_label.setText("Select Option:")
        self.config_spinbox(
            self.selecting_derivation_level_spinbox, 0, self.greatwall.tree_arity, 1, 0
        )

        if self.tacit_knowledge_combobox.currentText() == constants.FRACTAL:
            user_options = self.greatwall.get_fractal_query()
            for idx, widgets in enumerate(
                self.selecting_derivation_options_widgets_list
            ):
                if idx == 0:
                    selection_button = widgets
                else:
                    view, selection_button = widgets

                    image = QPixmap.fromImage(
                        view.rgb_array_to_Qimage(
                            view.gray_array_to_rgb_array(user_options[idx])
                        )
                    )
                    view.setFixedSize(QSize(200, 200))
                    view.setPhoto(image)

                    selection_button.setText(str(idx))
                    selection_button.setFixedSize(QSize(200, 25))

                selection_button.clicked.connect(
                    lambda state, x=idx: self.on_selection_button_click(x)
                )
        elif self.tacit_knowledge_combobox.currentText() == constants.SHAPE:
            user_options = self.greatwall.get_shape_query()
            for idx, selection_widget in enumerate(
                self.selecting_derivation_options_widgets_list
            ):
                if idx == 0:
                    pass
                else:
                    selection_widget.setText(user_options[idx])

                selection_widget.clicked.connect(
                    lambda state, x=idx: self.on_selection_button_click(x)
                )
        else:
            user_options = self.greatwall.get_li_str_query().split("\n")
            for idx, selection_widget in enumerate(
                self.selecting_derivation_options_widgets_list
            ):
                if idx == 0:
                    selection_widget.setText("Previous Step")
                else:
                    selection_widget.setText(user_options[idx])

                selection_widget.clicked.connect(
                    lambda state, x=idx: self.on_selection_button_click(x)
                )

    def config_result_confirmation_widgets(self):
        self.result_confirmation_current_level_label.setText(
            f"Level {self.greatwall.current_level} of {self.greatwall.tree_depth}"
        )
        self.result_confirmation_confirm_question_label.setText(
            "Do you confirm this result?"
        )
        self.result_confirmation_previous_step_button.setText("Previous Step")
        self.result_confirmation_previous_step_button.clicked.connect(
            lambda state: self.on_selection_button_click(0)
        )

    def config_result_widgets(self):
        self.result_show_hide_output_button.setText("Show output")

        self.result_finish_output_text.hide()
        self.result_finish_output_text.setText(self.greatwall_finish_result.hex())
        self.result_finish_output_text.setReadOnly(True)

    def error_state0_entered(self):
        print("Error State Entered")

        exception_message = f"Exception:\n{str(self.error_occurred)}"
        self.error_message_text.setText(exception_message)

        self.stacked.setCurrentWidget(self.error_view)

    def input_state1_entered(self):
        print("SM1 State 1 Entered")
        self.stacked.setCurrentWidget(self.input_view)
        # self.result_confirmation_result_hash_label.clear()
        # self.result_confirmation_result_hash_label.setText("")
        self.reinit_running_greatwall()

    def confirmation_state2_entered(self):
        print("SM1 State 2 Entered")

        # Config input confirmation widgets
        self.config_input_confirmation_widgets()

        self.stacked.setCurrentWidget(self.input_confirmation_view)

    def derivation_state3_entered(self):
        print("SM1 State 3 Entered")

        try:
            themed_success = self.greatwall.set_themed_mnemo(
                self.theme_combobox.currentText()
            )
            self.greatwall.set_fractal_function_type(
                self.fractal_function_combobox.currentText()
            )
            self.greatwall.set_tlp(self.tlp_spinbox.value())
            self.greatwall.set_depth(self.depth_spinbox.value())
            self.greatwall.set_arity(self.arity_spinbox.value())
            password_success = self.greatwall.set_sa0(self.password_text.toPlainText())

            if not themed_success or not password_success:
                self.error_occurred = ValueError(
                    "Config error. Password and Theme don't match"
                )
                self.gui_error_signal.emit()
                return

            # Config selecting derivation widgets layout
            self.config_selecting_derivation_widgets_layout()

            # Start the execution in a separate thread
            self.greatwall_thread = GreatWallThread(self.greatwall)
            self.greatwall_thread.finished.connect(self.on_thread_finish)
            self.greatwall_thread.canceled.connect(self.on_thread_cancel)
            self.greatwall_thread.error_occurred.connect(self.on_thread_error)
            self.init_selection_derivation_loop()

            self.stacked.setCurrentWidget(self.waiting_derivation_view)
        except Exception as e:
            self.error_occurred = e
            self.gui_error_signal.emit()

    def result_state4_entered(self):
        print("SM1 State 4 Entered")

        # Config result widgets
        self.config_result_widgets()

        self.stacked.setCurrentWidget(self.result_view)

    def init_selection_derivation_loop(self):
        if self.main_derivation_state.isRunning():
            self.main_derivation_state.stop()

        num_states = self.depth_spinbox.value() + 1

        # Remove existing states
        for each_transition in self.transitions_list:
            # Remove the transitions from states
            source_state = each_transition.sourceState()
            if source_state:
                source_state.removeTransition(each_transition)

        # Clear the transitions list after removal
        self.transitions_list.clear()

        # Create and add new states
        self.selecting_derivation_states_list.clear()
        for _ in range(num_states):
            state = QState()
            state.entered.connect(self.selection_derive_state_n_entered)
            self.main_derivation_state.addState(state)
            self.selecting_derivation_states_list.append(state)

        # Add transitions between states
        for idx, state in enumerate(self.selecting_derivation_states_list):
            # The first state doesn't transit with level_down_signal
            if idx > 0:
                previous_state = self.selecting_derivation_states_list[idx - 1]
                transition = QSignalTransition(self.level_down_signal)
                transition.setTargetState(previous_state)
                state.addTransition(transition)
                self.transitions_list.append(transition)

            # The last state doesn't transit with level_up_signal
            if idx < len(self.selecting_derivation_states_list) - 1:
                next_state = self.selecting_derivation_states_list[idx + 1]
                transition = QSignalTransition(self.level_up_signal)
                transition.setTargetState(next_state)
                state.addTransition(transition)
                self.transitions_list.append(transition)

        # Start the state machine
        self.main_derivation_state.setInitialState(
            self.selecting_derivation_states_list[0]
        )
        self.main_derivation_state.start()

    def selection_derive_state_n_entered(self):
        try:
            print(
                f"SM2 State Entered at level {self.greatwall.current_level} of {self.greatwall.tree_depth}"
            )
            self.run_greatwall_thread(self.selecting_derivation_option_number_selected)
        except Exception as e:
            self.error_occurred = e
            self.gui_error_signal.emit()

    def run_greatwall_thread(self, user_choice):
        if user_choice >= 0:
            self.greatwall_thread.user_choice = user_choice
            self.greatwall_thread.start()

    def reinit_running_greatwall(self):
        if hasattr(self, "greatwall_thread") and self.greatwall_thread.isRunning():
            self.greatwall.cancel_execution()
            self.greatwall_thread.cancel()
        if self.main_derivation_state.isRunning():
            self.main_derivation_state.stop()

        self.greatwall.current_level = 0

    def on_selection_button_click(self, selected_option: int):
        self.selecting_derivation_option_number_selected = selected_option
        if selected_option:
            self.level_up_signal.emit()
        else:
            self.level_down_signal.emit()

    def on_hide_show_button_click(self):
        self.result_finish_output_text.setVisible(
            not self.result_finish_output_text.isVisible()
        )

        button_text = (
            "Hide output"
            if self.result_finish_output_text.isVisible()
            else "Show output"
        )
        self.result_show_hide_output_button.setText(button_text)

    def on_copy_button_click(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.greatwall_finish_result.hex())

    def on_thread_finish(self):
        if self.greatwall.current_level >= self.greatwall.tree_depth:
            self.greatwall_finish_result = self.greatwall.finish_output()
            if self.tacit_knowledge_combobox.currentText() == constants.FRACTAL:
                formated_fractal = self.greatwall.fractal.update(
                    func_type=self.greatwall.fractal.func_type,
                    p_param=self.greatwall.fractal.get_valid_parameter_from_value(
                        self.greatwall_finish_result
                    ),
                )

                image = ImageViewer(self)

                rgb_array = image.gray_array_to_rgb_array(formated_fractal)
                qimage = image.rgb_array_to_Qimage(rgb_array)
                image = QPixmap.fromImage(qimage)

                self.result_confirmation_result_hash_label.setPixmap(
                    image.scaled(QSize(256, 256))
                )
            if self.tacit_knowledge_combobox.currentText() == constants.FORMOSA:
                formatted_mnemonic = self.greatwall.mnemo.format_mnemonic(
                    self.greatwall.mnemo.to_mnemonic(self.greatwall_finish_result)
                )
                formatted_mnemonic = "\n".join(
                    formatted_mnemonic.split("\n")[1 : self.greatwall.tree_arity + 1]
                )
                local_finish_output = formatted_mnemonic
                self.result_confirmation_result_hash_label.setText(local_finish_output)
            if self.tacit_knowledge_combobox.currentText() == constants.SHAPE:
                image_path = self.greatwall.shaper.draw_regular_shape(
                    self.greatwall_finish_result
                )
                image = QPixmap(str(image_path))
                self.result_confirmation_result_hash_label.setPixmap(image)
                self.result_confirmation_result_hash_label.resize(image.size())

            # Config result confirmation widgets
            self.config_result_confirmation_widgets()

            self.stacked.setCurrentWidget(self.result_confirmation_view)
        else:
            # Config selecting derivation widgets
            self.config_selecting_derivation_widgets()

            self.stacked.setCurrentWidget(self.selecting_derivation_view)

    def on_thread_cancel(self):
        print("Task canceled")

    def on_thread_error(self, error_msg):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("GreatWall Error Occurred")
        error_dialog.setInformativeText(error_msg)
        error_dialog.setWindowTitle("Thread Error")
        error_dialog.exec_()

    def on_exit_app(self):
        """Close the parent which exit the application. Bye, come again!"""
        print("Closed")
        self.close()


def main():
    app = QApplication([])
    window = GreatWallGui()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
