from PyQt5.QtCore import (
    QSignalTransition,
    QSize,
    QState,
    QStateMachine,
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from resources import constants
from resources.greatwall import GreatWall
from resources.knowledge.mnemonic.mnemonic import Mnemonic


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
                self.greatwall.initialize_state_hashes()
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


class ImageViewer(QGraphicsView):
    """Custom image viewer with zoom and pan capability."""

    def __init__(self, parent):
        super(ImageViewer, self).__init__(parent)
        self._zoom = 0
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)

        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
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
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
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
        self.available_tacit_knowledge = ["Fractal", "Formosa", "Shape"]
        self.selected_tacit_knowledge = ""

        # General Widgets
        self.back_button = QPushButton(self)
        self.next_button = QPushButton(self)

        # Input Widgets
        self.tacit_knowledge_label = QLabel(self)
        self.tacit_knowledge_combobox = QComboBox(self)

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
        # Attention to add widgets to this layout, they will be deleted later and can cause an exception
        self.derivation_layout = QVBoxLayout()
        self.selection_buttons: list[QPushButton] = []

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
        self.main_states: list[QState()] = []
        self.error_states: list[QState()] = []
        self.main_gui_sm = QStateMachine()
        self.loop_dynamic_sm = QStateMachine()
        self.dynamic_states: list[QState()] = []
        self.init_ui()
        self.init_main_app_state()

    def init_ui(self):
        self.setWindowTitle("Great Wall Sample")
        self.setGeometry(100, 100, 500, 300)

        # Hardcode to fast tests
        # self.password_text.setText("viboniboasmofiasbrchsprorirerugugucavehistmiinciwibowifltuor")

        self.configure_ui_widgets()
        self.configure_layout()

    def configure_ui_widgets(self):
        # Strings variables to easily translate in the future versions
        next_text = "Next"
        back_text = "Back"

        choose_tacit_knowledge_type = "Tacit knowledge Type"
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
        self.theme_label.setText(choose_theme)
        self.tlp_label.setText(choose_tlp)
        self.depth_label.setText(choose_depth)
        self.arity_label.setText(choose_arity)
        self.password_label.setText(password)

        # Set default input values
        self.tacit_knowledge_combobox.addItems(self.available_tacit_knowledge)
        self.tacit_knowledge_combobox.setCurrentText(self.available_tacit_knowledge[0])
        self.tacit_knowledge_combobox.currentTextChanged.connect(
            self.on_change_tacit_knowledge_combobox
        )
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

    def configure_confirmation_widgets(self):
        confirm_values = "Confirm your values"
        theme_chosen = "Theme\n"
        tlp_chosen = "TLP parameter\n"
        depth_chosen = "Tree depth\n"
        arity_chosen = "Tree arity\n"
        password_chosen = "Time-Lock Puzzle password\n"

        self.confirm_label.setText(confirm_values)
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
            pass
        elif self.tacit_knowledge_combobox.currentText() == constants.FORMOSA:
            # Set buttons to Formosa options
            user_options = self.greatwall.get_li_str_query().split("\n")
            if len(user_options) == len(self.selection_buttons) + 1:
                [
                    self.selection_buttons[i].setText(user_options[i])
                    for i in range(1, len(self.selection_buttons))
                ]
        elif self.tacit_knowledge_combobox.currentText() == constants.SHAPE:
            # Set buttons to Shape options
            user_options = self.greatwall.get_shape_query()
            if len(user_options) == len(self.selection_buttons):
                offset = QSize(25, 5)
                for button in self.selection_buttons[1:]:
                    button_index = self.selection_buttons.index(button)
                    image = QPixmap(str(user_options[button_index]))
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
        cancel_text = "0) Previous Step"

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
            button_text = f"{i}) " if i > 0 else cancel_text
            button = QPushButton(button_text, self)
            button.clicked.connect(lambda state, x=i: self.on_button_click(x))
            if button not in self.confirm_result_widgets and i == 0:
                # Button 0 'previous step' must be visible in the last step
                self.confirm_result_widgets.append(button)
            self.derivation_layout.addWidget(button)
            self.dependent_derivation_widgets.append(button)
            self.selection_buttons.append(button)

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
            self.show_layout_hide_others(self.wait_derivation_widgets)
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
                image_path = self.greatwall.shaper.draw_regular_shape(
                    self.finish_output
                )
                image = QPixmap(str(image_path))
                self.result_hash.setPixmap(image)
                self.result_hash.resize(image.size())

            self.configure_selection_buttons()
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