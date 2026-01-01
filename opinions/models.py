# -*- coding: utf-8 -*-

from django.db import models
from scotuswebcites import settings
from discovery.Pdf import Pdf


class Opinion(models.Model):

    category = models.CharField(max_length=100)
    discovered = models.DateTimeField('date discovered')
    published = models.DateField('date published')
    name = models.CharField(max_length=255)
    pdf_url = models.URLField(max_length=255)
    reporter = models.CharField(max_length=50, blank=True, null=True)
    docket = models.CharField(max_length=20)
    part = models.CharField(max_length=20)
    justice = models.ForeignKey(
        'justices.Justice',
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        self.local_pdf = False
        super(Opinion, self).__init__(*args, **kwargs)

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
