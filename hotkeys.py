"""Configurable Windows global hotkey; safe swap preserves a working old shortcut."""
import ctypes
import sys
from PySide6.QtCore import Qt, QTimer, QAbstractNativeEventFilter
from PySide6.QtGui import QKeySequence

DEFAULT_HOTKEY = 'Ctrl+Shift+L'
MOUSE_BUTTONS = {'MouseMiddle', 'MouseX1', 'MouseX2'}

def modifier_bits(modifiers):
    value = modifiers.value if hasattr(modifiers,'value') else int(modifiers)
    result = 0
    for flag, native in [(Qt.KeyboardModifier.ControlModifier,2),(Qt.KeyboardModifier.AltModifier,1),(Qt.KeyboardModifier.ShiftModifier,4),(Qt.KeyboardModifier.MetaModifier,8)]:
        if value & flag.value:result |= native
    return result

def mouse_binding(modifiers, button):
    bits = modifier_bits(modifiers)
    parts = [name for name,bit in [('Ctrl',2),('Alt',1),('Shift',4),('Meta',8)] if bits & bit]
    return parse_binding('+'.join(parts+[button]))[0]

def parse_binding(text):
    parts=text.split('+')
    if parts[-1] not in MOUSE_BUTTONS:
        if 'Mouse' in text:
            raise ValueError('Для мыши доступны колёсико (нажатие) и боковые кнопки X1/X2.')
        return parse_hotkey(text)
    allowed={'Ctrl':2,'Alt':1,'Shift':4,'Meta':8,'Win':8}
    bits=0
    for part in parts[:-1]:
        if part not in allowed or bits & allowed[part]:
            raise ValueError('Некорректное сочетание мыши. Добавьте Ctrl, Alt, Shift или Win.')
        bits |= allowed[part]
    if not bits:
        raise ValueError('Для кнопки мыши нужен Ctrl, Alt, Shift или Win.')
    names=[name for name,bit in [('Ctrl',2),('Alt',1),('Shift',4),('Meta',8)] if bits & bit]
    return '+'.join(names+[parts[-1]]),bits,parts[-1]



def parse_hotkey(text):
    sequence = QKeySequence.fromString(text, QKeySequence.SequenceFormat.PortableText)
    if sequence.isEmpty() or sequence.count() != 1:
        raise ValueError('Выберите одну комбинацию, не последовательность клавиш.')
    combination = sequence[0]
    key = combination.key().value
    modifiers = combination.keyboardModifiers().value
    mapping = [(Qt.KeyboardModifier.ControlModifier, 0x0002),
               (Qt.KeyboardModifier.AltModifier, 0x0001),
               (Qt.KeyboardModifier.ShiftModifier, 0x0004),
               (Qt.KeyboardModifier.MetaModifier, 0x0008)]
    native = 0
    known = 0
    for flag, value in mapping:
        known |= flag.value
        if modifiers & flag.value:
            native |= value
    if modifiers & ~known:
        raise ValueError('Эти модификаторы не поддерживаются.')
    f1, f24 = Qt.Key.Key_F1.value, Qt.Key.Key_F24.value
    if not native and not f1 <= key <= f24:
        raise ValueError('Добавьте Ctrl, Alt, Shift или Win. Без модификатора допускаются только F-клавиши.')
    if Qt.Key.Key_A.value <= key <= Qt.Key.Key_Z.value or Qt.Key.Key_0.value <= key <= Qt.Key.Key_9.value:
        vk = key
    elif f1 <= key <= f24:
        vk = 0x70 + key - f1
    else:
        special = {Qt.Key.Key_Space.value:0x20, Qt.Key.Key_Tab.value:0x09,
                   Qt.Key.Key_Home.value:0x24, Qt.Key.Key_End.value:0x23,
                   Qt.Key.Key_Insert.value:0x2D, Qt.Key.Key_Delete.value:0x2E,
                   Qt.Key.Key_PageUp.value:0x21, Qt.Key.Key_PageDown.value:0x22}
        if key not in special:
            raise ValueError('Используйте букву A–Z, цифру, F-клавишу, Space, Tab, Home, End, Insert, Delete, PgUp или PgDown.')
        vk = special[key]
    if native == 0x0002 and vk in (0x43,0x58,0x56):
        raise ValueError('Ctrl+C, Ctrl+X и Ctrl+V нужны для буфера обмена. Выберите другую комбинацию.')
    if vk == 0x7B:
        raise ValueError('F12 зарезервирована Windows. Выберите другую клавишу.')
    return sequence.toString(QKeySequence.SequenceFormat.PortableText), native, vk


