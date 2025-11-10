#!/usr/bin/env python3

# ddg_results_by_kwd_density.py
# ccr . 2025 Oct 28

"""Rank DuckDuckGo search results by keyword density.

Nowadays search results are dominated by Web pages showing high
keyword density, indicating they are search-engine-optimized or even
AI generated.  This script reads your search terms, retrieves search
results from *ddg* via *frogfind*, fetches each page, and computes the
keyword density there.

This script reads your search terms from standard input.

It writes a *markdown* report on standard output.

"""

ZERO = 0
SPACE = ' '
NULL = ''
NUL = '\x00'
NA = -1

import math
import sys
import re
import subprocess
import requests
from lxml import etree as ET
import lxml.html.soupparser as BS  # Beautiful Soup

STDIN = sys.stdin
STDOUT = sys.stdout
STDERR = sys.stderr

PAT_URL = re.compile('(http.*$)', re.DOTALL | re.MULTILINE)
PAT_DENSITY = re.compile('Keyword density:  ([^\n]*)', re.DOTALL | re.MULTILINE)
PAT_MIME = re.compile('([^/]+)/([^;]+)', re.DOTALL | re.MULTILINE)
WAIT_SECONDS = 5


class Query():

    def __init__(self, terms):
        self.terms_unquoted = terms[:-1]
        self.terms = self.terms_unquoted
        return

    def load_bytes(self):
        self.url = f'http://frogfind.com/?q={self.terms}'
        req = requests.get(self.url, timeout=5.0, headers={"User-Agent": "clanker_score"})
        if req.status_code == requests.codes.ok:
            self.search_results = req.text
#            print(req.text)
#            raise NotImplementedError
        else:
            self.search_results = NULL
        return self

    def load(self):
        self.load_bytes()
        self.doc = BS.fromstring(self.search_results)
#        ET.indent(self.doc, space="    ")
#        print(ET.tostring(self.doc, method='html', pretty_print=True).decode())
#        with open('/tmp/test.html', 'w') as unit:
#            unit.write(ET.tostring(self.doc).decode())
        return self

class Report():

    def init(self, terms):
        print('%Search Results', file=STDOUT)
        print(file=STDOUT)
        print(f'For:  **{terms}**', file=STDOUT)
        print(file=STDOUT)
        return self

    def cont(self, url, title, desc, size, keyword_density):
        print('---', file=STDOUT)
        print(file=STDOUT)
        print(f'+ **{title}**', file=STDOUT)
        print(file=STDOUT)
        try:
            density = float(keyword_density)
            if density >= 0.02:
                keyword_density = f'<font color=red>{keyword_density}</font>'
            else:
                keyword_density = f'<font color=green>{keyword_density}</font>'
        except ValueError:
            keyword_density = f'<font color=red>{keyword_density}</font>'
        print(f'  Size:  {size}B; Keyword Density:  {keyword_density}; <{url}>', file=STDOUT)
        print(file=STDOUT)
        print(desc, file=STDOUT)
        print(file=STDOUT)
        return self

    def term(self):
        print('''**Note:  Links with keyword density >= 0.02 are likely search-engine-optimized or AI generated.**''',
              file=STDOUT)
        return self


def calc_keyword_density(url):

    def mime(content_type):
        match = PAT_MIME.search(content_type)
        if match:
            (mime_type, mime_subtype) = match.group(1, 2)
        else:
            mime_type = 'text'
            mime_subtype = 'html'
            charset = 'utf-8'
        if mime_type.lower() in ['text']:
            if mime_subtype.lower() in ['html', 'markdown', 'plain']:
                result = 'text'
            else:
                result = 'other'
        elif mime_type.lower() in ['application']:
            if mime_subtype.lower() in ['pdf']:
                result = 'pdf'
            else:
                result = 'other'
        return result
    
    print(f'url:  {url}', file=STDERR)
    try:
        req = requests.get(url, timeout=5.0, headers={"User-Agent": "Chrome"})
        if req.status_code == requests.codes.ok:
            mime_type = mime(content_type=req.headers.get('content-type'))
            if mime_type in ['text']:
                src = req.text
                size = len(src)
                proc = subprocess.run(
                    args=['keyword_density'],
                    input=src,
                    text=True,
                    capture_output=True,
                    )
#                print(proc.stderr)
#                print(proc.stdout)
#                raise NotImplementedError
                txt = proc.stdout
                match = PAT_DENSITY.search(txt)
                if match:
                    density = match.group(1)
                else:
                    density = 'not found'
            else:
                size = ZERO
                density = mime_type
        else:
            size = ZERO
            density = f'"{req.status_code}"'
    except requests.exceptions.RequestException as err:
        print(f'>>>{err}', file=STDERR)
        size = ZERO
        density = 'ERR'
    return (size, density)


def generate_detail(report, elt):

    def get_child_0(elt, tag):
        if not elt is None:
            result = elt[ZERO]
            if result.tag == tag:
                pass
            else:
                result = None
        else:
            result = None
        return result

    a = elt.getparent()
    href = a.get('href')
    match = PAT_URL.search(href)
    if match:
        url = match.group(1)
    else:
        url = href
    title = NULL
    font = get_child_0(elt=a, tag='font')
    if not font is None:
        b = get_child_0(elt=font, tag='b')
        title = b.text
    desc = NULL
    br = a.getnext()
    if (not br is None) and (br.tag in ['br']):
        a = br.getnext()
        if (not a is None) and (a.tag in ['a']):
            br = a.getnext()
            if (not br is None) and (br.tag in ['br']):
                desc = br.tail
    (size_bytes, keyword_density) = calc_keyword_density(url)
    report.cont(url=url, title=title, desc=desc, size=size_bytes, keyword_density=keyword_density)
    return

    
def main_line():
    result = ZERO
#    (size, density) = calc_keyword_density('https://LacusVeris.com')
#    print(f'size:  {size}, density:  {density}')
#    raise NotImplementedError
    terms = STDIN.readline()
    query = Query(terms=terms)
    query.load()
    report = Report()
    report.init(terms=query.terms_unquoted)
    for font in query.doc.findall('.//font[@size="4"]'):
        generate_detail(report=report, elt=font)
    report.term()
    return result


def entry_point():
    retcd = main_line()
    sys.exit(retcd)


if __name__ == "__main__":
    entry_point()

    
# Fin
