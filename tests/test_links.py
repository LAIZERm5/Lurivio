import unittest
from links import extract_urls, valid_url

class LinkTests(unittest.TestCase):
    def test_full(self):
        self.assertEqual(extract_urls('Адрес: https://Example.com/Aa?x=1&y=2'), ['https://Example.com/Aa?x=1&y=2'])
    def test_bare(self):
        self.assertEqual(extract_urls('example.com/help'), ['https://example.com/help'])
    def test_www(self):
        self.assertEqual(extract_urls('www.example.org'), ['https://www.example.org'])
    def test_multiple_and_dedup(self):
        self.assertEqual(extract_urls('https://a.com https://b.org https://a.com'), ['https://a.com', 'https://b.org'])
    def test_punctuation(self):
        self.assertEqual(extract_urls('(https://example.com/a).'), ['https://example.com/a'])
    def test_balanced_parentheses(self):
        self.assertEqual(extract_urls('https://en.wikipedia.org/wiki/Example_(test)'), ['https://en.wikipedia.org/wiki/Example_(test)'])
    def test_email(self):
        self.assertEqual(extract_urls('me@example.com'), [])
    def test_no_link(self):
        self.assertEqual(extract_urls('Нажмите здесь'), [])
    def test_http(self):
        self.assertEqual(extract_urls('http://example.com:8080/a'), ['http://example.com:8080/a'])
    def test_cyrillic_domain(self):
        self.assertEqual(extract_urls('пример.рф'), ['https://пример.рф'])
    def test_invalid(self):
        for url in ['javascript:alert(1)', 'https://a b.com', 'https://', 'https://a.com:999999', 'https://me:secret@a.com']:
            self.assertFalse(valid_url(url), url)
    def test_no_guess(self):
        self.assertEqual(extract_urls('https://examp1e.com/O0'), ['https://examp1e.com/O0'])

if __name__ == '__main__':
    unittest.main()