class WindowsBackend:
    def __init__(self):
        self.mouse_hooks={}
        self.pending=[]
        self.timer=QTimer();self.timer.setInterval(20)
        self.timer.timeout.connect(self._dispatch)
        if sys.platform=='win32':
            from ctypes import wintypes
            self.user32=ctypes.WinDLL('user32',use_last_error=True)
            self.kernel32=ctypes.WinDLL('kernel32',use_last_error=True)
            self.proc_type=ctypes.WINFUNCTYPE(ctypes.c_ssize_t,ctypes.c_int,ctypes.c_size_t,ctypes.c_ssize_t)
            self.user32.SetWindowsHookExW.argtypes=[ctypes.c_int,self.proc_type,wintypes.HINSTANCE,wintypes.DWORD]
            self.user32.SetWindowsHookExW.restype=wintypes.HHOOK
            self.user32.CallNextHookEx.argtypes=[wintypes.HHOOK,ctypes.c_int,ctypes.c_size_t,ctypes.c_ssize_t]
            self.user32.CallNextHookEx.restype=ctypes.c_ssize_t
            self.user32.UnhookWindowsHookEx.argtypes=[wintypes.HHOOK];self.user32.UnhookWindowsHookEx.restype=wintypes.BOOL
            self.user32.GetAsyncKeyState.argtypes=[ctypes.c_int];self.user32.GetAsyncKeyState.restype=ctypes.c_short
            self.kernel32.GetModuleHandleW.argtypes=[wintypes.LPCWSTR];self.kernel32.GetModuleHandleW.restype=wintypes.HMODULE
            class MouseInfo(ctypes.Structure):
                _fields_=[('pt',wintypes.POINT),('mouseData',wintypes.DWORD),('flags',wintypes.DWORD),('time',wintypes.DWORD),('dwExtraInfo',ctypes.c_size_t)]
            self.mouse_info=MouseInfo

    def register(self, identifier, modifiers, key):
        if sys.platform != 'win32':return False
        return bool(self.user32.RegisterHotKey(None,identifier,modifiers | 0x4000,key))

    def clear_pending(self):
        self.pending=[]

    def _dispatch(self):
        jobs,self.pending=self.pending,[]
        for identifier,callback in jobs:
            if identifier in self.mouse_hooks:callback()

    def _modifiers(self):
        result=0
        for keys,bit in [((0x11,),2),((0x12,),1),((0x10,),4),((0x5B,0x5C),8)]:
            if any(self.user32.GetAsyncKeyState(key) & 0x8000 for key in keys):result|=bit
        return result

    def register_mouse(self, identifier, modifiers, button, callback, enabled):
        if sys.platform!='win32' or button not in MOUSE_BUTTONS:return False
        held=[False]
        def procedure(code,message,address):
            try:
                if code>=0:
                    info=ctypes.cast(address,ctypes.POINTER(self.mouse_info)).contents
                    # Ignore synthetic/injected mouse input. Only selected button
                    # down/up is consumed; no movement or unrelated clicks are kept.
                    xbutton=(info.mouseData>>16)&0xffff
                    selected=(button=='MouseMiddle' and message in (0x207,0x208)) or (button in ('MouseX1','MouseX2') and message in (0x20B,0x20C) and xbutton==(1 if button=='MouseX1' else 2))
                    if selected and not info.flags & 1:
                        if message in (0x208,0x20C) and held[0]:
                            held[0]=False;return 1
                        if message in (0x207,0x20B) and enabled() and self._modifiers()==modifiers:
                            held[0]=True
                            self.pending.append((identifier,callback))
                            return 1
            except Exception:
                # Never raise across a Windows callback boundary.
                pass
            return self.user32.CallNextHookEx(None,code,message,address)
        proc=self.proc_type(procedure)
        handle=self.user32.SetWindowsHookExW(14,proc,self.kernel32.GetModuleHandleW(None),0)
        if not handle:return False
        self.mouse_hooks[identifier]=(handle,proc)
        if not self.timer.isActive():self.timer.start()
        return True

    def unregister(self, identifier):
        if sys.platform!='win32':return
        item=self.mouse_hooks.pop(identifier,None)
        if item is not None:self.user32.UnhookWindowsHookEx(item[0])
        else:self.user32.UnregisterHotKey(None,identifier)
        self.pending=[job for job in self.pending if job[0]!=identifier]
        if not self.mouse_hooks:self.timer.stop()


class HotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback, text=DEFAULT_HOTKEY, backend=None):
        super().__init__()
        self.callback = callback
        self.backend = backend or WindowsBackend()
        self.identifier = 0x51A2
        self.registered = False
        self.text = ''
        self.error = ''
        self.suspended = False
        self.kind = 'keyboard'
        self._resume_required = False
        self.update(text)

    def update(self, text):
        try:
            canonical, modifiers, key = parse_binding(text)
        except ValueError as error:
            self.error = str(error)
            return False
        if self.registered and canonical == self.text:
            self.error = ''; return True
        next_id = 0x51A3 if self.identifier == 0x51A2 else 0x51A2
        # First reserve the candidate under another ID. If it fails the old key
        # is still live, so applying an occupied shortcut cannot break capture.
        is_mouse = isinstance(key,str)
        if is_mouse:
            success = hasattr(self.backend,'register_mouse') and self.backend.register_mouse(next_id,modifiers,key,self._fire,lambda:not self.suspended and self.registered)
        else:
            success = self.backend.register(next_id, modifiers, key)
        if not success:
            self.error = 'Не удалось включить сочетание мыши. Проверьте доступность глобальных сочетаний в Windows.' if is_mouse else 'Комбинация занята другой программой или зарезервирована системой. Выберите другую.'
            return False
        if self.registered:
            self.backend.unregister(self.identifier)
        self.kind = 'mouse' if is_mouse else 'keyboard'
        self.identifier = next_id; self.registered = True; self.text = canonical; self.error = ''
        return True

    def _fire(self):
        if not self.suspended and self.registered:
            self.callback()

    def set_suspended(self, value):
        value=bool(value)
        if value==self.suspended:return
        self.suspended=value
        if value:
            if hasattr(self.backend,'clear_pending'):self.backend.clear_pending()
            self._resume_required=self.registered
            # A reserved keyboard key may not reach the recorder. Temporarily
            # release it; keep mouse hooks installed but inactive while recording.
            if self.registered and self.kind=='keyboard':
                self.backend.unregister(self.identifier);self.registered=False
        elif self._resume_required and not self.registered:
            self.update(self.text)
        if not value:self._resume_required=False

    def nativeEventFilter(self, event_type, message):
        if sys.platform == 'win32' and self.registered and self.kind=='keyboard':
            from ctypes.wintypes import MSG
            msg = MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == self.identifier:
                QTimer.singleShot(0,self._fire)
                return True, 0
        return False, 0

    def unregister(self):
        if self.registered:
            self.backend.unregister(self.identifier)
            self.registered = False
        self._resume_required = False
