"""Lurivio 0.6.1 — Windows tray-first, local OCR link capture."""
import ctypes
import hashlib
import logging
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QTimer, QUrl
from PySide6.QtGui import QColor, QPainter, QPixmap, QIcon, QGuiApplication, QCursor, QDesktopServices, QPalette, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QComboBox, QCheckBox, QPlainTextEdit, QFrame, QScrollArea,
    QLayout, QStackedWidget, QButtonGroup, QSystemTrayIcon, QMenu, QSizeGrip, QMessageBox, QKeySequenceEdit,
)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from preferences import Preferences, HOME, set_startup, startup_enabled
from themes import THEMES, Background, Swatch, stylesheet, ThemedCheckBox as QCheckBox
from capture import RegionOverlay
from hotkeys import HotkeyFilter, DEFAULT_HOTKEY, parse_hotkey, parse_binding
from shortcut_recorder import ShortcutRecorder
from ocr_worker import OcrWorker
from links import valid_url
from i18n import manager as language_manager, tr, Label as QLabel, Button as QPushButton, CheckBox as QCheckBox, LineEdit as QLineEdit

logging.basicConfig(filename=HOME / 'errors.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s')


def label(text, name=None, wrap=False):
    widget = QLabel(text)
    if name:
        widget.setObjectName(name)
    widget.setWordWrap(wrap)
    return widget


def panel():
    frame = QFrame(); frame.setObjectName('panel')
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(24, 22, 24, 22); layout.setSpacing(16)
    return frame, layout


def app_icon():
    pm = QPixmap(64,64); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor('#DE6264')); p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(2,2,60,60,17,17)
    p.setPen(QColor('white')); font = p.font(); font.setBold(True); font.setPixelSize(39); p.setFont(font)
    p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, 'L'); p.end()
    return QIcon(pm)


class TitleBar(QWidget):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.window().windowHandle():
            self.window().windowHandle().startSystemMove()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().toggle_maximize()


