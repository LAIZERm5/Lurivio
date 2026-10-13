"""User-scoped preferences; no screenshots or URL history are persisted."""
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULTS = dict(theme='aurora', auto_copy=True, fast=True, close_to_tray=True,
                start_hidden=False, notifications=True, hotkey='Ctrl+Shift+L', language='ru', capture_mode='auto')
HOME = Path(os.environ.get('LURIVIO_HOME') or
            (str(Path(os.environ['LOCALAPPDATA']) / 'Lurivio') if os.environ.get('LOCALAPPDATA')
             else str(Path.home() / '.lurivio')))
HOME.mkdir(parents=True, exist_ok=True)

class Preferences:
    def __init__(self):
        self.path = HOME / 'settings.json'
        self.values = dict(DEFAULTS)
        try:
            source = self.path
            if not source.exists() and not os.environ.get('LURIVIO_HOME'):
                legacy_home = Path(os.environ['LOCALAPPDATA']) / 'ScreenLink' if os.environ.get('LOCALAPPDATA') else Path.home() / '.screenlink'
                source = legacy_home / 'settings.json'
            data = json.loads(source.read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                return
            for key, default in DEFAULTS.items():
                if key in data and type(data[key]) is type(default):
                    self.values[key] = data[key]
        except (OSError, ValueError, TypeError):
            pass

    def get(self, key):
        return self.values[key]

    def set(self, key, value):
        values = dict(self.values)
        values[key] = value
        tmp = self.path.with_suffix('.tmp')
        tmp.write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(tmp, self.path)
        self.values = values


def startup_command():
    if getattr(sys, 'frozen', False):
        args = [sys.executable, '--tray']
    else:
        executable = Path(sys.executable)
        windowless = executable.with_name('pythonw.exe')
        args = [str(windowless if windowless.exists() else executable),
                str(Path(__file__).resolve().with_name('Launch.py')), '--tray']
    return subprocess.list2cmdline(args)


def startup_enabled():
    if sys.platform != 'win32':
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
            value, _ = winreg.QueryValueEx(key, 'Lurivio')
            return value == startup_command()
    except OSError:
        return False


def set_startup(enabled):
    if sys.platform != 'win32':
        raise OSError('Автозапуск доступен только на Windows.')
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
        if enabled:
            command = startup_command()
            if len(command) > 260:
                raise OSError('Путь слишком длинный для автозапуска Windows. Переместите Lurivio в папку с более коротким путём.')
            winreg.SetValueEx(key, 'Lurivio', 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, 'Lurivio')
            except FileNotFoundError:
                pass
