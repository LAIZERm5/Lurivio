# Changelog

## 0.6.1 · QR recognition fix · Beta

- ZXing-C++ 2.3.0 primary QR decoder, OpenCV fallback, offline operation unchanged.
- Original-resolution scan before enhancement, quiet-zone/inversion retries and conservative rounded-module closing.
- Extra contrast/enlargement attempts in QR-only mode; return only validated UTF-8 payloads.
- Video-like fixtures: rounded modules, central logo, JPEG, coloured low contrast, tight crop, dense code in a large frame and unreadable partial code.
- New dependency included in setup, PyInstaller collection and license notices.
- No guarantee for a user's unseen Telegram/video code; a paused public/test frame is needed for diagnosis.


## 0.6.0 · Beta

- Click-to-record shortcut field and modal input capture; no manual text typing.
- Keyboard combinations and modifier + middle/side mouse buttons supported.
- Temporarily suspend the active shortcut during recording; restore it on cancel/finish.
- Single left tray click starts screen selection; right-click menu opens the app.
- Coalesce repeated tray activation events; block capture while recording/busy/quitting.
- RU/EN recorder UI and updated documentation/tests.
- Windows global mouse hook requires real Windows validation before public release.


## 0.5.0 · Lurivio · Beta release candidate

- Unified Lurivio branding across the executable, tray, icon, settings directory and build assets.
- Local OpenCV QR decoding; URLs, UTF-8 text, Wi-Fi and multiline payloads.
- Auto / OCR-only / QR-only modes with persisted preferences and cache isolation by mode.
- Manual review for non-HTTP/HTTPS QR payloads; no opening, execution or auto-pasting.
- Multiple QR result selection, editable multiline QR content and RU/EN translations.
- Legacy preference import; no automatic legacy startup changes.
- Updated documentation, Windows build workflow, SHA-256 asset checksums and draft prereleases.


## 0.4.0

- Нативная панель Windows со стандартными кнопками справа сверху.
- Обычное сворачивание в панель задач; настройка закрытия в трей сохранена.
- Живое переключение Русский / English с сохранением языка.
- Перевод меню, подсказок, ошибок, уведомлений и сообщений OCR.
- Распознанный текст, введённые адреса и буфер не переводятся.

## 0.3.0

- Настройка глобальной горячей клавиши без перезапуска.
- Безопасная смена регистрации: занятая новая клавиша не отключает старую.
- Проверка поддерживаемых клавиш, сброс к стандартной комбинации.
- Кэш одного последнего точного выделения, только в памяти; очистка вместе с результатом.
- Быстрая проверка одноцветной пустой области и более лёгкая подготовка строки.
- Структура GitHub-репозитория: документация RU/EN, скриншоты, MIT для своего кода,
  тесты, шаблоны issues/PR, Windows CI и публикация релиза по тегу.

## 0.2.0

- Предварительный прогрев и постоянный рабочий поток OCR.
- Быстрый режим строки и резервная детекция области.
- Пять скинов, настройки, трей и автозапуск после входа в Windows.
- Фоновое копирование без открытия окна на завершении OCR.

## 0.1.0

- Выделение области экрана, локальное OCR, извлечение HTTP(S)-адресов.
- Автоматическое и ручное копирование, редактирование и выбор нескольких ссылок.

Проверенный локально исходный код не означает, что каждый публичный Windows-релиз
уже протестирован на настоящем пользовательском компьютере.
