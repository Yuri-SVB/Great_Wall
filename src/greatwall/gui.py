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


class GreatWallWorker(QThread):
    """Custom Worker class to perform the time-consuming task."""

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
        self._zoom = 0
        self._empty = True
        self._photo = QGraphicsPixmapItem()
        self._scene = QGraphicsScene(self)
        self._scene.addItem(self._photo)

        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

    @classmethod
    def gray_array_to_Qimage(cls, gray_array, width=100, height=100):
        """
        Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
        colormap. The first dimension represents the vertical image axis.
        """
        if len(gray_array.shape) != 2:
            raise ValueError("gray2QImage can only convert 2D arrays")

        width, height = gray_array.shape

        cls._qimage = QImage(gray_array.data, width, height, QImage.Format_Indexed8)
        for i in range(max(width, height)):
            gray_array.setColor(i, QColor(i, i, i).rgb())
        return cls._qimage

    @classmethod
    def gray_array_to_rgb_array(cls, gray_array):
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

        cls._normalized_array = (
            (gray_array - np.min(gray_array))
            / (np.max(gray_array) - np.min(gray_array))
            if np.max(gray_array) - np.min(gray_array)
            else gray_array - np.min(gray_array)
        )

        cls._rgb_img = np.zeros((*gray_array.shape, 3), np.uint8, "C")
        for key in color_map.keys():
            start, end, *_rgb = color_map[key]
            boolean_array = np.logical_and(
                cls._normalized_array >= start, cls._normalized_array <= end
            )
            cls._rgb_img[boolean_array] = _rgb

        return cls._rgb_img

    @classmethod
    def rgb_array_to_Qimage(cls, array, width=100, height=100):
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

        cls._qimage = QImage(img.data, img.shape[0], img.shape[1], QImage.Format_RGB32)
        return cls._qimage

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        if self.hasPhoto():
            rect = QRectF(self._photo.pixmap().rect())
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
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
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
    sm2_is_running = pyqtSignal()
    level_up_signal = pyqtSignal()
    level_down_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.finish_output: bytes = bytes(0000)
        self.error_occurred = Exception
        self.button_number: int = 0
        self.transitions: list[QSignalTransition] = []

        self.greatwall = GreatWall()
        self.selected_tacit_knowledge = ""

        # General Widgets
        self.back_button = QPushButton(self)
        self.next_button = QPushButton(self)

        # Input Widgets
        self.tacit_knowledge_label = QLabel(self)
        self.tacit_knowledge_combobox = QComboBox(self)

        self.fractal_function_label = QLabel(self)
        self.fractal_function_combobox = QComboBox(self)

        self.theme_label = QLabel(self)
        self.theme_combobox = QComboBox(self)

        self.tlp_label = QLabel(self)
        self.tlp_spinbox = QSpinBox(self)

        self.depth_label = QLabel(self)
        self.depth_spinbox = QSpinBox(self)

        self.arity_label = QLabel(self)
        self.arity_spinbox = QSpinBox(self)

        self.password_label = QLabel(self)
        self.password_text = QTextEdit(self)

        # Confirmation Widgets
        self.confirm_label = QLabel(self)
        self.tacit_knowledge_type_confirm = QLabel(self)
        self.theme_confirm = QLabel(self)
        self.tlp_confirm = QLabel(self)
        self.depth_confirm = QLabel(self)
        self.arity_confirm = QLabel(self)
        self.password_confirm = QLabel(self)

        # Waiting Derivation Widgets
        self.wait_derive_label = QLabel(self)

        # Dependent Derivation Widgets
        self.select_label = QLabel(self)
        self.derivation_spinbox = QSpinBox(self)
        self.level_label = QLabel(self)
        # WARNING: Attention to add widgets to this layout, they will be
        # deleted later and can cause an exception.
        self.derivation_layout = QVBoxLayout()
        self.selection_buttons: list[
            Union[QPushButton, tuple[QPushButton, QGraphicsView]]
        ] = []

        # Result Widgets
        self.confirm_result_label = QLabel(self)
        self.result_hash = QLabel(self)

        # Finish Widgets
        self.finish_output_label = QLabel(self)
        self.finish_text = QTextEdit(self)
        self.hide_show_button = QPushButton(self)
        self.copy_clipboard_button = QPushButton(self)

        # Error widgets
        self.config_error_label = QLabel(self)
        self.execution_error_label = QLabel(self)
        self.unknown_error_label = QLabel(self)
        self.exception_label = QLabel(self)

        # List of general Widgets
        self.general_widgets = [self.next_button, self.back_button]

        # Lists of widgets per step
        self.input_state_widgets = [
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
        self.confirmation_widgets = [
            self.confirm_label,
            self.tacit_knowledge_type_confirm,
            self.theme_confirm,
            self.tlp_confirm,
            self.depth_confirm,
            self.arity_confirm,
            self.password_confirm,
        ]
        self.wait_derivation_widgets = [self.wait_derive_label]
        self.dependent_derivation_widgets: list[QWidget] = [
            self.level_label,
            self.select_label,
            self.derivation_spinbox,
        ]
        self.confirm_result_widgets: list[QWidget] = [
            self.level_label,
            self.confirm_result_label,
            self.result_hash,
        ]
        # Track the length of confirm_result_widgets,
        # widgets will be added to confirm_result_widgets and should be removed after deletion
        self.widget_to_remove = len(self.confirm_result_widgets)
        self.finish_widgets = [
            self.finish_output_label,
            self.finish_text,
            self.hide_show_button,
            self.copy_clipboard_button,
        ]
        self.error_widgets = [
            self.config_error_label,
            self.execution_error_label,
            self.unknown_error_label,
            self.exception_label,
        ]

        # List of widgets lists
        self.state_widgets: list[list[QWidget]] = []

        # Launch UI
        self.main_states: list[QState] = []
        self.error_states: list[QState] = []
        self.main_gui_sm = QStateMachine()
        self.loop_dynamic_sm = QStateMachine()
        self.dynamic_states: list[QState] = []
        self.init_ui()
        self.init_main_app_state()

    def init_ui(self):
        self.setWindowTitle("Great Wall Sample")
        self.setGeometry(100, 100, 500, 500)  # left, top, width, height

        # Hardcode to fast tests
        self.password_text.setText(
            "viboniboasmofiasbrchsprorirerugugucavehistmiinciwibowifltuor"
        )

        self.configure_ui_widgets()
        self.configure_layout()

    def configure_ui_widgets(self):
        # Strings variables to easily translate in the future versions
        next_text = "Next"
        back_text = "Back"

        choose_tacit_knowledge_type = "Tacit knowledge type"
        choose_fractal_function_type = "Fractal function type"
        choose_theme = "Choose Theme"
        choose_tlp = "Choose TLP parameter from 1 to 2016"
        choose_depth = "Choose tree depth from 1 to 256"
        choose_arity = "Choose tree arity from 2 to 256"
        password = "Enter Time-Lock Puzzle password:"
        result_confirm = "Do you confirm this result?"
        finish_output_message = "This is the result output:"
        wait_derive = "Wait the derivation to finish\nThis will take some time"
        config_error_message = "Some configuration might went wrong\n\tDouble check the theme chosen and your password"
        execution_error_message = "The GreatWall execution might went wrong\n\tPlease double check your dependencies version and try again"
        unknown_error_message = "Or some unexpected error occurred"
        hide_show = "Show output"
        copy_clipboard = "Copy output to clipboard"
        selection_text = "Select option"

        # General Widgets
        self.back_button.setText(next_text)
        self.next_button.setText(back_text)

        # Input Widgets
        self.tacit_knowledge_label.setText(choose_tacit_knowledge_type)
        self.fractal_function_label.setText(choose_fractal_function_type)
        self.theme_label.setText(choose_theme)
        self.tlp_label.setText(choose_tlp)
        self.depth_label.setText(choose_depth)
        self.arity_label.setText(choose_arity)
        self.password_label.setText(password)

        # Set default input values
        self.tacit_knowledge_combobox.addItems(
            constants.AVAILABLE_TACIT_KNOWLEDGE_TYPES
        )
        self.tacit_knowledge_combobox.setCurrentText(
            constants.AVAILABLE_TACIT_KNOWLEDGE_TYPES[0]
        )
        self.tacit_knowledge_combobox.currentTextChanged.connect(
            self.on_change_tacit_knowledge_combobox
        )
        self.fractal_function_combobox.addItems(constants.FRACTAL_FUNCTIONS)
        self.fractal_function_combobox.setCurrentText(constants.FRACTAL_FUNCTIONS[0])
        self.theme_combobox.addItems(constants.FORMOSA_THEMES)
        self.theme_combobox.setCurrentText(constants.FORMOSA_THEMES[0])
        self.on_change_tacit_knowledge_combobox()

        # Wait Derive Widget
        self.wait_derive_label.setText(wait_derive)

        # Confirmation Widgets
        self.select_label.setText(selection_text)
        self.configure_confirmation_widgets()

        # Result Widget
        self.confirm_result_label.setText(result_confirm)

        # Finish Widget
        self.finish_output_label.setText(finish_output_message)
        self.hide_show_button.setText(hide_show)
        self.hide_show_button.clicked.connect(self.on_hide_show_button_click)
        self.copy_clipboard_button.setText(copy_clipboard)
        self.copy_clipboard_button.clicked.connect(self.copy_to_clipboard)

        # Error widget
        self.config_error_label.setText(config_error_message)
        self.execution_error_label.setText(execution_error_message)
        self.unknown_error_label.setText(unknown_error_message)

        self.config_spinbox(self.tlp_spinbox, 1, 24 * 7 * 4 * 3, 1, 1)
        self.config_spinbox(self.depth_spinbox, 1, 256, 1, 1)
        self.config_spinbox(self.arity_spinbox, 1, 256, 1, 2)

    def on_change_tacit_knowledge_combobox(self):
        self.selected_tacit_knowledge = self.tacit_knowledge_combobox.currentText()
        self.fractal_function_combobox.setEnabled(
            self.tacit_knowledge_combobox.currentText() == constants.FRACTAL
        )

    def configure_confirmation_widgets(self):
        confirm_values = "Confirm your values"
        tacit_knowledge_type_chosen = "Tacit knowledge type\n"
        theme_chosen = "Theme\n"
        tlp_chosen = "TLP parameter\n"
        depth_chosen = "Tree depth\n"
        arity_chosen = "Tree arity\n"
        password_chosen = "Time-Lock Puzzle password\n"

        self.confirm_label.setText(confirm_values)
        self.tacit_knowledge_type_confirm.setText(
            tacit_knowledge_type_chosen + self.tacit_knowledge_combobox.currentText()
        )
        self.theme_confirm.setText(
            theme_chosen + str(self.theme_combobox.currentText())
        )
        self.tlp_confirm.setText(tlp_chosen + str(self.tlp_spinbox.value()))
        self.depth_confirm.setText(depth_chosen + str(self.depth_spinbox.value()))
        self.arity_confirm.setText(arity_chosen + str(self.arity_spinbox.value()))
        self.password_confirm.setText(
            password_chosen + self.password_text.toPlainText()
        )

    @staticmethod
    def config_spinbox(
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

    def configure_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Adding widgets to the main layout
        [main_layout.addWidget(widget) for widget in self.input_state_widgets]
        [main_layout.addWidget(widget) for widget in self.confirmation_widgets]
        [main_layout.addWidget(widget) for widget in self.wait_derivation_widgets]
        main_layout.addLayout(self.derivation_layout)
        [main_layout.addWidget(widget) for widget in self.confirm_result_widgets]
        [main_layout.addWidget(widget) for widget in self.finish_widgets]
        [main_layout.addWidget(widget) for widget in self.error_widgets]
        main_layout.addStretch(1)  # Add stretchable space to the end

        # Horizontal layout for buttons
        general_buttons_layout = QHBoxLayout()
        general_buttons_layout.addWidget(self.back_button)
        general_buttons_layout.addWidget(self.next_button)

        # Add the buttons layout to the main layout
        main_layout.addLayout(general_buttons_layout)

    def init_main_app_state(self):
        closing_app_state = QState()
        closing_app_state.setObjectName("Quit Application")

        input_state = QState()
        input_state.setObjectName("User Inputs")

        confirm_state = QState()
        confirm_state.setObjectName("User Confirm")

        dependent_derivation_state = QState()
        dependent_derivation_state.setObjectName("Dependent Derivation")

        output_state = QState()
        output_state.setObjectName("Output")

        gui_error_state = QState()
        gui_error_state.setObjectName("GUI Error")

        # List of states
        self.error_states = [
            gui_error_state,
        ]
        self.main_states = [
            closing_app_state,
            input_state,
            confirm_state,
            dependent_derivation_state,
            output_state,
        ] + self.error_states

        # Define transitions
        input_state.addTransition(self.next_button.clicked, confirm_state)
        input_state.addTransition(self.back_button.clicked, closing_app_state)
        confirm_state.addTransition(
            self.next_button.clicked, dependent_derivation_state
        )
        confirm_state.addTransition(self.back_button.clicked, input_state)
        dependent_derivation_state.addTransition(self.next_button.clicked, output_state)
        dependent_derivation_state.addTransition(self.back_button.clicked, input_state)
        output_state.addTransition(self.next_button.clicked, closing_app_state)
        output_state.addTransition(self.back_button.clicked, input_state)
        gui_error_state.addTransition(self.back_button.clicked, input_state)
        # Error transitions, add to all states except the error states
        [
            each_state.addTransition(self.gui_error_signal, gui_error_state)
            for each_state in set(self.main_states) - set(self.error_states)
        ]

        # Add states to the state machine
        [self.main_gui_sm.addState(each_state) for each_state in self.main_states]

        # Set initial state
        self.main_gui_sm.setInitialState(input_state)

        # Start the state machine
        self.main_gui_sm.start()

        # Connect states to methods
        closing_app_state.entered.connect(self.on_close_app)
        input_state.entered.connect(self.input_state1_entered)
        confirm_state.entered.connect(self.confirm_state2_entered)
        dependent_derivation_state.entered.connect(self.derivation_state3_entered)
        output_state.entered.connect(self.output_state4_entered)
        gui_error_state.entered.connect(self.handle_gui_errors)

    def configure_selection_buttons(self):
        self.level_label.setText(
            f"Level {self.greatwall.current_level} of {self.greatwall.tree_depth}"
        )
        if self.tacit_knowledge_combobox.currentText() == constants.FRACTAL:
            # Set buttons to Fractal options
            user_options = self.greatwall.get_fractal_query()
            if len(user_options) == len(self.selection_buttons):
                for idx, widgets in enumerate(self.selection_buttons[1:]):
                    button, view = widgets
                    button.setText(str(idx))
                    button.setFixedSize(QSize(200, 25))
                    image = QPixmap.fromImage(
                        view.rgb_array_to_Qimage(
                            view.gray_array_to_rgb_array(user_options[idx + 1])
                        )
                    )
                    view.setFixedSize(QSize(200, 200))
                    view.setPhoto(image)

        elif self.tacit_knowledge_combobox.currentText() == constants.FORMOSA:
            # Set buttons to Formosa options
            user_options = self.greatwall.get_li_str_query().split("\n")
            if len(user_options) == len(self.selection_buttons) + 1:
                for idx, widgets in enumerate(self.selection_buttons[1:]):
                    button, _ = widgets
                    button.setText(user_options[idx + 1])

        elif self.tacit_knowledge_combobox.currentText() == constants.SHAPE:
            # Set buttons to Shape options
            user_options = self.greatwall.get_shape_query()
            if len(user_options) == len(self.selection_buttons):
                offset = QSize(10, 10)
                for idx, widgets in enumerate(self.selection_buttons[1:]):
                    button, _ = widgets
                    image = QPixmap(str(user_options[idx + 1]))
                    icon = QIcon(image)
                    button.setIcon(icon)
                    button.setFixedSize(image.size() + offset)
                    button.setIconSize(image.size())

    def copy_to_clipboard(self):
        if not self.greatwall.is_finished:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(self.finish_output.hex())

    def configure_waiting_derivation_widgets(self):
        """Configure any message or effect to be shown while derive"""
        pass

    def configure_choose_derivation_widgets(self):
        cancel_text = "Previous Step"

        # Clear widgets from list and layout
        self.dependent_derivation_widgets.clear()
        self.selection_buttons.clear()
        if len(self.confirm_result_widgets) > self.widget_to_remove:
            self.confirm_result_widgets = self.confirm_result_widgets[
                : self.widget_to_remove
            ]

        # Destroy widgets in the layout by setting the parents as None
        for i in reversed(range(self.derivation_layout.count())):
            if (
                self.derivation_layout.itemAt(i) is None
                or self.derivation_layout.itemAt(i).widget() is None
                or self.derivation_layout.itemAt(i).widget() == self.level_label
            ):
                continue
            else:
                self.derivation_layout.itemAt(i).widget().deleteLater()
                self.derivation_layout.itemAt(i).widget().setParent(None)

        self.config_spinbox(self.derivation_spinbox, 0, self.greatwall.tree_arity, 1, 0)
        self.derivation_layout.addWidget(self.level_label)
        level_layout = QHBoxLayout()
        level_layout.addWidget(self.select_label)
        level_layout.addWidget(self.derivation_spinbox)
        level_layout.addStretch(1)
        self.derivation_layout.addLayout(level_layout)
        self.dependent_derivation_widgets.append(self.level_label)
        self.dependent_derivation_widgets.append(self.select_label)
        self.dependent_derivation_widgets.append(self.derivation_spinbox)
        for i in range(self.greatwall.tree_arity + 1):
            button = QPushButton("" if i > 0 else cancel_text, self)
            button.clicked.connect(lambda state, x=i: self.on_button_click(x))
            view = ImageViewer(self)

            if button not in self.confirm_result_widgets and i == 0:
                # Button 0 'previous step' must be visible in the last step
                self.confirm_result_widgets.append(button)

            if i == 0:
                self.derivation_layout.addWidget(button)
                self.dependent_derivation_widgets.append(button)
                self.selection_buttons.append((button, view))
            elif self.tacit_knowledge_combobox.currentText() == constants.FRACTAL:
                self.derivation_layout.addWidget(view)
                self.derivation_layout.addWidget(button)
                self.dependent_derivation_widgets.append(button)
                self.dependent_derivation_widgets.append(view)
                self.selection_buttons.append((button, view))
            else:
                self.derivation_layout.addWidget(button)
                self.dependent_derivation_widgets.append(button)
                self.selection_buttons.append((button, view))

    def on_button_click(self, button_number: int):
        self.button_number = button_number
        if button_number:
            self.level_up_signal.emit()
        else:
            self.level_down_signal.emit()

    def keyPressEvent(self, event):
        """When enter key is pressed the derivation_spinbox will act as one selection button pressed"""
        if not self.greatwall:
            return
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            value = self.derivation_spinbox.value()
            if (
                value <= len(self.selection_buttons)
                and self.greatwall.current_level < self.greatwall.tree_depth
            ):
                self.on_button_click(value)

    def show_layout_hide_others(self, widgets_to_show: list):
        """Hide all widgets and show the given widgets list, also show the general widgets"""
        self.state_widgets = [
            self.input_state_widgets,
            self.confirmation_widgets,
            self.dependent_derivation_widgets,
            self.wait_derivation_widgets,
            self.confirm_result_widgets,
            self.finish_widgets,
            self.error_widgets,
        ]
        for widgets_to_hide in self.state_widgets:
            for widget in widgets_to_hide:
                # Try to hide widget, it may have been deleted causing an exception
                try:
                    widget.hide()
                except RuntimeError:
                    continue
        [widget.show() for widget in self.general_widgets]
        [state_widget.show() for state_widget in widgets_to_show]

    def input_state1_entered(self):
        print("SM1 State 1 Entered")
        self.next_button.setText("Next")
        self.next_button.setEnabled(True)
        self.back_button.setText("Exit")
        self.back_button.setEnabled(True)
        self.result_hash.clear()
        self.result_hash.setText("")
        self.show_layout_hide_others(self.input_state_widgets)
        self.reinit_running_greatwall()

    def confirm_state2_entered(self):
        print("SM1 State 2 Entered")
        self.configure_confirmation_widgets()
        self.show_layout_hide_others(self.confirmation_widgets)
        next_text = "Next"
        back_text = "Reset"
        self.next_button.setText(next_text)
        self.back_button.setText(back_text)

    def derivation_state3_entered(self):
        print("SM1 State 3 Entered")
        next_text = "Next"
        reset_text = "Reset"
        self.next_button.setText(next_text)
        self.back_button.setText(reset_text)

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

            self.configure_waiting_derivation_widgets()
            self.configure_choose_derivation_widgets()
            self.show_layout_hide_others(self.wait_derivation_widgets)
            self.next_button.setEnabled(False)

            # Start the execution in a separate thread
            self.greatwall_thread = GreatWallWorker(self.greatwall)
            self.greatwall_thread.finished.connect(self.on_thread_finish)
            self.greatwall_thread.canceled.connect(self.on_thread_cancel)
            self.greatwall_thread.error_occurred.connect(self.on_thread_error)
            self.init_loop_dynamic_sm()

        except Exception as e:
            self.error_occurred = e
            self.gui_error_signal.emit()

    def init_loop_dynamic_sm(self):
        if self.loop_dynamic_sm.isRunning():
            self.loop_dynamic_sm.stop()

        num_states = self.depth_spinbox.value() + 1

        # Remove existing states
        for each_transition in self.transitions:
            # Remove the transitions from states
            source_state = each_transition.sourceState()
            if source_state:
                source_state.removeTransition(each_transition)

        # Clear the transitions list after removal
        self.transitions.clear()

        # Create and add new states
        self.dynamic_states.clear()
        for i in range(num_states):
            state = QState()
            state.entered.connect(self.loop_state_n_entered)
            self.loop_dynamic_sm.addState(state)
            self.dynamic_states.append(state)

        # Add transitions between states,
        # except the first state doesn't transit with level_down_signal
        # and the last state doesn't transit with level_up_signal
        for state_index in range(len(self.dynamic_states)):
            each_state = self.dynamic_states[state_index]

            if state_index < len(self.dynamic_states) - 1:
                next_state = self.dynamic_states[state_index + 1]
                transition = QSignalTransition(self.level_up_signal)
                transition.setTargetState(next_state)
                each_state.addTransition(transition)
                self.transitions.append(transition)

            if state_index:
                previous_state = self.dynamic_states[state_index - 1]
                transition = QSignalTransition(self.level_down_signal)
                transition.setTargetState(previous_state)
                each_state.addTransition(transition)
                self.transitions.append(transition)

        # Start the state machine
        self.loop_dynamic_sm.setInitialState(self.dynamic_states[0])
        self.loop_dynamic_sm.start()
        self.sm2_is_running.emit()
        self.run_greatwall_thread()

    def run_greatwall_thread(self, user_choice: int = 0):
        if user_choice >= 0:
            self.greatwall_thread.user_choice = user_choice
            self.greatwall_thread.start()

    def output_state4_entered(self):
        print("SM1 State 4 Entered")
        next_text = "Next"
        reset_text = "Reset"

        self.show_layout_hide_others(self.finish_widgets)
        self.finish_text.hide()
        self.finish_text.setText(self.finish_output.hex())
        self.finish_text.setReadOnly(True)
        self.next_button.setText(next_text)
        self.next_button.setEnabled(False)
        self.next_button.hide()
        self.back_button.setText(reset_text)

    def loop_state_n_entered(self):
        try:
            print(
                f"SM2 State Entered at level {self.greatwall.current_level} of {self.greatwall.tree_depth}"
            )
            # self.show_layout_hide_others(self.wait_derivation_widgets)
            self.next_button.setEnabled(False)
            self.run_greatwall_thread(self.button_number)
        except Exception as e:
            self.error_occurred = e
            self.gui_error_signal.emit()

    def handle_gui_errors(self):
        print("Error State Entered")
        next_text = "Next"
        reset_text = "Reset"
        exception_message = f"Exception:\n{str(self.error_occurred)}"
        self.exception_label.setText(exception_message)
        self.show_layout_hide_others(self.error_widgets)
        self.next_button.setText(next_text)
        self.next_button.setEnabled(False)
        self.next_button.hide()
        self.back_button.setText(reset_text)
        self.back_button.setEnabled(True)
        self.back_button.show()

    def reinit_running_greatwall(self):
        if hasattr(self, "greatwall_thread") and self.greatwall_thread.isRunning():
            self.greatwall.cancel_execution()
            self.greatwall_thread.cancel()
        if self.loop_dynamic_sm.isRunning():
            self.loop_dynamic_sm.stop()

        self.greatwall.current_level = 0

    def on_hide_show_button_click(self):
        self.finish_text.setVisible(not self.finish_text.isVisible())
        button_text = "Hide" if self.finish_text.isVisible() else "Show"
        self.hide_show_button.setText(f"{button_text} output")

    def on_thread_finish(self):
        if self.greatwall.current_level >= self.greatwall.tree_depth:
            self.finish_output = self.greatwall.finish_output()
            if self.selected_tacit_knowledge == constants.FRACTAL:
                formated_fractal = self.greatwall.fractal.update(
                    func_type=self.greatwall.fractal.func_type,
                    p_param=self.greatwall.fractal.get_valid_parameter_from_value(
                        self.finish_output
                    ),
                )

                rgb_array = ImageViewer.gray_array_to_rgb_array(formated_fractal)
                qimage = ImageViewer.rgb_array_to_Qimage(rgb_array)
                image = QPixmap.fromImage(qimage)

                self.result_hash.setPixmap(image)
                self.result_hash.resize(image.size())
            if self.selected_tacit_knowledge == constants.FORMOSA:
                formatted_mnemonic = self.greatwall.mnemo.format_mnemonic(
                    self.greatwall.mnemo.to_mnemonic(self.finish_output)
                )
                formatted_mnemonic = "\n".join(
                    formatted_mnemonic.split("\n")[1 : self.greatwall.tree_arity + 1]
                )
                local_finish_output = formatted_mnemonic
                self.result_hash.setText(local_finish_output)
            if self.selected_tacit_knowledge == constants.SHAPE:
                print(self.finish_output)
                image_path = self.greatwall.shaper.draw_regular_shape(
                    self.finish_output
                )
                image = QPixmap(str(image_path))
                self.result_hash.setPixmap(image)
                self.result_hash.resize(image.size())

            # self.configure_selection_buttons()
            self.show_layout_hide_others(self.confirm_result_widgets)
            self.next_button.setEnabled(True)
        else:
            self.configure_selection_buttons()
            self.show_layout_hide_others(self.dependent_derivation_widgets)

    def on_thread_cancel(self):
        print("Task canceled")

    def on_thread_error(self, error_msg):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("GreatWall Error Occurred")
        error_dialog.setInformativeText(error_msg)
        error_dialog.setWindowTitle("Thread Error")
        error_dialog.exec_()

    def on_close_app(self):
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
