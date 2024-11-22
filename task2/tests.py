import os
import unittest
from urllib.parse import unquote
from solution import get_html, get_next_page_url, get_letters_dict, main


class TestWrapStrict(unittest.TestCase):
    def test_get_html_1(self):
        self.assertIsInstance(get_html('https://ru.wikipedia.org/'), str)

    def test_get_html_raise(self):
        with self.assertRaises(ValueError):
            get_html('https://ru.wikipelia.org/')

    def test_get_next_page_url_1(self):
        self.assertEqual(
            get_next_page_url(
                unquote(get_html('https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту'), 'utf-8')
            ),
            'https://ru.wikipedia.org/w/index.php?title=Категория:Животные_по_алфавиту&pagefrom='
            'Азиатские+токи#mw-pages'
        )

    def test_get_next_page_url_2(self):
        self.assertEqual(
            get_next_page_url(
                unquote(get_html('https://ru.wikipedia.org/wiki/Обсуждение_категории:Животные_по_алфавиту'), 'utf-8')
            ),
            None
        )

    def test_get_letters_dict_1(self):
        self.assertEqual(
            get_letters_dict(
                unquote(get_html('https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту'), 'utf-8')
            ),
            {'А': 200}
        )

    def test_get_letters_dict_2(self):
        self.assertEqual(
            get_letters_dict(
                unquote(get_html('https://ru.wikipedia.org/w/index.php?title=Категория:Животные_по_алфавиту&from=Ию'), 'utf-8')
            ),
            {'Й': 4, 'К': 200 - 4}
        )

    def test_get_letters_dict_3(self):
        self.assertEqual(
            get_letters_dict(
                unquote(get_html('https://ru.wikipedia.org/wiki/Обсуждение_категории:Животные_по_алфавиту'),
                        'utf-8')
            ),
            None
        )
