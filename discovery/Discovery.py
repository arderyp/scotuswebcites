# -*- coding: utf-8 -*-

import lxml.html
import traceback
from dateutil import parser
from typing import Dict
from typing import List
from django.utils import timezone
from django.template.loader import get_template
from scotuswebcites import settings
from discovery.Pdf import Url
from discovery.Logger import Logger
from citations.models import Citation
from opinions.models import Opinion
from justices.models import Justice
from scotuswebcites.mail import send_email


class Discovery:
    TABLE_HEADER_FORMATS = [
        ['R-', 'Date', 'Docket', 'Name', 'Revised', 'J.', 'Citation'],
        ['R-', 'Date', 'Docket', 'Name', 'Revised', 'J.', 'Pt.'],

        ['R-', 'Date', 'Docket', 'Name', 'J.', 'Citation'],
        ['R-', 'Date', 'Docket', 'Name', 'J.', 'Pt.'],

        ['Date', 'Docket', 'Name', 'Revised', 'J.', 'Citation'],
        ['Date', 'Docket', 'Name', 'Revised', 'J.', 'Pt.'],

        ['Date', 'Docket', 'Name', 'J.', 'Citation'],
        ['Date', 'Docket', 'Name', 'J.', 'Pt.'],

        ['Term Year', 'Docket', 'Name', 'Revised', 'J.', 'Citation'],
        ['Term Year', 'Docket', 'Name', 'Revised', 'J.', 'Pt.'],

        ['Term Year', 'Date', 'Docket', 'Name', 'Revised', 'J.', 'Citation'],
        ['Term Year', 'Date', 'Docket', 'Name', 'Revised', 'J.', 'Pt.'],
    ]

    def __init__(self):
        self.BASE = 'http://www.supremecourt.gov'
        self.OPINIONS_BASE = self.BASE + '/opinions/'
        self.OPINIONS_MAIN_PAGE = self.OPINIONS_BASE + 'opinions.aspx'
        self.PATH_TABLES = "//table[@class='table table-bordered']"
        self.PATH_TABLE_ROWS = "%s/tr" % self.PATH_TABLES
        self.PATH_HEADERS = './/th/text()'
        self.START_TERM = 11  # 2011
        self.now = timezone.now()
        self.YYYYMMDD = self.now.strftime('%Y%m%d')

        self.category_urls = []
        self.pdfs_to_scrape = []
        self.failed_scrapes = []
        self.discovered_opinions = []
        self.new_justices = []
        self.new_opinions = []
        self.duplicate_opinions = []
        self.count_citations_ingested = 0
        self.count_citations_duplicate = 0

    def run(self):
        Logger.info('INITIATING DISCOVERY: %s' % self.now)
        Logger.info('[**%s**]' % self.OPINIONS_MAIN_PAGE)
        self.fetch_opinion_category_urls()
        self.get_opinions_from_categories()
        Logger.info('INITIATING OPINION INGEST')
        self.ingest_new_opinions()
        Logger.info('INITIATION CITATION SCRAPING AND INGEST')
        self.ingest_new_citations()
        Logger.info('DISCOVERY COMPLETE: %s' % self.now)

    def convert_date_string(self, date_string):
        """Convert date string into standard date object"""
        return parser.parse(date_string).date()

    def fetch_opinion_category_urls(self):
        """Find opinion page urls to scrape.

        We loop over the side navigation menu to find the
        appropriate slip, relating, and chambers urls for
        the current term. The chambers url is actually a
        static url that doesn't change each term. The slip
        and relating sections get a new url each term; so,
        my need to dynamically generate the historic urls
        by determining the current term, and generating all
        urls from the 2011 term to the current."""
        request = Url.get(self.OPINIONS_MAIN_PAGE)

        if request and request.status_code == 200:
            html = lxml.html.fromstring(request.text)
            search = "//ul[@class='sidenav-list']/li/a/@href"
            for href in html.xpath(search):
                if 'in-chambers' in href:
                    # The new SCOTUS site houses all chambers opinions
                    # on a single page now, so we don't need to dynamically
                    # generate chambers urls for previous terms.
                    self.category_urls.append(self.OPINIONS_BASE + href)
                elif 'slipopinion' in href or 'relatingtoorders' in href:
                    # Generate slip and relating urls for each term between
                    # starting term (2011) and current term
                    href_parts = href.rsplit('/', 1)
                    current_term = int(href_parts[1])
                    term_range = range(self.START_TERM, current_term + 1)
                    for term in term_range:
                        self.category_urls.append('%s%s/%d' % (self.OPINIONS_BASE, href_parts[0], term))

    def get_cell_labels(self, cells, table_headers):
        """We shouldn't have to do this, but the SCOTUS site has a
        persistent problem whereby malformed tables are not uncommon.
        Sporadically a table with have the header and some rows in the
        COLUMN_LABELS_LEGACY format, and other rows in the newer
        COLUMN_LABELS format. Ive contacted the court about this many
        times, and often times they clear their CDN cache the resolve
        the problem, but its become such a reoccurring annoyance that
        I felt the need to implement this workaround. The court hasn't
        provided any indication in our communication that they have any
        understanding of the problem or why it is happening.
        """
        count_cell = len(cells)
        count_headers = len(table_headers)
        acceptable_headers_counts = [len(f) for f in self.TABLE_HEADER_FORMATS]
        if count_cell != count_headers:
            cell_data = ', '.join([c.text_content() for c in cells])
            Logger.warning(
                'Cell/Header mismatch, found %d headers but %d cells: %s'
                % (count_headers, count_cell, cell_data)
            )
        if count_cell not in acceptable_headers_counts:
            raise RuntimeError(
                'Row has an unfamiliar number of cells: %d' % count_cell
            )
        for header_format in self.TABLE_HEADER_FORMATS:
            # First header element must match first element from
            # expected table_headers, since there are multiple
            # formats with the same length
            if len(header_format) == count_cell and header_format[0] == table_headers[0]:
                return header_format
        raise RuntimeError('Should never reach this error')

    def get_opinions_from_categories(self):
        for category_url in self.category_urls:
            request = Url.get(category_url)

            if self.is_us_report_url(request.url):
                # Not sure why, but the court website started doing this in some instances instead of
                # returning 404, 3xx, or blank page. These U.S. Reports pages have gigantic compilation
                # files consisting of huge collections of opinions that we already have, triggering
                # massive duplicate discoveries
                Logger.info('SKIPPING BLIND REDIRECT TO COMPILED U.S. REPORTS URL FROM: %s' % category_url)
                continue

            if not request:
                Logger.info('FAILED FETCHING: %s' % category_url)
                continue

            if request.status_code != 200:
                Logger.info('SKIPPING NNON-200 STATUS CODE [%d]: %s' % (request.status_code ,category_url))
                continue

            Logger.info('EXTRACTING OPINIONS FROM %s' % category_url)
            html = lxml.html.fromstring(request.text)

            if not html.xpath(self.PATH_TABLES):
                # Its a new term with an empty page, no table yet
                Logger.info('SKIPPING BLANK PAGE: %s' % category_url)
                continue

            table_headers = self.get_table_headers(html)

            for row in html.xpath(self.PATH_TABLE_ROWS):
                cells = row.xpath('td')
                if not cells:
                    continue

                revisions = []
                row_data = {}
                cell_index = 0
                cell_labels = self.get_cell_labels(cells, table_headers)

                # Parse data from rows in table
                for cell in cells:
                    cell_label = cell_labels[cell_index]
                    text = cell.text_content().strip()

                    # Skip rows with empty first cell, these
                    # can appear at the start of a new cycle
                    # when scotus adds new date pages that
                    # do not yet have records
                    if cell_index == 0 and not text:
                        break

                    if cell_label == 'Revised':
                        # Revised cells can have multiple links
                        # so we must have special handling for it
                        for anchor in cell.xpath('a'):
                            revisions.append({
                                'href': anchor.xpath('@href')[0],
                                'date_string': anchor.text_content(),
                            })
                    else:
                        row_data[cell_label] = text if text else None
                        if cell.xpath('a'):
                            href = cell.xpath('a/@href')
                            row_data[cell_label + '_Url'] = href[0] if href else None

                    cell_index += 1

                if row_data:
                    Logger.info('Discovered: %s' % row_data['Name'])

                    # Validate the justice, or add new record for him/her
                    if not Justice.objects.filter(id=row_data['J.']):
                        self.new_justices.append(row_data['J.'])
                        justice = Justice(id=row_data['J.'], name=row_data['J.'])
                        justice.save()

                    # Convert all scraped data to uniform unicode string
                    for label, data in row_data.items():
                        if data:
                            row_data[label] = str(data)

                    category = category_url.split('/')[-2]
                    part = row_data['Pt.'] if 'Pt.' in row_data else row_data['Citation']

                    # Create new opinion record from row data
                    self.discovered_opinions.append(Opinion(
                        category=category,
                        reporter=row_data['R-'] if 'R-' in row_data else None,
                        published=self.convert_date_string(row_data['Date']),
                        docket=row_data['Docket'],
                        name=row_data['Name'],
                        pdf_url=self.BASE + row_data['Name_Url'],
                        justice=Justice(row_data['J.']),
                        part=part,
                        discovered=self.now,
                    ))

                    # Create opinions for revision, if it exists
                    for revision in revisions:
                        date_string = revision['date_string']
                        href = revision['href']
                        Logger.info('Discovered: REVISION: %s' % row_data['Name'])
                        self.discovered_opinions.append(Opinion(
                            category=category,
                            reporter=row_data['R-'] if 'R-' in row_data else None,
                            published=self.convert_date_string(date_string),
                            docket=row_data['Docket'],
                            name='%s [REVISION]' % row_data['Name'],
                            pdf_url=self.BASE + href,
                            justice=Justice(row_data['J.']),
                            part=part,
                            discovered=self.now,
                        ))

    def get_table_headers(self, html):
        headers = False
        table_count = 1
        for table in html.xpath(self.PATH_TABLES):
            headers = table.xpath(self.PATH_HEADERS)
            if headers not in self.TABLE_HEADER_FORMATS:
                headers_string = ', '.join(headers)
                raise RuntimeError(
                    'Unfamiliar headers in table %d: %s'
                    % (table_count, headers_string)
                )
            table_count += 1
        if not headers:
            raise RuntimeError('Table is missing headers')
        return headers

    def ingest_new_opinions(self):
        # Sort opinions by publication date, oldest to newest
        self.discovered_opinions.sort(key=lambda o: o.published)
        for opinion in self.discovered_opinions:
            if self.opinion_already_exists(opinion):
                Logger.info('Skipping, already exists: %s' % opinion.name)
                continue
            if self.is_us_report_url(opinion.pdf_url):
                # I don't know why, but some opinion links point to these compiled U.S. Reports
                Logger.info('Skipping, U.S. Report compilation url: %s : %s' % (opinion.name, opinion.pdf_url))
                continue
            Logger.info('Ingesting: %s %s' % (opinion.name, opinion.pdf_url))
            opinion.save()
            self.new_opinions.append(opinion)

    def opinion_already_exists(self, opinion: Opinion) -> bool:
        return bool(
            Opinion.objects.filter(
                name=opinion.name,
                pdf_url=opinion.pdf_url,
                published=opinion.published,
                category=opinion.category,
                reporter=opinion.reporter,
                docket=opinion.docket,
                justice=opinion.justice
            )
        )
            
    def ingest_new_citations(self):
        for opinion in self.new_opinions:
            Logger.info('Downloading: %s %s' % (opinion.name, opinion.pdf_url))
            opinion.download()
            Logger.info('Scraping: %s %s' % (opinion.name, opinion.local_pdf))
            try:
                opinion.scrape()
            except:
                Logger.error(traceback.format_exc())
                self.failed_scrapes.append(opinion.name)
            if opinion.pdf.urls:
                self.ingest_new_citations_from_opinion(opinion)


    def ingest_new_citations_from_opinion(self, opinion: Opinion):
        Logger.info('Ingesting citations from %s' % opinion.name)
        # citations = [];
        citations_previous = self.get_citation_from_previous_publications(opinion)
        for url in opinion.pdf.urls:
            Logger.info('++Ingesting citation: %s' % url)
            citation = Citation(opinion=Opinion(opinion.id), scraped=url)
            citation.yyyymmdd = opinion.published.strftime("%Y%m%d")
            citation_previous = citations_previous[url] if url in citations_previous else None
            if not citation_previous:
                # Logger.info('++++Found NEW citation on duplicate opinion %s: %s' % (opinion.name, url))
                citation.get_statuses()  # check statuses on novel citation url
            elif not citation_previous.perma:
                Logger.info('++++Re-queuing known not-previously-perma-ed citation on duplicate opinion %s: %s' % (opinion.name, url))
                citation.get_statuses()  # check statuses on novel citation url
            else:
                # Detect duplicate/revised opinion, recycle previous validations and perma links.
                # The court often touched the same documents many times making working changes but leaving
                # the same web citations. If the opinion has tons of citations, this causes lots of
                # duplicate manual labor. Instead, we will simply re-use the perma links we created
                # for any citations with a direct match from the original opinion.
                Logger.info('~~~~Auto-validating duplicate citation on duplicate opinion %s: %s' % (opinion.name, url))
                citation.memento = citation_previous.memento
                citation.notified_subscribers = self.now
                citation.perma = citation_previous.perma
                citation.scrape_evaluation = citation_previous.scrape_evaluation
                citation.status = 'x';
                citation.validated = citation_previous.validated
                citation.verify_date = self.now
                citation.webcite = citation_previous.webcite
                self.count_citations_duplicate += 1
            citation.save()
            self.count_citations_ingested += 1

    # track all unique citations from all previous discoveries of opinion
    def get_citation_from_previous_publications(self, opinion: Opinion) -> Dict[str, Citation]:
        citations = {}
        previous_publications = self.get_previous_publications_of_opinion(opinion)
        if previous_publications:
            self.duplicate_opinions.append(opinion)
        for previous_publication in previous_publications:
            for citation in Citation.objects.filter(opinion_id=previous_publication.id):
                scraped = citation.scraped
                if scraped not in citations:
                    citations[scraped] = citation
        return citations

    # return list of early opinion derivations.
    # the court touches/updates records all the time, duplicating opinions in various drafts.
    def get_previous_publications_of_opinion(self, opinion: Opinion) -> List[Opinion]:
        try:
            return Opinion.objects.filter(
                name=opinion.name.strip(' [REVISION]').split(' Revisions: ')[0],
                published=opinion.published,
                category=opinion.category,
                reporter=opinion.reporter,
                docket=opinion.docket,
                justice=opinion.justice,
            )
        except Opinion.DoesNotExist:
            return []

    def send_email_report(self):
        if settings.EMAIL_HOST_USER != 'YOUR_GMAIL_ADDRESS':
            if self.new_opinions or self.new_justices or self.count_citations_ingested or self.failed_scrapes:
                count_opinions_new = len(self.new_opinions)
                count_opinions_duplicate = len(self.duplicate_opinions)
                subject = '[scotuswebcites] New Data Discovered'
                template_parameters = {
                    'count_opinions_new': str(count_opinions_new),
                    'count_opinions_duplicate': str(count_opinions_duplicate),
                    'count_citations_ingested': str(self.count_citations_ingested),
                    'count_citations_duplicate': str(self.count_citations_duplicate),
                    'count_citations_to_validate': str(self.count_citations_ingested - self.count_citations_duplicate),
                    'new_justices': self.new_justices,
                    'failed_scrapes': self.failed_scrapes,
                    'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else False,
                }
                body = get_template('discovery_report_email.html').render(template_parameters)
                Logger.info('+sending discovery report email from %s to %s' % (settings.SENDER_EMAIL, settings.CONTACT_EMAIL))
                send_email(subject, body, settings.CONTACT_EMAIL)

    def is_us_report_url(self, url: str) -> bool:
        return url.endswith('USReports.aspx') or '/preliminaryprint/' in url or '/boundvolumes/' in url