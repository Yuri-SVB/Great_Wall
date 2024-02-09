import sys
import unittest
from PyQt5.QtCore import QRect, QState, QCoreApplication, Qt
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

    def test_formosa_BIP39_happy_path(self):
        # test_init_ui
        self.assertEqual("Great Wall Sample", self.greatWallGui.windowTitle())
        self.assertEqual(QRect(100, 100, 500, 500), self.greatWallGui.geometry())

        # test_init_main_app_state
        self.assertEqual(len(self.greatWallGui.error_states), 1)
        self.assertEqual(len(self.greatWallGui.main_states), 5 + len(self.greatWallGui.error_states))
        main_gui_state_machine = self.greatWallGui.main_gui_sm
        while not main_gui_state_machine.isRunning():
            QCoreApplication.processEvents()

        # test_input_state1_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("User Inputs", current_state.objectName())

        self.assertTrue(self.greatWallGui.next_button.isEnabled())
        self.assertEqual("Next", self.greatWallGui.next_button.text())
        self.assertTrue(self.greatWallGui.back_button.isEnabled())
        self.assertEqual("Exit", self.greatWallGui.back_button.text())
        self.assertEqual("", self.greatWallGui.result_hash.text())
        self.assertFalse(self.greatWallGui.loop_dynamic_sm.isRunning())
        # TODO review Instance attribute greatwall_thread defined outside __init__
        # self.assertFalse(self.greatWallGui.greatwall_thread.isRunning())

        # default intput values
        self.assertEqual("Tacit knowledge type", self.greatWallGui.tacit_knowledge_label.text())
        self.assertEqual("Fractal", self.greatWallGui.tacit_knowledge_combobox.currentText())
        self.assertEqual("Fractal function type", self.greatWallGui.fractal_function_label.text())
        self.assertEqual("mandelbrot", self.greatWallGui.fractal_function_combobox.currentText())

        self.assertEqual("Choose Theme", self.greatWallGui.theme_label.text())
        self.assertEqual("BIP39", self.greatWallGui.theme_combobox.currentText())
        self.assertEqual("Choose TLP parameter from 1 to 2016", self.greatWallGui.tlp_label.text())
        self.assertEqual("1", self.greatWallGui.tlp_spinbox.text())
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

        QTest.mouseClick(self.greatWallGui.tlp_spinbox, Qt.LeftButton)
        QTest.keyClick(self.greatWallGui.tlp_spinbox, Qt.Key_Delete)
        QTest.keyClicks(self.greatWallGui.tlp_spinbox, input_tpl)

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
        self.assertEqual("1", self.greatWallGui.tlp_spinbox.text())
        self.assertEqual("2", self.greatWallGui.depth_spinbox.text(), )
        self.assertEqual("4", self.greatWallGui.arity_spinbox.text())
        self.assertEqual("bunker casino bulk hawk defy egg ignore plate view problem attract bridge truth fluid hub",
                         self.greatWallGui.password_text.toPlainText())

        self.greatWallGui.next_button.click()

        # test_confirm_state2_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("User Confirm", current_state.objectName())

        self.assertEqual("Confirm your values", self.greatWallGui.confirm_label.text())
        self.assertEqual("Theme\nBIP39", self.greatWallGui.theme_confirm.text())
        self.assertEqual("TLP parameter\n1", self.greatWallGui.tlp_confirm.text())
        self.assertEqual("Tree depth\n2", self.greatWallGui.depth_confirm.text())
        self.assertEqual("Tree arity\n4", self.greatWallGui.arity_confirm.text())
        self.assertEqual(
            "Time-Lock Puzzle password\n"
            "bunker casino bulk hawk defy egg ignore plate view problem attract bridge truth fluid hub",
            self.greatWallGui.password_confirm.text())

        self.assertTrue(self.greatWallGui.next_button.isEnabled())
        self.assertEqual("Next", self.greatWallGui.next_button.text())
        self.assertTrue(self.greatWallGui.back_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.back_button.text())

        self.greatWallGui.next_button.click()

        # test_derivation_state3_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("Dependent Derivation", current_state.objectName())

        self.assertEqual("Wait the derivation to finish\n"
                         "This will take some time",
                         self.greatWallGui.wait_derive_label.text())

        self.assertFalse(self.greatWallGui.next_button.isEnabled())
        self.assertTrue(self.greatWallGui.back_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.back_button.text())

        QTest.qWait(12000)
        QCoreApplication.processEvents()

        # test_loop_state_0_entered
        self.assertFalse(self.greatWallGui.next_button.isEnabled())
        self.assertTrue(self.greatWallGui.back_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.back_button.text())

        self.assertEqual("Level 0 of 2", self.greatWallGui.level_label.text())
        self.assertEqual("Select option", self.greatWallGui.select_label.text())

        target_button = find_button_by_text(self, "bicycle number sun")
        target_button.click()
        QTest.qWait(100)

        # test_loop_state_1_entered
        self.assertFalse(self.greatWallGui.next_button.isEnabled())
        self.assertTrue(self.greatWallGui.back_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.back_button.text())

        self.assertEqual("Level 1 of 2", self.greatWallGui.level_label.text())
        self.assertEqual("Select option", self.greatWallGui.select_label.text())

        target_button = find_button_by_text(self, "goat wire matter")
        target_button.click()
        QTest.qWait(100)

        # test_loop_state_2_entered
        self.assertTrue(self.greatWallGui.next_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.back_button.text())
        self.assertTrue(self.greatWallGui.back_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.back_button.text())

        self.assertEqual("Level 2 of 2", self.greatWallGui.level_label.text())
        self.assertEqual("Do you confirm this result?", self.greatWallGui.confirm_result_label.text())

        self.greatWallGui.next_button.click()

        # test_output_state4_entered
        current_state = next(iter(main_gui_state_machine.configuration()))
        self.assertIsInstance(current_state, QState)
        self.assertEqual("Output", current_state.objectName())

        self.assertEqual("This is the result output:", self.greatWallGui.finish_output_label.text())

        self.assertFalse(self.greatWallGui.next_button.isEnabled())
        self.assertTrue(self.greatWallGui.back_button.isEnabled())
        self.assertEqual("Reset", self.greatWallGui.back_button.text())

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
            self.greatWallGui.finish_text.toPlainText())


def find_button_by_text(self, target_text):
    target_button = None
    for button, widgets in self.greatWallGui.selection_buttons:
        if target_text in button.text():
            target_button = button
    return target_button


if __name__ == '__main__':
    unittest.main()
