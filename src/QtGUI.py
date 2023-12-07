from PyQt5.QtCore import QStateMachine, QState, QThread, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QLabel, QPushButton,
                             QComboBox, QSpinBox, QTextEdit, QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import Qt
from greatwall import GreatWall
from src.mnemonic.mnemonic import Mnemonic


# Custom Worker class to perform the time-consuming task
class GreatWallWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, greatwall: GreatWall):
        super().__init__()
        self.greatwall = greatwall

    def run(self):
        self.greatwall.execute_greatwall()
        self.finished.emit()


class GreatWallQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.finish_output: bytes = bytes(0000)
        self.greatwall = None

        # General Widgets
        self.back_button = QPushButton(self)
        self.next_button = QPushButton(self)

        # Input Widgets
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

        # Dependent Derivation Widgets
        self.derivation_spinbox = QSpinBox(self)
        self.derivation_layout = QVBoxLayout()
        self.selection_buttons = []
        self.confirm_labels = []

        # Result Widgets
        # self.result_confirm_layout = QVBoxLayout()
        self.confirm_result_label = QLabel(self)
        self.result_hash = QLabel(self)

        # Finish Widgets
        self.finish_output_label = QLabel(self)
        self.finish_text = QTextEdit(self)

        # List of general Widgets
        self.general_widgets = [self.next_button, self.back_button]

        # Lists of widgets per step
        self.input_state_widgets = [self.theme_label, self.theme_combobox, self.tlp_label, self.tlp_spinbox,
                                    self.depth_label, self.depth_spinbox, self.arity_label, self.arity_spinbox,
                                    self.password_label, self.password_text]
        self.confirmation_widgets = [self.confirm_label, self.theme_confirm, self.tlp_confirm, self.depth_confirm,
                                     self.arity_confirm, self.password_confirm]
        self.dependent_derivation_widgets = [self.derivation_spinbox]
        self.confirm_result_widgets = [self.confirm_result_label, self.result_hash]
        self.finish_widgets = [self.finish_output_label, self.finish_text]

        # List of widgets lists
        self.state_widgets = []

        # Threaded execution objects
        self.worker_thread = QThread

        # Launch UI
        self.state_machine = QStateMachine()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Great Wall Sample")
        self.setGeometry(100, 100, 100, 100)

        self.password_text.setGeometry(0, 0, 100, 50)
        # Hardcode to fast tests
        self.password_text.setText("viboniboasmofiasbrchsprorirerugugucavehistmiinciwibowifltuor")

        self.configure_ui_widgets()
        self.configure_layout()
        self.init_state_machine()

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

        # General Widgets
        self.back_button.setText(next_text)
        self.next_button.setText(back_text)

        # Input Widgets
        self.theme_label.setText(choose_theme)
        self.tlp_label.setText(choose_tlp)
        self.depth_label.setText(choose_depth)
        self.arity_label.setText(choose_arity)
        self.password_label.setText(password)

        # Confirmation Widgets
        self.configure_confirmation_widgets()

        # Result Widget
        self.confirm_result_label.setText(result_confirm)

        # Finish Widget
        self.finish_output_label.setText(finish_output_message)

        themes = Mnemonic.find_themes()
        self.theme_combobox.addItems(themes)
        self.theme_combobox.setCurrentText(themes[0])
        # Hardcode to fast tests
        # self.theme_combobox.setCurrentText("medieval_fantasy")

        self.config_spinbox(self.tlp_spinbox, 1, 24*7*4*3, 1, 1)
        self.config_spinbox(self.depth_spinbox, 1, 256, 1, 1)
        # Hardcode to fast tests
        # self.config_spinbox(self.depth_spinbox, 1, 256, 1, 2)
        self.config_spinbox(self.arity_spinbox, 2, 256, 1, 2)

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
        theme_chosen = "Theme\n"
        tlp_chosen = "TLP parameter\n"
        depth_chosen = "Tree depth\n"
        arity_chosen = "Tree arity\n"
        password_chosen = "Time-Lock Puzzle password\n"

        self.confirm_label.setText("Confirm your values")
        self.theme_confirm.setText(theme_chosen + str(self.theme_combobox.currentText()))
        self.tlp_confirm.setText(tlp_chosen + str(self.tlp_spinbox.value()))
        self.depth_confirm.setText(depth_chosen + str(self.depth_spinbox.value()))
        self.arity_confirm.setText(arity_chosen + str(self.arity_spinbox.value()))
        self.password_confirm.setText(password_chosen + self.password_text.toPlainText())

    def configure_choose_derivation_widgets(self):
        if not self.greatwall:
            return

        cancel_text = "0) Previous Step"

        # Clear widgets from list and layout
        self.dependent_derivation_widgets = []
        self.selection_buttons = []
        [self.derivation_layout.itemAt(i).widget().setParent(None)
         for i in reversed(range(self.derivation_layout.count()))]

        self.config_spinbox(self.derivation_spinbox, 0, self.greatwall.tree_arity, 1, 0)
        self.derivation_layout.addWidget(self.derivation_spinbox)
        self.dependent_derivation_widgets.append(self.derivation_spinbox)
        for i in range(self.greatwall.tree_arity + 1):
            button_text = f"{i}) Idle" if i > 0 else cancel_text
            button = QPushButton(button_text, self)
            button.clicked.connect(lambda state, x=i: self.button_clicked(x))
            self.derivation_layout.addWidget(button)
            self.dependent_derivation_widgets.append(button)
            self.selection_buttons.append(button)

    def button_clicked(self, button_number):
        if not self.greatwall:
            return
        self.greatwall.derive_from_user_choice(button_number)
        self.loop_derivation()

    def keyPressEvent(self, event):
        """When enter key is pressed the derivation_spinbox will act as one selection button pressed"""
        if not self.greatwall:
            return
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            value = self.derivation_spinbox.value()
            if value <= len(self.selection_buttons) and self.greatwall.current_level < self.greatwall.tree_depth:
                self.button_clicked(value)

    def configure_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Adding widgets to the main layout
        [main_layout.addWidget(widget) for widget in self.input_state_widgets]
        [main_layout.addWidget(widget) for widget in self.confirmation_widgets]
        main_layout.addLayout(self.derivation_layout)
        [main_layout.addWidget(widget) for widget in self.confirm_result_widgets]
        [main_layout.addWidget(widget) for widget in self.finish_widgets]
        main_layout.addStretch(1)  # Add stretchable space to the end

        # Horizontal layout for buttons
        general_buttons_layout = QHBoxLayout()
        general_buttons_layout.addWidget(self.back_button)
        general_buttons_layout.addStretch(1)  # Add stretchable space between buttons
        general_buttons_layout.addWidget(self.next_button)

        # Add the buttons layout to the main layout
        main_layout.addLayout(general_buttons_layout)

    def configure_selection_buttons(self, valid_options: list[str]):
        if len(valid_options) == len(self.selection_buttons)+1:
            [self.selection_buttons[i].setText(valid_options[i]) for i in range(1, len(self.selection_buttons))]

    def init_state_machine(self):

        quit_state = QState()
        quit_state.setObjectName("State 0")

        user_input_state = QState()
        user_input_state.setObjectName("State 1")

        confirm_state = QState()
        confirm_state.setObjectName("State 2")

        dependent_derivation_state = QState()
        dependent_derivation_state.setObjectName("State 3")

        result_state = QState()
        result_state.setObjectName("State 4")

        # Define transitions
        user_input_state.addTransition(self.next_button.clicked, confirm_state)
        user_input_state.addTransition(self.back_button.clicked, quit_state)
        confirm_state.addTransition(self.next_button.clicked, dependent_derivation_state)
        confirm_state.addTransition(self.back_button.clicked, user_input_state)
        dependent_derivation_state.addTransition(self.next_button.clicked, result_state)
        dependent_derivation_state.addTransition(self.back_button.clicked, user_input_state)
        result_state.addTransition(self.next_button.clicked, quit_state)
        result_state.addTransition(self.back_button.clicked, user_input_state)

        # Add states to the state machine
        self.state_machine.addState(quit_state)
        self.state_machine.addState(user_input_state)
        self.state_machine.addState(confirm_state)
        self.state_machine.addState(dependent_derivation_state)
        self.state_machine.addState(result_state)

        # Set initial state
        self.state_machine.setInitialState(user_input_state)

        # Start the state machine
        self.state_machine.start()

        # Connect states to methods
        quit_state.entered.connect(self.close_application)
        user_input_state.entered.connect(self.state1_entered)
        confirm_state.entered.connect(self.state2_entered)
        dependent_derivation_state.entered.connect(self.state3_entered)
        result_state.entered.connect(self.state4_entered)

    def show_layout_hide_others(self, widgets: list):
        """Hide all widgets and show the given widgets list, also show the general widgets"""
        self.state_widgets = [self.input_state_widgets, self.confirmation_widgets,
                              self.dependent_derivation_widgets, self.confirm_result_widgets,
                              self.finish_widgets]
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

        self.greatwall = GreatWall()
        self.greatwall.set_themed_mnemo(self.theme_combobox.currentText())
        self.greatwall.set_tlp(self.tlp_spinbox.value())
        self.greatwall.set_depth(self.depth_spinbox.value())
        self.greatwall.set_arity(self.arity_spinbox.value())
        self.greatwall.set_sa0(self.password_text.toPlainText())

        self.configure_choose_derivation_widgets()
        self.show_layout_hide_others(self.dependent_derivation_widgets)
        # Start the execution in a separate thread
        self.worker_thread = GreatWallWorker(self.greatwall)
        self.worker_thread.finished.connect(self.handle_execution_finished)
        self.worker_thread.start()

    def handle_execution_finished(self):
        # Perform actions when the execution is finished
        self.loop_derivation()

    def state4_entered(self):
        print('State 4 Entered')
        next_text = "Next"
        reset_text = "Reset"

        self.show_layout_hide_others(self.finish_widgets)
        self.finish_text.setText(self.finish_output.hex())
        self.finish_text.setReadOnly(True)
        self.next_button.setText(next_text)
        self.next_button.setEnabled(False)
        self.next_button.hide()
        self.back_button.setText(reset_text)

    def split_string(self, string: str) -> str:
        """Split the given string into four lines"""
        ret = ""
        quarter = len(string) // 4 + len(string) % 4
        for i in [0, 1, 2, 3]:
            # Split string in equal parts, last part is unequal if it isn't divisible by four
            ret += string[i * quarter: (i + 1) * quarter if i != 3 else len(string)] + "\n"
        return ret[:-1]

    def loop_derivation(self):
        if not self.greatwall:
            return
        if self.greatwall.current_level >= self.greatwall.tree_depth:
            self.finish_output = self.greatwall.finish_output()
            formatted_mnemonic = self.greatwall.mnemo.format_mnemonic(
                self.greatwall.mnemo.to_mnemonic(self.finish_output)
            )
            formatted_mnemonic = "\n".join(formatted_mnemonic.split("\n")[1:])
            # local_finish_output = self.split_string(self.finish_output.hex()) + "\n" + formatted_mnemonic
            local_finish_output = formatted_mnemonic
            self.result_hash.setText(local_finish_output)
            self.show_layout_hide_others(self.confirm_result_widgets)
            self.dependent_derivation_widgets[1].show()
            self.next_button.setEnabled(True)
        else:
            self.show_layout_hide_others(self.dependent_derivation_widgets)
            user_options = self.greatwall.get_li_str_query().split("\n")
            self.configure_selection_buttons(user_options)
            self.next_button.setEnabled(False)

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
