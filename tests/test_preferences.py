import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from preferences import Preferences
import preferences

class PreferenceTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            prefs=Preferences();prefs.path=Path(directory)/'settings.json'
            prefs.set('hotkey','Ctrl+Alt+K')
            self.assertEqual(json.loads(prefs.path.read_text())['hotkey'],'Ctrl+Alt+K')
    def test_failed_write_keeps_state(self):
        with tempfile.TemporaryDirectory() as directory:
            prefs=Preferences();prefs.path=Path(directory)/'settings.json';before=dict(prefs.values)
            with patch('preferences.os.replace',side_effect=PermissionError('test')):
                with self.assertRaises(PermissionError):prefs.set('hotkey','Ctrl+Alt+K')
            self.assertEqual(prefs.values,before)

class MigrationTests(unittest.TestCase):
    def test_legacy_settings_read_without_changing_old_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);old=root/'ScreenLink';old.mkdir()
            old_path=old/'settings.json';old_path.write_text(json.dumps({'language':'en','hotkey':'Ctrl+Alt+K','theme':'graphite'}))
            new=root/'Lurivio';new.mkdir()
            with patch.object(preferences,'HOME',new), patch.dict(os.environ,{'LOCALAPPDATA':str(root)}):
                with patch.dict(os.environ,{},clear=False):
                    saved=os.environ.pop('LURIVIO_HOME',None)
                    try:
                        prefs=Preferences()
                        self.assertEqual(prefs.get('language'),'en')
                        self.assertEqual(prefs.get('hotkey'),'Ctrl+Alt+K')
                        self.assertEqual(prefs.get('capture_mode'),'auto')
                        prefs.set('capture_mode','qr')
                        self.assertTrue((new/'settings.json').exists())
                        self.assertNotIn('capture_mode',json.loads(old_path.read_text()))
                    finally:
                        if saved is not None:os.environ['LURIVIO_HOME']=saved
    def test_non_object_settings_do_not_crash(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'settings.json').write_text('[]')
            with patch.object(preferences,'HOME',root):
                self.assertEqual(Preferences().get('capture_mode'),'auto')

if __name__=='__main__':unittest.main()
