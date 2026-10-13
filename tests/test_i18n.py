import unittest
from i18n import manager,tr

class TranslationTests(unittest.TestCase):
    def tearDown(self):manager.set_language('ru')
    def test_static(self):
        manager.set_language('en')
        self.assertEqual(tr('Настройки'),'Settings')
        self.assertEqual(tr('Выделите ссылку мышью   ·   Esc — отмена'),'Drag to select the URL   ·   Esc — cancel')
    def test_dynamic(self):
        manager.set_language('en')
        self.assertEqual(tr('OCR: 12 мс · Режим: строка / кэш · Обработка локально'),
                         'OCR: 12 ms · Mode: single line / cache · Local processing')
        self.assertEqual(tr('Сохранено: Ctrl+Alt+K. Уже работает без перезапуска.'),
                         'Saved: Ctrl+Alt+K. Active without restarting.')
        self.assertNotIn('Проверьте',tr('Найдено ссылок: 2. Нажмите уведомление и выберите адрес. Проверьте символы: OCR не уверен.'))
    def test_russian(self):
        manager.set_language('ru')
        self.assertEqual(tr('Настройки'),'Настройки')
    def test_unknown_language(self):
        manager.set_language('not-valid')
        self.assertEqual(manager.language,'ru')

if __name__=='__main__':unittest.main()
