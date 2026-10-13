import unittest
from hotkeys import parse_hotkey, HotkeyFilter

class Backend:
    def __init__(self): self.keys={}; self.blocked=set()
    def register(self, identifier, modifiers, key):
        if (modifiers,key) in self.blocked: return False
        self.keys[identifier]=(modifiers,key); return True
    def unregister(self, identifier): self.keys.pop(identifier,None)

class HotkeyTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_hotkey('Ctrl+Alt+K'),('Ctrl+Alt+K',3,0x4B))
        self.assertEqual(parse_hotkey('F8'),('F8',0,0x77))
        self.assertEqual(parse_hotkey('Meta+Shift+L')[1:],(12,0x4C))
    def test_reject(self):
        for text in ['', 'L', 'Ctrl+K, Ctrl+C','Ctrl+F12','Ctrl+Escape']:
            with self.assertRaises(ValueError,msg=text): parse_hotkey(text)
    def test_atomic_swap(self):
        backend=Backend(); key=HotkeyFilter(lambda:None,backend=backend)
        original=key.identifier
        backend.blocked.add((3,0x4B))
        self.assertFalse(key.update('Ctrl+Alt+K'))
        self.assertIn(original,backend.keys)
        self.assertEqual(key.text,'Ctrl+Shift+L')
        backend.blocked.clear()
        self.assertTrue(key.update('Ctrl+Alt+K'))
        self.assertNotIn(original,backend.keys)
        self.assertEqual(len(backend.keys),1)
        self.assertTrue(key.update('Ctrl+Alt+K'))
        key.unregister(); self.assertFalse(backend.keys)

if __name__=='__main__': unittest.main()
