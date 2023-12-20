from PyQt5.QtCore import QStateMachine, QState, QThread, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QLabel, QPushButton, QMessageBox,
                             QComboBox, QSpinBox, QTextEdit, QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import Qt
from greatwall import GreatWall
from src.mnemonic.mnemonic import Mnemonic


# Custom Worker class to perform the time-consuming task
class GreatWallWorker(QThread):
    finished = pyqtSignal()
    canceled = pyqtSignal()
    error_occurred = pyqtSignal(str)  # Signal for passing error messages

    def __init__(self, greatwall: GreatWall):
        super().__init__()
        self.greatwall = greatwall
        self._is_canceled = False

    def run(self):
        try:
            self.greatwall.execute_greatwall()
            if not self._is_canceled:
                self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def cancel(self):
        self._is_canceled = True
        self.canceled.emit()


class GreatWallQt(QMainWindow):
    gui_error_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.finish_output: bytes = bytes(0000)
        self.greatwall = GreatWall()
        self.error_occurred = Exception

        # General Widgets
        self.back_button = QPushButton(self)
        self.next_button = QPushButton(self)

        # Input Widgets
        self.user_query_combobox = QComboBox(self)
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
        self.derivation_spinbox = QSpinBox(self)
        self.derivation_layout = QVBoxLayout()
        self.selection_buttons = []
        self.confirm_labels = []

        # Result Widgets
        self.confirm_result_label = QLabel(self)
        self.result_hash = QLabel(self)

        # Finish Widgets
        self.finish_output_label = QLabel(self)
        self.finish_text = QTextEdit(self)
        self.hide_show_button = QPushButton(self)
        self.copy_clipboard_button = QPushButton(self)

        # List of general Widgets
        self.general_widgets = [self.next_button, self.back_button]

        # Error widgets
        self.config_error_label = QLabel(self)
        self.execution_error_label = QLabel(self)
        self.unknown_error_label = QLabel(self)
        self.exception_label = QLabel(self)

        # Lists of widgets per step
        self.input_state_widgets = [self.user_query_combobox, self.theme_label, self.theme_combobox, self.tlp_label,
                                    self.tlp_spinbox, self.depth_label, self.depth_spinbox, self.arity_label,
                                    self.arity_spinbox, self.password_label, self.password_text]
        self.confirmation_widgets = [self.confirm_label, self.theme_confirm, self.tlp_confirm, self.depth_confirm,
                                     self.arity_confirm, self.password_confirm]
        self.wait_derivation_widgets = [self.wait_derive_label]
        self.dependent_derivation_widgets = [self.derivation_spinbox]
        self.confirm_result_widgets = [self.confirm_result_label, self.result_hash]
        self.finish_widgets = [self.finish_output_label, self.finish_text, self.hide_show_button,
                               self.copy_clipboard_button]
        self.error_widgets = [self.config_error_label, self.execution_error_label,
                              self.unknown_error_label, self.exception_label]

        # List of widgets lists
        self.state_widgets = []

        # Threaded execution objects
        self.worker_thread = GreatWallWorker(self.greatwall)

        # Launch UI
        self.all_states = []
        self.error_states = []
        self.state_machine = QStateMachine()
        self.dyn_state_machine = QStateMachine()
        self.dyn_states = []
        self.init_ui()
        self.init_state_machine()

    def init_ui(self):
        self.setWindowTitle("Great Wall Sample")
        self.setGeometry(100, 100, 100, 100)

        self.password_text.setGeometry(0, 0, 100, 50)
        # Hardcode to fast tests
        self.password_text.setText("viboniboasmofiasbrchsprorirerugugucavehistmiinciwibowifltuor")

        self.configure_ui_widgets()
        self.configure_layout()

    def configure_ui_widgets(self):

        # Strings variables to easily translate in the future versions
        next_text = "Next"
        back_text = "Back"

        choose_theme = "Choose Theme"
        choose_tlp = "Choose TLP parameter from 1 to 2016"
        choose_depth = "Choose tree depth from 1 to 256"
        choose_arity = "Choose tree arity from 2 to 256"
        password = "Enter Time-Lock Puzzle password:"
        result_confirm = "Do you confirm this result?"
        finish_output_message = "This is the result output:"
        wait_derive = "Wait the derivation to finish\nThis will take some time"
        config_error_message = "Some configuration might went wrong\n\tDouble check the theme chosen and your password"
        execution_error_message = \
            "The GreatWall execution might went wrong\n\tPlease double check your dependencies version and try again"
        unknown_error_message = "Or some unexpected error occurred"
        hide_show = "Show output"
        copy_clipboard = "Copy output to clipboard"

        # General Widgets
        self.back_button.setText(next_text)
        self.next_button.setText(back_text)

        # Input Widgets
        self.theme_label.setText(choose_theme)
        self.tlp_label.setText(choose_tlp)
        self.depth_label.setText(choose_depth)
        self.arity_label.setText(choose_arity)
        self.password_label.setText(password)
        query_types = ["Formosa", "Shape"]
        self.user_query_combobox.addItems(query_types)
        self.user_query_combobox.setCurrentText(query_types[0])
        self.user_query_combobox.currentTextChanged.connect(self.change_query_type)
        themes = Mnemonic.find_themes()
        self.theme_combobox.addItems(themes)
        self.theme_combobox.setCurrentText(themes[0])
        # Hardcode to fast tests
        # self.theme_combobox.setCurrentText("medieval_fantasy")

        # Wait Derive Widget
        self.wait_derive_label.setText(wait_derive)

        # Confirmation Widgets
        self.configure_confirmation_widgets()

        # Result Widget
        self.confirm_result_label.setText(result_confirm)

        # Finish Widget
        self.finish_output_label.setText(finish_output_message)
        self.hide_show_button.setText(hide_show)
        self.hide_show_button.clicked.connect(self.hide_show_output)
        self.copy_clipboard_button.setText(copy_clipboard)
        self.copy_clipboard_button.clicked.connect(self.copy_to_clipboard)

        # Error widget
        self.config_error_label.setText(config_error_message)
        self.execution_error_label.setText(execution_error_message)
        self.unknown_error_label.setText(unknown_error_message)

        self.config_spinbox(self.tlp_spinbox, 1, 24*7*4*3, 1, 1)
        self.config_spinbox(self.depth_spinbox, 1, 256, 1, 1)
        # Hardcode to fast tests
        # self.config_spinbox(self.depth_spinbox, 1, 256, 1, 2)
        self.config_spinbox(self.arity_spinbox, 2, 256, 1, 2)

    def change_query_type(self):
        is_formosa = self.user_query_combobox.currentText() == "Formosa"
        self.theme_combobox.setEnabled(is_formosa)
        # self.theme_combobox.setVisible(is_formosa)
        self.theme_label.setEnabled(is_formosa)
        # self.theme_label.setVisible(is_formosa)

    def hide_show_output(self):
        self.finish_text.setVisible(not self.finish_text.isVisible())
        button_text = "Hide" if self.finish_text.isVisible() else "Show"
        self.hide_show_button.setText(f"{button_text} output")

    def copy_to_clipboard(self):
        if not self.greatwall.is_finished:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(self.finish_output.hex())

    @staticmethod
    def config_spinbox(spinbox: QSpinBox,
                       min_value: int,
                       max_value: int,
                       step_value: int = 1,
                       default_value: int = 0,
                       set_wrapping: bool = True):
        """Easy configure any spinbox with one line call"""
        spinbox.setRange(min_value, max_value)
        spinbox.setSingleStep(step_value)
        spinbox.setValue(default_value)
        spinbox.setWrapping(set_wrapping)

    def configure_confirmation_widgets(self):
        confirm_values = "Confirm your values"
        theme_chosen = "Theme\n"
        tlp_chosen = "TLP parameter\n"
        depth_chosen = "Tree depth\n"
        arity_chosen = "Tree arity\n"
        password_chosen = "Time-Lock Puzzle password\n"

        self.confirm_label.setText(confirm_values)
        self.theme_confirm.setText(theme_chosen + str(self.theme_combobox.currentText()))
        self.tlp_confirm.setText(tlp_chosen + str(self.tlp_spinbox.value()))
        self.depth_confirm.setText(depth_chosen + str(self.depth_spinbox.value()))
        self.arity_confirm.setText(arity_chosen + str(self.arity_spinbox.value()))
        self.password_confirm.setText(password_chosen + self.password_text.toPlainText())

    def configure_waiting_derivation_widgets(self):
        """Configure any message or effect to be shown while derive"""
        pass

    def configure_choose_derivation_widgets(self):
        if not self.greatwall:
            return

        cancel_text = "0) Previous Step"

        # Clear widgets from list and layout
        self.dependent_derivation_widgets = []
        self.selection_buttons = []
        # Destroy widgets by setting the parents as None
        for i in reversed(range(self.derivation_layout.count())):
            self.derivation_layout.itemAt(i).widget().setParent(None)
            if self.derivation_layout.itemAt(i) is not None:
                self.derivation_layout.itemAt(i).widget().deleteLater()

        self.config_spinbox(self.derivation_spinbox, 0, self.greatwall.tree_arity, 1, 0)
        self.derivation_layout.addWidget(self.derivation_spinbox)
        self.dependent_derivation_widgets.append(self.derivation_spinbox)
        for i in range(self.greatwall.tree_arity + 1):
            button_text = f"{i}) " if i > 0 else cancel_text
            button = QPushButton(button_text, self)
            button.clicked.connect(lambda state, x=i: self.button_clicked(x))
            self.derivation_layout.addWidget(button)
            self.dependent_derivation_widgets.append(button)
            self.selection_buttons.append(button)

    def button_clicked(self, button_number):
        print("button check", True if button_number else False)
        if button_number > 0:
            self.clicked_next_state(button_number)
        else:
            self.clicked_previous_state()
        # self.loop_derivation()

    def keyPressEvent(self, event):
        """When enter key is pressed the derivation_spinbox will act as one selection button pressed"""
        if not self.greatwall:
            return
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            value = self.derivation_spinbox.value()
            if value <= len(self.selection_buttons) and self.greatwall.current_level < self.greatwall.tree_depth:
                self.button_clicked(value)

    def clicked_next_state(self, button_number):
        """Method to adapt the dynamic state machine state transition"""
        self.greatwall.derive_from_user_choice(button_number)

    def clicked_previous_state(self):
        """Method to adapt the dynamic state machine state transition"""
        self.greatwall.derive_from_user_choice(0)

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
        general_buttons_layout.addStretch(1)  # Add stretchable space between buttons
        general_buttons_layout.addWidget(self.next_button)

        # Add the buttons layout to the main layout
        main_layout.addLayout(general_buttons_layout)

    def configure_selection_buttons(self):
        if self.user_query_combobox.currentText() == "Formosa":
            user_options = self.greatwall.get_li_str_query().split("\n")
            if len(user_options) == len(self.selection_buttons)+1:
                [self.selection_buttons[i].setText(user_options[i]) for i in range(1, len(self.selection_buttons))]
        else:
            # user_options = self.greatwall.get_shape_query()
            # if len(user_options) == len(self.selection_buttons)+1:
            #     [self.selection_buttons[i].setText("") for i in range(1, len(self.selection_buttons))]
            pass

    def init_state_machine(self):

        quit_state = QState()
        quit_state.setObjectName("State 0")

        user_input_state = QState()
        user_input_state.setObjectName("State 1")

        confirm_state = QState()
        confirm_state.setObjectName("State 2")

        dependent_derivation_state = QState()
        dependent_derivation_state.setObjectName("State 3")

        finish_output_state = QState()
        finish_output_state.setObjectName("State 4")

        gui_error_state = QState()
        gui_error_state.setObjectName("State X01")

        # List of states
        self.error_states = [gui_error_state, ]
        self.all_states = [quit_state, user_input_state, confirm_state, dependent_derivation_state,
                           finish_output_state] + self.error_states

        # Define transitions
        user_input_state.addTransition(self.next_button.clicked, confirm_state)
        user_input_state.addTransition(self.back_button.clicked, quit_state)
        confirm_state.addTransition(self.next_button.clicked, dependent_derivation_state)
        confirm_state.addTransition(self.back_button.clicked, user_input_state)
        dependent_derivation_state.addTransition(self.next_button.clicked, finish_output_state)
        dependent_derivation_state.addTransition(self.back_button.clicked, user_input_state)
        finish_output_state.addTransition(self.next_button.clicked, quit_state)
        finish_output_state.addTransition(self.back_button.clicked, user_input_state)
        gui_error_state.addTransition(self.back_button.clicked, user_input_state)
        # Error transitions, add to all states except the error states
        [each_state.addTransition(self.gui_error_signal, gui_error_state)
         for each_state in set(self.all_states)-set(self.error_states)]

        # Add states to the state machine
        [self.state_machine.addState(each_state) for each_state in self.all_states]

        # Set initial state
        self.state_machine.setInitialState(user_input_state)

        # Start the state machine
        self.state_machine.start()

        # Connect states to methods
        quit_state.entered.connect(self.close_application)
        user_input_state.entered.connect(self.state1_entered)
        confirm_state.entered.connect(self.state2_entered)
        dependent_derivation_state.entered.connect(self.state3_entered)
        finish_output_state.entered.connect(self.state4_entered)
        gui_error_state.entered.connect(self.handle_gui_errors)

    def update_dynamic_states(self):
        # TODO fix this
        if self.dyn_state_machine.isRunning():
            self.dyn_state_machine.stop()

        # Emulate a change in the number of steps or states
        num_states = self.depth_spinbox.value()  # Get the number of states dynamically

        # Remove existing states
        for state in self.dyn_states:
            state.removeTransition(self.clicked_next_state)  # Disconnect next state from existing states
            state.removeTransition(self.clicked_previous_state)  # Disconnect previous state from existing states
            self.dyn_state_machine.removeState(state)
            state.deleteLater()

        # Create and add new states
        self.dyn_states = []
        for i in range(num_states):
            state = QState()
            # Add transitions, properties, etc., to the state as needed
            # ...
            state.entered.connect(self.loop_derivation)
            self.dyn_state_machine.addState(state)
            self.dyn_states.append(state)

        # Add transitions between states
        for state_index in range(1, len(self.dyn_states)-1):
            current_state = self.dyn_states[state_index]
            next_state = self.dyn_states[state_index+1]
            previous_state = self.dyn_states[state_index-1]
            current_state.addTransition(self.clicked_next_state, next_state)
            current_state.addTransition(self.clicked_previous_state, previous_state)

        # Start the state machine
        self.dyn_state_machine.setInitialState(self.dyn_states[0])  # Set initial state
        self.dyn_state_machine.start()

    def show_layout_hide_others(self, widgets: list):
        """Hide all widgets and show the given widgets list, also show the general widgets"""
        self.state_widgets = [self.input_state_widgets, self.confirmation_widgets,
                              self.dependent_derivation_widgets, self.wait_derivation_widgets,
                              self.confirm_result_widgets, self.finish_widgets, self.error_widgets]
        for widgets_list in self.state_widgets:
            [widget.hide() for widget in widgets_list]
        [widget.show() for widget in self.general_widgets]
        [state_widget.show() for state_widget in widgets]

    def state1_entered(self):
        print('State 1 Entered')
        self.next_button.setEnabled(True)
        self.back_button.setEnabled(True)
        self.show_layout_hide_others(self.input_state_widgets)
        next_text = "Next"
        exit_text = "Exit"
        self.next_button.setText(next_text)
        self.back_button.setText(exit_text)
        self.cancel_task()

    def state2_entered(self):
        print('State 2 Entered')
        self.configure_confirmation_widgets()
        self.show_layout_hide_others(self.confirmation_widgets)
        next_text = "Next"
        back_text = "Reset"
        self.next_button.setText(next_text)
        self.back_button.setText(back_text)

    def state3_entered(self):
        print('State 3 Entered')
        next_text = "Next"
        reset_text = "Reset"
        self.next_button.setText(next_text)
        self.back_button.setText(reset_text)

        try:
            themed_success = self.greatwall.set_themed_mnemo(self.theme_combobox.currentText())
            self.greatwall.set_tlp(self.tlp_spinbox.value())
            self.greatwall.set_depth(self.depth_spinbox.value())
            self.greatwall.set_arity(self.arity_spinbox.value())
            password_success = self.greatwall.set_sa0(self.password_text.toPlainText())

            if not themed_success or not password_success:
                self.error_occurred = ValueError("Config error. Password and theme don't match")
                self.gui_error_signal.emit()
                return

            self.configure_waiting_derivation_widgets()
            self.configure_choose_derivation_widgets()
            self.show_layout_hide_others(self.wait_derivation_widgets)
            self.next_button.setEnabled(False)

            # Start the execution in a separate thread
            self.worker_thread = GreatWallWorker(self.greatwall)
            self.worker_thread.finished.connect(self.handle_execution_finished)
            self.worker_thread.canceled.connect(self.handle_execution_canceled)
            self.worker_thread.error_occurred.connect(self.handle_greatwall_error)
            self.worker_thread.start()
        except Exception as e:
            self.error_occurred = e
            self.gui_error_signal.emit()

    def handle_execution_finished(self):
        # TODO fix this
        # Perform actions when the execution is finished
        self.update_dynamic_states()
        # self.loop_derivation()

    def handle_execution_canceled(self):
        print("Task canceled")

    def handle_greatwall_error(self, error_msg):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("GreatWall Error Occurred")
        error_dialog.setInformativeText(error_msg)
        error_dialog.setWindowTitle("Thread Error")
        error_dialog.exec_()

    def cancel_task(self):
        if self.worker_thread.isRunning():
            self.greatwall.cancel_execution()  # Set the cancellation flag in GreatWall
            self.worker_thread.cancel()

    def state4_entered(self):
        print('State 4 Entered')
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

    def loop_derivation(self):
        try:
            # TODO fix this
            print("State changed / 2nd SM")
            print(self.greatwall.current_level)
            if self.greatwall.current_level >= self.greatwall.tree_depth:
                self.finish_output = self.greatwall.finish_output()
                formatted_mnemonic = self.greatwall.mnemo.format_mnemonic(
                    self.greatwall.mnemo.to_mnemonic(self.finish_output)
                )
                formatted_mnemonic = "\n".join(formatted_mnemonic.split("\n")[1:self.greatwall.tree_arity+1])
                local_finish_output = formatted_mnemonic
                self.result_hash.setText(local_finish_output)
                self.show_layout_hide_others(self.confirm_result_widgets)
                self.dependent_derivation_widgets[1].show()
                self.next_button.setEnabled(True)
            else:
                self.show_layout_hide_others(self.dependent_derivation_widgets)
                self.configure_selection_buttons()
                self.next_button.setEnabled(False)
        except Exception as e:
            self.error_occurred = e
            self.gui_error_signal.emit()

    def handle_gui_errors(self):
        print('Error state Entered')
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

    def close_application(self):
        """ Close the parent which exit the application. Bye, come again!"""
        print("Closed")
        self.close()


def main():
    app = QApplication([])
    window = GreatWallQt()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
