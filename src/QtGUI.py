from PyQt5.QtCore import QStateMachine, QState
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QTabWidget, QLabel, QPushButton, QComboBox,
                             QSpinBox, QLineEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QCheckBox)
from greatwall import GreatWall
from src.mnemonic.mnemonic import Mnemonic


class GreatWallQt(QMainWindow):
    def __init__(self):
        super().__init__()
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

        self.input_state_widgets = [self.theme_label, self.theme_combobox, self.tlp_label, self.tlp_spinbox,
                                    self.depth_label, self.depth_spinbox, self.arity_label, self.arity_spinbox,
                                    self.password_label, self.password_text]
        self.confirmation_widgets = [self.confirm_label, self.theme_confirm, self.tlp_confirm, self.depth_confirm,
                                     self.arity_confirm, self.password_confirm]
        self.dependent_derivation_widgets = [self.derivation_spinbox]

        # Launch UI
        self.state_machine = QStateMachine()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Simple State Machine Example")
        self.setGeometry(100, 100, 100, 100)

        self.password_text.setGeometry(0, 0, 100, 50)

        self.configure_ui_widgets()
        self.configure_layout()
        self.init_state_machine()

    def configure_ui_widgets(self):

        choose_theme = "Choose Theme"
        choose_tlp = "Choose TLP parameter from 1 to 2016"
        choose_depth = "Choose tree depth from 1 to 256"
        choose_arity = "Choose tree arity from 2 to 256"
        password = "Enter Time-Lock Puzzle password:"

        # General Widgets
        self.back_button.setText("Back")
        self.next_button.setText("Next")

        # Input Widgets
        self.theme_label.setText(choose_theme)
        self.tlp_label.setText(choose_tlp)
        self.depth_label.setText(choose_depth)
        self.arity_label.setText(choose_arity)
        self.password_label.setText(password)

        # Confirmation Widgets
        self.configure_confirmation_widgets()

        themes = Mnemonic.find_themes()
        self.theme_combobox.addItems(themes)
        self.theme_combobox.setCurrentText(themes[0])

        self.config_spinbox(self.tlp_spinbox, 1, 24*7*4*3, 1, 1)
        self.config_spinbox(self.depth_spinbox, 1, 256, 1, 1)
        self.config_spinbox(self.arity_spinbox, 2, 256, 1, 2)

    @staticmethod
    def config_spinbox(spinbox: QSpinBox,
                       min_value: int,
                       max_value: int,
                       step_value: int = 1,
                       default_value: int = 0,
                       set_wrapping: bool = True):
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

    def configure_derivation_widgets(self):
        # Clear widgets from list and layout
        self.dependent_derivation_widgets = []
        [self.derivation_layout.itemAt(i).widget().setParent(None)
         for i in reversed(range(self.derivation_layout.count()))]

        self.config_spinbox(self.derivation_spinbox, 0, self.greatwall.tree_arity, 1, 0)
        self.derivation_layout.addWidget(self.derivation_spinbox)
        self.dependent_derivation_widgets.append(self.derivation_spinbox)
        for i in range(self.greatwall.tree_arity + 1):
            button_text = f"Button {i}" if i > 0 else "Cancel"
            button = QPushButton(button_text, self)
            button.clicked.connect(lambda state, x=i: self.button_clicked(x))
            self.derivation_layout.addWidget(button)
            self.dependent_derivation_widgets.append(button)

    def button_clicked(self, button_number):
        if button_number == 0:
            print("Cancel button clicked")
        else:
            print(f"Button {button_number} clicked")

    def configure_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Adding widgets to the main layout
        [main_layout.addWidget(widget) for widget in self.input_state_widgets]
        [main_layout.addWidget(widget) for widget in self.confirmation_widgets]
        main_layout.addLayout(self.derivation_layout)
        main_layout.addStretch(1)  # Add stretchable space to the end

        # Horizontal layout for buttons
        general_buttons_layout = QHBoxLayout()
        general_buttons_layout.addWidget(self.back_button)
        general_buttons_layout.addStretch(1)  # Add stretchable space between buttons
        general_buttons_layout.addWidget(self.next_button)

        # Add the buttons layout to the main layout
        main_layout.addLayout(general_buttons_layout)

    # def configure_derivation_layout(self):
    #     [self.derivation_layout.addWidget(widget) for widget in self.dependent_derivation_widgets]

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

    def state1_entered(self):
        print('State 1 Entered')
        self.next_button.setEnabled(True)
        self.back_button.setEnabled(True)
        [state_widget.hide() for state_widget in self.confirmation_widgets]
        [state_widget.hide() for state_widget in self.dependent_derivation_widgets]
        [state_widget.show() for state_widget in self.input_state_widgets]
        self.back_button.setText("Exit")

    def state2_entered(self):
        print('State 2 Entered')
        self.configure_confirmation_widgets()
        [state_widget.hide() for state_widget in self.input_state_widgets]
        [state_widget.hide() for state_widget in self.dependent_derivation_widgets]
        [state_widget.show() for state_widget in self.confirmation_widgets]
        self.back_button.setText("Back")

    def state3_entered(self):
        print('State 3 Entered')
        [state_widget.hide() for state_widget in self.input_state_widgets]
        [state_widget.hide() for state_widget in self.confirmation_widgets]
        [state_widget.show() for state_widget in self.dependent_derivation_widgets]
        self.back_button.setText("Reset")

        self.greatwall = GreatWall()
        self.greatwall.set_themed_mnemo(self.theme_combobox.currentText())
        self.greatwall.set_tlp(self.tlp_spinbox.value())
        self.greatwall.set_depth(self.depth_spinbox.value())
        self.greatwall.set_arity(self.arity_spinbox.value())
        self.greatwall.set_sa0(self.password_text.toPlainText())

        self.configure_derivation_widgets()
        [state_widget.show() for state_widget in self.dependent_derivation_widgets]
        self.greatwall.execute_greatwall()
        self.loop_derivation()

    def state4_entered(self):
        pass

    def loop_derivation(self):
        if self.greatwall.is_finished:
            self.next_button.setEnabled(True)

        else:
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
