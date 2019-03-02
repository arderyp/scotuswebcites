# -*- coding: utf-8 -*-

from django.db import models
from scotuswebcites import settings
from discovery.Url import Url


class Citation(models.Model):
    SCRAPE_EVALUATIONS = (
        (u'gs', u'good scrape'),
        (u'bs', u'bad scrape'),
        (u'bc', u'bad citation'),
    )
    STATUSES = (
        (u'a', u'available'),
        (u'u', u'unavailable'),
        (u'r', u'redirect'),
    )
    MEMENTO = 'http://timetravel.mementoweb.org/list'

    opinion = models.ForeignKey(
        'opinions.Opinion',
        on_delete=models.CASCADE,
    )
    scraped = models.URLField(max_length=255)
    scrape_evaluation = models.CharField(
        max_length=2,
        choices=SCRAPE_EVALUATIONS,
        default=u'gs'
    )
    status = models.CharField(
        max_length=1,
        choices=STATUSES,
        default=u'a'
    )
    validated = models.URLField(max_length=255, null=True)
    verify_date = models.DateTimeField(u'date verified by admin', null=True)
    memento = models.URLField(max_length=255, null=True)
    webcite = models.URLField(max_length=255, null=True)
    perma = models.URLField(max_length=255, null=True)
    notified_subscribers = models.DateTimeField(
        u'date subscribers notified of validated citation url',
        blank=True,
        null=True
    )

    def get_statuses(self):

        # If not ORM query object, yyyymmdd must be set manually
        # before calling this method
        if self.opinion.published is not None:
            self.yyyymmdd = self.opinion.published.strftime("%Y%m%d")
        elif not hasattr(self, 'yyyymmdd'):
            return

        working_url = self.validated if self.validated else self.scraped
        memento_url = "%s/%s/%s" % (Citation.MEMENTO, self.yyyymmdd, working_url)

        request = Url.get(working_url)

        if not request or request.status_code == 404:
            # invalid resource
            self.status = 'u'
        elif request.status_code // 100 == 2:
            # valid 2xx response
            self.status = 'a'
        elif request and (request.url != working_url):
            # 3xx status codes aren't captured, so must compare before and after urls
            if request.url != working_url + '/':
                if request.url.split('://')[1] != working_url.split('://')[1]:
                    self.status = 'r'

        request = Url.get(memento_url)

        if request and request.status_code == 200:
            self.memento = memento_url

    def csv_row(self):
        """Return pertinent data for csv report.

        All emtpy/null values are converted to blank strings (''),
        and all date/datetime objects are converted to yyyy-mm-dd
        format. All data is ultimately encoded before being written,
        which turns out to be necessary.
        """
        from datetime import date, datetime

        self.status_string = [x[1] for x in Citation.STATUSES if x[0] == self.status][0]
        self.evaluation_string = [x[1] for x in Citation.SCRAPE_EVALUATIONS if x[0] == self.scrape_evaluation][0]

        data = [
            self.scraped,
            self.validated,
            self.verify_date,
            self.evaluation_string,
            self.status_string,
            self.memento,
            self.webcite,
            self.perma,
            self.opinion.name,
            self.opinion.justice.name,
            self.opinion.category,
            self.opinion.published,
            self.opinion.discovered,
            self.opinion.pdf_url,
            self.opinion.reporter,
            self.opinion.docket,
            self.opinion.part,
        ]

        # Standardize and encode fields is necessary to print csv data
        encoded_data = []
        for item in data:
            if not item:
                item = ''
            elif isinstance(item, date) or isinstance(item, datetime):
                item = item.strftime('%Y-%m-%d')
            encoded_data.append(item)

        return encoded_data

    def get_ondemand_captures(self):
        if not self.validated:
            return

        self.webcite_api_capture()
        self.perma_api_capture()

