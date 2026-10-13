"""Live Russian/English UI translations. OCR text and URLs are never translated."""
import re
import string
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit
from themes import ThemedCheckBox

EN = {
 'РАБОЧЕЕ ПРОСТРАНСТВО':'WORKSPACE',
 'Захват ссылки':'Capture link', 'Оформление':'Appearance', 'Настройки':'Settings',
 'Выделить область\nEsc — отменить':'Select a region\nEsc — cancel',
 'ЛОКАЛЬНО · БЕЗ ОБЛАКА':'LOCAL · NO CLOUD', 'Версия 0.6.1':'Version 0.6.1',
 'СТУДИЯ ССЫЛОК':'LINK STUDIO', 'КОЛЛЕКЦИЯ СКИНОВ':'THEME COLLECTION', 'НАСТРОЙКИ':'SETTINGS',
 '● ЗАГРУЗКА OCR':'● LOADING OCR', '● ГОТОВО':'● READY', '● OCR НЕДОСТУПЕН':'● OCR UNAVAILABLE',
 'Модель загружается заранее, пока вы работаете.':'The model preloads while you work.',
 'Выдели. Скопируй. Вставь.':'Select. Copy. Paste.',
 'Ссылка на видео или картинке — в буфере обмена.\nБез загрузки скриншотов и лишних окон.':'A URL in a video or image — on your clipboard.\nNo screenshot uploads or extra windows.',
 '01  Выделить адрес':'01  Select a URL', 'Выделить область экрана':'Select a screen region',
 'Сразу копировать единственную найденную ссылку':'Automatically copy a single detected URL',
 '02  Дождитесь уведомления → 03  Вставьте через Ctrl+V\nМожно также использовать меню «Вставить».':'02  Wait for the notification → 03  Paste with Ctrl+V\nOr use Paste in the context menu.',
 'OCR загружается в фоне. Выделение уже доступно.':'OCR is loading in the background. You can already select a region.',
 'Состояние распознавания':'Recognition status', 'Последний результат':'Last result', 'Очистить':'Clear',
 'Найденные результаты':'Detected results', 'Распознанную ссылку можно исправить':'You can edit the detected URL',
 'Ссылка для копирования':'URL to copy', 'Копировать':'Copy',
 'Проверьте 0/O, 1/l и домен. Ссылки сами не открываются.':'Check 0/O, 1/l and the domain. URLs never open automatically.',
 'Весь распознанный текст':'Show all recognized text', 'Распознанный текст':'Recognized text',
 'Выберите настроение.':'Choose your mood.',
 'Пять скинов. Оформление меняется сразу и сохраняется.':'Five themes. Changes apply instantly and are saved.',
 'Пастель, коралл и холодное стекло':'Pastels, coral and cool glass',
 'Тёмная студия с коралловым акцентом':'A dark studio with coral accents',
 'Бумага, тонкая сетка и шалфей':'Paper, a fine grid and sage',
 'Светлый жемчуг и системный синий':'Light pearl and system blue',
 'Ночной индиго и лавандовый акцент':'Midnight indigo and lavender accents',
 'Применить':'Apply', 'Выбрано':'Selected', 'Работает, пока вы работаете.':'Working while you work.',
 'Фоновый режим, запуск Windows и скорость распознавания.':'Background mode, Windows startup and OCR performance.',
 'Язык интерфейса / Interface language':'Interface language',
 'Русский или English — язык меняется сразу и сохраняется.':'Russian or English — changes apply instantly and are saved.',
 'Горячая клавиша':'Keyboard shortcut',
 'Нажмите на поле и введите удобную комбинацию.':'Click the field and press your preferred key combination.',
 'Горячая клавиша для выделения':'Screen capture shortcut', 'Сбросить':'Reset',
 'По умолчанию: Ctrl+Shift+L. Изменение действует без перезапуска.':'Default: Ctrl+Shift+L. Changes work without restarting.',
 'Скорость и уведомления':'Performance and notifications', 'Быстрый режим для одной строки':'Fast mode for a single line',
 'Выделяйте только строку с адресом. При сомнении OCR автоматически\nперейдёт к распознаванию всей области.':'Select only the URL line. If uncertain, OCR automatically\nfalls back to region detection.',
 'Уведомлять, когда ссылка готова':'Notify me when the URL is ready', 'Фоновая работа':'Background behavior',
 'Закрывать окно в трей, а не завершать приложение':'Close to the tray instead of quitting',
 'Запускать приложение сразу в трее':'Start the app hidden in the tray',
 'Запускать при входе в Windows':'Start at Windows sign-in',
 'При входе в Windows приложение всегда стартует в трее.\nДля полного выхода: значок Lurivio → «Завершить».':'At Windows sign-in the app always starts in the tray.\nTo quit: Lurivio tray icon → Quit.',
 'Приватность':'Privacy',
 'Скриншоты и история результатов не сохраняются. Настройки — на этом\nкомпьютере. Буфер обмена подчиняется настройкам Windows.':'Screenshots and result history are not saved. Preferences stay\non this computer. Clipboard behavior follows Windows settings.',
 'Открыть папку настроек':'Open preferences folder',
 'Не удалось сохранить настройки. Проверьте доступ к папке пользователя.':'Could not save preferences. Check access to your user folder.',
 'Не удалось сохранить язык. Проверьте доступ к папке настроек.':'Could not save the language. Check access to the preferences folder.',
 'Горячие клавиши доступны в запущенной Windows-версии.':'Global shortcuts are available in the running Windows app.',
 'Не удалось сохранить комбинацию.':'Could not save the shortcut.',
 ' Старая комбинация восстановлена.':' The previous shortcut was restored.',
 ' Повторите выбор и сохранение.':' Try selecting and saving again.',
 'Автозапуск включён: при входе в Windows — в трей.':'Startup enabled: hidden in the tray at Windows sign-in.',
 'Автозапуск выключен.':'Startup disabled.', 'Выделить область':'Select a region',
 'Открыть Lurivio':'Open Lurivio', 'Копировать результат':'Copy the result', 'Завершить':'Quit',
 'OCR готов. Горячая клавиша недоступна — измените её в настройках.':'OCR is ready. The shortcut is unavailable — change it in Settings.',
 'Готово. Выделите адрес — затем вставьте его в нужное поле.':'Ready. Select a URL, then paste it into your target field.',
 'OCR прогрет · Обработка локально · Без загрузки скриншотов':'OCR warmed up · Local processing · No screenshot uploads',
 'Результат и кэш очищены. Буфер обмена не изменён.':'Result and cache cleared. The clipboard is unchanged.',
 'OCR недоступен. Перезапустите приложение через Start.bat.':'OCR is unavailable. Restart the app using Start.bat.',
 'Экран недоступен. Защищённое видео или экран входа могут не попадать в снимок.':'Screen capture is unavailable. Protected video and secure desktops may not be captured.',
 'Выделение отменено. Буфер обмена не изменён.':'Selection cancelled. The clipboard is unchanged.',
 'Распознаю…':'Recognizing…', 'Ожидаю загрузки OCR. Область уже выделена.':'Waiting for OCR to load. Your region is already selected.',
 'Очередь распознавания занята. Попробуйте снова.':'The OCR queue is busy. Try again.',
 'Ссылка не найдена. Выделите адрес крупнее или проверьте распознанный текст.':'No URL found. Select a clearer region or check the recognized text.',
 'Ссылка скопирована — вставьте через Ctrl+V или «Вставить».':'URL copied — use Ctrl+V or Paste.',
 ' Проверьте символы: OCR не уверен.':' Check the characters: OCR is uncertain.',
 'Разрешены только ссылки http:// и https://.':'Only http:// and https:// URLs are allowed.',
 'Некорректный адрес. Исправьте его перед копированием.':'Invalid URL. Edit it before copying.',
 'Ссылка в буфере. Вставьте через Ctrl+V или меню «Вставить».':'URL on the clipboard. Use Ctrl+V or Paste.',
 'Ссылка скопирована — можно вставлять.':'URL copied — ready to paste.',
 'Не удалось запустить приложение: канал уже занят.':'Could not start the app: the instance channel is busy.',
 'Горячая клавиша недоступна. Измените её в настройках или используйте значок в трее.':'Shortcut unavailable. Change it in Settings or use the tray icon.',
 'Выделите ссылку мышью   ·   Esc — отмена':'Drag to select the URL   ·   Esc — cancel',
 'Выберите одну комбинацию, не последовательность клавиш.':'Choose one key combination, not a sequence.',
 'Эти модификаторы не поддерживаются.':'These modifiers are not supported.',
 'Добавьте Ctrl, Alt, Shift или Win. Без модификатора допускаются только F-клавиши.':'Add Ctrl, Alt, Shift or Win. Only function keys can be used without a modifier.',
 'Используйте букву A–Z, цифру, F-клавишу, Space, Tab, Home, End, Insert, Delete, PgUp или PgDown.':'Use A–Z, a digit, a function key, Space, Tab, Home, End, Insert, Delete, PgUp or PgDown.',
 'Ctrl+C, Ctrl+X и Ctrl+V нужны для буфера обмена. Выберите другую комбинацию.':'Ctrl+C, Ctrl+X and Ctrl+V are needed for the clipboard. Choose another shortcut.',
 'F12 зарезервирована Windows. Выберите другую клавишу.':'F12 is reserved by Windows. Choose another key.',
 'Комбинация занята другой программой или зарезервирована системой. Выберите другую.':'This shortcut is occupied or reserved by the system. Choose another.',
 'Автозапуск доступен только на Windows.':'Startup registration is available only on Windows.',
 'Путь слишком длинный для автозапуска Windows. Переместите Lurivio в папку с более коротким путём.':'The path is too long for Windows startup. Move Lurivio to a shorter path.',
 'Ошибка OCR. Попробуйте другую область. Технический журнал: errors.log в папке настроек.':'OCR failed. Try another region. Technical log: errors.log in the preferences folder.',
 'Не удалось загрузить OCR. Повторите установку через Start.bat или проверьте errors.log.':'Could not load OCR. Reinstall using Start.bat or check errors.log.',
 'Lurivio не запустился. Запустите Diagnose.bat для проверки.':'Lurivio could not start. Run Diagnose.bat to troubleshoot.',
 '\nЖурнал: ':'\nLog: ', 'Lurivio — ошибка запуска':'Lurivio — startup error',
 'строка':'single line', 'область':'region', 'пустая область':'empty region', 'кэш':'cache',
}
EN.update({
 'Для QR нужна новая библиотека ZXing. Полностью закройте приложение и запустите Start.bat для обновления.':'QR recognition needs the new ZXing library. Fully quit the app and run Start.bat to update.',
 'Нажмите на поле, затем нажмите нужные клавиши или модификатор с кнопкой мыши.':'Click the field, then press your keys or a modifier with a mouse button.',
 'Мышь: Ctrl / Alt / Shift / Win + MouseMiddle, MouseX1 или MouseX2.\nЛКМ и ПКМ не назначаются; ЛКМ по значку трея запускает выделение.':'Mouse: Ctrl / Alt / Shift / Win + MouseMiddle, MouseX1 or MouseX2.\nLeft/right clicks cannot be assigned; left-click the tray icon to capture.',
 'Сочетание записано. Нажмите «Применить», чтобы включить его.':'Shortcut recorded. Click Apply to activate it.',
 'Запись сочетания':'Record shortcut',
 'Нажмите нужное сочетание':'Press your preferred shortcut',
 'Клавиатура: например Ctrl+Alt+K.\nМышь: удерживайте Ctrl, Alt, Shift или Win и нажмите\nколёсико либо боковую кнопку внутри этого окна.\nEsc — отмена. ЛКМ, ПКМ и прокрутка не назначаются.':'Keyboard: for example Ctrl+Alt+K.\nMouse: hold Ctrl, Alt, Shift or Win and press\nthe middle or a side button inside this window.\nEsc cancels. Left/right clicks and scrolling cannot be assigned.',
 'Ожидаю нажатия…':'Waiting for input…',
 'Отмена':'Cancel',
 'Модификатор нажат. Добавьте клавишу или кнопку мыши.':'Modifier held. Add a key or mouse button.',
 'Нажмите для записи сочетания':'Click to record a shortcut',
 'Нажмите поле, затем нажмите сочетание клавиш или модификатор с кнопкой мыши.':'Click the field, then press a key combination or a modifier with a mouse button.',
 'Для мыши доступны колёсико (нажатие) и боковые кнопки X1/X2.':'Mouse shortcuts support the middle click and side buttons X1/X2.',
 'Некорректное сочетание мыши. Добавьте Ctrl, Alt, Shift или Win.':'Invalid mouse shortcut. Add Ctrl, Alt, Shift or Win.',
 'Для кнопки мыши нужен Ctrl, Alt, Shift или Win.':'A mouse button requires Ctrl, Alt, Shift or Win.',
 'Не удалось включить сочетание мыши. Проверьте доступность глобальных сочетаний в Windows.':'Could not enable the mouse shortcut. Check global shortcut availability in Windows.',

 'Ссылка или QR-код с экрана — в буфере обмена.\nРаспознавание локально, без загрузки снимков.':'A URL or QR code from your screen — on your clipboard.\nLocal recognition, no screenshot uploads.',
 '01  Выделить ссылку или QR-код':'01  Select a URL or QR code',
 'Содержимое QR-кода':'QR code content',
 'Режим распознавания':'Recognition mode',
 'Авто: ссылки и QR-коды':'Auto: URLs and QR codes',
 'Только ссылки (OCR)':'URLs only (OCR)',
 'Только QR-коды':'QR codes only',
 'Авто: сначала QR-коды, затем текст ссылок. Только ссылки — без проверки QR.\nТолько QR — без OCR. Для QR выделяйте весь код и светлую рамку.':'Auto: QR codes first, then URL text. URLs only skips QR scanning.\nQR only skips OCR. Select the whole QR code and its light border.',
 'QR с обычным текстом, Wi-Fi или другими данными копируется только вручную.\nНичего не открывается и не выполняется автоматически.':'QR text, Wi-Fi and other data are copied only manually.\nNothing is opened or executed automatically.',
 'QR-код не найден. Выделите весь код вместе со светлой рамкой.':'No QR code found. Select the entire code and its light border.',
 'QR-код распознан. Проверьте содержимое и нажмите «Копировать».':'QR code decoded. Review the content and click Copy.',
 'Содержимое QR в буфере. Вставьте через Ctrl+V или «Вставить».':'QR content on the clipboard. Use Ctrl+V or Paste.',
 'Содержимое QR скопировано.':'QR content copied.',
 'Выделите ссылку или QR мышью   ·   Esc — отмена':'Drag to select a URL or QR code   ·   Esc — cancel',
})
TEMPLATES = {
 'Обработка: {ms} мс · Режим: {mode} · Локально':'Processing: {ms} ms · Mode: {mode} · Local',
 'Найдено QR-кодов: {total}. Выберите результат и нажмите «Копировать».':'QR codes found: {total}. Choose a result and click Copy.',
 'Сохранено: {shortcut}. Уже работает без перезапуска.':'Saved: {shortcut}. Active without restarting.',
 'Готово. Выделение: {shortcut} → вставка: Ctrl+V.':'Ready. Capture: {shortcut} → paste: Ctrl+V.',
 'Не удалось изменить автозапуск: {error}':'Could not change startup: {error}',
 'OCR: {ms} мс · Режим: {mode} · Обработка локально':'OCR: {ms} ms · Mode: {mode} · Local processing',
 'Найдено ссылок: {total}. Нажмите уведомление и выберите адрес.':'URLs found: {total}. Click the notification and choose one.',
}

