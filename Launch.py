"""Windowless launcher with a visible error dialog if startup fails."""
import ctypes
import logging
import runpy
import sys
from pathlib import Path

if __name__ == '__main__':
    try:
        runpy.run_path(str(Path(__file__).resolve().with_name('app.py')), run_name='__main__')
    except SystemExit:
        raise
    except Exception:
        try:
            from preferences import HOME, Preferences
            from i18n import manager, tr
            manager.set_language(Preferences().get('language'))
            logging.basicConfig(filename=HOME / 'errors.log', level=logging.ERROR)
            logging.exception('Application startup failed')
            message = tr('Lurivio не запустился. Запустите Diagnose.bat для проверки.')+tr('\nЖурнал: ')+str(HOME / 'errors.log')
        except Exception:
            try:
                from preferences import Preferences
                english = Preferences().get('language') == 'en'
            except Exception:
                english = False
            message = 'Lurivio could not start. Run Diagnose.bat to troubleshoot.' if english else 'Lurivio не запустился. Запустите Diagnose.bat для проверки.'
        if sys.platform=='win32':
            ctypes.windll.user32.MessageBoxW(None,message,'Lurivio',0x10)
        else:
            print(message,file=sys.stderr)
        sys.exit(1)
