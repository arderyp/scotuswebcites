# -*- coding: utf-8 -*-

import lxml.html

from django.utils import timezone
from django.core.mail import send_mail
from dateutil import parser

from scotus import settings
from discovery.Pdf import Url
from opinions.models import Opinion
from justices.models import Justice


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

    def convert_date_string(self, date_string):
        """Convert date string into standard date object"""
        return parser.parse(date_string).date()


    def fetch_opinion_category_urls(self):
        request = Url.get(self.OPINIONS_MAIN_PAGE)

        if request and request.status_code == 200:
            html = lxml.html.fromstring(request.text)
            search = "//div[@class='panel-body dslist2']/ul/li/a/@href"
            for category in html.xpath(search):
                self.category_urls.append(self.OPINIONS_BASE + category)
            
    def get_opinions_from_categories(self):
        table_rows = "//table[@class='table table-bordered']/tr"
        header_cells = '%s/th/text()' % table_rows
        new_justices = []

        for category_url in self.category_urls:
            category = category_url.split('/')[-2]
            request = Url.get(category_url)    

            if request and request.status_code == 200:
                html = lxml.html.fromstring(request.text)
                column_labels = html.xpath(header_cells)

                for row in html.xpath(table_rows):
                    row_data = {}
                    cell_count = 0

                    # Parse data from rows in table
                    for cell in row.xpath('td'):
                        cell_label = column_labels[cell_count]
                        if cell.xpath('a') or cell_label == 'Revised':
                            text = cell.xpath('a/text()')[0] if cell.xpath('a/text()') else None
                            href = cell.xpath('a/@href')[0] if cell.xpath('a/@href') else None
                            row_data[cell_label] = text
                            row_data[cell_label + '_Url'] = href
                        else:
                            cell_text = cell.xpath('text()')
                            row_data[cell_label] = cell_text[0].strip() if cell_text else None
                        cell_count += 1

                    if row_data:
                        # Older pages don't have revised column
                        if 'Revised' not in column_labels:
                            row_data['Revised'] = None
                            row_data['Revised_Url'] = None

                        print 'Discovered: %s\t(%s)' % (row_data['Name'], category_url)

                        # Validate the justice, or add new record for him/her
                        if not Justice.objects.filter(id=row_data['J.']):
                            justice = Justice(id=row_data['J.'], name=row_data['J.'])
                            justice.save()
                            new_justices.append(row_data['J.'])

                        # Convert all scraped data to unicode
                        for label, data in row_data.iteritems():
                            if data:
                                row_data[label] = unicode(data)

                        # Create new opinion record from row data
                        self.discovered_opinions.append(Opinion(
                            category=category,
                            reporter=row_data['-R'] if '-R' in row_data else None,
                            published=self.convert_date_string(row_data['Date']),
                            docket=row_data['Docket'],
                            name=row_data['Name'],
                            pdf_url=self.BASE + row_data['Name_Url'],
                            justice=Justice(row_data['J.']),
                            part=row_data['Pt.'],
                            revised_date=self.convert_date_string(row_data['Revised']) if row_data['Revised'] else None,
                            revised_pdf_url=self.BASE + row_data['Revised_Url'] if row_data['Revised_Url'] else None,
                            discovered=timezone.now(),
                        ))

        # REMOVE
        # REPLACE THIS WITH MORE GENERAL IMPLIMENTATION TO EMAIL
        # ADMIN WITH NEW JUSTICE/OPINION/EMAIL COUNTS
        # Notify user if unrecognized justice codes detected
        if new_justices:
            send_mail('[scotuswebcites] New Justice Detected',
                      ', '.join(new_justices),
                      settings.EMAIL_HOST_USER,
                      [settings.CONTACT_EMAIL])

    def ingest_new_opinions(self):
        # Sort opinions by publication date, oldest to newest
        self.discovered_opinions.sort(key=lambda o: o.published)

        for opinion in self.discovered_opinions:
            if opinion.already_exists():
                print 'Skipping: %s' % opinion.name
                continue

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
