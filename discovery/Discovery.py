# -*- coding: utf-8 -*-

from scotus import settings
from django.utils import timezone
from django.db.models import Q

from discovery.Pdf import Url
from opinions.models import Opinion
from justices.models import Justice

import lxml.html
from datetime import datetime


class Discovery:
    def __init__(self):
        self.discovered_opinions = []
        self.new_opinions = []
        self.category_urls = []
        self.pdfs_to_scrape = []
        self.BASE = 'http://www.supremecourt.gov'
        self.OPINIONS_BASE = self.BASE + '/opinions/'
        self.OPINIONS_MAIN_PAGE = self.OPINIONS_BASE + 'opinions.aspx'
        self.YYYYMMDD = timezone.now().strftime('%Y%m%d')

    def run(self):
        print '[INITATING DISCOVERY - %s]' % timezone.now()
        print '[**%s**]' % self.OPINIONS_MAIN_PAGE
        self.fetch_opinion_category_urls()
        self.get_opinions_from_categories()
        print '[INITIATING OPINION INGEST]'
        self.ingest_new_opinions()
        print '[INITIATION CITATION SCRAPING AND INGEST]'
        self.ingest_new_citations()
        print '[DISCOVERY COMPLETE]'

    def fetch_opinion_category_urls(self):
        request = Url.get(self.OPINIONS_MAIN_PAGE)

        if request and request.status_code == 200:
            html = lxml.html.fromstring(request.text)
            search = "//div[@class='panel-body dslist2']/ul/li/a/@href"
            for category in html.xpath(search):
                self.category_urls.append(self.OPINIONS_BASE + category)
            
    def get_opinions_from_categories(self):
        for category_url in self.category_urls:
            category = category_url.split('/')[-2]
            request = Url.get(category_url)    

            if request and request.status_code == 200:
                html = lxml.html.fromstring(request.text)
                search = "//table[@class='table table-bordered']/tr"

                for row in html.xpath(search):
                    opinion = []
                    for cell in row.xpath('./td'):
                        opinion.append(cell.text_content().strip())
                        for pdf_path in cell.xpath('./a/@href'):
                            opinion.append(self.BASE + pdf_path.strip())
                            
                    if opinion:
                        # Slip opinions have extra 'reporter' column as first
                        # column. Add blank first column to non slip opinions
                        if len(opinion) == 6:
                            opinion = [''] + opinion

                        # Standardize published date to YYYY-MM-DD format
                        opinion[1] = opinion[1].replace('-', '/')
                        opinion[1] = datetime.strptime(opinion[1], '%m/%d/%y').strftime('%Y-%m-%d')                

                        print 'Discovered: %s  %s' % (opinion[3], opinion[4])

                        #TODO: email when new justice created so can create name on back end
                        if not Justice.objects.filter(id=opinion[5]):
                            justice = Justice(id=opinion[5], name=opinion[5])
                            justice.save()

                        self.discovered_opinions.append(Opinion(
                            category=category,
                            reporter=opinion[0],
                            published=opinion[1],
                            docket=opinion[2],
                            name=opinion[3],
                            pdf_url=opinion[4],
                            justice=Justice(opinion[5]),
                            part=opinion[6],
                            discovered=timezone.now(),
                        ))

    def ingest_new_opinions(self):
        # Sort opinions by publication date, oldest to newest
        self.discovered_opinions.sort(key=lambda o: o.published)

        for opinion in self.discovered_opinions:
            if opinion.already_exists():
                print 'Skipping: %s' % opinion.name
                continue

            # There appear to be validly seperate opinions with the same name AND justice, so I am removing this republished check altogether for now
            #if opinion.was_republished():
            #    print 'Ingesting  (REPUBLISHED): %s' % opinion.name
            #    opinion.set_updated_on_previously_published()
            #else:
            #    print 'Ingesting: %s  %s' % (opinion.name, opinion.pdf_url)

            print 'Ingesting: %s  %s' % (opinion.name, opinion.pdf_url)

            opinion.save()
            self.new_opinions.append(opinion)
            
    def ingest_new_citations(self):
        for opinion in self.new_opinions:
            print 'Downloading: %s  %s' % (opinion.name, opinion.pdf_url)
            opinion.download()
            print 'Scraping: %s  %s' % (opinion.name, opinion.local_pdf)
            opinion.scrape()

            if opinion.pdf.urls:
                print 'Ingesting citations from %s' % opinion.name
                opinion.ingest_citations()
