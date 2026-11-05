"""Download Visibly articles as inert review data; never write to site/."""
import json
import os
import re
import time
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlencode

BASE = 'https://heyvisibly.com/api/v1'
MAX_BYTES = 5_000_000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('API redirect refused to protect credentials')


def numeric_id(value):
    value = str(value)
    if not re.fullmatch(r'[1-9][0-9]{0,17}', value):
        raise ValueError('Expected a positive numeric Visibly ID')
    return value


def request_json(path, token):
    # Only fixed API paths are requested. Article URLs and images are never fetched.
    req = Request(BASE + path, headers={'Authorization': 'Bearer ' + token,
                                      'Accept': 'application/json'})
    time.sleep(1.1)  # Stay below the documented 60 requests/minute.
    with build_opener(NoRedirect).open(req, timeout=30) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('API response exceeds size limit')
    return json.loads(data)


def collect(site_id, get):
    site_id = numeric_id(site_id)
    result = {}
    for page in range(1, 101):
        payload = get('/sites/' + site_id + '/articles?' + urlencode(
            {'page': page, 'per_page': 100}))
        items = payload['data']
        if not isinstance(items, list):
            raise ValueError('Expected an article list')
        for item in items:
            article_id = numeric_id(item['id'])
            if article_id in result:
                raise ValueError('Repeated article ID; check API pagination')
            article = get('/articles/' + article_id)['data']
            if numeric_id(article['id']) != article_id:
                raise ValueError('Article ID mismatch')
            # Keep original body and protected link metadata unchanged, inside JSON.
            result[article_id] = article
        meta = payload.get('meta') or {}
        last = meta.get('last_page')
        if last is not None:
            if page >= int(last):
                break
        elif len(items) < 100:
            break
    else:
        raise ValueError('Pagination limit reached; no partial export written')
    return result


def main():
    token = os.environ.get('VISIBLY_API_KEY', '').strip()
    if not token:
        raise ValueError('Missing VISIBLY_API_KEY secret')
    articles = collect(os.environ.get('VISIBLY_SITE_ID', ''),
                       lambda path: request_json(path, token))
    output = Path('visibly-review')
    output.mkdir(exist_ok=False)
    for article_id, article in articles.items():
        (output / (article_id + '.json')).write_text(json.dumps(
            {'review_status': 'pending', 'article': article},
            ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'README.txt').write_text(
        'Review data only. Do not upload this folder to the public site.\n'
        'HTML bodies are untrusted text: do not open them as HTML.\n'
        'Review facts, rights, external links and protected links before publication.\n',
        encoding='utf-8')
    print(f'Exported {len(articles)} articles for review; public site unchanged.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        # Do not echo remote bodies or exception text, which may contain credentials.
        raise SystemExit('Visibly export failed. Check credentials, site ID and API availability.')
