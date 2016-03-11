# -*- coding: utf-8 -*-

import re
import slate
from discovery.Url import Url


class Pdf:
    common_endings = ['com', 'gov', 'net', 'edu', 'mil', 'htm', 'tml', 'php', 'asp', 'pdf', ]
    punctuation = ['?', '=', ':', '_', '-', '#', '$', '%', '+', ]
    should_stop = ['(', ')', '(all', '(as', ]
    should_strip = should_stop + ['.', ',', ';', ]
    partial_urls = [
        'www', 'www.',
        'http', 'https',
        'http:', 'https:',
        'http:/', 'https:/',
        'http://', 'https://',
        'http://www', 'https://www',
        'http://www.', 'https://www.',
    ]

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
        if self.local_file:
            with open(self.local_file, 'rb') as binary_input:
                self.document = slate.PDF(binary_input)
            for page in self.document:
                text = re.sub('http', '\nhttp', page.decode('utf8'))
                lines = text.split('\n')
                for line in lines:
                    if line.startswith('http'):
                        url = self.extract_url_from_line(line)
                        if url not in self.urls:
                            self.urls.append(url)

    def extract_url_from_line(self, line):
        """Extract url string from line of text

        Many of the cited urls have poor formatting, such as spaces
        before and after slashes, spaces after http://, punctuation
        at the end of the string, etc.  We clean that up here. The
        weirdness is so inconsistent that we can't systematically
        fix everything at the moment, which is why a user must verify
        all scraped links
        """

        # Try to clean up weird encoding character
        words = line.split()
        for word in words:
            words[words.index(word)] = word.strip()

        url = words[0]
        next_word = 1

        # Process url string
        while True:
            if len(words) <= next_word:
                break

            nxt = words[next_word]
            if nxt[0] in self.should_stop:
                break

            # Glue next substring onto end of url string
            if url in self.partial_urls or url[-1] in self.punctuation or \
                nxt[0] in self.punctuation or '/' in nxt or '-' in nxt or '_' in nxt:

                url = url + nxt
                next_word += 1
            else:
                break

        for substring in self.should_strip:
            if url.endswith(substring):
                url = url.rstrip(substring)

        return url