def compile_template(source):
    pattern = ''
    for literal, name, _, _ in string.Formatter().parse(source):
        pattern += re.escape(literal)
        if name:
            pattern += '(?P<' + name + '>.*?)'
    return re.compile('^'+pattern+'$', re.DOTALL)
PATTERNS = [(compile_template(source),dest) for source,dest in TEMPLATES.items()]

class LanguageManager(QObject):
    changed = Signal()
    def __init__(self):
        super().__init__(); self.language = 'ru'
    def set_language(self, value):
        value = value if value in ('ru','en') else 'ru'
        if value != self.language:
            self.language = value; self.changed.emit()

manager = LanguageManager()

def tr(source):
    if manager.language != 'en' or not isinstance(source,str):
        return source
    if source in EN:
        return EN[source]
    # Resolve appended notices without re-translating already localized text.
    notice = ' Проверьте символы: OCR не уверен.'
    if source.endswith(notice):
        return tr(source[:-len(notice)]) + EN[notice]
    for pattern,destination in PATTERNS:
        match = pattern.fullmatch(source)
        if match:
            return destination.format(**{key:tr(value) for key,value in match.groupdict().items()})
    # These are message fragments, not user text. Only labels/placeholders/tray
    # messages use tr(); editable URLs and raw OCR text use native widgets.
    result = source
    for original in sorted(EN,key=len,reverse=True):
        if len(original) > 8 and original in result:
            result = result.replace(original,EN[original])
    # OCR enum composition: 'строка / кэш'.
    if source.endswith(' / кэш'):
        return tr(source[:-len(' / кэш')]) + ' / cache'
    return result

