# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from scotus import settings
from discovery.Pdf import Pdf
from discovery.Pdf import Url
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
    justice = models.ForeignKey('justices.Justice'); 
    updated = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self.local_pdf = False
        self.republished = False
        self.updated_date = False
        self.previous_publications = []
        self.previous_publication_citations = []
        super(Opinion, self).__init__(*args, **kwargs)

    def get_counts_and_update_date(self):
        self.citation_count = Citation.objects.filter(opinion=self.id).count()
        if self.updated:
            self.updated_date = Opinion.objects.filter(name=self.name).latest('published').published

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

    def was_republished(self):
        prevs = Opinion.objects.filter(name=self.name, justice=self.justice)

        if prevs:
            self.republished = True

            for prev in prevs:
                self.previous_publications.append(prev)

                # Gather previous citations
                for previous in Citation.objects.filter(opinion__name=self.name).exclude(opinion_id=self.id):

                    # prevous scraped
                    self.previous_publication_citations.append(previous.scraped)

                    # previous validated
                    if previous.validated != '0':
                        self.previous_publication_citations.append(previous.validated)

        return self.republished

    def set_updated_on_previously_published(self):
        for prev in self.previous_publications:
            prev.updated = True
            prev.save()

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

            new_citation.yyyymmdd = self.published.replace('-', '')
            new_citation.get_statuses()
            new_citation.save()
