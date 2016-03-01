# -*- coding: utf-8 -*-

from django.db import models
from scotus import settings
from discovery.Pdf import Pdf
from discovery.Logger import Logger
from citations.models import Citation

class Opinion(models.Model):

    category = models.CharField(max_length=100)
    discovered = models.DateTimeField('date discovered')
    published = models.DateField('date published')
    name = models.CharField(max_length=255)
    pdf_url = models.URLField(max_length=255)
    reporter = models.CharField(max_length=50, blank=True, null=True)
    docket = models.CharField(max_length=20)
    part = models.CharField(max_length=20)
    justice = models.ForeignKey('justices.Justice')

    def __init__(self, *args, **kwargs):
        self.local_pdf = False
        self.republished = False
        self.previous_publications = []
        self.previous_publication_citations = []
        super(Opinion, self).__init__(*args, **kwargs)

    def get_counts_and_update_date(self):
        self.citation_count = Citation.objects.filter(opinion=self.id).count()

    def already_exists(self):
        if Opinion.objects.filter(
            name=self.name,
            pdf_url=self.pdf_url,
            published=self.published,
            category=self.category,
            reporter=self.reporter,
            docket=self.docket,
            justice=self.justice,
            part=self.part):

            return True

        return False

    def get_local_pdf(self):
        if not self.id:
            return False

        self.local_pdf = settings.PDF_DIR + str(self.id) + '.pdf'
        return self.local_pdf

    def download(self):
        if not self.local_pdf:
            self.get_local_pdf()

        self.pdf = Pdf(
            self.pdf_url,
            self.local_pdf,
        )

        self.pdf.download()
        

    def scrape(self):
        if self.pdf:
            self.pdf.scrape_urls()

    def ingest_citations(self):
        self.ingested_citation_count = 0

        for url in self.pdf.urls:
            if url in self.previous_publication_citations:
                Logger.info('--Skipping previously discovered citation for %s: %s' % (self.name, url))
                continue

            Logger.info('++Ingesting citation: %s' % url)

            new_citation = Citation(
                opinion=Opinion(self.id),
                scraped=url,
            )

            new_citation.yyyymmdd = self.published.strftime("%Y%m%d")
            new_citation.get_statuses()
            new_citation.save()
            self.ingested_citation_count += 1
