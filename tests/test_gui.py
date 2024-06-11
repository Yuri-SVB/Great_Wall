import sys
import unittest

from PyQt5.QtCore import QState, QCoreApplication, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from gui import GreatWallGui
from resources.greatwall import GreatWall

app = QApplication(sys.argv)


class TestGreatWallGui(unittest.TestCase):
    def setUp(self):
        self.greatWallGui = GreatWallGui()
        self.greatWallGui.greatwall = GreatWall()

    def tearDown(self):
        self.greatWallGui.close()

    def test_formosa_BIP39_integration(self):
        # test_init_main_app_state
        main_gui_state_machine = self.greatWallGui.main_gui_state
        while not main_gui_state_machine.isRunning():
            QCoreApplication.processEvents()

        # test_input_state1_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("User Inputs", current_state.objectName())

        self.assertTrue(self.greatWallGui.input_next_navigation_button.isEnabled())
        self.assertEqual("Next", self.greatWallGui.input_next_navigation_button.text())
        self.assertTrue(self.greatWallGui.input_exit_navigation_button.isEnabled())
        self.assertEqual("Exit", self.greatWallGui.input_exit_navigation_button.text())
        self.assertEqual("", self.greatWallGui.result_finish_output_text.toPlainText())

        # default intput values
        self.assertEqual("Tacit knowledge type", self.greatWallGui.tacit_knowledge_label.text())
        self.assertEqual("Fractal", self.greatWallGui.tacit_knowledge_combobox.currentText())
        self.assertEqual("Fractal function type", self.greatWallGui.fractal_function_label.text())
        self.assertEqual("mandelbrot", self.greatWallGui.fractal_function_combobox.currentText())

        self.assertEqual("Choose Theme", self.greatWallGui.theme_label.text())
        self.assertEqual("BIP39", self.greatWallGui.theme_combobox.currentText())
        self.assertEqual("Choose TLP parameter from 1 to 2016", self.greatWallGui.tlp_param_label.text())
        self.assertEqual("1", self.greatWallGui.tlp_param_spinbox.text())
        self.assertEqual("Choose tree depth from 1 to 256", self.greatWallGui.depth_label.text())
        self.assertEqual("1", self.greatWallGui.depth_spinbox.text(), )
        self.assertEqual("Choose tree arity from 2 to 256", self.greatWallGui.arity_label.text())
        self.assertEqual("2", self.greatWallGui.arity_spinbox.text())
        self.assertEqual("Enter Time-Lock Puzzle password:", self.greatWallGui.password_label.text())
        self.assertEqual("", self.greatWallGui.password_text.toPlainText())

        # given
        input_tacit_knowledge = "Formosa"
        input_theme = "BIP39"
        input_tpl = "1"
        input_depth = "2"
        input_arity = "4"
        input_password = "bunker casino bulk hawk defy egg ignore plate view problem attract bridge truth fluid hub"

        # when
        QTest.mouseClick(self.greatWallGui.tacit_knowledge_combobox, Qt.LeftButton)
        QTest.keyClicks(self.greatWallGui.tacit_knowledge_combobox, input_tacit_knowledge)

        index = self.greatWallGui.theme_combobox.findText(input_theme)
        self.greatWallGui.theme_combobox.setCurrentIndex(index)

        QTest.mouseClick(self.greatWallGui.tlp_param_spinbox, Qt.LeftButton)
        QTest.keyClick(self.greatWallGui.tlp_param_spinbox, Qt.Key_Delete)
        QTest.keyClicks(self.greatWallGui.tlp_param_spinbox, input_tpl)

        QTest.mouseClick(self.greatWallGui.depth_spinbox, Qt.LeftButton)
        QTest.keyClick(self.greatWallGui.depth_spinbox, Qt.Key_Delete)
        QTest.keyClicks(self.greatWallGui.depth_spinbox, input_depth)

        QTest.mouseClick(self.greatWallGui.arity_spinbox, Qt.LeftButton)
        QTest.keyClick(self.greatWallGui.arity_spinbox, Qt.Key_Delete)
        QTest.keyClicks(self.greatWallGui.arity_spinbox, input_arity)

        QTest.mouseClick(self.greatWallGui.password_text, Qt.LeftButton)
        QTest.keyClicks(self.greatWallGui.password_text, input_password)

        self.assertEqual("Formosa", self.greatWallGui.tacit_knowledge_combobox.currentText())
        self.assertEqual("BIP39", self.greatWallGui.theme_combobox.currentText())
        self.assertEqual("1", self.greatWallGui.tlp_param_spinbox.text())
        self.assertEqual("2", self.greatWallGui.depth_spinbox.text(), )
        self.assertEqual("4", self.greatWallGui.arity_spinbox.text())
        self.assertEqual("bunker casino bulk hawk defy egg ignore plate view problem attract bridge truth fluid hub",
                         self.greatWallGui.password_text.toPlainText())

        self.greatWallGui.input_next_navigation_button.click()

        # test_confirm_state2_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("User Inputs Confirmation", current_state.objectName())

        self.assertEqual("Confirm your values", self.greatWallGui.input_confirmation_label.text())
        self.assertEqual("Theme\nBIP39", self.greatWallGui.input_confirmation_theme_label.text())
        self.assertEqual("Choose TLP parameter from 1 to 2016", self.greatWallGui.tlp_param_label.text())
        self.assertEqual("Choose tree depth from 1 to 256", self.greatWallGui.depth_label.text())
        self.assertEqual("Choose tree arity from 2 to 256", self.greatWallGui.arity_label.text())
        self.assertEqual(
            "Enter Time-Lock Puzzle password:",
            self.greatWallGui.password_label.text())

        self.assertTrue(self.greatWallGui.input_confirmation_next_navigation_button.isEnabled())
        self.assertEqual("Next", self.greatWallGui.input_confirmation_next_navigation_button.text())
        self.assertTrue(self.greatWallGui.input_confirmation_back_navigation_button.isEnabled())
        self.assertEqual("Back", self.greatWallGui.input_confirmation_back_navigation_button.text())

        self.greatWallGui.input_confirmation_next_navigation_button.click()

        # test_derivation_state3_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("Derivation", current_state.objectName())

        self.assertEqual("Please, wait until the derivation finish!\n"
                         "Be patient, this will take some time...",
                         self.greatWallGui.waiting_derivation_label.text())

        self.assertEqual("Next", self.greatWallGui.waiting_next_navigation_button.text())
        self.assertFalse(self.greatWallGui.waiting_next_navigation_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.waiting_reset_navigation_button.text())
        self.assertTrue(self.greatWallGui.waiting_reset_navigation_button.isEnabled())

        QTest.qWait(10000)
        QCoreApplication.processEvents()

        # test_derivation_loop_0_entered
        self.assertEqual("Next", self.greatWallGui.selecting_next_navigation_button.text())
        self.assertFalse(self.greatWallGui.selecting_next_navigation_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.selecting_reset_navigation_button.text())
        self.assertTrue(self.greatWallGui.selecting_reset_navigation_button.isEnabled())

        self.assertEqual("Level 0 of 2", self.greatWallGui.selecting_derivation_current_level_label.text())
        self.assertEqual("Select Option:", self.greatWallGui.selecting_derivation_level_label.text())

        target_button = find_button_by_text(self, "bicycle number sun")
        target_button.click()
        QTest.qWait(100)

        # test_derivation_loop_1_entered
        self.assertFalse(self.greatWallGui.selecting_next_navigation_button.isEnabled())
        self.assertTrue(self.greatWallGui.selecting_reset_navigation_button.isEnabled())

        self.assertEqual("Level 1 of 2", self.greatWallGui.selecting_derivation_current_level_label.text())
        self.assertEqual("Select Option:", self.greatWallGui.selecting_derivation_level_label.text())

        target_button = find_button_by_text(self, "goat wire matter")
        target_button.click()
        QTest.qWait(100)

        # test_derivation_confirm_result_entered
        self.assertEqual("Next", self.greatWallGui.result_confirmation_next_navigation_button.text())
        self.assertTrue(self.greatWallGui.result_confirmation_next_navigation_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.result_confirmation_reset_navigation_button.text())
        self.assertTrue(self.greatWallGui.result_confirmation_reset_navigation_button.isEnabled())

        self.assertEqual("Level 2 of 2", self.greatWallGui.result_confirmation_current_level_label.text())
        self.assertEqual("Do you confirm this result?", self.greatWallGui.result_confirmation_confirm_question_label.text())

        self.greatWallGui.result_confirmation_next_navigation_button.click()

        # test_output_state4_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("Result", current_state.objectName())

        self.assertEqual("This is the result output:", self.greatWallGui.result_finish_message_label.text())

        self.assertTrue(self.greatWallGui.result_reset_navigation_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.result_reset_navigation_button.text())

        # then
        self.assertEqual(
            "ffaadb1759c0b0d2a162be2fdab6ae32"
            "44625435e30869577eb4281e43bed525"
            "f9d2fd46b3762e602ba0292443cd39a0"
            "e5463f6fb34fb64d2b32bb2242b96023"
            "943161856d0a33f88b933010cfb34c20"
            "7d676088ef0ec531afccbc58223f8a10"
            "b4519a61e5b500b763d07f3c3aa56e5e"
            "98d759211fbee13b36d80707c6893e15",
            self.greatWallGui.result_finish_output_text.toPlainText())


def find_button_by_text(self, target_text):
    target_button = None
    for idx, selection_widget in enumerate(
                self.greatWallGui.selecting_derivation_options_widgets_list
            ):
        if target_text in selection_widget.text():
            target_button = selection_widget
    return target_button


if __name__ == '__main__':
    unittest.main()