class TextMixin:
    def _bind(self, source):
        self.source_text = source
        self._accessible_source = None
        manager.changed.connect(self._retranslate)
    def setText(self, source):
        self.source_text = source
        super().setText(tr(source))
    def setAccessibleName(self, source):
        self._accessible_source = source
        super().setAccessibleName(tr(source))
    def _retranslate(self):
        super().setText(tr(self.source_text))
        if self._accessible_source is not None:
            super().setAccessibleName(tr(self._accessible_source))

class Label(TextMixin,QLabel):
    def __init__(self,source='',parent=None):
        super().__init__(tr(source),parent); self._bind(source)

class Button(TextMixin,QPushButton):
    def __init__(self,source='',parent=None):
        super().__init__(tr(source),parent); self._bind(source)

class CheckBox(TextMixin,ThemedCheckBox):
    def __init__(self,source='',parent=None):
        super().__init__(tr(source),parent); self._bind(source)

class LineEdit(QLineEdit):
    # Only chrome is translated. setText is deliberately not overridden.
    def __init__(self,parent=None):
        super().__init__(parent); self._placeholder_source = ''; self._accessible_source = ''
        manager.changed.connect(self._retranslate)
    def setPlaceholderText(self,source):
        self._placeholder_source = source; super().setPlaceholderText(tr(source))
    def setAccessibleName(self,source):
        self._accessible_source = source; super().setAccessibleName(tr(source))
    def _retranslate(self):
        super().setPlaceholderText(tr(self._placeholder_source))
        super().setAccessibleName(tr(self._accessible_source))
