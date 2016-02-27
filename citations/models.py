from django.db import models
from scotus import settings
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

    opinion = models.ForeignKey('opinions.Opinion')
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
    verify_date = models.DateTimeField(u'date verified', null=True)
    memento = models.URLField(max_length=255, null=True)
    webcite = models.URLField(max_length=255, null=True)
    perma = models.URLField(max_length=255, null=True)

    def get_statuses(self):

        # If not ORM query object, yyyymmdd must be set manually before
        # calling this method
        if self.opinion.published is not None:
            self.yyyymmdd = self.opinion.published.strftime("%Y%m%d")
        elif not hasattr(self, 'yyyymmdd'):
            return

        working_url = self.validated if self.validated else self.scraped
        memento_url = "%s/%s/%s" % (Citation.MEMENTO, self.yyyymmdd, working_url)

        request = Url.get(working_url)

        if not request or request.status_code == 404:
            self.status = 'u'

        # 300 status codes aren't captured, so must compare before and after urls
        elif request and (request.url != working_url):
            if request.url != working_url + '/':
                if request.url.split('://')[1] != working_url.split('://')[1]:
                    self.status = 'r'

        request = Url.get(memento_url)

        if request and request.status_code == 200:
            self.memento = memento_url

    def csv_row(self):
        ST = Citation.STATUSES
        st = self.status
        SE = Citation.SCRAPE_EVALUATIONS
        se = self.scrape_evaluation

        self.st = [x[1] for x in ST if x[0] == st][0]
        self.se = [x[1] for x in SE if x[0] == se][0]
        

        for attr in self.__dict__:
            if attr == 'opinion' or attr.startswith('_'):
                continue

            data = getattr(self, attr)

            if data is None:
                data = ''
            elif not type(data) in [str, unicode]:
                data = str(data)

            setattr(self, attr, data.encode('utf8'))

        self.opinion.name = self.opinion.name.encode('utf8')
        self.opinion.justice.name = self.opinion.justice.name.encode('utf8')
        self.opinion.category = self.opinion.category.encode('utf8')
        self.opinion.published = self.opinion.published.strftime('%Y-%m-%d').encode('utf8')
        self.opinion.discovered = self.opinion.discovered.strftime('%Y-%m-%d').encode('utf8')
        self.opinion.pdf_url = self.opinion.pdf_url.encode('utf8')
        self.opinion.reporter = self.opinion.reporter.encode('utf8')
        self.opinion.docket = self.opinion.docket.encode('utf8')
        self.opinion.part = self.opinion.part.encode('utf8')
        

        return [
            self.scraped,
            self.validated,
            self.verify_date,
            self.se,
            self.st,
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


    #TODO: add pertinent metadat to via api queries below
    #TODO: handle try exceptions more fully
    def get_ondemand_captures(self):
        if not self.validated:
            return

        self.webcite_api_capture()
        self.perma_api_capture()

    def webcite_api_capture(self):
        if not settings.WEBCITE['enabled']:
            return

        from requests import post
        import xml.etree.ElementTree as ET
        
        archive = settings.WEBCITE['api_query'] % (self.validated, settings.CONTACT_EMAIL)
        response = post(archive)
        xml = response.text
        root = ET.fromstring(xml)

        try:
            self.webcite = root.findall('resultset')[0].findall('result')[0].findall('webcite_url')[0].text
        except:
            return

        
    def perma_api_capture(self):
        if not settings.PERMA['enabled']:
            return

        import json
        from requests import post

        data = {
            'url': self.validated,
            'title': 'SCOTUS Opinion Citation',
        }
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }

        try:
            response = post(
                settings.PERMA['api_query'] % settings.PERMA['api_key'],
                data=json.dumps(data),
                headers=headers,
            )
            archive_dict = json.loads(response.text)
            self.perma = '%s/%s' % (settings.PERMA['archive_base'], archive_dict['guid'])
        except:
            return
