from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtCore import QStateMachine, QState


class GreatWallQt(QMainWindow):
    def __init__(self):
        super().__init__()

        self.button = QPushButton('Click Me', self)
        self.state_machine = QStateMachine()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Simple State Machine Example')
        self.setGeometry(300, 200, 400, 300)

        self.button.setGeometry(150, 150, 100, 30)

        self.init_state_machine()

    def init_state_machine(self):

        user_input_state = QState()
        user_input_state.setObjectName('State 1')

        user_dependent_derivation = QState()
        user_dependent_derivation.setObjectName('State 2')

        # Define transitions
        user_input_state.addTransition(self.button.clicked, user_dependent_derivation)
        user_dependent_derivation.addTransition(self.button.clicked, user_input_state)

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
        self.button.setText('Go to State 2')

    def state2_entered(self):
        print('State 2 Entered')
        self.button.setText('Go to State 1')


def main():
    app = QApplication([])
    window = GreatWallQt()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
