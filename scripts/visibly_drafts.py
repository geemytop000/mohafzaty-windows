"""Download Visibly articles as inert review data; never write to site/."""
import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlencode, urlsplit

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


def validate_feed_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname not in
            {'heyvisibly.com', 'www.heyvisibly.com'} or parsed.username or
            parsed.password or parsed.port not in (None, 443) or parsed.fragment):
        raise ValueError('Expected an HTTPS Visibly feed URL')
    return url


def collect_feed(url):
    validate_feed_url(url)
    result = {}
    seen = set()
    for page in range(100):
        if url in seen:
            raise ValueError('Repeated feed page')
        seen.add(url)
        req = Request(validate_feed_url(url), headers={'Accept': 'application/feed+json, application/json'})
        with build_opener(NoRedirect).open(req, timeout=30) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Feed exceeds size limit')
        payload = json.loads(raw)
        if payload.get('version') not in ('https://jsonfeed.org/version/1', 'https://jsonfeed.org/version/1.1'):
            raise ValueError('Expected JSON Feed v1 or v1.1')
        items = payload['items']
        if not isinstance(items, list):
            raise ValueError('Expected feed items')
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id']:
                raise ValueError('Invalid feed item ID')
            key = hashlib.sha256(item['id'].encode()).hexdigest()
            if key in result:
                raise ValueError('Repeated feed article')
            if not any(isinstance(item.get(k), str) and item[k].strip()
                       for k in ('content_html', 'content_text')):
                raise ValueError('Feed item has no content')
            # Preserve content and protected links as inert JSON, never as a web page.
            result[key] = item
        next_url = payload.get('next_url')
        if not next_url:
            return result
        # Do not let feed content choose a new endpoint for a credentialed request.
        if next_url != url:
            raise ValueError('Paginated feed requires endpoint review; no partial export written')
        url = next_url
    raise ValueError('Feed pagination limit reached')


def main():
    feed_url = os.environ.get('VISIBLY_FEED_URL', '').strip()
    if not feed_url:
        raise ValueError('Missing VISIBLY_FEED_URL secret')
    articles = collect_feed(feed_url)
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
    except HTTPError as error:
        raise SystemExit('Visibly feed HTTP error: ' + str(error.code))
    except Exception as error:
        allowed = {'Missing VISIBLY_FEED_URL secret', 'Expected an HTTPS Visibly feed URL',
                   'Expected JSON Feed v1 or v1.1', 'Expected feed items',
                   'Invalid feed item ID', 'Feed item has no content',
                   'Repeated feed article', 'Feed exceeds size limit',
                   'API redirect refused to protect credentials',
                   'Paginated feed requires endpoint review; no partial export written'}
        reason = str(error) if type(error) is ValueError and str(error) in allowed else type(error).__name__
        raise SystemExit('Visibly export failed: ' + reason)
