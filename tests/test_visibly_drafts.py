import importlib.util
from pathlib import Path
import unittest
import io
import json
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('drafts', Path(__file__).resolve().parents[1] / 'scripts/visibly_drafts.py')
drafts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drafts)


class DraftSafety(unittest.TestCase):
    def test_feed_urls_restricted(self):
        for url in ['http://heyvisibly.com/feed', 'https://evil.test/feed', 'https://heyvisibly.com@evil.test/feed', 'https://heyvisibly.com:444/feed']:
            with self.assertRaises(ValueError):
                drafts.validate_feed_url(url)
        self.assertEqual(drafts.validate_feed_url('https://heyvisibly.com/feed?token=secret'), 'https://heyvisibly.com/feed?token=secret')

    def test_feed_export_inert_and_safe_filename(self):
        payload = {'version': 'https://jsonfeed.org/version/1', 'items': [
            {'id': '../../site/index.html', 'content_html': '<script>alert(1)</script>'}]}
        with patch.object(drafts, 'build_opener') as opener:
            opener.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
            articles = drafts.collect_feed('https://heyvisibly.com/feed')
        self.assertEqual(len(articles), 1)
        self.assertEqual(len(next(iter(articles))), 64)
        self.assertEqual(next(iter(articles.values()))['content_html'], '<script>alert(1)</script>')

    def test_feed_rejects_unreviewed_pagination(self):
        payload = {'version': 'https://jsonfeed.org/version/1', 'items': [], 'next_url': 'https://evil.test'}
        with patch.object(drafts, 'build_opener') as opener:
            opener.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
            with self.assertRaises(ValueError):
                drafts.collect_feed('https://heyvisibly.com/feed')

    def test_empty_feed_valid(self):
        payload = {'version': 'https://jsonfeed.org/version/1.1', 'items': []}
        with patch.object(drafts, 'build_opener') as opener:
            opener.return_value.open.return_value = io.BytesIO(json.dumps(payload).encode())
            self.assertEqual(drafts.collect_feed('https://heyvisibly.com/feed'), {})

    def test_reject_path_injection(self):
        for value in ['../site', '1?url=https://evil.test', '0', '', '1/2']:
            with self.assertRaises(ValueError):
                drafts.numeric_id(value)

    def test_paginated_export_preserves_body_as_data(self):
        body = '<script>alert(1)</script><a data-visibly-protected href="https://example.com">link</a>'
        def get(path):
            if '/articles?' in path:
                page = 1 if 'page=1&' in path else 2
                return {'data': [{'id': page}], 'meta': {'last_page': 2}}
            return {'data': {'id': path.rsplit('/', 1)[1], 'body': body}}
        result = drafts.collect('7', get)
        self.assertEqual(set(result), {'1', '2'})
        self.assertEqual(result['1']['body'], body)

    def test_reject_wrong_article(self):
        def get(path):
            return {'data': [{'id': 1}]} if '?' in path else {'data': {'id': 2}}
        with self.assertRaises(ValueError):
            drafts.collect('7', get)

    def test_reject_repeated_pages(self):
        def get(path):
            return {'data': [{'id': 1}], 'meta': {'last_page': 2}} if '?' in path else {'data': {'id': 1}}
        with self.assertRaises(ValueError):
            drafts.collect('7', get)

    def test_redirect_refused(self):
        with self.assertRaises(ValueError):
            drafts.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.test')


if __name__ == '__main__':
    unittest.main()
