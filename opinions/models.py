# -*- coding: utf-8 -*-

from django.db import models
from scotus import settings
from discovery.Pdf import Pdf
from justices.models import Justice
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
    revised_date = models.DateField('date revised', blank=True, null=True)
    revised_pdf_url = models.URLField(max_length=255, blank=True, null=True)

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
            name=unicode(self.name),
            pdf_url=unicode(self.pdf_url),
            published=unicode(self.published),
            category=unicode(self.category),
            reporter=unicode(self.reporter),
            docket=unicode(self.docket),
            justice=unicode(self.justice),
            part=unicode(self.part)):

            return True

        return False

    # TODO Should this be removed now that there is a revised field?
    # def was_republished(self):
    #     prevs = Opinion.objects.filter(name=self.name, justice=self.justice)
    #
    #     if prevs:
    #         self.republished = True
    #
    #         for prev in prevs:
    #             self.previous_publications.append(prev)
    #
    #             # Gather previous citations
    #             for previous in Citation.objects.filter(opinion__name=self.name).exclude(opinion_id=self.id):
    #
    #                 # prevous scraped
    #                 self.previous_publication_citations.append(previous.scraped)
    #
    #                 # previous validated
    #                 if previous.validated != '0':
    #                     self.previous_publication_citations.append(previous.validated)
    #
    #     return self.republished

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
        for url in self.pdf.urls:
            if url in self.previous_publication_citations:
                print '--Skipping previously discovered citation for %s: %s' % (self.name, url)
                continue

            print '++Ingesting citation: %s' % url
            new_citation = Citation(
                opinion=Opinion(self.id),
                scraped=url,
            )

            new_citation.yyyymmdd = self.published.strftime("%Y%m%d")
            new_citation.get_statuses()
            new_citation.save()
