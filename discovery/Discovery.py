# -*- coding: utf-8 -*-

import lxml.html
import traceback
from dateutil import parser

from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from scotus import settings
from discovery.Pdf import Url
from discovery.Logger import Logger
from opinions.models import Opinion
from justices.models import Justice


class Discovery:
    def __init__(self):
        self.discovered_opinions = []
        self.new_opinions = []
        self.category_urls = []
        self.pdfs_to_scrape = []
        self.new_justices = []
        self.failed_scrapes = []
        self.ingested_citations_count = 0
        self.BASE = 'http://www.supremecourt.gov'
        self.OPINIONS_BASE = self.BASE + '/opinions/'
        self.OPINIONS_MAIN_PAGE = self.OPINIONS_BASE + 'opinions.aspx'
        self.YYYYMMDD = timezone.now().strftime('%Y%m%d')

    def run(self):
        Logger.info('INITIATING DISCOVERY: %s' % timezone.now())
        Logger.info('[**%s**]' % self.OPINIONS_MAIN_PAGE)
        self.fetch_opinion_category_urls()
        self.get_opinions_from_categories()
        Logger.info('INITIATING OPINION INGEST')
        self.ingest_new_opinions()
        Logger.info('INITIATION CITATION SCRAPING AND INGEST')
        self.ingest_new_citations()
        Logger.info('DISCOVERY COMPLETE')

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

        for category_url in self.category_urls:
            category = category_url.split('/')[-2]
            request = Url.get(category_url)    

            if request and request.status_code == 200:
                Logger.info('EXTRACTING OPINIONS FROM %s' % category_url)

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
                        Logger.info('Discovered: %s' % row_data['Name'])

                        # Validate the justice, or add new record for him/her
                        if not Justice.objects.filter(id=row_data['J.']):
                            self.new_justices.append(row_data['J.'])
                            justice = Justice(id=row_data['J.'], name=row_data['J.'])
                            justice.save()

                        # Convert all scraped data to unicode
                        for label, data in row_data.iteritems():
                            if data:
                                row_data[label] = unicode(data)

                        # Create new opinion record from row data
                        self.discovered_opinions.append(Opinion(
                            category=category,
                            reporter=row_data['R-'] if 'R-' in row_data else None,
                            published=self.convert_date_string(row_data['Date']),
                            docket=row_data['Docket'],
                            name=row_data['Name'],
                            pdf_url=self.BASE + row_data['Name_Url'],
                            justice=Justice(row_data['J.']),
                            part=row_data['Pt.'],
                            discovered=timezone.now(),
                        ))

                        # Create opinions for revision, if it exists
                        if 'Revised' in row_data and row_data['Revised']:
                            Logger.info('Discovered REVISION: %s' % row_data['Name'])
                            self.discovered_opinions.append(Opinion(
                                category=category,
                                reporter=row_data['R-'] if 'R-' in row_data else None,
                                published=self.convert_date_string(row_data['Revised']),
                                docket=row_data['Docket'],
                                name='%s [REVISION]' % row_data['Name'],
                                pdf_url=self.BASE + row_data['Revised_Url'],
                                justice=Justice(row_data['J.']),
                                part=row_data['Pt.'],
                                discovered=timezone.now(),
                            ))

    def ingest_new_opinions(self):
        # Sort opinions by publication date, oldest to newest
        self.discovered_opinions.sort(key=lambda o: o.published)

        for opinion in self.discovered_opinions:
            if opinion.already_exists():
                Logger.info('Skipping: %s' % opinion.name)
                continue

            Logger.info('Ingesting: %s  %s' % (opinion.name, opinion.pdf_url))

            opinion.save()
            self.new_opinions.append(opinion)
            
    def ingest_new_citations(self):
        for opinion in self.new_opinions:
            Logger.info('Downloading: %s  %s' % (opinion.name, opinion.pdf_url))
            opinion.download()
            Logger.info('Scraping: %s  %s' % (opinion.name, opinion.local_pdf))

            try:
                opinion.scrape()
            except:
                Logger.error(traceback.format_exc())
                self.failed_scrapes.append(opinion.name)

            if opinion.pdf.urls:
                Logger.info('Ingesting citations from %s' % opinion.name)
                opinion.ingest_citations()
                self.ingested_citations_count += opinion.ingested_citation_count

    def _send_email_report(self):
        if settings.EMAIL_HOST_USER != 'YOUR_GMAIL_ADDRESS':
            if self.new_opinions or self.new_justices or self.ingested_citations_count or self.failed_scrapes:
                subject = '[scotuswebcites] New Data Discovered'
                recipient = settings.CONTACT_EMAIL
                sender = settings.EMAIL_HOST_USER
                context = Context({
                    'new_opinions_count': str(len(self.new_opinions)),
                    'ingested_citations_count': str(self.ingested_citations_count),
                    'new_justices': self.new_justices,
                    'failed_scrapes': self.failed_scrapes,
                    'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else False,
                })
                body = get_template('discovery_report_email.html').render(context)
                Logger.info('+sending discovery report email from %s to %s' % (sender, recipient))
                msg = EmailMultiAlternatives(subject, body, sender, [recipient])
                msg.attach_alternative(body, "text/html")
                msg.send()
