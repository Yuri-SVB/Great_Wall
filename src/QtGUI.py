from PyQt5.QtCore import QStateMachine, QState
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QTabWidget, QLabel, QPushButton, QComboBox,
                             QSpinBox, QLineEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QCheckBox)


class GreatWallQt(QMainWindow):
    def __init__(self):
        super().__init__()

        # Widgets
        self.theme_label = QLabel("Choose Theme", self)
        self.theme_combobox = QComboBox(self)

        self.tlp_label = QLabel("Choose TLP parameter from 1 to 2016", self)
        self.tlp_spinbox = QSpinBox(self)

        self.depth_label = QLabel("Choose tree depth from 1 to 256", self)
        self.depth_spinbox = QSpinBox(self)

        self.arity_label = QLabel("Choose tree arity from 2 to 256", self)
        self.arity_spinbox = QSpinBox(self)

        self.password_label = QLabel(self)
        self.password_text = QTextEdit(self)

        self.back_button = QPushButton("Back", self)
        self.next_button = QPushButton("Next", self)

        # Launch UI
        self.state_machine = QStateMachine()
        self.init_ui()
        self.configure_ui_widgets()
        self.configure_layout()
        self.init_state_machine()

    def init_ui(self):
        self.setWindowTitle("Simple State Machine Example")
        self.setGeometry(300, 200, 400, 300)

        # self.next_button.setGeometry(150, 150, 100, 30)

    def configure_ui_widgets(self):

        self.back_button.setText("Back")
        self.next_button.setText("Next")
        self.theme_label.setText("Choose Theme")
        self.tlp_label.setText("Choose TLP parameter from 1 to 2016")
        self.depth_label.setText("Choose tree depth from 1 to 256")
        self.arity_label.setText("Choose tree arity from 2 to 256")
        self.password_label.setText("Enter Time-Lock Puzzle password:")

        themes = ["Theme0", "Theme1", "Theme2"]
        self.theme_combobox.addItems(themes)
        self.theme_combobox.setCurrentText(themes[0])
        # self.theme_combobox.currentTextChanged.connect(self.set_base_theme)

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

    def configure_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Adding widgets to the main layout
        for widget in [self.theme_label, self.theme_combobox,
                       self.tlp_label, self.tlp_spinbox,
                       self.depth_label, self.depth_spinbox,
                       self.arity_label, self.arity_spinbox,
                       self.password_label, self.password_text]:
            main_layout.addWidget(widget)

        # Horizontal layout for buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch(1)  # Add stretchable space between buttons
        buttons_layout.addWidget(self.next_button)

        # Add the buttons layout to the main layout
        main_layout.addLayout(buttons_layout)

    def init_state_machine(self):

        user_input_state = QState()
        user_input_state.setObjectName('State 1')

        user_dependent_derivation = QState()
        user_dependent_derivation.setObjectName('State 2')

        # Define transitions
        user_input_state.addTransition(self.next_button.clicked, user_dependent_derivation)
        user_dependent_derivation.addTransition(self.back_button.clicked, user_input_state)

        # Add states to the state machine
        self.state_machine.addState(user_input_state)
        self.state_machine.addState(user_dependent_derivation)

        # Set initial state
        self.state_machine.setInitialState(user_input_state)

        # Start the state machine
        self.state_machine.start()

        # Connect states to methods
        user_input_state.entered.connect(self.state1_entered)
        user_dependent_derivation.entered.connect(self.state2_entered)

    def state1_entered(self):
        print('State 1 Entered')
        self.back_button.setText("Exit")
        self.back_button.clicked.connect(self.close_application)
        try:
            self.back_button.clicked.disconnect(self.state1_entered)
        except TypeError:
            pass

    def state2_entered(self):
        print('State 2 Entered')
        self.back_button.setText("Back")
        self.back_button.clicked.connect(self.state1_entered)
        try:
            self.back_button.clicked.disconnect(self.close_application)
        except TypeError:
            pass

    def state3_entered(self):
        print('State 3 Entered')
        self.back_button.setText("Back")
        self.back_button.clicked.connect(self.state1_entered)
        try:
            self.back_button.clicked.disconnect(self.close_application)
        except TypeError:
            pass

    def close_application(self):
        """ Close the parent which exit the application. Bye, come again!"""
        self.close()


def main():
    app = QApplication([])
    window = GreatWallQt()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