class MainWindow(QMainWindow):
    def __init__(self, preferences=None, start_worker=True):
        super().__init__()
        self.prefs = preferences or Preferences()
        if self.prefs.get('theme') not in THEMES:
            self.prefs.values['theme'] = 'aurora'
        language_manager.set_language(self.prefs.get('language'))
        self.setWindowTitle('Lurivio 0.6.1')
        self.setWindowIcon(app_icon())
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)
        self.resize(1040, 860); self.setMinimumSize(940, 680)
        self.last_is_qr = False; self.busy = False; self.capturing = False; self.ocr_ready = False
        self.shortcut_recording = False; self.quitting = False; self.capture_hwnd = None; self.overlay = None; self.hotkey = None
        self.tray_available = QSystemTrayIcon.isSystemTrayAvailable()
        self.worker = OcrWorker()
        self.worker.ready.connect(self.on_ready)
        self.worker.result.connect(self.on_result)
        self.worker.failed.connect(self.on_error)
        self.worker.finished.connect(self.on_worker_stopped)
        self.build_ui()
        self.build_tray()
        language_manager.changed.connect(self.retranslate_auxiliary)
        self.retranslate_auxiliary()
        self.apply_theme(self.prefs.get('theme'), save=False)
        if start_worker:
            self.worker.start()

    def build_ui(self):
        wrapper = QWidget()
        self.setCentralWidget(wrapper)
        outside = QVBoxLayout(wrapper); outside.setContentsMargins(8,8,8,8)
        self.shell = Background(); outside.addWidget(self.shell)
        shell_layout = QHBoxLayout(self.shell); shell_layout.setContentsMargins(0,0,0,0); shell_layout.setSpacing(0)
        side = QFrame(); side.setObjectName('sidebar'); side.setFixedWidth(214)
        side_layout = QVBoxLayout(side); side_layout.setContentsMargins(20,24,20,20); side_layout.setSpacing(12)
        brand = QHBoxLayout(); brand.setSpacing(10)
        logo = label('L'); logo.setFixedSize(34,34)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet('background:#DE6264;color:white;border-radius:10px;font-weight:700;font-size:22px;')
        brand.addWidget(logo); brand.addWidget(label('Lurivio','brand')); side_layout.addLayout(brand)
        side_layout.addWidget(label('LINK CAPTURE STUDIO','micro'))
        side_layout.addSpacing(30)
        side_layout.addWidget(label('РАБОЧЕЕ ПРОСТРАНСТВО','micro'))
        self.nav = []
        group = QButtonGroup(self); group.setExclusive(True)
        for index, text in enumerate(['Захват ссылки', 'Оформление', 'Настройки']):
            button = QPushButton(text); button.setObjectName('nav'); button.setCheckable(True)
            group.addButton(button, index); self.nav.append(button); side_layout.addWidget(button)
        group.idClicked.connect(self.select_page)
        self.nav[0].setChecked(True)
        side_layout.addStretch(1)
        self.shortcut_side = label(self.prefs.get('hotkey').replace('+',' + '),'section')
        self.shortcut_side.setWordWrap(True)
        side_layout.addWidget(self.shortcut_side)
        side_layout.addWidget(label('Выделить область\nEsc — отменить', 'muted', True))
        side_layout.addSpacing(16)
        side_layout.addWidget(label('ЛОКАЛЬНО · БЕЗ ОБЛАКА','micro'))
        side_layout.addWidget(label('Версия 0.6.1', 'muted'))
        shell_layout.addWidget(side)
        main = QWidget(); main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(24,12,24,16); main_layout.setSpacing(12)
        titlebar = TitleBar(); titlebar.setMinimumHeight(56)
        top = QHBoxLayout(titlebar); top.setContentsMargins(0,0,0,0); top.setSpacing(2)
        self.header = label('СТУДИЯ ССЫЛОК','micro'); self.header.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        top.addWidget(self.header); top.addStretch(1)
        self.badge = label('● ЗАГРУЗКА OCR','badge'); top.addWidget(self.badge)
        main_layout.addWidget(titlebar)
        self.pages = QStackedWidget(); main_layout.addWidget(self.pages,1)
        self.capture_page = self.make_capture_page(); self.pages.addWidget(self.scroll_page(self.capture_page))
        self.theme_page = self.make_theme_page(); self.pages.addWidget(self.scroll_page(self.theme_page))
        self.settings_page = self.make_settings_page(); self.pages.addWidget(self.scroll_page(self.settings_page))
        bottom = QHBoxLayout(); bottom.setSpacing(8)
        self.metrics = label('Модель загружается заранее, пока вы работаете.','muted')
        self.metrics.setWordWrap(True); bottom.addWidget(self.metrics,1)
        grip = QSizeGrip(self); grip.setFixedSize(18,18); bottom.addWidget(grip, alignment=Qt.AlignmentFlag.AlignBottom)
        main_layout.addLayout(bottom)
        shell_layout.addWidget(main,1)

    def scroll_page(self, widget):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(widget)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        return scroll

    def page_layout(self):
        widget = QWidget(); layout = QVBoxLayout(widget)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        layout.setContentsMargins(0,8,0,8); layout.setSpacing(16)
        return widget, layout

    def make_capture_page(self):
        widget, layout = self.page_layout()
        layout.addWidget(label('Выдели. Скопируй. Вставь.','hero'))
        layout.addWidget(label('Ссылка или QR-код с экрана — в буфере обмена.\nРаспознавание локально, без загрузки снимков.', 'muted', True))
        frame, content = panel()
        row = QHBoxLayout(); row.setSpacing(14)
        row.addWidget(label('01  Выделить ссылку или QR-код','section'),1)
        self.shortcut_capture = label(self.prefs.get('hotkey').replace('+',' + '),'muted')
        self.shortcut_capture.setWordWrap(True); self.shortcut_capture.setMaximumWidth(240)
        row.addWidget(self.shortcut_capture)
        content.addLayout(row)
        self.capture_button = QPushButton('Выделить область экрана'); self.capture_button.setObjectName('primary')
        self.capture_button.clicked.connect(self.begin_capture); content.addWidget(self.capture_button)
        self.auto_copy = QCheckBox('Сразу копировать единственную найденную ссылку')
        self.auto_copy.setChecked(self.prefs.get('auto_copy'))
        self.auto_copy.toggled.connect(lambda value: self.save_option('auto_copy', value)); content.addWidget(self.auto_copy)
        content.addWidget(label('02  Дождитесь уведомления → 03  Вставьте через Ctrl+V\nМожно также использовать меню «Вставить».', 'muted', True))
        layout.addWidget(frame)
        self.status = label('OCR загружается в фоне. Выделение уже доступно.','status',True)
        self.status.setAccessibleName('Состояние распознавания'); layout.addWidget(self.status)
        frame, content = panel()
        result_top = QHBoxLayout(); result_top.addWidget(label('Последний результат','section'),1)
        self.clear_button = QPushButton('Очистить'); self.clear_button.clicked.connect(self.clear_result); result_top.addWidget(self.clear_button)
        content.addLayout(result_top)
        self.choices = QComboBox(); self.choices.setAccessibleName('Найденные результаты')
        self.choices.currentIndexChanged.connect(self.use_choice); self.choices.hide(); content.addWidget(self.choices)
        row = QHBoxLayout(); row.setSpacing(12)
        self.url_edit = QLineEdit(); self.url_edit.setPlaceholderText('Распознанную ссылку можно исправить')
        self.url_edit.setAccessibleName('Ссылка для копирования')
        self.url_edit.textChanged.connect(self.update_copy_button); self.url_edit.returnPressed.connect(self.copy_url)
        self.copy_button = QPushButton('Копировать'); self.copy_button.clicked.connect(self.copy_url); self.copy_button.setEnabled(False)
        self.qr_edit = QPlainTextEdit(); self.qr_edit.setFixedHeight(112)
        self.qr_edit.setAccessibleName(tr('Содержимое QR-кода')); self.qr_edit.hide()
        self.qr_edit.textChanged.connect(self.update_copy_button)
        row.addWidget(self.url_edit,1); row.addWidget(self.qr_edit,1); row.addWidget(self.copy_button); content.addLayout(row)
        content.addWidget(label('Проверьте 0/O, 1/l и домен. Ссылки сами не открываются.','muted',True))
        self.text_toggle = QCheckBox('Весь распознанный текст'); content.addWidget(self.text_toggle)
        self.raw_text = QPlainTextEdit(); self.raw_text.setReadOnly(True); self.raw_text.setMinimumHeight(100)
        self.raw_text.setAccessibleName('Распознанный текст'); self.raw_text.hide()
        self.text_toggle.toggled.connect(self.raw_text.setVisible); content.addWidget(self.raw_text)
        layout.addWidget(frame); layout.addStretch(1)
        return widget

    def make_theme_page(self):
        widget, layout = self.page_layout()
        layout.addWidget(label('Выберите настроение.','title'))
        layout.addWidget(label('Пять скинов. Оформление меняется сразу и сохраняется.', 'muted',True))
        grid = QGridLayout(); grid.setHorizontalSpacing(16); grid.setVerticalSpacing(16)
        self.theme_cards = {}
        for i, (key, theme) in enumerate(THEMES.items()):
            frame = QFrame(); frame.setObjectName('themeCard'); frame.setMinimumHeight(180)
            content = QVBoxLayout(frame); content.setContentsMargins(16,16,16,16); content.setSpacing(8)
            content.addWidget(Swatch(key)); content.addWidget(label(theme['name'],'section'))
            content.addWidget(label(theme['desc'],'muted',True))
            button = QPushButton('Применить'); button.clicked.connect(lambda checked=False, k=key: self.apply_theme(k))
            content.addWidget(button)
            grid.addWidget(frame, i//2, i%2); self.theme_cards[key] = (frame,button)
        layout.addLayout(grid); layout.addStretch(1)
        return widget

    def option(self, content, text, key, description=None):
        checkbox = QCheckBox(text); checkbox.setChecked(self.prefs.get(key))
        checkbox.toggled.connect(lambda checked: self.save_option(key, checked))
        content.addWidget(checkbox)
        if description:
            content.addWidget(label(description,'muted',True))
        return checkbox

    def make_settings_page(self):
        widget, layout = self.page_layout()
        layout.addWidget(label('Работает, пока вы работаете.','title'))
        layout.addWidget(label('Фоновый режим, запуск Windows и скорость распознавания.', 'muted',True))
        frame, content = panel(); content.addWidget(label('Язык интерфейса / Interface language','section'))
        self.language_combo = QComboBox()
        self.language_combo.addItem('Русский','ru'); self.language_combo.addItem('English','en')
        self.language_combo.setCurrentIndex(1 if language_manager.language=='en' else 0)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        content.addWidget(self.language_combo)
        content.addWidget(label('Русский или English — язык меняется сразу и сохраняется.','muted',True))
        layout.addWidget(frame)
        frame, content = panel(); content.addWidget(label('Горячая клавиша','section'))
        content.addWidget(label('Нажмите на поле, затем нажмите нужные клавиши или модификатор с кнопкой мыши.','muted',True))
        row = QHBoxLayout(); row.setSpacing(12)
        self.hotkey_edit = ShortcutRecorder(self.prefs.get('hotkey'))
        self.hotkey_edit.recordingStarted.connect(self.start_shortcut_recording)
        self.hotkey_edit.recordingFinished.connect(self.finish_shortcut_recording)
        self.hotkey_edit.recorded.connect(lambda _:self.hotkey_status.setText('Сочетание записано. Нажмите «Применить», чтобы включить его.'))
        self.hotkey_edit.setMinimumHeight(56)
        self.hotkey_edit.setAccessibleName('Горячая клавиша для выделения')
        row.addWidget(self.hotkey_edit,1)
        self.hotkey_apply = QPushButton('Применить'); self.hotkey_apply.clicked.connect(self.apply_hotkey)
        row.addWidget(self.hotkey_apply)
        reset = QPushButton('Сбросить'); reset.clicked.connect(self.reset_hotkey); row.addWidget(reset)
        content.addLayout(row)
        self.hotkey_status = label('По умолчанию: Ctrl+Shift+L. Изменение действует без перезапуска.','muted',True)
        content.addWidget(self.hotkey_status)
        content.addWidget(label('Мышь: Ctrl / Alt / Shift / Win + MouseMiddle, MouseX1 или MouseX2.\nЛКМ и ПКМ не назначаются; ЛКМ по значку трея запускает выделение.', 'muted',True))
        layout.addWidget(frame)
        frame, content = panel(); content.addWidget(label('Режим распознавания','section'))
        self.mode_combo = QComboBox()
        self.refresh_mode_items()
        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        content.addWidget(self.mode_combo)
        content.addWidget(label('Авто: сначала QR-коды, затем текст ссылок. Только ссылки — без проверки QR.\nТолько QR — без OCR. Для QR выделяйте весь код и светлую рамку.', 'muted', True))
        content.addWidget(label('QR с обычным текстом, Wi-Fi или другими данными копируется только вручную.\nНичего не открывается и не выполняется автоматически.', 'muted', True))
        layout.addWidget(frame)
        frame, content = panel(); content.addWidget(label('Скорость и уведомления','section'))
        self.fast_checkbox = self.option(content, 'Быстрый режим для одной строки', 'fast',
            'Выделяйте только строку с адресом. При сомнении OCR автоматически\nперейдёт к распознаванию всей области.')
        self.notification_checkbox = self.option(content, 'Уведомлять, когда ссылка готова', 'notifications')
        layout.addWidget(frame)
        frame, content = panel(); content.addWidget(label('Фоновая работа','section'))
        self.tray_checkbox = self.option(content, 'Закрывать окно в трей, а не завершать приложение', 'close_to_tray')
        self.hidden_checkbox = self.option(content, 'Запускать приложение сразу в трее', 'start_hidden')
        self.startup_checkbox = QCheckBox('Запускать при входе в Windows')
        self.startup_checkbox.setChecked(startup_enabled()); self.startup_checkbox.setEnabled(sys.platform=='win32')
        self.startup_checkbox.toggled.connect(self.toggle_startup); content.addWidget(self.startup_checkbox)
        content.addWidget(label('При входе в Windows приложение всегда стартует в трее.\nДля полного выхода: значок Lurivio → «Завершить».', 'muted',True))
        layout.addWidget(frame)
        frame, content = panel(); content.addWidget(label('Приватность','section'))
        content.addWidget(label('Скриншоты и история результатов не сохраняются. Настройки — на этом\nкомпьютере. Буфер обмена подчиняется настройкам Windows.', 'muted',True))
        open_settings = QPushButton('Открыть папку настроек'); open_settings.clicked.connect(self.open_config_folder)
        content.addWidget(open_settings); layout.addWidget(frame)
        self.settings_status = label('', 'muted',True); layout.addWidget(self.settings_status)
        layout.addStretch(1); return widget

    def refresh_mode_items(self):
        self.mode_combo.blockSignals(True)
        self.mode_combo.clear()
        for source, value in [('Авто: ссылки и QR-коды','auto'),('Только ссылки (OCR)','ocr'),('Только QR-коды','qr')]:
            self.mode_combo.addItem(tr(source),value)
        index = self.mode_combo.findData(self.prefs.get('capture_mode'))
        self.mode_combo.setCurrentIndex(max(0,index))
        self.mode_combo.setAccessibleName(tr('Режим распознавания'))
        self.mode_combo.blockSignals(False)

    def change_mode(self, index):
        value = self.mode_combo.itemData(index)
        try:
            self.prefs.set('capture_mode', value)
        except OSError:
            self.refresh_mode_items()
            self.settings_status.setText('Не удалось сохранить настройки. Проверьте доступ к папке пользователя.')

    def change_language(self, index):
        value = self.language_combo.itemData(index)
        if value not in ('ru','en'):
            return
        try:
            self.prefs.set('language',value)
        except OSError:
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(1 if language_manager.language=='en' else 0)
            self.language_combo.blockSignals(False)
            self.settings_status.setText('Не удалось сохранить язык. Проверьте доступ к папке настроек.')
            return
        language_manager.set_language(value)

    def add_tray_action(self, menu, source, callback):
        action = menu.addAction(tr(source),callback)
        self.tray_actions.append((action,source))
        return action

    def retranslate_auxiliary(self):
        self.refresh_mode_items()
        self.qr_edit.setAccessibleName(tr('Содержимое QR-кода'))
        for action,source in self.tray_actions:
            action.setText(tr(source))
        self.choices.setAccessibleName(tr('Найденные результаты'))
        self.hotkey_edit.setAccessibleName(tr('Горячая клавиша для выделения'))
        self.raw_text.setAccessibleName(tr('Распознанный текст'))
        self.language_combo.setAccessibleName(tr('Язык интерфейса / Interface language'))
        self.language_combo.blockSignals(True)
        self.language_combo.setCurrentIndex(1 if language_manager.language=='en' else 0)
        self.language_combo.blockSignals(False)
        if self.overlay and self.capturing:
            self.overlay.update()

    def select_page(self, index):
        self.pages.setCurrentIndex(index)
        self.header.setText(['СТУДИЯ ССЫЛОК','КОЛЛЕКЦИЯ СКИНОВ','НАСТРОЙКИ'][index])
        self.nav[index].setChecked(True)

    def save_option(self, key, value):
        try:
            self.prefs.set(key,value)
        except OSError:
            self.settings_status.setText('Не удалось сохранить настройки. Проверьте доступ к папке пользователя.')

    def apply_theme(self, key, save=True):
        if key not in THEMES:
            key = 'aurora'
        QApplication.instance().setProperty('lurivioTheme', key)
        self.shell.theme = key; self.shell.update()
        QApplication.instance().setStyleSheet(stylesheet(key))
        input_palette = self.url_edit.palette()
        input_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(THEMES[key]['muted']))
        self.url_edit.setPalette(input_palette)
        for item_key,(frame,button) in self.theme_cards.items():
            frame.setProperty('selected', item_key == key)
            frame.style().unpolish(frame); frame.style().polish(frame)
            button.setText('Выбрано' if item_key == key else 'Применить')
        if save:
            self.save_option('theme',key)

    def start_shortcut_recording(self):
        self.shortcut_recording = True
        self.tray_capture_timer.stop()
        if self.hotkey:self.hotkey.set_suspended(True)

    def finish_shortcut_recording(self):
        if self.hotkey:
            self.hotkey.set_suspended(False)
            if not self.hotkey.registered:
                self.hotkey_status.setText(self.hotkey.error)
        self.shortcut_recording = False

    def apply_hotkey(self):
        text = self.hotkey_edit.binding()
        try:
            canonical, _, _ = parse_binding(text)
        except ValueError as error:
            self.hotkey_status.setText(str(error)); return
        if self.hotkey is None or not self.hotkey.update(canonical):
            self.hotkey_status.setText(self.hotkey.error if self.hotkey else 'Горячие клавиши доступны в запущенной Windows-версии.')
            return
        old = self.prefs.get('hotkey')
        try:
            self.prefs.set('hotkey',canonical)
        except OSError:
            restored = self.hotkey.update(old)
            self.hotkey_status.setText('Не удалось сохранить комбинацию.' + (' Старая комбинация восстановлена.' if restored else ' Повторите выбор и сохранение.'))
            self.refresh_hotkey_labels(self.hotkey.text)
            return
        self.refresh_hotkey_labels(canonical)
        self.hotkey_status.setText('Сохранено: '+canonical+'. Уже работает без перезапуска.')
        if not self.busy:
            self.status.setText('Готово. Выделение: '+canonical+' → вставка: Ctrl+V.')

    def refresh_hotkey_labels(self, text):
        self.hotkey_edit.set_binding(text)
        self.shortcut_side.setText(text.replace('+',' + ')); self.shortcut_capture.setText(text.replace('+',' + '))
        self.tray.setToolTip('Lurivio — '+text)

    def reset_hotkey(self):
        self.hotkey_edit.set_binding(DEFAULT_HOTKEY)
        self.apply_hotkey()

    def toggle_startup(self, enabled):
        try:
            set_startup(enabled)
            self.settings_status.setText('Автозапуск включён: при входе в Windows — в трей.' if enabled else 'Автозапуск выключен.')
        except OSError as error:
            self.startup_checkbox.blockSignals(True); self.startup_checkbox.setChecked(startup_enabled()); self.startup_checkbox.blockSignals(False)
            self.settings_status.setText('Не удалось изменить автозапуск: '+str(error))

    def open_config_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(HOME)))

    def build_tray(self):
        self.tray_capture_timer = QTimer(self); self.tray_capture_timer.setSingleShot(True)
        self.tray_capture_timer.timeout.connect(self.begin_capture)
        self.tray = QSystemTrayIcon(app_icon(), self); self.tray.setToolTip('Lurivio — '+self.prefs.get('hotkey'))
        menu = QMenu(self)
        self.tray_actions = []
        self.add_tray_action(menu,'Выделить область',self.begin_capture)
        self.add_tray_action(menu,'Открыть Lurivio',self.show_window)
        self.add_tray_action(menu,'Копировать результат',self.copy_url)
        menu.addSeparator(); self.add_tray_action(menu,'Настройки',self.show_settings)
        menu.addSeparator(); self.add_tray_action(menu,'Завершить',self.request_exit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.messageClicked.connect(self.show_window)
        if self.tray_available:
            self.tray.show()

    def tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            if self.shortcut_recording or self.busy or self.capturing or self.quitting:
                return
            # Give the Windows overflow flyout time to close. Both notifications
            # of a double click share one timer and never open a second capture.
            if not self.tray_capture_timer.isActive():
                self.tray_capture_timer.start(180)

    def show_window(self):
        self.showNormal(); self.raise_(); self.activateWindow()

    def show_settings(self):
        self.select_page(2); self.show_window()

    def minimize_to_tray(self):
        if self.tray_available:
            self.hide()
        else:
            self.showMinimized()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def notify(self, text):
        if self.tray_available and self.prefs.get('notifications'):
            self.tray.showMessage('Lurivio', tr(text), QSystemTrayIcon.MessageIcon.Information, 2500)

    def on_ready(self):
        self.ocr_ready = True; self.badge.setText('● OCR' if self.busy else '● ГОТОВО')
        if not self.busy:
            if self.hotkey is not None and not self.hotkey.registered:
                self.status.setText('OCR готов. Горячая клавиша недоступна — измените её в настройках.')
            else:
                self.status.setText('Готово. Выделите адрес — затем вставьте его в нужное поле.')
        self.metrics.setText('OCR прогрет · Обработка локально · Без загрузки скриншотов')

    def update_copy_button(self):
        value = self.qr_edit.toPlainText() if self.last_is_qr else self.url_edit.text()
        self.copy_button.setEnabled(bool(value.strip()))

    def use_choice(self, index):
        value = self.choices.itemData(index)
        if value is None:
            return
        if self.last_is_qr:
            self.qr_edit.setPlainText(value)
        else:
            self.url_edit.setText(value)

    def reset_result_fields(self):
        self.last_is_qr = False
        self.qr_edit.clear(); self.qr_edit.hide(); self.url_edit.show()
        self.url_edit.clear(); self.raw_text.clear(); self.choices.clear(); self.choices.hide()

    def clear_result(self):
        self.reset_result_fields()
        self.worker.clear_cache()
        self.status.setText('Результат и кэш очищены. Буфер обмена не изменён.')

    def begin_capture(self):
        if self.busy or self.capturing or self.quitting or self.shortcut_recording:
            return
        if not self.worker.isRunning():
            self.on_error('OCR недоступен. Перезапустите приложение через Start.bat.'); return
        self.capturing = True
        if sys.platform == 'win32':
            from ctypes import wintypes
            ctypes.windll.user32.GetForegroundWindow.restype = wintypes.HWND
            self.capture_hwnd = ctypes.windll.user32.GetForegroundWindow()
        else:
            self.capture_hwnd = None
        # Store and restore the foreground window on Windows. Completion never
        # forces focus to Lurivio and never injects keystrokes into another app.
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        was_visible = self.isVisible()
        self.hide()
        QTimer.singleShot(100 if was_visible else 30, lambda: self.show_overlay(screen))

    def show_overlay(self, screen):
        try:
            shot = screen.grabWindow(0)
            if shot.isNull():
                raise RuntimeError('Empty capture')
            self.overlay = RegionOverlay(screen, shot)
            self.overlay.selected.connect(self.run_ocr); self.overlay.cancelled.connect(self.cancel_capture)
            self.overlay.show(); self.overlay.raise_(); self.overlay.activateWindow()
        except Exception:
            logging.exception('Screen capture failed'); self.capturing = False
            self.restore_target()
            self.on_error('Экран недоступен. Защищённое видео или экран входа могут не попадать в снимок.')

    def restore_target(self):
        if sys.platform=='win32' and self.capture_hwnd:
            try:
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                user32.IsWindow.argtypes = [wintypes.HWND]
                user32.SetForegroundWindow.argtypes = [wintypes.HWND]
                if user32.IsWindow(self.capture_hwnd):
                    user32.SetForegroundWindow(self.capture_hwnd)
            except (OSError, ValueError):
                pass
        self.capture_hwnd = None

    def cancel_capture(self):
        self.capturing = False
        self.status.setText('Выделение отменено. Буфер обмена не изменён.')
        QTimer.singleShot(0,self.restore_target)
        if not self.tray_available:
            QTimer.singleShot(0,self.show_window)

    def run_ocr(self, image):
        self.capturing = False; self.busy = True
        self.capture_button.setEnabled(False)
        self.reset_result_fields()
        self.status.setText('Распознаю…' if self.ocr_ready else 'Ожидаю загрузки OCR. Область уже выделена.')
        self.badge.setText('● OCR')
        QTimer.singleShot(0,self.restore_target)
        try:
            self.worker.submit(image, self.prefs.get('fast'), self.prefs.get('capture_mode'))
        except Exception:
            self.on_error('Очередь распознавания занята. Попробуйте снова.')

    def finish_job(self):
        self.busy = False; self.capture_button.setEnabled(True)
        self.badge.setText('● ГОТОВО' if self.ocr_ready else '● OCR НЕДОСТУПЕН')

    def on_result(self, urls, text, confidence, seconds, mode):
        self.finish_job()
        self.reset_result_fields()
        self.last_is_qr = mode.startswith('QR')
        self.qr_edit.setVisible(self.last_is_qr); self.url_edit.setVisible(not self.last_is_qr)
        self.raw_text.setPlainText(text)
        self.metrics.setText(f'Обработка: {seconds*1000:.0f} мс · Режим: {mode} · Локально')
        if not urls:
            message = 'QR-код не найден. Выделите весь код вместе со светлой рамкой.' if self.last_is_qr else 'Ссылка не найдена. Выделите адрес крупнее или проверьте распознанный текст.'
            self.status.setText(message); self.notify(message)
        else:
            self.choices.clear()
            for value in urls:
                preview = value.replace('\n',' ').replace('\r',' ')
                self.choices.addItem(preview[:100] + ('…' if len(preview)>100 else ''), value)
            self.choices.setVisible(len(urls)>1); self.use_choice(0)
            safe_auto = not self.last_is_qr or valid_url(urls[0])
            if len(urls)==1 and self.auto_copy.isChecked() and safe_auto:
                self.copy_url(notify=False)
                message = 'Ссылка скопирована — вставьте через Ctrl+V или «Вставить».'
            else:
                message = ('QR-код распознан. Проверьте содержимое и нажмите «Копировать».' if self.last_is_qr and len(urls)==1 else f'Найдено QR-кодов: {len(urls)}. Выберите результат и нажмите «Копировать».' if self.last_is_qr else f'Найдено ссылок: {len(urls)}. Нажмите уведомление и выберите адрес.')
                self.status.setText(message)
            if confidence < .85:
                message += ' Проверьте символы: OCR не уверен.'
                self.status.setText(self.status.source_text+' Проверьте символы: OCR не уверен.')
            self.notify(message)
        # In environments without a tray, never leave the application inaccessible.
        if not self.tray_available and not self.isVisible():
            self.show_window()

    def on_error(self, message):
        self.finish_job(); self.status.setText(message); self.notify(message)
        if not self.tray_available and not self.isVisible():
            self.show_window()

    def copy_url(self, checked=False, notify=True):
        if self.last_is_qr:
            value = self.qr_edit.toPlainText()
            if not value.strip():
                return False
            QApplication.clipboard().setText(value)
            self.status.setText('Содержимое QR в буфере. Вставьте через Ctrl+V или «Вставить».')
            if notify:
                self.notify('Содержимое QR скопировано.')
            return True
        value = self.url_edit.text().strip()
        if not value:
            return False
        if not value.lower().startswith(('https://','http://')):
            if '://' in value:
                self.status.setText('Разрешены только ссылки http:// и https://.'); return False
            value = 'https://'+value
        if not valid_url(value):
            self.status.setText('Некорректный адрес. Исправьте его перед копированием.'); return False
        self.url_edit.setText(value); QApplication.clipboard().setText(value)
        self.status.setText('Ссылка в буфере. Вставьте через Ctrl+V или меню «Вставить».')
        if notify:
            self.notify('Ссылка скопирована — можно вставлять.')
        return True

    def request_exit(self):
        if self.quitting:
            return
        self.quitting = True
        self.tray_capture_timer.stop()
        if self.overlay and self.capturing:
            self.overlay.close()
        if self.hotkey:
            self.hotkey.unregister()
        self.tray.hide(); self.hide()
        if self.worker.isRunning():
            self.worker.stop()
        else:
            QApplication.quit()

    def on_worker_stopped(self):
        if self.quitting:
            QApplication.quit()

    def closeEvent(self, event):
        if not self.quitting and self.prefs.get('close_to_tray') and self.tray_available:
            self.hide(); event.ignore()
        else:
            event.ignore(); self.request_exit()


def main():
    app = QApplication(sys.argv); app.setApplicationName('Lurivio'); app.setStyle('Fusion')
    prefs = Preferences(); language_manager.set_language(prefs.get('language'))
    # Windows uses a per-user named pipe. No network listener and no second OCR process.
    pipe_name = 'Lurivio.v06.'+hashlib.sha256(str(HOME).encode()).hexdigest()[:16]
    client = QLocalSocket(); client.connectToServer(pipe_name)
    if client.waitForConnected(300):
        if '--tray' not in sys.argv:
            client.write(b'SHOW'); client.waitForBytesWritten(300)
        client.disconnectFromServer(); return 0
    QLocalServer.removeServer(pipe_name)
    server = QLocalServer()
    if not server.listen(pipe_name):
        QMessageBox.warning(None,'Lurivio',tr('Не удалось запустить приложение: канал уже занят.')); return 1
    window = MainWindow(prefs)
    app.setQuitOnLastWindowClosed(False)
    hotkey = HotkeyFilter(window.begin_capture, prefs.get('hotkey')); window.hotkey = hotkey
    app.installNativeEventFilter(hotkey)
    app.aboutToQuit.connect(hotkey.unregister)
    def incoming():
        sock = server.nextPendingConnection()
        if sock is None:
            return
        def read():
            if b'SHOW' in bytes(sock.readAll()):
                window.show_window()
            sock.disconnectFromServer()
        sock.readyRead.connect(read); sock.disconnected.connect(sock.deleteLater)
        if sock.bytesAvailable():
            read()
    server.newConnection.connect(incoming)
    if sys.platform=='win32' and not hotkey.registered:
        window.status.setText('Горячая клавиша недоступна. Измените её в настройках или используйте значок в трее.')
        window.hotkey_status.setText(hotkey.error)
    hidden = '--tray' in sys.argv or prefs.get('start_hidden')
    if not hidden or not window.tray_available:
        window.show()
    result = app.exec()
    window.worker.stop(); window.worker.wait()
    server.close()
    return result

if __name__=='__main__':
    sys.exit(main())
