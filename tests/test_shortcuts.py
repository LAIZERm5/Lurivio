import unittest
from unittest.mock import Mock
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QDialog, QSystemTrayIcon
from PySide6.QtTest import QTest
from hotkeys import parse_binding,mouse_binding,HotkeyFilter
from shortcut_recorder import RecordingDialog,ShortcutRecorder
from test_hotkeys import Backend
from app import MainWindow
from preferences import Preferences

APP=QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)

class MouseBackend(Backend):
    def __init__(self):super().__init__();self.enabled={}
    def register_mouse(self,identifier,modifiers,button,callback,enabled):
        if (modifiers,button) in self.blocked:return False
        self.keys[identifier]=(modifiers,button);self.enabled[identifier]=(callback,enabled);return True
    def unregister(self,identifier):super().unregister(identifier);self.enabled.pop(identifier,None)

class BindingTests(unittest.TestCase):
    def test_mouse_parse_and_normalize(self):
        self.assertEqual(parse_binding('Alt+Ctrl+MouseMiddle'),('Ctrl+Alt+MouseMiddle',3,'MouseMiddle'))
        self.assertEqual(parse_binding('Win+MouseX2'),('Meta+MouseX2',8,'MouseX2'))
    def test_mouse_requires_modifier(self):
        for value in ['MouseMiddle','Ctrl+MouseLeft','Ctrl+Ctrl+MouseX1','Alt+Unknown+MouseX2']:
            with self.assertRaises(ValueError):parse_binding(value)
    def test_keyboard_unchanged(self):
        self.assertEqual(parse_binding('Ctrl+Alt+K'),('Ctrl+Alt+K',3,0x4b))
    def test_switch_keyboard_mouse_keyboard(self):
        backend=MouseBackend();hk=HotkeyFilter(lambda:None,backend=backend)
        self.assertTrue(hk.update('Ctrl+Alt+MouseMiddle'));self.assertEqual(hk.kind,'mouse')
        self.assertEqual(len(backend.keys),1)
        self.assertTrue(hk.update('F8'));self.assertEqual(hk.kind,'keyboard');self.assertFalse(backend.enabled)
        hk.unregister();self.assertFalse(backend.keys)
    def test_failed_mouse_preserves_keyboard(self):
        backend=MouseBackend();hk=HotkeyFilter(lambda:None,backend=backend)
        backend.blocked.add((3,'MouseX1'))
        self.assertFalse(hk.update('Ctrl+Alt+MouseX1'));self.assertTrue(hk.registered)
        self.assertEqual(hk.text,'Ctrl+Shift+L');hk.unregister()
    def test_suspend_keyboard_and_resume(self):
        backend=MouseBackend();callback=Mock();hk=HotkeyFilter(callback,backend=backend)
        hk.set_suspended(True);self.assertFalse(backend.keys);hk._fire();callback.assert_not_called()
        hk.set_suspended(False);self.assertTrue(hk.registered);hk._fire();callback.assert_called_once();hk.unregister()
    def test_mouse_suspended_not_consumed(self):
        backend=MouseBackend();hk=HotkeyFilter(lambda:None,backend=backend)
        hk.update('Ctrl+MouseX2');_,enabled=backend.enabled[hk.identifier]
        self.assertTrue(enabled());hk.set_suspended(True);self.assertFalse(enabled())
        hk.set_suspended(False);self.assertTrue(enabled());hk.unregister()
    def test_resume_conflict_reported(self):
        backend=MouseBackend();hk=HotkeyFilter(lambda:None,backend=backend)
        hk.set_suspended(True);backend.blocked.add((6,0x4c));hk.set_suspended(False)
        self.assertFalse(hk.registered);self.assertTrue(hk.error);hk.unregister()

class RecorderTests(unittest.TestCase):
    def setUp(self):
        self.dialog=RecordingDialog();self.dialog.show();APP.processEvents()
    def tearDown(self):
        self.dialog.reject();self.dialog.deleteLater();APP.processEvents()
    def test_actual_keypress(self):
        QTest.keyClick(self.dialog,Qt.Key.Key_K,Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.AltModifier)
        self.assertEqual(self.dialog.value,'Ctrl+Alt+K');self.assertEqual(self.dialog.result(),QDialog.DialogCode.Accepted)
    def test_actual_mouse_press(self):
        QTest.mouseClick(self.dialog,Qt.MouseButton.MiddleButton,Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.AltModifier)
        self.assertEqual(self.dialog.value,'Ctrl+Alt+MouseMiddle')
    def test_side_button(self):
        QTest.mouseClick(self.dialog,Qt.MouseButton.BackButton,Qt.KeyboardModifier.ShiftModifier)
        self.assertEqual(self.dialog.value,'Shift+MouseX1')
    def test_bare_mouse_rejected(self):
        QTest.mouseClick(self.dialog,Qt.MouseButton.MiddleButton)
        self.assertIsNone(self.dialog.value);self.assertTrue(self.dialog.isVisible())
    def test_escape_cancels(self):
        QTest.keyClick(self.dialog,Qt.Key.Key_Escape)
        self.assertIsNone(self.dialog.value);self.assertEqual(self.dialog.result(),QDialog.DialogCode.Rejected)
    def test_readonly_field_opens_recorder(self):
        self.dialog.reject()
        field=ShortcutRecorder('Ctrl+Shift+L');field.show();APP.processEvents()
        started=Mock();finished=Mock();field.recordingStarted.connect(started);field.recordingFinished.connect(finished)
        QTimer.singleShot(50,lambda:QTest.keyClick(APP.activeModalWidget(),Qt.Key.Key_M,Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.ShiftModifier))
        QTest.mouseClick(field,Qt.MouseButton.LeftButton)
        self.assertTrue(field.isReadOnly());self.assertEqual(field.binding(),'Ctrl+Shift+M')
        started.assert_called_once();finished.assert_called_once();field.deleteLater();APP.processEvents()

class TrayTests(unittest.TestCase):
    def setUp(self):
        self.window=MainWindow(Preferences(),start_worker=False)
        self.window.begin_capture=Mock();self.window.tray_capture_timer.timeout.disconnect()
        self.window.tray_capture_timer.timeout.connect(self.window.begin_capture)
        self.window.show_window=Mock()
    def tearDown(self):
        self.window.tray_capture_timer.stop();self.window.tray.hide();self.window.hide();self.window.deleteLater();APP.processEvents()
    def test_single_left_click_captures(self):
        self.window.tray_activated(QSystemTrayIcon.ActivationReason.Trigger)
        QTest.qWait(250);self.window.begin_capture.assert_called_once();self.window.show_window.assert_not_called()
    def test_double_click_coalesces(self):
        self.window.tray_activated(QSystemTrayIcon.ActivationReason.Trigger)
        self.window.tray_activated(QSystemTrayIcon.ActivationReason.DoubleClick)
        QTest.qWait(250);self.window.begin_capture.assert_called_once()
    def test_right_click_keeps_menu(self):
        self.window.tray_activated(QSystemTrayIcon.ActivationReason.Context)
        QTest.qWait(250);self.window.begin_capture.assert_not_called()
    def test_recording_blocks_capture(self):
        self.window.shortcut_recording=True
        self.window.tray_activated(QSystemTrayIcon.ActivationReason.Trigger)
        QTest.qWait(250);self.window.begin_capture.assert_not_called()
    def test_busy_blocks_capture(self):
        self.window.busy=True;self.window.tray_activated(QSystemTrayIcon.ActivationReason.Trigger)
        self.assertFalse(self.window.tray_capture_timer.isActive())

if __name__=='__main__':unittest.main()
