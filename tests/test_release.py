"""Keep tag/build metadata synchronized with the displayed app version."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ReleaseMetadataTests(unittest.TestCase):
    def test_version_in_app_and_translation(self):
        version=(ROOT/'VERSION').read_text().strip()
        self.assertIn('Lurivio '+version,(ROOT/'app.py').read_text())
        self.assertIn('Версия '+version,(ROOT/'i18n.py').read_text())
    def test_windows_resource_version(self):
        version=(ROOT/'VERSION').read_text().strip()
        resource=(ROOT/'tools/windows_version.txt').read_text()
        self.assertIn("StringStruct('ProductVersion', '"+version+"')",resource)
        self.assertIn('filevers='+str(tuple(int(x) for x in version.split('.'))+(0,)),resource)
    def test_release_stays_draft_and_validates_tag(self):
        workflow=(ROOT/'.github/workflows/windows.yml').read_text()
        self.assertIn('--draft --prerelease',workflow)
        self.assertIn('Tag must match VERSION',workflow)
        self.assertIn('Refusing to replace assets of a published release',workflow)
if __name__=='__main__':unittest.main()
