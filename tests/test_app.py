"""GUI logic tests: no real Win32 calls, local clipboard only."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app import MainWindow
from preferences import Preferences
from i18n import manager

APP=QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)

class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        prefs=Preferences();prefs.path=Path(self.tmp.name)/'settings.json'
        prefs.values.update(language='ru',theme='aurora',auto_copy=True,capture_mode='auto')
        self.window=MainWindow(prefs,start_worker=False)
        self.window.tray_available=True
        APP.clipboard().setText('untouched')
    def tearDown(self):
        self.window.tray.hide();self.window.hide();self.window.deleteLater()
        APP.processEvents();self.tmp.cleanup()
    def result(self,values,mode='QR'):
        self.window.on_result(values,'\n\n'.join(values),1.0,.1,mode)
    def test_qr_url_auto_copies_exactly(self):
        value='https://example.com/Guide?x=1&y=2#test.'
        self.result([value]);self.assertEqual(APP.clipboard().text(),value)
        self.assertTrue(self.window.last_is_qr)
    def test_non_url_requires_manual_copy(self):
        value='WIFI:T:WPA;S:Home;P:test-only;;'
        self.result([value]);self.assertEqual(APP.clipboard().text(),'untouched')
        self.assertTrue(self.window.copy_url(notify=False));self.assertEqual(APP.clipboard().text(),value)
    def test_multiline_text_survives_language_switch(self):
        value='Привет\nКонтакт\n+123456789'
        self.result([value]);self.window.language_combo.setCurrentIndex(1)
        self.assertEqual(self.window.qr_edit.toPlainText(),value)
        self.assertEqual(self.window.nav[2].text(),'Settings')
        self.assertEqual(self.window.mode_combo.itemText(0),'Auto: URLs and QR codes')
        self.window.copy_url(notify=False);self.assertEqual(APP.clipboard().text(),value)
    def test_multiple_requires_choice(self):
        self.result(['https://example.com/a','https://example.com/b'])
        self.assertEqual(APP.clipboard().text(),'untouched')
        self.window.choices.setCurrentIndex(1);self.window.copy_url(notify=False)
        self.assertEqual(APP.clipboard().text(),'https://example.com/b')
    def test_qr_scheme_is_not_auto_copied(self):
        self.result(['javascript:alert(1)'])
        self.assertEqual(APP.clipboard().text(),'untouched')
    def test_switch_to_ocr_clears_qr_state(self):
        self.result(['hello'])
        self.result(['https://example.org/a'],'строка')
        self.assertFalse(self.window.last_is_qr)
        self.assertEqual(APP.clipboard().text(),'https://example.org/a')
        self.assertEqual(self.window.qr_edit.toPlainText(),'')
    def test_mode_saved_and_native_flags(self):
        self.window.mode_combo.setCurrentIndex(2)
        self.assertEqual(self.window.prefs.get('capture_mode'),'qr')
        flags=self.window.windowFlags()
        self.assertFalse(flags & Qt.WindowType.FramelessWindowHint)
        self.assertTrue(flags & Qt.WindowType.WindowCloseButtonHint)
    def test_blank_qr_keeps_clipboard(self):
        self.result([])
        self.assertEqual(APP.clipboard().text(),'untouched')
        self.assertFalse(self.window.copy_button.isEnabled())

if __name__=='__main__':unittest.main()
