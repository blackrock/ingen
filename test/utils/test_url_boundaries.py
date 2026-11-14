import unittest

from ingen.utils.url_constructor import UrlConstructor


class TestUrlBoundaries(unittest.TestCase):
    def test_existing_query_and_fragment_survive_appended_parameters(self):
        constructor = UrlConstructor('https://example.test/data?existing=1#results',
                                     [{'id': 'q', 'type': 'const', 'value': 'hello world'}])
        self.assertEqual(constructor.get_urls(),
                         ['https://example.test/data?existing=1&q=hello%20world#results'])

    def test_empty_parameters_leave_url_unchanged(self):
        url = 'https://example.test/data?existing=1#results'
        self.assertEqual(UrlConstructor(url, []).get_urls(), [url])
