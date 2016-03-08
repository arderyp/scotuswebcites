# -*- coding: utf-8 -*-

import re
import io

from discovery.Url import Url

from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter

class Pdf:
    def __init__(self, url=False, local_file=False):
        self.url = url
        self.local_file = local_file
        self.urls = []

    def download(self):
        if not self.url or not self.local_file:
            return False

        request = Url.get(self.url)
        if not request or request.status_code != 200:
            return False

        with open(self.local_file, 'w') as local:
            local.write(request.content) 
            local.close()
 
        return True

    def scrape_urls(self):
        self.extract_text()
        self.extract_urls_from_text()

    def extract_text(self):
        pdf_data = file(self.local_file, 'rb').read()
        pdf_stream = io.BytesIO(pdf_data)
        laparams = LAParams()
        resource_manager = PDFResourceManager(caching=True)
        codec = 'utf-8'
        output_stream = io.BytesIO()
        pagenos = set()

        device = TextConverter(
            resource_manager,
            output_stream,
            codec=codec,
            laparams=laparams,
        )

        interpreter = PDFPageInterpreter(
            resource_manager,
            device,
        )

        pages = PDFPage.get_pages(
            pdf_stream,
            pagenos,
            maxpages=0,
            caching=True,
            check_extractable=True,
        )

        for page in pages:
            interpreter.process_page(page)

        self.text = output_stream.getvalue().decode('utf8')

    def extract_urls_from_text(self):
        if self.text:
            #TODO: find pythonic way of doing replacement on multiple needle/search terms for all newlines
            #TODO: should be using r'' string format?
            # Replace newlines with spaces, then create newlines at instances of 'http'
            text = re.sub('(\n|\r|&#xD)', '', self.text)
            text = re.sub('http', '\nhttp', text)
            lines = text.split('\n')

            # Loop over newlines created, url should be first element
            for line in lines:
                if line.startswith('http'):
                    url = self.extract_url_from_line(line)

                    # Some opinions cite the same link multiple times. Add if not
                    # already in list
                    if not url in self.urls:
                        self.urls.append(url)

    def extract_url_from_line(self, line):
        # Many of the cited urls have poor formatting, such as spaces
        # before and after slashes, spaces after http://, punctuation
        # at the end of the string, etc.  We clean that up here. The
        # weirdness is so inconsistent that we can't systematically
        # fix everything at the moment, which is why a user must verify
        # all scraped links

        #TODO instead os setting these dictionary each time this function is called,
        # why not store them as static properties on the Url class?
        common_endings = [
            'com',
            'gov',
            'net',
            'edu',
            'mil',
            'htm',
            'tml',
            'php',
            'asp',
            'pdf',
        ]
        punctuation = [
            '?',
            '=',
            ':',
            '_',
            '-',
            '#',
            '$',
            '%',
            '+',
        ]
        partials = [
            'www', 'www.',
            'http', 'https',
            'http:', 'https:',
            'http:/', 'https:/',
            'http://', 'https://',
            'http://www', 'https://www',
            'http://www.', 'https://www.',
        ]
        stop = [
            '(',
            ')',
            '(all',
            '(as',
        ]
        strip = stop + [
            '.',
            ',',
            ';',
        ]

        words = line.split()

        # Try to clean up weird encoding character
        for word in words:
            words[words.index(word)] = word.strip()

        url = words[0]
        next_word = 1

        # Glue pieces together
        while True:
            if len(words) <= next_word:
                break

            nxt = words[next_word]
            if nxt[0] in stop:
                break

            if url in partials or url[-1] in punctuation or \
                nxt[0] in punctuation or '/' in nxt or '-' in nxt:

                url = url + nxt
                next_word += 1
            else:
                break

        for s in strip:
            if url[-len(s):] == s:
                url = url.rstrip(s)

        return url
